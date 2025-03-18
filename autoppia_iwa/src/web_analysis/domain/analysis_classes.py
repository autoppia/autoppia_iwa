from copy import deepcopy
from typing import Any

from pydantic import BaseModel, Field


class LLMWebAnalysis(BaseModel):
    one_phrase_summary: str
    summary: str
    categories: list[str]
    functionality: list[str]
    media_files_description: str | list[dict[str, Any]] | list[str] | None = None
    key_words: list[str]
    relevant_fields: list[str | dict[str, str | Any]] | None = None
    curiosities: str | None = None
    accessibility: str | list[str] | None = None
    user_experience: str | None = None
    advertisements: str | None = None
    seo_considerations: str | None = None
    additional_notes: str | None = None


class SinglePageAnalysis(BaseModel):
    page_url: str
    elements_analysis_result: list[dict]
    web_summary: LLMWebAnalysis
    html_source: str


class DomainAnalysis(BaseModel):
    domain: str
    status: str
    page_analyses: list[SinglePageAnalysis]
    started_time: str
    ended_time: str
    total_time: float
    start_url: str
    category: str = ""
    features: list[str] = Field(default_factory=list, description="List of features")
    urls: list[str] = Field(default_factory=list, description="List of urls")

    def dump_excluding_page_analyses(self):
        dump = self.model_dump()
        dump["page_analyses"] = None
        return dump

    def dump_excluding_page_analyses_except_one(self, page_url_to_not_exclude: str):
        dump = self.model_dump()
        page_analyses = deepcopy(self.page_analyses)

        # Filter out pages except the one that should not be excluded
        filtered_page_analyses = [page for page in page_analyses if page.page_url == page_url_to_not_exclude]

        dump["page_analyses"] = filtered_page_analyses if filtered_page_analyses else None
        return dump

    def get_page_analysis(self, url: str):
        for page_analysis in self.page_analyses:
            if page_analysis.page_url == url:
                return page_analysis
        return None
