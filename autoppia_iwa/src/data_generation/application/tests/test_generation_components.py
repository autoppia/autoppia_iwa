import json
from typing import List, Dict, Optional
from pydantic import BaseModel, ValidationError

# --- Candidate Test Generator ---


class CandidateTestGenerator:
    def __init__(self, llm_service, system_message: str, allowed_events: List[str]):
        self.llm_service = llm_service
        self.system_message = system_message
        self.allowed_events = allowed_events

    def generate_candidates(
        self, 
        task_description: str, 
        html_source: str, 
        summary_page_url: dict, 
        relevant_fields: Optional[List] = None
    ) -> List[Dict]:
        user_message_parts = [
            f"Task Description: {task_description}",
            f"HTML Content: {html_source}",
        ]
        if summary_page_url:
            # Copy summary and extract keywords for CheckHTMLTest
            summary_dict = summary_page_url.copy()
            keywords = summary_dict.pop("key_words", None)
            if keywords:
                user_message_parts.append(f"Allowed keywords for CheckHTMLTest: {keywords}")
            user_message_parts.append(f"Page Analysis Summary: {summary_dict}")
        if relevant_fields:
            user_message_parts.append(f"Relevant words for the CheckPageViewTest: {relevant_fields}")
        user_message_parts.append("Generate tests following the specified format.")
        user_message = "\n\n".join(user_message_parts)

        response = self.llm_service.make_request(
            message_payload=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_message}
            ],
            chat_completion_kwargs={
                "temperature": 0.6,
                "top_k": 50,
                # We expect a JSON response containing candidate tests.
            },
        )
        try:
            candidates = json.loads(response).get("tests", [])
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            candidates = []
        return candidates

# --- Schema Model for Tests ---


class TestSchemaModel(BaseModel):
    type: str
    event_name: Optional[str] = None
    html_keywords: Optional[List[str]] = None
    url: Optional[str] = None

# --- Parsing & Validation Module ---


class TestParserValidator:
    def __init__(self, schema: dict):
        self.schema = schema  # For future use if you want to validate against a full JSON schema

    def validate_tests(self, raw_tests: List[Dict]) -> List[Dict]:
        valid_tests = []
        for test in raw_tests:
            try:
                # Validate using our Pydantic model
                validated = TestSchemaModel.parse_obj(test)
                valid_tests.append(validated.dict())
            except ValidationError as ve:
                print(f"Validation error: {ve}")
        return valid_tests

# --- Classification & Ranking Engine ---


class TestClassifierRanker:
    def __init__(self, allowed_events: List[str]):
        self.allowed_events = allowed_events

    def classify_and_rank(self, tests: List[Dict]) -> List[Dict]:
        # For now, assign a fixed score and filter out any CheckEventTest with an event not in allowed_events.
        ranked_tests = []
        for test in tests:
            score = 1.0  # Placeholder ranking score
            if test["type"] == "CheckEventTest":
                if test.get("event_name") in self.allowed_events:
                    test["score"] = score
                    ranked_tests.append(test)
            else:
                test["score"] = score
                ranked_tests.append(test)
        # Sort tests by score descending (here trivial because all scores are equal)
        ranked_tests.sort(key=lambda x: x["score"], reverse=True)
        return ranked_tests

# --- Test Selection Module ---


class TestSelectionModule:
    def select_tests(self, ranked_tests: List[Dict]) -> List[Dict]:
        # For this example, select one test per type to get a balanced set.
        selected = {}
        for test in ranked_tests:
            ttype = test["type"]
            if ttype not in selected:
                selected[ttype] = test
        return list(selected.values())
