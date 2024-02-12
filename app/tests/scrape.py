from bs4 import BeautifulSoup
import requests

from django.test import TestCase
from app.tasks import (
    get_protocol,
    get_html,
    normalize_url,
    get_root_url,
    contains_substring,
    parse_page_for_email,
    parse_page_for_phone,
)
from unittest.mock import patch


class TestUtils(TestCase):
    def test_get_protocol_success(self):
        domain = "example.com"
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.url = "http://example.com"
            protocol = get_protocol(domain)
            self.assertEqual(protocol, "http://example.com")

    def test_get_protocol_connection_error(self):
        domain = "example.com"
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection error")
            protocol = get_protocol(domain)
            self.assertIsNone(protocol)
        pass

    # Add similar test cases for other methods like get_html, get_soup, etc.
    def test_get_html_success(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = "<html></html>"
            html = get_html("https://somewhere.com/somewhere")
            self.assertEqual(html, "<html></html>")

        invalid_url = "https://dassadasdcbwrIDSKC.com/dsadas"
        html = get_html(invalid_url)
        self.assertEqual(html, "")

        not_even_url = "regardless of input IT SHOULD ALWAYS FAIL"
        html = get_html(not_even_url)
        self.assertEqual(html, "")

    def test_contains_substring(self):
        # Create a BeautifulSoup element for testing
        html = """
        <div class='test' id='zxc' list_attr='value1 value2'>
            <p attr1='test1'>
                Test content
            </p>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        # TRUE
        # Test substring contained in text
        self.assertTrue(contains_substring(element, "content"))

        # Test substring contained in tag name
        self.assertTrue(contains_substring(element, "div"))

        # Test substring contained in attribute name
        self.assertTrue(contains_substring(element, "class"))
        self.assertTrue(contains_substring(element, "id"))

        # Test substring contained in attribute value
        self.assertTrue(contains_substring(element, "test"))
        self.assertTrue(contains_substring(element, "zx"))

        # It should handle attribute multiple attribute values which are lists
        self.assertTrue(contains_substring(element, "value1"))
        self.assertTrue(contains_substring(element, "ue2"))
        self.assertTrue(contains_substring(element, "1 val"))

        # FALSE
        # It should not return true for children attributes or tag name
        self.assertFalse(contains_substring(element, "attr1"))
        self.assertFalse(contains_substring(element, "test1"))
        self.assertFalse(contains_substring(element, "p"))

        # Test substring not contained
        self.assertFalse(contains_substring(element, "nonexistent"))

    def test_get_root_url(self):
        url_http = "http://example.com/page"
        expected_root_url_http = "http://example.com"
        self.assertEqual(get_root_url(url_http), expected_root_url_http)

        url_https = "https://www.example.com/page/page2/page3"
        expected_root_url_https = "https://www.example.com"
        self.assertEqual(get_root_url(url_https), expected_root_url_https)

        url_no_path = "https://example.com"
        expected_root_url_no_path = "https://example.com"
        self.assertEqual(get_root_url(url_no_path), expected_root_url_no_path)

    def test_normalize_url(self):
        expected_normalized_url = "/example.com/page"
        # Relative URL with no leading slash
        href_no_leading_slash = "example.com/page"
        self.assertEqual(
            normalize_url(href_no_leading_slash),
            expected_normalized_url,
        )

        # Relative URL with leading slash
        href_with_leading_slash = "/example.com/page"
        self.assertEqual(
            normalize_url(href_with_leading_slash),
            expected_normalized_url,
        )

        # Relative URL with trailing slash
        href_with_leading_slash = "example.com/page/"
        self.assertEqual(
            normalize_url(href_with_leading_slash), expected_normalized_url
        )

        # Relative URL with leading and trailing slash
        href_with_leading_slash = "example.com/page/"
        self.assertEqual(
            normalize_url(href_with_leading_slash), expected_normalized_url
        )

        expected_normalized_url_absolute = "https://example.com/page"
        # Absolute URL
        href_absolute = "https://example.com/page"
        self.assertEqual(
            normalize_url(href_absolute), expected_normalized_url_absolute
        )

        # Absolute URL with trailing slash
        href_absolute = "https://example.com/page/"
        self.assertEqual(
            normalize_url(href_absolute), expected_normalized_url_absolute
        )


class TestParsing(TestCase):
    def test_parse_page_for_email(self):
        # Test case 1: Email present in page
        html_with_email = """
        <html>
            <body>john.doe@example.com</body>
        </html>
        """
        soup_with_email = BeautifulSoup(html_with_email, "html.parser")
        expected_email = "john.doe@example.com"
        self.assertEqual(parse_page_for_email(soup_with_email), expected_email)

        # Test case 2: Email not present in page
        html_without_email = """
        <html>
            <body>No email @ddress</body>
        </html>"""
        soup_without_email = BeautifulSoup(html_without_email, "html.parser")
        expected_result = None
        self.assertEqual(
            parse_page_for_email(soup_without_email), expected_result
        )

    def test_parse_page_for_phone(self):
        # Keyword in parent attr value
        html_with_email = """
        <body>
            <h1>Welcome to Example Page</h1>
            <p>This is a sample HTML page.</p>
            <div class="mobile">
                <p> +1 (123) 456-7890</p>
            </div>
            <footer>
                <p>For more information</p>
            </footer>
        </body>
            """
        soup = BeautifulSoup(html_with_email, "html.parser")
        expected_phone = "+1 (123) 456-7890"
        self.assertEqual(parse_page_for_phone(soup), expected_phone)

        # Keyword as grandparent tag
        html_with_email = """
        <body>
            <h1>Welcome to Example Page</h1>
            <p>This is a sample HTML page.</p>
            <phone>
                <div>
                    <p> +1 (123) 456-7890</p>
                </div>
            </phone>
            <footer>
                <p>For more information</p>
            </footer>
        </body>
            """
        soup = BeautifulSoup(html_with_email, "html.parser")
        expected_phone = "+1 (123) 456-7890"
        self.assertEqual(parse_page_for_phone(soup), expected_phone)

        # Keyword next to phone text
        html_with_email = """
        <body>
            <h1>Welcome to Example Page</h1>
            <p>This is a sample HTML page.</p>
            <div>
                <p>tel:   +1 (123) 456-7890</p>
            </div>
            <footer>
                <p>For more information</p>
            </footer>
        </body>
            """
        soup = BeautifulSoup(html_with_email, "html.parser")
        expected_phone = "+1 (123) 456-7890"
        self.assertEqual(parse_page_for_phone(soup), expected_phone)

        # Keyword in sibling
        html_with_email = """
        <body>
            <h1>Welcome to Example Page</h1>
            <div>
                <p>phone:</p>
                <p> +1 (123) 456-7890</p>
            </div>
            <footer>
                <p>For more information</p>
            </footer>
        </body>
            """
        soup = BeautifulSoup(html_with_email, "html.parser")
        expected_phone = "+1 (123) 456-7890"
        self.assertEqual(parse_page_for_phone(soup), expected_phone)
