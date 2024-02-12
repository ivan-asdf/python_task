import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from app.models import Contact, CollectorJob

from .common import change_job_status, create_contact

MAX_DEPTH = 10  # Max depth for following links
MAX_PAGES = 200  # Max pages to download
TIME_LIMIT = 180  # Max time task runs
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "en-US",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101"
        " Firefox/54.0"
    ),
}


def get_protocol(domain):
    url = "http://" + domain
    try:
        r = requests.get(url, timeout=10, headers=DEFAULT_REQUEST_HEADERS)
    except requests.ConnectionError as e:
        print(f"Error fetching {url}: {e}")
        return None

    url = get_root_url(r.url)
    print(f"PROTOCOL_URL: {url}")
    return url


def get_html(url):
    try:
        response = requests.get(
            url, timeout=10, headers=DEFAULT_REQUEST_HEADERS
        )
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return ""
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


def normalize_url(href):
    if not href.startswith("http"):
        if not href.startswith("/"):
            href = "/" + href

    return href.rstrip("/")


def get_root_url(url):
    parsed_url = urlparse(url)
    root_url = parsed_url.scheme + "://" + parsed_url.netloc
    return root_url


def contains_substring(element, s):
    # If contained in total text
    if s in element.get_text():
        return True

    # If contained in tag name
    if s in element.name:
        return True

    # If contained in attribute name or value
    for attr, value in element.attrs.items():
        if isinstance(value, list):
            value = " ".join(value)
        if s in attr or s in value:
            return True
    return False


def parse_page_for_phone(soup):
    keywords = ["phone", "tel", "mobile"]
    # Create a list of potentialy searchable elements
    # Gather all elements that contain(as substring) the keywords in:
    # attribute keys, attribute values, tag names and text
    searchable_elements = []
    for word in keywords:
        for element in soup.find_all():
            if contains_substring(element, word):
                # Include children of element
                # The keyword might be contained in element several levels up
                # from a target element that holds just the phone
                for e in element.find_all(recursive=True):
                    searchable_elements.append(e)
                    parent = e.parent
                    # Include siblings of element
                    # A sibling might contain the keyword
                    # While the target element might contain just the phone
                    for sibling in parent.children:
                        searchable_elements.append(sibling)

    # Gist of the regex:
    # Search for a phone number that is the ONLY content inside an element
    # It is between 5-15 digits
    # It might have spaces(0 to 2) between the digits
    # It might be prefixed: mobile:, tel:, phone: & whitespace characters
    regex = r"^(?:[^a-zA-Z\d\+])*(?:mobile:\s*)?(?:tel:\s*)?(?:phone:\s*)?((?:\+?[\s\-()]{0,2}[\d()*][\s\-()]{0,2}){5,15})(?:[^a-zA-Z\d])*$"
    for e in searchable_elements:
        text = e.get_text()
        if text != "":
            match = re.search(regex, text)
            if match:
                return match.group(1).strip()

    return None


def parse_page_for_email(soup):
    regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    text = soup.get_text()

    match = re.search(regex, text)
    if match:
        return match.group(0).strip()


def crawl_web_pages(url_and_data, depth):
    if depth >= MAX_DEPTH:
        yield None

    new_url_and_data = {}
    for url in url_and_data:
        if url_and_data[url] is None:

            html = get_html(url)
            url_and_data[url] = html
            soup = BeautifulSoup(html, "html.parser")
            for data in soup(["style", "script"]):
                data.decompose()
            yield soup

            links = soup.find_all("a", href=True)
            for link in links:
                href = link["href"]
                if href.startswith(get_root_url(url)):  # Absolute URL
                    page_url = normalize_url(href)
                elif href.startswith("http"):  # Foreign domain absolute URL
                    continue
                else:  # Relative URL
                    page_url = url + normalize_url(href)

                new_url_and_data[page_url] = None

    yield from crawl_web_pages({**new_url_and_data, **url_and_data}, depth + 1)


@shared_task(soft_time_limit=TIME_LIMIT)
def run_scrape_job(collector_job_id):
    try:
        job = CollectorJob.objects.get(pk=collector_job_id)
        change_job_status(job)

        base_url = get_protocol(job.domain.name)
        if base_url is None:
            job.status = CollectorJob.INVALID
            job.save()
            return

        phone_set = False
        email_set = False
        page_gen = crawl_web_pages({base_url: None}, 0)
        for _ in range(MAX_PAGES):
            soup = next(page_gen)
            if soup is None:
                break

            if not phone_set:
                phone = parse_page_for_phone(soup)
                if phone:
                    create_contact(job, Contact.PHONE, phone)
                    phone_set = True

            if not email_set:
                email = parse_page_for_email(soup)
                if email:
                    create_contact(job, Contact.EMAIL, email)
                    email_set = True

            if email_set and phone_set:
                break

    except SoftTimeLimitExceeded:
        print("Task timed out")
        job.status = CollectorJob.COMPLETED
        job.save()
    else:
        job.status = CollectorJob.COMPLETED
        job.save()
