from urllib.parse import urljoin, urlparse

import networkx as nx
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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

    def get_links_selenium(self, url):
        """
        Get links from a URL using Selenium.

        Args:
            url (str): The URL to get links from.

        Returns:
            list[str]: A list of links found on the page.
        """
        # Set up the Selenium driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # Fetch the page
        driver.get(url)
        driver.implicitly_wait(10)  # Wait for 10 seconds to load the page

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.find_all("a", href=True)
        urls = [link["href"] for link in links if link["href"].startswith("http")]

        # Close the browser
        driver.quit()

        return urls

    # Function to create a graph
    def create_graph(self, home_url):
        graph = nx.DiGraph()
        graph.add_node(home_url)
        links = self.crawl_urls(start_url=home_url, max_depth=1)

        for link in links:
            graph.add_edge(home_url, link)

        return graph, links
