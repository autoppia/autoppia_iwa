import random
import string
from pathlib import Path

from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from autoppia_iwa.config.config import CHROME_PATH, CHROMEDRIVER_PATH, PROFILE, PROFILE_DIR
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventEmittedTest, CheckPageViewEventTest, FindInHtmlTest


def extract_html(page_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")

    # Check if PROFILE_DIR exists
    profile_dir = PROFILE_DIR
    if profile_dir and Path(profile_dir).exists():
        options.add_argument(f"--user-data-dir={profile_dir}")

    # Check if PROFILE exists
    profile = PROFILE
    if profile:
        options.add_argument(f"--profile-directory={profile}")

    # Check if CHROME_PATH exists
    chrome_path = CHROME_PATH
    if chrome_path and Path(chrome_path).exists():
        options.binary_location = chrome_path

    # Check if CHROMEDRIVER_PATH exists
    chromedriver_path = CHROMEDRIVER_PATH
    if chromedriver_path and Path(chromedriver_path).exists():
        driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
        try:
            driver.get(page_url)
            html = driver.page_source
            return html
        except Exception as e:
            print(e)
        finally:
            driver.quit()
    else:
        raise RuntimeError("ChromeDriver path is not valid or not set")


def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "noscript", "meta", "link"]):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove hidden elements (e.g., elements with "display: none" in style or having the "hidden" attribute)
    for tag in soup.find_all():
        # Check if the element's style contains 'display: none'
        if tag.has_attr("style") and "display: none" in tag["style"]:
            tag.decompose()
            continue

        # Check if the element has the 'hidden' attribute
        if tag.has_attr("hidden"):
            tag.decompose()
            continue

    # Remove inline event attributes and other non-essential attributes
    for tag in soup.find_all():
        # Remove event handler attributes (e.g., onclick, onmouseover)
        event_attrs = [attr for attr in tag.attrs if attr.startswith("on")]
        for attr in event_attrs:
            del tag[attr]

        # Optionally remove other non-essential attributes such as class, id, and style
        for attr in ["class", "id", "style"]:
            if attr in tag.attrs:
                del tag[attr]

    # Remove empty elements that do not have text or child elements
    for tag in soup.find_all():
        if not tag.text.strip() and not tag.find_all():
            tag.decompose()

    # Extract the main content (preferably the <body> if available)
    cleaned_html = soup.body if soup.body else soup
    return cleaned_html.prettify()


def instantiate_test(test_data):
    if test_data["test_type"] == "frontend":
        return FindInHtmlTest(description=test_data["description"], test_type=test_data["test_type"], keywords=test_data["keywords"])
    elif test_data["test_type"] == "backend":
        if "page_view_url" in test_data:
            return CheckPageViewEventTest(description=test_data["description"], test_type=test_data["test_type"], page_view_url=test_data["page_view_url"])
        return CheckEventEmittedTest(description=test_data["description"], test_type=test_data["test_type"], event_name=test_data["event_name"])
    else:
        raise ValueError(f"Unknown test type: {test_data['test_type']}")


def generate_random_web_agent_id(length=16):
    """Generates a random alphanumeric string for the web_agent ID."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))
