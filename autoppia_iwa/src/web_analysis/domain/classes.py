import json
from dataclasses import dataclass, field, fields

from pydantic import BaseModel

from autoppia_iwa.src.llms.domain.utils import OpenAIUtilsMixin


@dataclass
class EventTriggered:
    type: str

    def to_dict(self):
        field_names = [f.name for f in fields(self)]
        d = {k: getattr(self, k) for k in field_names}
        return d


@dataclass
class Element:
    tag: str
    attributes: dict[str, str]
    textContent: str
    children: list["Element"] = field(default_factory=list)
    id: str | None = None
    element_id: int | None = None
    parent_element_id: int | None = None
    path: str | None = None
    events_triggered: list[EventTriggered] = field(default_factory=list)
    analysis: str | None = None

    def to_dict(self):
        field_names = [f.name for f in fields(self)]
        d = {k: getattr(self, k) for k in field_names}
        if "children" in d:
            d["children"] = [child.to_dict() for child in self.children]
        if "events_triggered" in d:
            d["events_triggered"] = [event.to_dict() if isinstance(event, EventTriggered) else event for event in self.events_triggered]
            for event in d["events_triggered"]:
                if "target" in event:
                    del event["target"]
        return d

    def calculate_element_size(self) -> int:
        element_dict = self.to_dict()
        element_size = OpenAIUtilsMixin.num_tokens_from_string(json.dumps(element_dict))
        children_size = OpenAIUtilsMixin.num_tokens_from_string(json.dumps(element_dict.get("children", [])))
        return element_size + children_size

    def analyze(self, max_tokens, analyze_element_function, analyze_parent_function) -> dict:
        tokens = self.calculate_element_size()
        result = {"tag": self.tag, "size": tokens, "analysis": None, "children": []}

        if tokens < max_tokens:
            print(f"Element {self.tag} with tokens {tokens} is smaller than max_tokens: {max_tokens}")
            result["analysis"] = analyze_element_function(self)
        else:
            print(f"Element {self.tag} with tokens {tokens} is bigger than max_tokens: {max_tokens}")
            for child in self.children:
                result["children"].append(child.analyze(max_tokens, analyze_element_function, analyze_parent_function))
            result["analysis"] = analyze_parent_function(self, result["children"])

        print(f"For element {self.tag} analysis result: {result}")
        return result


# ---------WEB CRAWL--------
class WebCrawlerConfig(BaseModel):
    start_url: str
    max_depth: int = 2
