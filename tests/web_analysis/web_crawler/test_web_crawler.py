import asyncio

import matplotlib.pyplot as plt
import networkx as nx

from autoppia_iwa.src.web_analysis.application.web_crawler import WebCrawler
from autoppia_iwa.src.web_analysis.domain.classes import WebCrawlerConfig

crawler_config = WebCrawlerConfig(start_url="https://ajedrezenmadrid.com", max_depth=2)

web_crawler = WebCrawler(crawler_config)

crawled_urls = web_crawler.crawl_urls()

print("Crawled URLs:")
for url in crawled_urls:
    print(url)


async def run_async_playwright():
    all_links = await web_crawler.get_links("https://ajedrezenmadrid.com")
    print("Links obtained using async Playwright:")
    for link in all_links:
        print(link)


if __name__ == "__main__":
    asyncio.run(run_async_playwright())

    # Create a graph of the crawled URLs
    graph, links = web_crawler.create_graph()

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
