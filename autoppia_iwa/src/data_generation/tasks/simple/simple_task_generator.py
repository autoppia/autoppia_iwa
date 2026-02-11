import asyncio
import copy
import importlib
import inspect
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url, resolve_v2_seed_from_url
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.interfaces import ILLM

from .prompts import GLOBAL_TASK_GENERATION_PROMPT

TASK_GENERATION_LEVEL_NAME = "TASK_GENERATION"
TASK_GENERATION_LEVEL_NO = 23


@dataclass(slots=True)
class ConstraintContext:
    url: str
    v2_seed: int


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
        self._seed_cache: dict[str, int] = {}
        self._dataset_cache: dict[tuple, Any] = {}

    async def generate(self, prompts_per_use_case: int = 1, use_cases: list[str] | None = None, dynamic: bool = True) -> list[Task]:
        """
        Generate tasks for use cases in the web project.

        Args:
            prompts_per_use_case: Number of prompts per use case
            use_cases: Optional list of specific use case names to generate. If None, generates for all use cases.
            dynamic: If True, tasks will include random seeds for dynamic content
        """
        all_tasks: list[Task] = []

        # Get use cases to process (default: all use cases)
        web_use_cases = self.web_project.use_cases

        # Filter to specific use cases if requested
        if use_cases:
            web_use_cases = [uc for uc in self.web_project.use_cases if uc.name in use_cases]
            if not web_use_cases:
                logger.warning(f"No matching use cases found for: {use_cases}. Available: {[uc.name for uc in self.web_project.use_cases]}")
                return all_tasks
            _log_task_generation(f"Using {len(web_use_cases)} specified use cases: {[uc.name for uc in web_use_cases]}")

        for use_case in web_use_cases:
            _log_task_generation(f"Generating tasks for use case: {use_case.name}", context="USE_CASE")
            try:
                tasks_for_use_case = await self.generate_tasks_for_use_case(use_case, prompts_per_use_case, dynamic=dynamic)
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

    async def generate_tasks_for_use_case(self, use_case: UseCase, number_of_prompts: int = 1, dynamic: bool = True) -> list[Task]:
        """
        Generate tasks for a specific use case by calling the LLM with relevant context.

        Each prompt is generated independently with its own seed and constraints,
        ensuring variety when multiple prompts are requested.

        Args:
            use_case: The use case to generate tasks for
            number_of_prompts: Number of prompts to generate (each with unique seed/constraints)
            dynamic: If True, tasks will include random seeds for dynamic content
        """
        tasks: list[Task] = []

        # Generate each prompt independently
        for _ in range(number_of_prompts):
            # Build task URL with unique seed for each prompt
            task_url = self._build_task_url_with_seed(dynamic=dynamic)
            seed = get_seed_from_url(task_url) if dynamic else 1

            # Load dataset for this specific seed
            dataset: dict[str, list[dict]] = {}

            # IMPORTANT: Create a deep copy of use_case for this task to preserve constraints
            # Each task needs its own copy so constraints aren't overwritten by subsequent iterations
            use_case_copy = copy.deepcopy(use_case)

            # Generate constraints specific to this seed's dataset
            if hasattr(use_case_copy, "generate_constraints_async"):
                dataset = await self._load_dataset(seed) or {}

                try:
                    constraints_info = await use_case_copy.generate_constraints_async(task_url=task_url, dataset=dataset)
                except Exception as e:
                    logger.error(f"Constraint generation failed for '{use_case_copy.name}': {e}")
                    continue  # Skip this iteration
            else:
                constraints_info = "**IMPORTANT:** Do **NOT** invent, assume, or include any constraints. No constraints are provided for this use case."

            # Build the LLM prompt (always generate 1 prompt per call)
            if not use_case_copy.additional_prompt_info:
                use_case_copy.additional_prompt_info = f"GENERATE PROMPT LIKE: {use_case_copy.get_example_prompts_str()}"

            llm_prompt = GLOBAL_TASK_GENERATION_PROMPT.format(
                use_case_name=use_case_copy.name,
                use_case_description=use_case_copy.description,
                additional_prompt_info=use_case_copy.additional_prompt_info,
                constraints_info=constraints_info,
            )

            # Call the LLM and get a single prompt
            prompt_list = await self._call_llm_with_retry(llm_prompt)

            # Process only the first prompt from the LLM response for this iteration
            # This ensures we generate exactly number_of_prompts tasks total
            if not prompt_list:
                logger.warning(f"No prompts returned from LLM for use case '{use_case_copy.name}'")
                continue

            # Take only the first prompt for this iteration
            prompt_text = prompt_list[0]

            try:
                # Build replace kwargs with this seed's data
                replace_kwargs: dict[str, Any] = {}
                if use_case_copy.replace_func:
                    sig = inspect.signature(use_case_copy.replace_func)
                    if "seed_value" in sig.parameters:
                        replace_kwargs["seed_value"] = seed
                    if "dataset" in sig.parameters:
                        # Only extract if dataset is a dict, otherwise pass through as-is
                        if isinstance(dataset, dict) and dataset:
                            # Extract first list value from dict (most projects use {"entity_type": [...]})
                            entity_list = next((v for v in dataset.values() if isinstance(v, list)), None)
                            replace_kwargs["dataset"] = entity_list
                        else:
                            replace_kwargs["dataset"] = dataset

                # Apply replacements (async or sync)
                if hasattr(use_case_copy, "apply_replacements_async"):
                    replaced_prompt = await use_case_copy.apply_replacements_async(prompt_text, **replace_kwargs)
                else:
                    replaced_prompt = use_case_copy.apply_replacements(prompt_text, **replace_kwargs)

                # Create and append task - use the COPY which has constraints preserved
                tasks.append(
                    Task(
                        web_project_id=self.web_project.id,
                        url=task_url,
                        prompt=replaced_prompt,
                        use_case=use_case_copy,  # Use the copy with preserved constraints
                    )
                )
            except Exception as ex:
                logger.error(f"Could not assemble Task for prompt '{prompt_text}': {ex!s}")

        random.shuffle(tasks)
        return tasks

    async def _preload_dataset_for_use_case(self, use_case: UseCase, v2_seed: int) -> Any:
        """
        Load complete dataset for the current project with given seed.

        Each project has its own `get_all_data` function in its `data_utils.py` module
        that returns a dictionary with all relevant entities for that project. This pattern
        allows each project to auto-manage its data loading and maintain separation of concerns.
        Attempt to pre-load the dataset for a given use case if its generator supports it and the loader signature is compatible.

        Returns None if dataset cannot be loaded (server unavailable, etc.) - this is OK,
        constraints can still be generated using GPT without the dataset.
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

        try:
            return await self._load_dataset_for_module(module_name, v2_seed)
        except Exception as e:
            # Don't propagate errors - dataset is optional
            logger.debug(f"Could not preload dataset for use case '{use_case.name}': {e}. Will generate constraints without dataset.")
            return None

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

    async def _load_dataset(self, seed: int) -> dict[str, list[dict]] | None:
        """
        Load complete dataset for the current project with given seed.

        Uses the project's `fetch_data` function in its `data_utils.py` module.
        For single-entity projects, wraps the result in a dictionary with entity type as key.
        For multi-entity projects, fetches all entity types and combines them.
        """
        try:
            # Use the same method as _get_project_module_name to find the project directory
            # This ensures consistency and handles the path correctly
            project_dir = self._get_project_module_name()

            if not project_dir:
                logger.debug(f"No project directory found for {self.web_project.id}")
                return None

            # Import the module
            module = importlib.import_module(f"autoppia_iwa.src.demo_webs.projects.{project_dir}.data_utils")
            fetch_data = getattr(module, "fetch_data", None)

            if not fetch_data:
                logger.debug(f"No fetch_data function found in {project_dir}/data_utils.py")
                return None

            # Inspect function signature to determine if entity_type is required
            sig = inspect.signature(fetch_data)
            has_entity_type_param = "entity_type" in sig.parameters

            if has_entity_type_param:
                # Multi-entity project (e.g., autocrm_5)
                # Get entity types from project metadata or known list
                entity_types = self._get_entity_types_for_project(project_dir)
                if not entity_types:
                    logger.debug(f"Could not determine entity types for {project_dir}")
                    return None

                dataset = {}
                for entity_type in entity_types:
                    try:
                        result = fetch_data(entity_type=entity_type, seed_value=seed, count=50)
                        items = await result if inspect.isawaitable(result) else result
                        if items:
                            dataset[entity_type] = items
                    except Exception as e:
                        logger.debug(f"Error fetching {entity_type} for {project_dir}: {e}")
                        continue

                if dataset:
                    total_items = sum(len(v) for v in dataset.values() if isinstance(v, list))
                    _log_task_generation(f"Loaded dataset for {self.web_project.id} with seed={seed} ({total_items} items across {len(dataset)} entities)", context="OPTIMIZATION")
                return dataset if dataset else None
            else:
                # Single-entity project (e.g., autocinema_1, autobooks_2)
                result = fetch_data(seed_value=seed, count=50)
                items = await result if inspect.isawaitable(result) else result

                if not items:
                    return None

                # Determine entity type for this project
                entity_type = self._get_entity_type_for_project(project_dir)
                if not entity_type:
                    logger.debug(f"Could not determine entity type for {project_dir}")
                    return None

                dataset = {entity_type: items}
                total_items = len(items)
                _log_task_generation(f"Loaded dataset for {self.web_project.id} with seed={seed} ({total_items} items across 1 entity)", context="OPTIMIZATION")
                return dataset

        except Exception as e:
            logger.debug(f"Could not load dataset for {self.web_project.id}: {e}")
            return None

    def _get_entity_type_for_project(self, project_dir: str) -> str | None:
        """Get the primary entity type for a single-entity project."""
        # Map project directories to their entity types
        entity_type_map = {
            "autocinema_1": "movies",
            "autobooks_2": "books",
            "autozone_3": "products",
            "autodining_4": "restaurants",
            "automail_6": "emails",
            "autodelivery_7": "restaurants",
            "autolodge_8": "hotels",
            "autoconnect_9": "users",  # Primary entity, but has multiple
            "autowork_10": "jobs",  # Primary entity, but has multiple
            "autocalendar_11": "events",
            "autolist_12": "tasks",
            "autodrive_13": "places",  # Primary entity, but has multiple
            "autohealth_14": "appointments",  # Primary entity, but has multiple
        }
        return entity_type_map.get(project_dir)

    def _get_entity_types_for_project(self, project_dir: str) -> list[str] | None:
        """Get all entity types for a multi-entity project."""
        # Map project directories to their entity types
        entity_types_map = {
            "autocrm_5": ["matters", "clients", "logs", "events", "files"],
            "autoconnect_9": ["users", "posts", "jobs", "recommendations"],
            "autowork_10": ["jobs", "experts", "hires", "skills"],
            "autodrive_13": ["places", "rides"],
            "autohealth_14": ["appointments", "doctors", "prescriptions", "medical-records"],
        }
        return entity_types_map.get(project_dir)

    def _get_project_module_name(self) -> str | None:
        """Auto-detect project module name from filesystem.

        Finds the directory in src/demo_webs/projects/ that starts with project.id.
        Example: "autocinema" → finds "autocinema_1"
        """

        project_id = self.web_project.id
        projects_dir = Path(__file__).resolve().parents[3] / "demo_webs" / "projects"

        try:
            # Find directories starting with project_id
            matches = [d.name for d in projects_dir.iterdir() if d.is_dir() and d.name.startswith(f"{project_id}_")]
            if matches:
                return matches[0]

            # Fallback: try exact match
            exact_match = projects_dir / project_id
            if exact_match.is_dir():
                return project_id

        except Exception:
            pass

        return None

    def _get_base_url(self) -> str:
        return self.web_project.urls[0] if self.web_project.urls else self.web_project.frontend_url

    def _build_constraint_url(self, base_url: str, dynamic: bool | None) -> str:
        if not dynamic:
            return base_url

        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        if "seed" in query_params:
            return base_url

        seed_value = random.randint(1, 999)
        query_params["seed"] = [str(seed_value)]
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    async def _build_constraint_context(self, base_url: str, dynamic: bool | None) -> ConstraintContext:
        constraint_url = self._build_constraint_url(base_url, dynamic)
        v2_seed = await self._resolve_seed(constraint_url)
        return ConstraintContext(url=constraint_url, v2_seed=v2_seed)

    async def _resolve_seed(self, url: str) -> int:
        if url in self._seed_cache:
            return self._seed_cache[url]
        v2_seed = await resolve_v2_seed_from_url(url)
        self._seed_cache[url] = v2_seed
        return v2_seed

    @staticmethod
    def _dataset_length(dataset: Any) -> int | None:
        if dataset is None:
            return None
        try:
            return len(dataset)
        except TypeError:
            return None

    async def _update_use_cases_prompt_info(self, base_url: str) -> None:
        module_name = self._get_project_module_name()
        if not module_name:
            return

        module_path = f"autoppia_iwa.src.demo_webs.projects.{module_name}.use_cases"

        try:
            import importlib

            use_cases_module = importlib.import_module(module_path)
        except ImportError:
            return

        if not hasattr(use_cases_module, "update_use_cases_prompt_info"):
            return

        try:
            base_seed = await self._resolve_seed(base_url)
            gen_module_path = f"autoppia_iwa.src.demo_webs.projects.{module_name}.generation_functions"
            dataset = await self._load_dataset_for_module(gen_module_path, base_seed)
            dataset_count = self._dataset_length(dataset)

            await use_cases_module.update_use_cases_prompt_info(seed_value=base_seed, dataset=dataset, count=dataset_count)
            logger.debug(f"Updated use cases prompt info for {self.web_project.id} with API data")
        except Exception as exc:
            logger.debug(f"Could not update use cases prompt info for {self.web_project.id}: {exc}")

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

    def _build_task_url_with_seed(self, dynamic: bool = True) -> str:
        """Build the task URL with random seed if dynamic generation is enabled."""
        base_url = self.web_project.frontend_url

        if not dynamic:
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
