from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from copy import deepcopy


class LLMWebAnalysis(BaseModel):
    one_phrase_summary: str
    summary: str
    categories: List[str]
    functionality: List[str]
    media_files_description: Optional[Union[str, List[Dict[str, Any]], List[str]]] = None
    key_words: List[str]
    relevant_fields: Optional[List[Union[str, Dict[str, Union[str, Any]]]]] = None
    curiosities: Optional[str] = None
    accessibility: Optional[Union[str, List[str]]] = None
    user_experience: Optional[str] = None
    advertisements: Optional[str] = None
    seo_considerations: Optional[str] = None
    additional_notes: Optional[str] = None


class SinglePageAnalysis(BaseModel):
    page_url: str
    elements_analysis_result: List[Dict]
    web_summary: LLMWebAnalysis
    html_source: str


class DomainAnalysis(BaseModel):
    domain: str
    status: str
    page_analyses: List[SinglePageAnalysis]
    started_time: str
    ended_time: str
    total_time: float
    start_url: str
    category:str = ""
    features:List[str] = Field(default_factory=list, description="List of features")
    urls:List[str] = Field(default_factory=list, description="List of urls")

    def dump_excluding_page_analyses(self):
        dump = self.model_dump()
        dump["page_analyses"] = None
        return dump

    def dump_excluding_page_analyses_except_one(self, page_url_to_not_exclude: str):
        dump = self.model_dump()
        page_analyses = deepcopy(self.page_analyses)

        # Filter out pages except the one that should not be excluded
        filtered_page_analyses = [
            page for page in page_analyses if page.page_url == page_url_to_not_exclude
        ]

        dump["page_analyses"] = filtered_page_analyses if filtered_page_analyses else None
        return dump

    def get_page_analysis(self, url:str):
        for page_analysis in self.page_analyses:
            if page_analysis.page_url == url:
                return page_analysis
        return None
