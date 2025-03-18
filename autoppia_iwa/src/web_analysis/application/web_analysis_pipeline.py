import time
from datetime import datetime
from urllib.parse import urlparse

from dependency_injector.wiring import Provide

from autoppia_iwa.config.config import LLM_CONTEXT_WINDOW
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.web_analysis.application.web_crawler import WebCrawler
from autoppia_iwa.src.web_analysis.application.web_llm_utils import WebLLMAnalyzer
from autoppia_iwa.src.web_analysis.application.web_page_structure_extractor import WebPageStructureExtractor
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis, SinglePageAnalysis
from autoppia_iwa.src.web_analysis.domain.classes import WebCrawlerConfig

MAX_TOKENS_ELEMENT_ANALYZER = LLM_CONTEXT_WINDOW


class WebAnalysisPipeline:
    def __init__(
        self,
        start_url: str,
        analysis_repository: BaseMongoRepository = Provide[DIContainer.analysis_repository],
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.llm_service = llm_service
        self.analysis_repository = analysis_repository

        crawler_config = WebCrawlerConfig(start_url=start_url)
        self.web_crawler = WebCrawler(crawler_config)
        self.page_structure_extractor = WebPageStructureExtractor()
        self.llm_analyzer = WebLLMAnalyzer(llm_service=self.llm_service)

        self.page_analyses: list[SinglePageAnalysis] = []

    async def analyze(
        self,
        save_results_in_db: bool = True,
        get_analysis_from_cache: bool = True,
        enable_crawl: bool = True,
    ) -> DomainAnalysis:
        """
        Executes a full analysis for a domain, processing all URLs.

        Args:
            save_results_in_db (bool): Whether to save the results in the database. Default is True.
            get_analysis_from_cache (bool): Whether to check for cached results before analyzing. Default is True.
            enable_crawl (bool): Whether to crawl the domain for URLs. Default is True.

        Returns:
            DomainAnalysis: The analysis result.
        """
        cached_result = self._get_analysis_from_cache() if get_analysis_from_cache else None
        if cached_result:
            return cached_result

        self._initialize_analysis()
        urls_to_analyze = self._get_urls_to_analyze(enable_crawl)

        for url in urls_to_analyze:
            try:
                await self._analyze_url(url)
            except Exception as e:
                print(f"Error analyzing {url}: {e}")
        self._finalize_analysis()

        if save_results_in_db:
            self._save_results_in_db()

        if not isinstance(self.analysis_result, DomainAnalysis):
            self.analysis_result = DomainAnalysis(**self.analysis_result)

        self.analysis_result.urls = urls_to_analyze

        return self.analysis_result

    def _get_analysis_from_cache(self) -> DomainAnalysis | None:
        """
        Check if analysis results already exist in the database.

        Returns:
            Optional[DomainAnalysis]: Cached analysis result, or None if not found or invalid.
        """
        try:
            cached_result = self.analysis_repository.find_one({"start_url": self.start_url})
            # print(cached_result)
            if cached_result:
                if not cached_result.get("page_analyses"):
                    print(f"Cached analysis for '{self.start_url}' has empty page_analyses. Ignoring cache.")
                    return None
                print(f"Analysis for '{self.start_url}' already exists in Cache")
                return DomainAnalysis(**cached_result)
            print(f"No cached data found for url {self.start_url}")
            return None
        except Exception as e:
            print(f"Error checking cache for {self.start_url}: {e}")
            return None

    def _initialize_analysis(self):
        """
        Initialize metadata for the analysis process.
        """
        self.start_time = time.time()
        self.analysis_result = DomainAnalysis(
            domain=self.domain,
            status="processing",
            page_analyses=[],
            started_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ended_time="",
            total_time=0,
            start_url=self.start_url,
        )

    def _get_urls_to_analyze(self, enable_crawl) -> list[str]:
        """
        Crawl and retrieve URLs to analyze from the starting domain.

        Returns:
            List[str]: A list of URLs to analyze.
        """
        try:
            if not enable_crawl:
                return [self.start_url]
            all_urls = self.web_crawler.crawl_urls()
            return list(set(all_urls))
        except Exception as e:
            print(f"Error crawling URLs for {self.start_url}: {e}")
            return []

    async def _analyze_url(self, url: str):
        """
        Analyze a URL with error handling to ensure the pipeline continues.

        Args:
            url (str): The URL to analyze.
        """
        try:
            # Extract HTML structure
            elements, html_source = await self.page_structure_extractor.get_elements(url)

            # Analyze each element using the LLM
            elements_analysis_result = []
            for element in elements:
                print(f"Analysing element: {element.tag} from url {url}")
                try:
                    elements_analysis_result.append(
                        element.analyze(
                            max_tokens=MAX_TOKENS_ELEMENT_ANALYZER,
                            analyze_element_function=self.llm_analyzer.analyze_element,
                            analyze_parent_function=self.llm_analyzer.analyze_element_parent,
                        )
                    )
                except Exception as e:
                    print(f"Error analyzing element {element.element_id}: {e}")

            # Summarize the page
            page_summary_analysis = self.llm_analyzer.summarize_web_page(
                domain=self.domain,
                page_url=url,
                elements_analysis_result=elements_analysis_result,
            )
            if page_summary_analysis:
                single_page_analysis = SinglePageAnalysis(
                    page_url=url,
                    elements_analysis_result=elements_analysis_result,
                    web_summary=page_summary_analysis,
                    html_source=html_source,
                )
                self.page_analyses.append(single_page_analysis)

        except Exception as e:
            print(f"Failed to analyze URL {url}. Reason: {e}")

    def _finalize_analysis(self):
        """
        Finalize the analysis by updating metadata and storing results.
        """
        self.analysis_result.status = "done"
        self.analysis_result.page_analyses = self.page_analyses
        self.analysis_result.ended_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.analysis_result.total_time = time.time() - self.start_time

    def _save_results_in_db(self):
        """
        Save the analysis result in the database. If a document already exists for the start_url,
        perform an update to replace the corrupted analysis with the new one.
        """
        try:
            existing = self.analysis_repository.find_one({"start_url": self.start_url})
            data = self.analysis_result.model_dump()
            if existing:
                result = self.analysis_repository.update({"start_url": self.start_url}, data)
                print("Analysis results updated successfully." if result else "No documents updated.")
            else:
                self.analysis_repository.save(data)
                print("Analysis results saved successfully.")
        except Exception as e:
            print(f"Failed to save analysis results. Reason: {e}")
