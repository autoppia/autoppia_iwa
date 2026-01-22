import asyncio
import inspect
import json
import random
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.interfaces import ILLM

from .prompts import GLOBAL_TASK_GENERATION_PROMPT

TASK_GENERATION_LEVEL_NAME = "TASK_GENERATION"
TASK_GENERATION_LEVEL_NO = 23


def _ensure_task_generation_level() -> None:
    """Ensure the TASK_GENERATION level exists when fallback logging is used."""
    try:
        logger.level(TASK_GENERATION_LEVEL_NAME)
    except ValueError:
        logger.level(TASK_GENERATION_LEVEL_NAME, TASK_GENERATION_LEVEL_NO)


def _log_task_generation(message: str, context: str = "TASK_GENERATION") -> None:
    """Log task generation events with TASK_GENERATION level or fallback."""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_task_generation_event

        log_task_generation_event(message, context=context)
    except ImportError:
        _ensure_task_generation_level()
        prefix = "" if context == "TASK_GENERATION" else f"[{context}] "
        logger.log(TASK_GENERATION_LEVEL_NAME, f"{prefix}{message}")


class SimpleTaskGenerator:
    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ):
        self.web_project = web_project
        self.llm_service = llm_service
        self._dataset_cache: dict[tuple[str, int], Any] = {}

    async def generate(self, prompts_per_use_case: int = 1, use_cases: list[str] | None = None, dynamic: bool = True) -> list[Task]:
        """
        Generate tasks for use cases in the web project.
        
        Args:
            prompts_per_use_case: Number of prompts per use case
            use_cases: Optional list of specific use case names to generate. If None, generates for all use cases.
            dynamic: If True, tasks will include random seeds for dynamic content
        """
        self.dynamic = dynamic
        all_tasks: list[Task] = []

        # Get use cases to process
        if use_cases:
            # Filter to specific use cases
            web_use_cases = [uc for uc in self.web_project.use_cases if uc.name in use_cases]
            if not web_use_cases:
                logger.warning(f"No matching use cases found for: {use_cases}. Available: {[uc.name for uc in self.web_project.use_cases]}")
                return all_tasks
            _log_task_generation(f"Using {len(web_use_cases)} specified use cases: {[uc.name for uc in web_use_cases]}")
        else:
            # Use all available use cases
            web_use_cases = self.web_project.use_cases


        for use_case in web_use_cases:
            _log_task_generation(f"Generating tasks for use case: {use_case.name}", context="USE_CASE")
            try:
                tasks_for_use_case = await self.generate_tasks_for_use_case(use_case, prompts_per_use_case)
                all_tasks.extend(tasks_for_use_case)
                _log_task_generation(
                    f"Generated {len(tasks_for_use_case)} tasks for use case '{use_case.name}' (requested {prompts_per_use_case})",
                    context="USE_CASE",
                )
            except Exception as e:
                logger.error(f"Error generating tasks for {use_case.name}: {e!s}")
                import traceback

                traceback.print_exc()
                continue

        _log_task_generation(f"Total generated tasks across all use cases: {len(all_tasks)}", context="SUMMARY")
        return all_tasks

    async def generate_tasks_for_use_case(self, use_case: UseCase, number_of_prompts: int = 1) -> list[Task]:
        """
        Generate tasks for a specific use case by calling the LLM with relevant context.

        Args:
            use_case: The use case to generate tasks for
            number_of_prompts: Number of prompts to generate
        """
        # Build task URL (with random seed if dynamic)
        task_url = self._build_task_url_with_seed()
        
        # Initialize dataset as empty list (will be loaded if needed)
        dataset: list[dict] = []

        # Generate initial constraints - load dataset first
        if hasattr(use_case, "generate_constraints_async"):
            # Extract seed from URL and load dataset
            seed = get_seed_from_url(task_url) if self.dynamic else 1
            loaded_dataset = await self._load_dataset(seed)
            
            # If dataset available, use it; otherwise keep empty list
            if loaded_dataset:
                dataset = loaded_dataset
            
            # Generate constraints with dataset
            try:
                constraints_info = await use_case.generate_constraints_async(dataset=dataset)
            except Exception as e:
                logger.error(f"Constraint generation failed for '{use_case.name}': {e}")
                return []  # Skip this use case
        else:
            constraints_info = "**IMPORTANT:** Do **NOT** invent, assume, or include any constraints. No constraints are provided for this use case."

        # Build the LLM prompt using a template
        if not use_case.additional_prompt_info:
            use_case.additional_prompt_info = f"GENERATE PROMPT LIKE: {use_case.get_example_prompts_str()}"
        llm_prompt = GLOBAL_TASK_GENERATION_PROMPT.format(
            use_case_name=use_case.name,
            use_case_description=use_case.description,
            additional_prompt_info=use_case.additional_prompt_info,
            constraints_info=constraints_info,
            number_of_prompts=number_of_prompts,
        )

        # Call the LLM (with retry logic) and parse the list of strings result
        prompt_list = await self._call_llm_with_retry(llm_prompt)
        
        # For each prompt string, create a Task
        tasks: list[Task] = []
        seed_value_for_replace = get_seed_from_url(task_url) if self.dynamic else 1

        for prompt_text in prompt_list:
            try:
                # Build replace kwargs once (used by both sync and async)
                replace_kwargs: dict[str, Any] = {}
                if use_case.replace_func:
                    sig = inspect.signature(use_case.replace_func)
                    if "seed_value" in sig.parameters:
                        replace_kwargs["seed_value"] = seed_value_for_replace
                    if "dataset" in sig.parameters:
                        replace_kwargs["dataset"] = dataset
                
                # Apply replacements (async or sync)
                if hasattr(use_case, "apply_replacements_async"):
                    replaced_prompt = await use_case.apply_replacements_async(prompt_text, **replace_kwargs)
                else:
                    replaced_prompt = use_case.apply_replacements(prompt_text, **replace_kwargs)
                
                # Create and append task
                tasks.append(Task(
                    web_project_id=self.web_project.id,
                    url=task_url,
                    prompt=replaced_prompt,
                    use_case=use_case,
                    relevant_data=self.web_project.relevant_data,
                ))
            except Exception as ex:
                logger.error(f"Could not assemble Task for prompt '{prompt_text}': {ex!s}")

        random.shuffle(tasks)
        return tasks

    async def _load_dataset(self, seed: int) -> list[dict] | None:
        """
        Load dataset for the current project with given seed.
        Uses cache to avoid redundant loads.
        """
        cache_key = (self.web_project.id, seed)
        if cache_key in self._dataset_cache:
            return self._dataset_cache[cache_key]

        # Try to load _get_data from project's generation_functions module
        project_module = f"autoppia_iwa.src.demo_webs.projects.{self.web_project.id}_1.generation_functions"
        
        try:
            import importlib
            import inspect
            
            gen_module = importlib.import_module(project_module)
            loader = getattr(gen_module, "_get_data", None)
            
            if loader is None:
                return None
            
            # Call loader
            dataset_result = loader(seed_value=seed)
            dataset = await dataset_result if inspect.isawaitable(dataset_result) else dataset_result
            
            if dataset:
                self._dataset_cache[cache_key] = dataset
                _log_task_generation(f"Loaded dataset for {self.web_project.id} with seed={seed} ({len(dataset)} items)", context="OPTIMIZATION")
            
            return dataset
            
        except Exception as e:
            logger.debug(f"Could not load dataset for {self.web_project.id}: {e}")
            return None

    def _build_task_url_with_seed(self) -> str:
        """Build the task URL with random seed if dynamic generation is enabled."""
        base_url = self.web_project.frontend_url
        
        if not self.dynamic:
            return base_url
        
        # Add random seed to URL
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        query_params["seed"] = [str(random.randint(1, 999))]
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))


    async def _call_llm_with_retry(self, llm_prompt: str) -> list[str]:
        """
        Calls the LLM with the given prompt, parsing the response as a list of strings with retry.
        Returns a list of prompt strings.
        """
        max_retries = 3
        retry_delay = 0.1
        
        system_prompt = "You are a helpful assistant that generates user tasks as a list of strings."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": llm_prompt}]

        for attempt in range(max_retries):
            try:
                resp_text = await self.llm_service.async_predict(messages=messages, json_format=True)
                parsed_data = self._parse_llm_response(resp_text)
                if parsed_data:
                    return parsed_data
                logger.warning(f"Attempt {attempt + 1}: Could not parse LLM response, retrying...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
            except Exception as e:
                logger.error(f"Error on LLM call attempt {attempt + 1}: {e!s}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))

        logger.error(f"All {max_retries} attempts to parse LLM response have failed.")
        return []

    def _parse_llm_response(self, resp_text: Any) -> list[str]:
        """
        Universal parser: siempre devuelve una lista de strings (prompts),
        limpiando <think> y dicts con claves raras.
        """
        try:
            # Si ya es lista (OpenAI)
            if isinstance(resp_text, list):
                return [str(item) for item in resp_text]

            # Si ya es dict con lista (DeepSeek a veces devuelve {"prompts": [...]} o {"</think>": [...]})
            if isinstance(resp_text, dict):
                for v in resp_text.values():
                    if isinstance(v, list):
                        return [str(item) for item in v]
                return []

            if isinstance(resp_text, str):
                # Clean the response first
                cleaned = self._clean_list_response(resp_text)

                # Try to parse as JSON array
                try:
                    data = json.loads(cleaned)
                    if isinstance(data, list):
                        return [str(item) for item in data]
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")

        return []

    def _clean_list_response(self, content: str) -> str:
        """
        Clean response to ensure it's a valid JSON array of strings.
        Removes markdown, think tags, and other unwanted formatting.
        """
        import json

        if not content:
            return "[]"

        # First, remove <think>...</think> blocks completely (including multiline)
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)

        # Remove any remaining XML-like tags except <username> and <password>
        content = re.sub(r"<(?!/?(?:username|password|web_agent_id)\b)[^>]+>", "", content)

        # Remove markdown code blocks
        content = re.sub(r"```(?:json)?\s*\n?", "", content)
        content = re.sub(r"```\s*$", "", content)

        # Remove any text before the first [ and after the last ]
        content = content.strip()
        start_idx = content.find("[")
        end_idx = content.rfind("]")

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx : end_idx + 1]

        # Try to validate and fix JSON
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                # Ensure all items are strings
                cleaned_list = [str(item) for item in parsed]
                return json.dumps(cleaned_list)
            else:
                # If it's not a list, wrap it
                return json.dumps([str(parsed)])
        except json.JSONDecodeError:
            # If parsing fails, try to extract array-like content
            array_match = re.search(r"\[[\s\S]*?\]", content)
            if array_match:
                try:
                    parsed = json.loads(array_match.group())
                    if isinstance(parsed, list):
                        return json.dumps([str(item) for item in parsed])
                except json.JSONDecodeError:
                    pass

        # Fallback: return empty array
        return "[]"

    @staticmethod
    def _assemble_task(web_project_id: str, url: str, prompt: str, use_case: UseCase, relevant_data: dict[str, Any]) -> Task:
        """
        Assembles a final Task object from the prompt string and loaded page info.
        """
        return Task(
            web_project_id=web_project_id,
            prompt=prompt,
            url=url,
            specifications=BrowserSpecification(),
            relevant_data=relevant_data,
            use_case=use_case,
        )
