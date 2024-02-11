from celery import shared_task
from django.db import Error
from .models import Contact, CollectorJob
from .constants import ERRORS

import whois
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re


def make_sure_list(string_or_list):
    if isinstance(string_or_list, str):
        return [string_or_list]
    elif isinstance(string_or_list, list):
        return string_or_list
    else:
        raise TypeError("Input must be either a string or a list")


def create_contact_from_data(whois_data, whois_data_key, contact_type, job):
    if (contact_type != Contact.EMAIL) and (contact_type != Contact.PHONE):
        raise Error("Invalid contact_type give.")

    if whois_data_key in whois_data:
        contact_data = whois_data[whois_data_key]
        if contact_data is not None:
            contact_data = make_sure_list(contact_data)
            for contact in contact_data:
                Contact.objects.create(
                    user=job.collector.user,
                    domain=job.domain,
                    collector=job.collector,
                    collector_job=job,
                    contact_type=contact_type,
                    contact=contact,
                )


def change_job_status(job):
    status = job.status
    if status == CollectorJob.CREATED:
        job.status = CollectorJob.RUNNING
        job.save()
    elif status == CollectorJob.RUNNING:
        pass
    else:
        raise Error(ERRORS.RUNNING_ALREADY_COMPLETE_COLLECTOR_JOB)


@shared_task
def run_whois_job(collector_job_id):
    job = CollectorJob.objects.get(pk=collector_job_id)
    change_job_status(job)

    try:
        whois_data = whois.whois(job.domain.name)
    except whois.parser.PywhoisError as e:
        print(f"python-whois error: {e}")
        job.status = CollectorJob.INVALID
        job.save()
    else:
        print(whois_data)
        create_contact_from_data(
            whois_data,
            "emails",
            Contact.EMAIL,
            job,
        )
        create_contact_from_data(
            whois_data,
            "phone",
            Contact.PHONE,
            job,
        )

        job.status = CollectorJob.COMPLETED
        job.save()


def get_protocol(domain):
    url = "http://" + domain
    r = requests.get(url, timeout=10, headers={"Accept-Language": "en-US"})
    # for h in r.history:
    #     print(h, h.url)

    url = get_root_url(r.url)
    print(f"PROTOCOL_URL: {url}")
    return url


def get_html(url):
    # try:
    #     urlparse(url)
    # except Error as e:
    #     print(f"Invalid url {url}: {e}")
    #     return ""

    try:
        response = requests.get(
            url, timeout=10, headers={"Accept-Language": "en-US"}
        )
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return ""
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


def sanitize(href):
    if not href.startswith("http"):
        if not href.startswith("/"):
            href = "/" + href

    return href.rstrip("/")


def get_root_url(url):
    parsed_url = urlparse(url)
    root_url = parsed_url.scheme + "://" + parsed_url.netloc
    # print(f"URL {root_url}")
    return root_url

    # Find the index of the third '/' occurrence
    # index = url.find('/', 8)
    # if index != -1:
    #     return url[:index]
    # else:
    #     return url


def parse_page_for_phone(text):
    # Define the regex pattern
    # regex_pattern = r'(?:(?:\+|00)([1-9]\d{0,2})[.\- ]?)?(?:(?:\([1-9]\d{0,3}\)[.\- ]?)?(?:[1-9]\d{2}[.\- ]?|[1-9]\d{3}[.\- ]?)(?:\d{3}[.\- ]?\d{4}))'
    # +123-456-7890
    # (123) 456 7890
    # 123.456.7890
    # 1234567890k
    # regex1 = r"\b(?:\+?\d{1,3}[-.●\s]?)?\(?\d{3}\)?[-.●\s]?\d{3}[-.●\s]?\d{4}\b"
    # regex2 = r"^\+(?:1\s?)?\(\d{3}\)\s?\d{3}-\d{4}$"

    # patterns = [
    #     regex1,
    #     regex2,
    # ]

    # # Search for the first occurrence of the phone number
    # matches = []
    # for regex in patterns:
    #     match = re.search(regex, text)
    #     if match:
    #         matches.append(match.group(0))

    # return matches
    keywords = ["phone", "tel", "mobile"]
    soup = BeautifulSoup(text, "html.parser")
    for data in soup(["style", "script"]):
        data.decompose()
    # elements = []
    #regex = r"^(mobile:)?(tel:)?(phone)?\+?(?:[\s\-()]{0,2}[\d()*][\s\-()]{0,2}){5,15}$"
    regex = r"^([^a-z])*(mobile:)?(tel:)?(phone)?\+?(?:[\s\-()]{0,2}[\d()*][\s\-()]{0,2}){5,15}([^a-z])*$"
    for word in keywords:
        for element in soup.find_all():
            if contains_substring(element, word):
                e = element
                #print(f"ELEMENT: {element} WORD: {word}")
                #for e in element.find_all(recursive=True):
                # text = get_direct_text(child)
                text = e.get_text()
                if text != "":
                    #if e.name == "a" and word == "tel":
                    print(f"CHILD: {e}")
                    print(f"TEXT: {text}")
                    match = re.search(regex, text)
                    if match:
                        print(element, word)
                        return match.group(0).strip()

    # return elements
    return None


def get_direct_text(element):
    element_text = element.string
    if element_text:
        return element_text
    else:
        return ""


def contains_substring(element, s):
    # if s in get_direct_text(element):
    #     return True

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


def get_page_links(url_and_data, depth):
    if depth >= 10:
        yield None

    new_url_and_data = {}
    for url in url_and_data:
        if url_and_data[url] is None:
            # log
            # i = 0
            # for u in url_and_data:
            #     if url_and_data[u] is not None:
            #         i = i + 1
                    # print(u)
            # print(f"DOWNLOADING: {url}")
            print(url)
            # print(f"ALREADY DOWNLOADED {i}")
            # print(f"DEPTH: {depth}")
            # log
            html = get_html(url)
            url_and_data[url] = html
            yield html

            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)
            for link in links:
                href = link["href"]
                if href.startswith(get_root_url(url)):  # Absolute URL
                    page_url = sanitize(href)
                    # print(f"HERE: url: {url}, href: {href}, get_root_url: {get_root_url(url)}")
                    # print(f"URL {page_url} HREF")
                elif href.startswith("http"):  # Foreign domain absolute URL
                    continue
                else:  # Relative URL
                    # print(f"HERE: url: {url}, href: {sanitize(href)}")
                    page_url = url + sanitize(href)

                new_url_and_data[page_url] = None
            # print(f"NEW URL_AND_DATA: {new_url_and_data.keys()}")

    yield from get_page_links({**new_url_and_data, **url_and_data}, depth + 1)


@shared_task
def run_scrape_job(collector_job_id):
    job = CollectorJob.objects.get(pk=collector_job_id)
    change_job_status(job)

    base_url = get_protocol(job.domain.name)

    page_gen = get_page_links({base_url: None}, 0)
    for _ in range(1):
        html = next(page_gen)
        if html is None:
            break

        phone = parse_page_for_phone(html)
        if phone:
            print(f"PHONE: {phone}")
            break
        # if elements:
        #     for e in elements:
        # print(e)
