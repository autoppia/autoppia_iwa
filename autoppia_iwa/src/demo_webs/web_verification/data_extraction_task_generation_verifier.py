"""
Data-extraction task-generation verifier for the web verification pipeline.

Generates DEtasks for each configured DE use case and validates generation quality:
- one task per expected DE use case
- seed consistency in URL
- expected answer presence
- expected answer exists in the seed dataset
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
from collections import defaultdict
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import WebProject


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def _normalize_use_case_name(value: str | None) -> str:
    return str(value or "").strip().upper()


def _normalize_expected(expected_answer: Any) -> list[str]:
    if isinstance(expected_answer, list):
        return [str(value) for value in expected_answer if str(value).strip()]
    if expected_answer is None:
        return []
    text = str(expected_answer).strip()
    return [text] if text else []


class DataExtractionTaskGenerationVerifier:
    """Generates DEtasks and validates basic generation correctness for a project."""

    def __init__(
        self,
        web_project: WebProject,
        *,
        task_generator: SimpleTaskGenerator | None = None,
    ) -> None:
        self.web_project = web_project
        self.task_generator = task_generator or SimpleTaskGenerator(web_project=web_project)

    async def verify_for_project(self, *, seed: int = 1, use_cases: list[str] | None = None) -> dict[str, Any]:
        expected_use_cases = self._resolve_expected_use_cases(use_cases=use_cases)
        if not expected_use_cases:
            return {
                "skipped": True,
                "reason": f"No DE use cases configured for project '{self.web_project.id}'",
                "project_id": self.web_project.id,
                "seed": seed,
                "expected_use_cases": [],
                "generated_count": 0,
                "passed_count": 0,
                "total_count": 0,
                "all_passed": None,
                "results": [],
            }

        generated_tasks, generation_error = await self._generate_de_tasks(seed=seed, selected_use_cases=set(expected_use_cases))
        if generated_tasks is None:
            return {
                "skipped": True,
                "reason": generation_error or "Could not generate DE tasks",
                "project_id": self.web_project.id,
                "seed": seed,
                "expected_use_cases": expected_use_cases,
                "generated_count": 0,
                "passed_count": 0,
                "total_count": 0,
                "all_passed": None,
                "results": [],
            }

        dataset = await self._load_dataset(seed)
        dataset_text = self._dataset_to_text(dataset)
        normalized_dataset_text = _normalize_text(dataset_text)

        tasks_by_use_case: dict[str, list[Task]] = defaultdict(list)
        for task in generated_tasks:
            use_case_name = _normalize_use_case_name(getattr(task, "de_use_case_name", None))
            tasks_by_use_case[use_case_name].append(task)

        results: list[dict[str, Any]] = []

        for use_case_name in expected_use_cases:
            bucket = tasks_by_use_case.pop(use_case_name, [])
            if not bucket:
                results.append(
                    {
                        "use_case": use_case_name,
                        "task_id": None,
                        "ok": False,
                        "detail": "No generated DEtask for this use case",
                        "checks": {
                            "has_task": False,
                            "single_task_for_use_case": False,
                        },
                    }
                )
                continue

            if len(bucket) > 1:
                results.append(
                    {
                        "use_case": use_case_name,
                        "task_id": None,
                        "ok": False,
                        "detail": f"Expected one DEtask for use case, found {len(bucket)}",
                        "checks": {
                            "has_task": True,
                            "single_task_for_use_case": False,
                        },
                    }
                )
                continue

            task = bucket[0]
            results.append(self._validate_generated_task(task=task, use_case_name=use_case_name, seed=seed, normalized_dataset_text=normalized_dataset_text))

        for unexpected_use_case, bucket in sorted(tasks_by_use_case.items()):
            for task in bucket:
                results.append(
                    {
                        "use_case": unexpected_use_case,
                        "task_id": getattr(task, "id", None),
                        "ok": False,
                        "detail": "Unexpected DEtask generated for non-requested use case",
                        "checks": {
                            "expected_use_case": False,
                        },
                        "prompt": getattr(task, "prompt", ""),
                        "expected_answer": self._extract_expected_answer(task),
                    }
                )

        passed_count = sum(1 for item in results if item.get("ok"))
        total_count = len(results)
        all_passed = bool(total_count > 0 and passed_count == total_count)

        return {
            "skipped": False,
            "project_id": self.web_project.id,
            "seed": seed,
            "expected_use_cases": expected_use_cases,
            "generated_count": len(generated_tasks),
            "generated_use_cases": sorted({_normalize_use_case_name(getattr(task, "de_use_case_name", None)) for task in generated_tasks}),
            "passed_count": passed_count,
            "total_count": total_count,
            "all_passed": all_passed,
            "results": results,
        }

    async def _generate_de_tasks(self, *, seed: int, selected_use_cases: set[str]) -> tuple[list[Task] | None, str | None]:
        project_module_name = self.task_generator._get_project_module_name()
        if not project_module_name:
            return None, f"Could not resolve project module for '{self.web_project.id}'"

        module_path = f"autoppia_iwa.src.demo_webs.projects.{project_module_name}.dataExtractionUseCases"
        try:
            de_module = importlib.import_module(module_path)
        except Exception as exc:
            return None, f"Could not import DE use cases module '{module_path}': {exc}"

        generate_fn = getattr(de_module, "generate_de_tasks", None)
        if not callable(generate_fn):
            return None, f"Module '{module_path}' does not expose callable generate_de_tasks"

        seeded_url = self._build_seeded_url(self.web_project.frontend_url, seed=seed)
        generated = generate_fn(
            seed=int(seed),
            task_url=seeded_url,
            selected_use_cases=set(selected_use_cases),
        )
        de_tasks = await generated if inspect.isawaitable(generated) else generated
        if not isinstance(de_tasks, list):
            return None, "generate_de_tasks did not return a list"

        tasks = [task for task in de_tasks if isinstance(task, Task)]
        return tasks, None

    async def _load_dataset(self, seed: int) -> dict[str, list[dict]] | None:
        return await self.task_generator._load_dataset(seed)

    def _resolve_expected_use_cases(self, *, use_cases: list[str] | None) -> list[str]:
        if use_cases:
            return sorted({_normalize_use_case_name(name) for name in use_cases if str(name).strip()})

        project_use_cases = getattr(self.web_project, "data_extraction_use_cases", None) or []
        normalized_project_use_cases = sorted({_normalize_use_case_name(name) for name in project_use_cases if str(name).strip()})
        if normalized_project_use_cases:
            return normalized_project_use_cases

        return self._get_default_de_use_cases_from_module()

    def _get_default_de_use_cases_from_module(self) -> list[str]:
        project_module_name = self.task_generator._get_project_module_name()
        if not project_module_name:
            return []

        module_path = f"autoppia_iwa.src.demo_webs.projects.{project_module_name}.dataExtractionUseCases"
        try:
            de_module = importlib.import_module(module_path)
        except Exception:
            return []

        defs = getattr(de_module, "DATA_EXTRACTION_USE_CASES", None)
        if not isinstance(defs, list):
            return []
        names = []
        for item in defs:
            name = _normalize_use_case_name(getattr(item, "name", None))
            if name:
                names.append(name)
        return sorted(set(names))

    def _validate_generated_task(
        self,
        *,
        task: Task,
        use_case_name: str,
        seed: int,
        normalized_dataset_text: str,
    ) -> dict[str, Any]:
        prompt = str(getattr(task, "prompt", "") or "")
        expected_answer = self._extract_expected_answer(task)
        expected_values = _normalize_expected(expected_answer)
        task_use_case_name = _normalize_use_case_name(getattr(task, "de_use_case_name", None))
        task_seed = self._extract_seed_from_url(getattr(task, "url", ""))

        checks = {
            "has_prompt": bool(prompt.strip()),
            "has_expected_answer": bool(expected_values),
            "use_case_matches": bool(task_use_case_name == use_case_name),
            "seed_matches": bool(task_seed == int(seed)),
            "expected_answer_in_dataset": self._expected_in_dataset(normalized_dataset_text, expected_values),
            "has_data_extraction_test": self._has_data_extraction_test(task),
        }

        failed_checks = [name for name, ok in checks.items() if not ok]
        ok = len(failed_checks) == 0
        detail = "Generated DEtask is consistent with seed dataset and expected answer" if ok else f"Failed checks: {', '.join(failed_checks)}"

        return {
            "use_case": use_case_name,
            "task_id": getattr(task, "id", None),
            "ok": ok,
            "detail": detail,
            "checks": checks,
            "prompt": prompt,
            "expected_answer": expected_answer,
            "task_seed": task_seed,
        }

    @staticmethod
    def _has_data_extraction_test(task: Task) -> bool:
        return any(getattr(test, "type", None) == "DataExtractionTest" for test in getattr(task, "tests", []) or [])

    @staticmethod
    def _extract_expected_answer(task: Task) -> Any:
        expected = getattr(task, "de_expected_answer", None)
        if expected is not None:
            return expected

        for test in getattr(task, "tests", []) or []:
            if getattr(test, "type", None) == "DataExtractionTest":
                return getattr(test, "expected_answer", None)
        return None

    @staticmethod
    def _expected_in_dataset(normalized_dataset_text: str, expected_values: list[str]) -> bool:
        if not normalized_dataset_text:
            return False
        if not expected_values:
            return False
        return any(_normalize_text(expected) in normalized_dataset_text for expected in expected_values)

    @staticmethod
    def _dataset_to_text(dataset: dict[str, list[dict]] | None) -> str:
        if not dataset:
            return ""
        try:
            return json.dumps(dataset, ensure_ascii=False, sort_keys=True)
        except Exception:
            return str(dataset)

    @staticmethod
    def _extract_seed_from_url(url: str) -> int | None:
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if query.get("seed"):
                return int(str(query["seed"][0]).strip())
        except Exception:
            return None
        return None

    @staticmethod
    def _build_seeded_url(base_url: str, *, seed: int) -> str:
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        query_params["seed"] = [str(int(seed))]
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
