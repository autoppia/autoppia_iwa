import time
from dataclasses import fields
from typing import List, Optional, Union

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from autoppia_iwa.config.config import CHROME_PATH, CHROMEDRIVER_PATH, PROFILE, PROFILE_DIR
from autoppia_iwa.src.web_analysis.domain.classes import Element


class WebPageStructureExtractor:
    """
    A web page structure extractor that extracts structured data from web pages.

    This class provides methods to extract structured data from web pages, including HTML elements, text content, and attributes.
    """

    ALLOWED_HTML_TAGS = [
        "header",
        "nav",
        "main",
        "section",
        "article",
        "aside",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "form",
        "p",
        "div",
        "a",
        "span",
        "ul",
        "li",
        "button",
        "input",
        "select",
        "textarea",
        "img",
        "video",
        "audio",
    ]

    def __init__(self):
        self.driver = None

    def get_elements(
        self,
        source: Union[str, BeautifulSoup],
        allowed_tags: Optional[List[str]] = None,
    ) -> tuple[List[Element], str]:
        """
        Extract structured data from a web page.

        Args:
            source (Union[str, BeautifulSoup]): The URL or BeautifulSoup object to extract structured data from.
            allowed_tags (list, optional): The allowed HTML tags to extract. Defaults to None.

        Returns:
            tuple: A tuple containing the extracted elements and the HTML source.
        """
        allowed_tags = allowed_tags if allowed_tags else WebPageStructureExtractor.ALLOWED_HTML_TAGS

        # Determine if the source is a URL or BeautifulSoup object
        if isinstance(source, str):
            if not source.startswith("http://") and not source.startswith("https://"):
                source = "http://" + source

            # Initialize Selenium and navigate to URL
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument(f"--user-data-dir={PROFILE_DIR}")
            chrome_options.add_argument(f"--profile-directory={PROFILE}")
            chrome_options.add_argument("--start-maximized")
            chrome_options.binary_location = CHROME_PATH
            self.driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
            self.driver.get(source)
            # TODO: Reduced the sleep time for locally deployed app
            time.sleep(2)  # Wait for the page to load
            # Get HTML source from Selenium driver
            html_source = self.driver.page_source
            soup = BeautifulSoup(html_source, "html.parser")
        else:
            # Use the provided BeautifulSoup object
            soup = source

        # Clean the HTML and extract elements
        cleaned_soup = self.__clean_soup(soup)
        elements = []
        cleaned_soup_body = cleaned_soup.find("body")
        element_id_counter = 0
        if cleaned_soup_body is None:
            # If there's no body, use the entire cleaned_soup
            cleaned_soup_body = cleaned_soup

        for soup_element in cleaned_soup_body.find_all(allowed_tags, recursive=False):  # type: ignore
            element, element_id_counter = self.__convert_soup_element_to_element(soup_element, allowed_tags, None, "/", element_id_counter)
            elements.append(element)
        return elements, cleaned_soup.prettify()

    def __clean_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Clean the HTML soup by removing unnecessary tags and attributes.

        Args:
            soup (BeautifulSoup): The HTML soup to clean.

        Returns:
            BeautifulSoup: The cleaned HTML soup.
        """
        # Tags and attributes to exclude during the cleaning process
        TAGS_TO_EXCLUDE = ["style", "script", "svg"]
        ATTRIBUTES_TO_EXCLUDE = ["class", "name", "style"]
        DATA_ATTRIBUTES_PREFIX = "data-"

        # Remove unwanted tags
        for data in soup(TAGS_TO_EXCLUDE):
            data.decompose()

        # Remove unwanted attributes
        for tag in soup():
            for attribute in ATTRIBUTES_TO_EXCLUDE:
                if attribute in tag.attrs:
                    del tag[attribute]

        # Remove data- attributes
        for tag in soup():
            for attr in list(tag.attrs):
                if attr.startswith(DATA_ATTRIBUTES_PREFIX):
                    del tag[attr]

        return soup

    def __convert_soup_element_to_element(
        self,
        soup_element,
        allowed_tags: List[str],
        parent_id: Optional[int],
        base_path: str,
        current_id: int,
    ) -> tuple[Element | None, int]:
        """
        Extract the hierarchy of an HTML element.

        Args:
            soup_element (Soup Element): The HTML element to extract the hierarchy from.
            allowed_tags (list): The allowed HTML tags to extract.
            parent_id (int): The ID of the parent element.
            base_path (str): The path of the parent element.
            current_id (int): The current ID counter.

        Returns:
            Element: The extracted hierarchy of the HTML element.
            int: The updated current ID counter.
        """
        # If the tag is not allowed, do not process the element
        if soup_element.name not in allowed_tags:
            return None, current_id

        # Assign unique ID to element
        current_id += 1
        element_id = current_id
        path = f"{base_path}/{element_id}"

        # Extract basic information from the element
        info = {
            "tag": soup_element.name,
            "attributes": dict(soup_element.attrs),
            "children": [],
            "textContent": soup_element.get_text().strip(),
            "id": soup_element.get("id"),
            "element_id": element_id,
            "parent_element_id": parent_id,
            "path": path,
            "data_attributes": {k: v for k, v in soup_element.attrs.items() if k.startswith("data-")},
        }

        # Extract attributes starting with "data-"
        if not info["data_attributes"]:
            del info["data_attributes"]

        # Add specific attributes for certain tags
        if soup_element.name == "a":
            info["link_target"] = soup_element.get("href")
        if soup_element.name == "input":
            info["input_type"] = soup_element.get("type")
        if soup_element.name in ["input", "textarea", "select"]:
            info["value"] = soup_element.get("value")
        try:
            if "display:none" in str(soup_element.get("style")):
                info["invisible"] = True
        except Exception:
            pass

        # Filter the information to include only valid keys for the Element class
        valid_keys = {f.name for f in fields(Element)}
        filtered_info = {k: v for k, v in info.items() if k in valid_keys}

        # TODO ESTO NO TIENE SENTIDO
        filtered_info["events_triggered"] = []
        filtered_info["analysis"] = None

        # Create Element object
        element = Element(**filtered_info)

        # Recursively process element children
        for child in soup_element.children:
            child_info, current_id = self.__convert_soup_element_to_element(child, allowed_tags, element_id, path, current_id)
            if child_info:
                element.children.append(child_info)

        return element, current_id
