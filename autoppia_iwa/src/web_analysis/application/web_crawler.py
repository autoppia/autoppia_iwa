from urllib.parse import urljoin, urlparse

import networkx as nx
import requests
from bs4 import BeautifulSoup

from autoppia_iwa.src.shared.web_utils import async_extract_html
from autoppia_iwa.src.web_analysis.domain.classes import WebCrawlerConfig


class WebCrawler:
    """
    A web crawler that crawls URLs starting from a given start URL.

    Args:
        start_url (str): The URL to start crawling from.

    Attributes:
        domain (str): The domain of the start URL.
    """

    def __init__(self, crawler_config: WebCrawlerConfig):
        parsed = urlparse(crawler_config.start_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"
        self.config = crawler_config

    def crawl_urls(self):
        """
        Crawl URLs starting from the given start URL (synchronous - uses requests).
        """
        visited_urls = set()
        all_urls = []

        def strip_query_params(url):
            parsed_local = urlparse(url)
            return f"{parsed_local.scheme}://{parsed_local.netloc}{parsed_local.path}"

        def _crawl(url, depth):
            if not url.startswith(self.domain):
                return

            normalized_url = strip_query_params(url)

            if normalized_url in visited_urls:
                return
            if depth > self.config.max_depth:
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

            soup_local = BeautifulSoup(response.text, "html.parser")
            for a_tag in soup_local.find_all("a"):
                new_url = a_tag.get("href")
                if new_url:
                    new_url = urljoin(url, new_url)
                    _crawl(new_url, depth + 1)

        _crawl(self.config.start_url, 0)
        return all_urls

    @staticmethod
    async def get_links(url):
        """
        Get links from a URL using the async Playwright API.
        """
        html = await async_extract_html(url)
        soup_local = BeautifulSoup(html, "html.parser")
        links = soup_local.find_all("a", href=True)
        urls = [link["href"] for link in links if link["href"].startswith("http")]

        return urls

    def create_graph(self):
        """
        Creates a directed graph of links from the given home_url, depth=1.
        """
        graph = nx.DiGraph()
        graph.add_node(self.config.start_url)
        links = self.crawl_urls()
        for link in links:
            graph.add_edge(self.config.start_url, link)
        return graph, links
