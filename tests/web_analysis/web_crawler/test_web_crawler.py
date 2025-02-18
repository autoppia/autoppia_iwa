from urllib.parse import urljoin, urlparse

import matplotlib.pyplot as plt
import networkx as nx
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from autoppia_iwa.src.web_analysis.domain.classes import WebCrawlerConfig


class WebCrawler:
    def __init__(self, startUrl):
        parsed = urlparse(startUrl)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"

    def crawl_urls(self, start_url, max_depth=2):
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
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        driver.implicitly_wait(10)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.find_all("a", href=True)
        urls = [link["href"] for link in links if link["href"].startswith("http")]

        driver.quit()

        return urls

    def create_graph(self, home_url):
        graph = nx.DiGraph()
        graph.add_node(home_url)
        links = self.crawl_urls(start_url=home_url, max_depth=1)

        for link in links:
            graph.add_edge(home_url, link)

        return graph, links


# Define the configuration for the web crawler
crawler_config = WebCrawlerConfig(start_url="https://ajedrezenmadrid.com", max_depth=2)

# Initialize the web crawler with the start URL
web_crawler = WebCrawler(crawler_config.start_url)

# Use the crawler to get URLs up to the maximum depth
crawled_urls = web_crawler.crawl_urls(crawler_config.start_url, crawler_config.max_depth)

# Print the crawled URLs
print("Crawled URLs:")
for url in crawled_urls:
    print(url)

# Get links from a specific URL using Selenium
selenium_links = web_crawler.get_links("https://ajedrezenmadrid.com")

# Print the links obtained using Selenium
print("Links obtained using Selenium:")
for link in selenium_links:
    print(link)

# Create a graph of the crawled URLs
graph, links = web_crawler.create_graph(crawler_config.start_url)

# Print the links in the graph
print("Links in the graph:")
for link in links:
    print(link)

# Visualize the graph
plt.figure(figsize=(12, 12))
nx.draw(
    graph,
    with_labels=True,
    node_size=3000,
    node_color="skyblue",
    font_size=10,
    font_weight="bold",
)
plt.title("Web Crawler Graph")
plt.savefig("web_crawler_graph.png")
