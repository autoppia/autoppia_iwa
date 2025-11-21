import asyncio
import json
import random
import re
from typing import Any

from dependency_injector.wiring import Provide
from loguru import logger
from PIL import Image

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM

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


class GlobalTaskGenerationPipeline:
    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLM = Provide[DIContainer.llm_service],
        max_retries: int = 3,
        retry_delay: float = 0.1,
    ):
        self.web_project = web_project
        self.llm_service = llm_service
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._dataset_cache: dict[tuple[str, int], Any] = {}
        self._dataset_cache: dict[tuple[str, int], Any] = {}

    async def generate(self, num_use_cases: int, prompts_per_use_case: int = 5, use_cases: list[str] | None = None, dynamic: bool | None = None) -> list[Task]:
        """
        Generate tasks for all use cases in the web project.
        """
        all_tasks: list[Task] = []

        # If there are no use cases, just return empty
        if not self.web_project.use_cases:
            logger.warning("No use cases found in web project.")
            return all_tasks

        web_use_cases = self.web_project.use_cases
        selective_use_cases = []
        if use_cases:
            selective_use_cases = [uc for uc in web_use_cases if uc.name in use_cases]
            if not selective_use_cases:
                use_case_msg = num_use_cases if num_use_cases else "all"
                logger.warning(f"No matching use cases found for the provided names. Using {use_case_msg} use cases instead.")
            else:
                _log_task_generation("Selecting only the specified use cases for task generation.")
                web_use_cases = selective_use_cases

        if num_use_cases and not selective_use_cases:
            web_use_cases = random.sample(web_use_cases, min(num_use_cases, len(web_use_cases)))

        # Update use cases' prompt info with API data if needed (generic for all projects)
        # This checks if the project's use_cases module has an update_use_cases_prompt_info function
        try:
            from autoppia_iwa.src.demo_webs.projects.data_provider import resolve_v2_seed_from_url

            # Map project IDs to module directory names
            project_id_to_module = {
                "autocinema": "autocinema_1",
                "autobooks": "autobooks_2",
                "autozone": "autozone_3",
                "autodining": "autodining_4",
                "autocrm": "autocrm_5",
                "automail": "automail_6",
                "autodelivery": "autodelivery_7",
                "autolodge": "autolodge_8",
                "autoconnect": "autoconnect_9",
                "autowork": "autowork_10",
                "autocalender": "autocalender_11",
                "autolist": "autolist_12",
                "autodrive": "autodrive_13",
            }

            module_name = project_id_to_module.get(self.web_project.id)
            if module_name:
                module_path = f"autoppia_iwa.src.demo_webs.projects.{module_name}.use_cases"

                try:
                    import importlib

                    use_cases_module = importlib.import_module(module_path)

                    if hasattr(use_cases_module, "update_use_cases_prompt_info"):
                        base_url = self.web_project.urls[0] if self.web_project.urls else self.web_project.frontend_url
                        v2_seed = await resolve_v2_seed_from_url(base_url)

                        dataset_for_info = None
                        gen_module_path = f"autoppia_iwa.src.demo_webs.projects.{module_name}.generation_functions"
                        dataset_for_info = await self._load_dataset_for_module(gen_module_path, v2_seed)
                        dataset_count = len(dataset_for_info) if dataset_for_info is not None and hasattr(dataset_for_info, "__len__") else None

                        await use_cases_module.update_use_cases_prompt_info(
                            seed_value=v2_seed,
                            dataset=dataset_for_info,
                            count=dataset_count,
                        )
                        logger.debug(f"Updated use cases prompt info for {self.web_project.id} with API data")
                except (ImportError, AttributeError):
                    # Project doesn't have update_use_cases_prompt_info function, which is fine
                    pass
        except Exception as e:
            logger.debug(f"Could not update use cases prompt info for {self.web_project.id}: {e}")

        _log_task_generation(f"Generating tasks for all use cases with {prompts_per_use_case} tasks each. Selected {len(web_use_cases)} use cases.")

        for use_case in web_use_cases:
            _log_task_generation(f"Generating tasks for use case: {use_case.name}", context="USE_CASE")
            try:
                tasks_for_use_case = await self.generate_tasks_for_use_case(use_case, prompts_per_use_case, dynamic=dynamic)
                all_tasks.extend(tasks_for_use_case)
                _log_task_generation(f"Generated {len(tasks_for_use_case)} tasks for use case '{use_case.name}'", context="USE_CASE")
            except Exception as e:
                logger.error(f"Error generating tasks for {use_case.name}: {e!s}")
                import traceback

                traceback.print_exc()
                continue

        _log_task_generation(f"Total generated tasks across all use cases: {len(all_tasks)}", context="SUMMARY")
        return all_tasks

    async def generate_tasks_for_use_case(self, use_case: UseCase, number_of_prompts: int = 5, dynamic: bool | None = None) -> list[Task]:
        """
        Generate tasks for a specific use case by calling the LLM with relevant context.

        Args:
            use_case: The use case to generate tasks for
            number_of_prompts: Number of prompts to generate
            dynamic: boolean, seed will be applied to tasks if true
        """
        additional_system_prompt = None
        # Get base URL for initial constraint generation (before tasks are created)
        base_url = self.web_project.urls[0] if self.web_project.urls else self.web_project.frontend_url

        # Pre-compute URL with seed if dynamic is True
        # This ensures constraints are generated with the same seed that will be used in the task URL
        constraint_url = base_url
        if dynamic:
            from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

            seed_value = random.randint(1, 999)
            parsed = urlparse(base_url)
            query_params = parse_qs(parsed.query)

            # Only add if 'seed' not already in URL
            if "seed" not in query_params:
                query_params["seed"] = [str(seed_value)]
                new_query = urlencode(query_params, doseq=True)
                constraint_url = urlunparse(parsed._replace(query=new_query))

        # Generate initial constraints with URL that includes seed (if applicable)
        dataset = None
        if hasattr(use_case, "generate_constraints_async"):
            dataset = await self._preload_dataset_for_use_case(use_case, constraint_url)
            constraints_info = await use_case.generate_constraints_async(task_url=constraint_url, dataset=dataset)
        else:
            constraints_info = "**IMPORTANT:** Do **NOT** invent, assume, or include any constraints. No constraints are provided for this use case."
            additional_system_prompt = constraints_info

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
        prompt_list = await self._call_llm_with_retry(llm_prompt, additional_system_prompt=additional_system_prompt)
        # For each prompt string, create a Task
        url = base_url

        tasks: list[Task] = []
        # Extract seed value from constraint_url for replace functions
        import inspect

        from autoppia_iwa.src.demo_webs.projects.data_provider import resolve_v2_seed_from_url

        # Get seed for replace functions (use resolve to get v2 seed)
        seed_value_for_replace = await resolve_v2_seed_from_url(constraint_url)

        for prompt_text in prompt_list:
            try:
                # Use async version if available, otherwise fall back to sync
                if hasattr(use_case, "apply_replacements_async"):
                    replace_kwargs: dict[str, Any] = {}
                    replace_func = use_case.replace_func
                    if replace_func:
                        sig = inspect.signature(replace_func)
                        if "seed_value" in sig.parameters:
                            replace_kwargs["seed_value"] = seed_value_for_replace
                        if "dataset" in sig.parameters:
                            replace_kwargs["dataset"] = dataset
                    replaced_prompt = await use_case.apply_replacements_async(prompt_text, **replace_kwargs)
                else:
                    replace_kwargs = {}
                    replace_func = use_case.replace_func
                    if replace_func:
                        sig = inspect.signature(replace_func)
                        if "seed_value" in sig.parameters:
                            replace_kwargs["seed_value"] = seed_value_for_replace
                        if "dataset" in sig.parameters:
                            replace_kwargs["dataset"] = dataset
                    replaced_prompt = use_case.apply_replacements(prompt_text, **replace_kwargs)
                # If we pre-generated a v2-seed, set it on the task before creation
                # This ensures the task uses the same v2-seed that was used for constraint generation
                task_data = {
                    "web_project_id": self.web_project.id,
                    "url": constraint_url if dynamic else url,
                    "prompt": replaced_prompt,
                    "html": "",
                    "clean_html": "",
                    "screenshot": None,
                    "screenshot_desc": "",
                    "use_case": use_case,
                    "relevant_data": self.web_project.relevant_data,
                    "dynamic": dynamic or False,
                }
                # Create the task
                # If constraint_url has v2-seed, it will be extracted by assign_v2_seed_to_url() during Task.__init__
                task_obj = Task(**task_data)
                tasks.append(task_obj)
            except Exception as ex:
                logger.error(f"Could not assemble Task for prompt '{prompt_text}': {ex!s}")

        # Shuffle them if you wish, for variety
        random.shuffle(tasks)
        return tasks

    async def _preload_dataset_for_use_case(self, use_case: UseCase, constraint_url: str) -> Any:
        """
        Attempt to pre-load the dataset for a given use case if its generator supports it and the loader signature is compatible.
        """
        generator = use_case.constraints_generator
        if not generator:
            return None

        import inspect

        sig = inspect.signature(generator)
        if "dataset" not in sig.parameters:
            return None

        module_name = getattr(generator, "__module__", None)
        if not module_name:
            return None

        from autoppia_iwa.src.demo_webs.projects.data_provider import resolve_v2_seed_from_url

        v2_seed = await resolve_v2_seed_from_url(constraint_url)
        return await self._load_dataset_for_module(module_name, v2_seed)

    async def _load_dataset_for_module(self, module_name: str, v2_seed: int) -> Any:
        """
        Load and cache dataset results for a generation_functions module keyed by module + seed.
        """
        cache_key = (module_name, v2_seed)
        if cache_key in self._dataset_cache:
            return self._dataset_cache[cache_key]

        import importlib
        import inspect

        try:
            gen_module = importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - best effort
            _log_task_generation(f"Dataset preload skipped (import failed): {exc}", context="OPTIMIZATION")
            return None

        loader = getattr(gen_module, "_get_data", None)
        if loader is None:
            return None

        loader_sig = inspect.signature(loader)
        required_params = [
            param for param in loader_sig.parameters.values() if param.default is inspect._empty and param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        if required_params:
            _log_task_generation(f"Dataset preload skipped due to required params: {[p.name for p in required_params]}", context="OPTIMIZATION")
            return None

        try:
            dataset_result = loader(seed_value=v2_seed)
            dataset = await dataset_result if inspect.isawaitable(dataset_result) else dataset_result
            if dataset:
                _log_task_generation(f"Pre-loaded dataset with v2_seed={v2_seed} ({len(dataset)} items)", context="OPTIMIZATION")
                self._dataset_cache[cache_key] = dataset
            return dataset
        except Exception as exc:  # pragma: no cover - best effort
            _log_task_generation(f"Could not pre-load dataset: {exc}", context="WARNING")
            return None

    async def _call_llm_with_retry(self, llm_prompt: str, additional_system_prompt: str | None = None) -> list[str]:
        """
        Calls the LLM with the given prompt, parsing the response as a list of strings with retry.
        Returns a list of prompt strings.
        """
        base_system_prompt = "You are a helpful assistant that generates user tasks as a list of strings."
        system_prompt = f"{base_system_prompt} {additional_system_prompt}" if additional_system_prompt else base_system_prompt

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": llm_prompt}]

        for attempt in range(self.max_retries):
            try:
                resp_text = await self.llm_service.async_predict(messages=messages, json_format=True)
                parsed_data = self._parse_llm_response(resp_text)
                if parsed_data:
                    return parsed_data
                logger.warning(f"Attempt {attempt + 1}: Could not parse LLM response, retrying...")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
            except Exception as e:
                logger.error(f"Error on LLM call attempt {attempt + 1}: {e!s}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        logger.error(f"All {self.max_retries} attempts to parse LLM response have failed.")
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
    def _assemble_task(
        web_project_id: str, url: str, prompt: str, html: str, clean_html: str, screenshot: Image.Image | None, screenshot_desc: str, use_case: UseCase, relevant_data: dict[str, Any]
    ) -> Task:
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
