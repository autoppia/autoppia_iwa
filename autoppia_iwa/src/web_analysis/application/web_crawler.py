from urllib.parse import urljoin, urlparse

import networkx as nx
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class WebCrawler:
    """
    A web crawler that crawls URLs starting from a given start URL.

    Args:
        start_url (str): The URL to start crawling from.

    Attributes:
        domain (str): The domain of the start URL.
    """

    def __init__(self, start_url):
        """
        Initialize the web crawler with a start URL.

        Args:
            start_url (str): The URL to start crawling from.
        """
        parsed = urlparse(start_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"

    def crawl_urls(self, start_url, max_depth=2):
        """
        Crawl URLs starting from the given start URL.

        Args:
            start_url (str): The URL to start crawling from.
            max_depth (int, optional): The maximum depth to crawl. Defaults to 2.

        Returns:
            list[str]: A list of crawled URLs.
        """
        visited_urls = set()
        all_urls = []

        def strip_query_params(url):
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        def _crawl(url, depth):
            if not url.startswith(self.domain):
                return

            normalized_url = strip_query_params(url)

            if normalized_url in visited_urls:
                return
            if depth > max_depth:
                return

            visited_urls.add(normalized_url)
            all_urls.append(url)

            try:
                response = requests.get(url)
            except Exception as e:
                print(f"Failed to fetch {url}. Reason: {e}")
                return

            if response.status_code != 200:
                return

            soup = BeautifulSoup(response.text, "html.parser")

            for a_tag in soup.find_all("a"):
                new_url = a_tag.get("href")
                if new_url:
                    new_url = urljoin(url, new_url)
                    _crawl(new_url, depth + 1)

        _crawl(start_url, 0)

        return all_urls

    def get_links(self, url):
        """
        Get links from a URL using Playwright (replacing Selenium).

        Args:
            url (str): The URL to get links from.

        Returns:
            list[str]: A list of links found on the page.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        urls = [link["href"] for link in links if link["href"].startswith("http")]

        return urls

    def create_graph(self, home_url):
        graph = nx.DiGraph()
        graph.add_node(home_url)
        links = self.crawl_urls(start_url=home_url, max_depth=1)

        for link in links:
            graph.add_edge(home_url, link)

        return graph, links
