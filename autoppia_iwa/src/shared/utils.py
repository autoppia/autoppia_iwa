# file: web_utils.py

import random
import string
from io import BytesIO
from typing import Dict, Any, Tuple

from PIL import Image
from bs4 import BeautifulSoup, Comment
from playwright.async_api import async_playwright

from autoppia_iwa.src.llms.infrastructure.ui_parser_service import UIParserService
import re

################################################################################
# Generate Random Web Agent ID
################################################################################


def generate_random_web_agent_id(length: int = 16) -> str:
    """
    Generates a random alphanumeric string for the web_agent ID.
    """
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for _ in range(length))


################################################################################
# get_html_and_screenshot
################################################################################

async def get_html_and_screenshot(page_url: str) -> Tuple[str, str]:
    """
    Navigates to page_url using Playwright in headless mode, extracts & cleans HTML,
    captures a screenshot, and uses UIParserService to generate a textual summary
    of that screenshot. Returns (cleaned_html, screenshot_description).
    """
    screenshot_description = ""
    cleaned_html = ""

    async with async_playwright() as p:
        browser_type = p.chromium
        browser = await browser_type.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(page_url, timeout=60000)

        # 1) Extract raw HTML, clean it
        raw_html = await page.content()
        cleaned_html = clean_html(raw_html)

        # 2) Take screenshot in memory
        screenshot_bytes = await page.screenshot()

        await context.close()
        await browser.close()

    # 3) Summarize screenshot using UIParserService
    try:
        image = Image.open(BytesIO(screenshot_bytes)).convert("RGB")
        ui_parser = UIParserService()
        screenshot_description = ui_parser.summarize_image(image)
    except Exception as e:
        print(f"Screenshot parse error: {e}")
        screenshot_description = ""

    return cleaned_html, screenshot_description


################################################################################
# Synchronous HTML Extraction
################################################################################

def sync_extract_html(page_url: str) -> str:
    """
    Uses Playwright in sync mode to extract HTML from a page.
    Adjust if your environment doesn't support sync Playwright.
    """
    from playwright.sync_api import sync_playwright

    launch_options = {"headless": True, "args": ["--start-maximized"]}

    with sync_playwright() as p:
        browser_type = p.chromium
        browser = browser_type.launch(**launch_options)
        context = browser.new_context()
        page = context.new_page()
        page.goto(page_url)
        html = page.content()
        context.close()
        browser.close()
    return html


################################################################################
# Asynchronous HTML Extraction
################################################################################

async def extract_html(page_url: str) -> str:
    """
    Uses Playwright in async mode to extract raw HTML from a page.
    """
    launch_options = {"headless": True, "args": ["--start-maximized"]}

    async with async_playwright() as p:
        browser_type = p.chromium
        browser = await browser_type.launch(**launch_options)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(page_url)
        html = await page.content()
        await context.close()
        await browser.close()
    return html


################################################################################
# Clean HTML
################################################################################

def clean_html(html_content: str) -> str:
    """
    Removes scripts, styles, hidden tags, inline event handlers, etc.,
    returning a 'clean' version of the DOM.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove scripts, styles, metas, links, noscript
    for tag in soup(["script", "style", "noscript", "meta", "link"]):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Remove hidden elements and inline events
    for tag in soup.find_all(True):
        if tag.has_attr("style") and tag["style"]:
            style_lc = tag["style"].lower()
            if "display: none" in style_lc or "visibility: hidden" in style_lc:
                tag.decompose()
                continue
        if tag.has_attr("hidden"):
            tag.decompose()
            continue
        # Remove inline event handlers + style/id/class
        for attr in list(tag.attrs):
            if attr.startswith("on") or attr in ["class", "id", "style"]:
                del tag[attr]

    # Remove empty tags
    for tag in soup.find_all():
        if not tag.text.strip() and not tag.find_all():
            tag.decompose()

    clean_soup = soup.body if soup.body else soup
    return clean_soup.prettify()


################################################################################
# Detect Interactive Elements (forms, buttons, links, etc.)
################################################################################

def detect_interactive_elements(cleaned_html: str) -> Dict[str, Any]:
    """
    Inspects the cleaned HTML to find possible interactive elements:
      - forms (with their inputs)
      - buttons or anchors with text
      - textareas, selects, etc.

    Returns a dict summarizing them for LLM usage, e.g.:
    {
      "forms": [
        {"fields": ["name", "email", "message"]}
      ],
      "buttons": ["Send", "Submit"],
      "links": ["Home", "Applications", "Overview", ...]
    }
    """
    summary = {"forms": [], "buttons": [], "links": []}
    soup = BeautifulSoup(cleaned_html, "html.parser")

    # Forms and their fields
    for form in soup.find_all("form"):
        form_info = []
        for inp in form.find_all(["input", "textarea", "select"]):
            placeholder = inp.get("placeholder") or inp.get("name") or inp.get("type")
            if placeholder:
                form_info.append(placeholder)
        summary["forms"].append({"fields": form_info})

    # Buttons (including input[type=submit])
    for btn in soup.find_all(["button", "input"], type="submit"):
        text = btn.text.strip() or btn.get("value") or "Submit"
        if text:
            summary["buttons"].append(text)

    # Links (anchor text)
    for a in soup.find_all("a"):
        link_text = a.text.strip()
        if link_text:
            summary["links"].append(link_text)

    return summary


def extract_json_in_markdown(text: str) -> str:
    """
    Extract the first fenced code block (```json ... ``` or just ``` ... ```).
    If none is found, return text.strip() as a fallback.
    """
    pattern = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()
