# file: autoppia_iwa/src/data_generation/application/task_contextual_validator.py
from typing import List
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.llms.infrastructure.llm_service import ILLMService


class TaskContextualValidator:
    def __init__(self, domain_analysis: DomainAnalysis, llm_service: ILLMService):
        self.domain_analysis = domain_analysis
        self.llm_service = llm_service

    def validate_tasks(self, tasks: List[Task]) -> List[Task]:
        """Performs both heuristic and LLM-based validation. Returns only the valid tasks."""
        filtered_tasks = []
        for task in tasks:
            if self._heuristic_check(task):
                # If heuristic check passes, we do optional LLM check
                if self._llm_based_check(task):
                    filtered_tasks.append(task)
        return filtered_tasks

    def _heuristic_check(self, task: Task) -> bool:
        """
        Check if the task references features that do not exist in the domain.
        For now, let's do a naive check:
         - If domain_analysis.features is provided,
         - check if the task prompt references any known or unknown features
        """
        # Example: If your domain has features = ["login", "checkout", "search"]
        # and the task prompt includes certain keywords, we can do a quick check:
        prompt_lower = task.prompt.lower()

        # If you want to do something more advanced (like parse the prompt), do it here.
        # For now, let's do a naive example:
        required_features = []
        if "login" in prompt_lower or "log in" in prompt_lower:
            required_features.append("login")
        if "cart" in prompt_lower or "checkout" in prompt_lower:
            required_features.append("checkout")
        if "search" in prompt_lower:
            required_features.append("search")

        # Check if these required features are present in domain_analysis.features
        for feat in required_features:
            if feat not in self.domain_analysis.features:
                print(f"Task FAILED heuristic check: missing feature '{feat}' in domain.")
                return False

        # If no checks fail, we assume it passes
        return True

    def _llm_based_check(self, task: Task) -> bool:
        """
        Optional step: Confirm the task is valid within the domain context using LLM feedback.
        We'll pass a short message containing domain summary and the task prompt.
        Return True if the LLM says 'valid', else False.
        """
        domain_summary = f"Domain Type: {self.domain_analysis.category or 'Unknown'}\\nFeatures: {self.domain_analysis.features}"
        # We'll keep it short to save tokens:
        messages = [
            {
                "role": "system",
                "content": "You are a validation assistant. Determine if the user task is feasible given the domain info."
            },
            {
                "role": "user",
                "content": (
                    f"Domain Info:\n{domain_summary}\n\n"
                    f"Task Prompt:\n{task.prompt}\n\n"
                    "Is this task valid and feasible? Reply exactly with 'VALID' or 'INVALID'."
                ),
            },
        ]

        response = self.llm_service.make_request(
            message_payload=messages,
            chat_completion_kwargs={
                "temperature": 0.0,
                "max_tokens": 10
            },
        )

        if not response:
            return False

        # Very naive parse: check if response contains 'VALID'
        # You might want to parse carefully or do a direct string compare.
        # Usually you'd parse JSON or a strict format. We'll keep it simple:
        resp_lower = response.lower()
        return "valid" in resp_lower
