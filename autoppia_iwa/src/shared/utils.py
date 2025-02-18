import random
import string
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from playwright.sync_api import sync_playwright
from autoppia_iwa.config.config import CHROME_PATH, PROFILE, PROFILE_DIR
from autoppia_iwa.src.data_generation.domain.tests_classes import (
    CheckEventEmittedTest,
    CheckPageViewEventTest,
    FindInHtmlTest,
)


def extract_html(page_url):
    launch_options = {"headless": True, "args": ["--start-maximized"]}
    # If CHROME_PATH exists, use it as the executable path for the browser
    chrome_path = CHROME_PATH
    if chrome_path and Path(chrome_path).exists():
        launch_options["executable_path"] = chrome_path

    # Use persistent context if PROFILE_DIR is provided
    use_persistent = PROFILE_DIR and Path(PROFILE_DIR).exists()

    with sync_playwright() as p:
        browser_type = p.chromium
        if use_persistent:
            # Launch persistent context with the given user data directory.
            context = browser_type.launch_persistent_context(PROFILE_DIR, **launch_options)
        else:
            browser = browser_type.launch(**launch_options)
            context = browser.new_context()

        page = context.new_page()

        page.goto(page_url)
        html = page.content()

        context.close()
        if not use_persistent:
            browser.close()

        return html


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
        if tag.has_attr("style") and "display: none" in tag["style"]:
            tag.decompose()
            continue
        if tag.has_attr("hidden"):
            tag.decompose()
            continue

    # Remove inline event attributes and other non-essential attributes
    for tag in soup.find_all():
        event_attrs = [attr for attr in tag.attrs if attr.startswith("on")]
        for attr in event_attrs:
            del tag[attr]
        for attr in ["class", "id", "style"]:
            if attr in tag.attrs:
                del tag[attr]

    # Remove empty elements that do not have text or child elements
    for tag in soup.find_all():
        if not tag.text.strip() and not tag.find_all():
            tag.decompose()

    cleaned_html = soup.body if soup.body else soup
    return cleaned_html.prettify()


def instantiate_test(test_data):
    if test_data["test_type"] == "frontend":
        return FindInHtmlTest(
            description=test_data["description"],
            test_type=test_data["test_type"],
            keywords=test_data["keywords"],
        )
    elif test_data["test_type"] == "backend":
        if "page_view_url" in test_data:
            return CheckPageViewEventTest(
                description=test_data["description"],
                test_type=test_data["test_type"],
                page_view_url=test_data["page_view_url"],
            )
        return CheckEventEmittedTest(
            description=test_data["description"],
            test_type=test_data["test_type"],
            event_name=test_data["event_name"],
        )
    else:
        raise ValueError(f"Unknown test type: {test_data['test_type']}")


def generate_random_web_agent_id(length=16):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))
