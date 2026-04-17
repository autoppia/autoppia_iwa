import copy
import inspect
import random
from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import UseCase

from .flow import (
    build_data_extraction_generation_prompt,
    generate_tasks_from_project_data_extraction_use_cases,
)


class DataExtractionTaskGenerator(SimpleTaskGenerator):
    """
    Dedicated generator for DataExtraction tasks.

    It reuses shared infra from SimpleTaskGenerator (URL/seed helpers, dataset loading,
    LLM retry/parsing) but owns the DE-specific prompt and task assembly flow.
    """

    async def generate(
        self,
        prompts_per_use_case: int = 1,
        use_cases: list[str] | None = None,
        dynamic: bool = True,
        *,
        test_types: str = "data_extraction_only",
        data_extraction_use_cases: list[str] | None = None,
    ) -> list[Task]:
        _ = test_types  # API compatibility with TaskGenerationPipeline
        all_tasks: list[Task] = []

        generated_from_de_use_cases = await generate_tasks_from_project_data_extraction_use_cases(
            web_project=self.web_project,
            prompts_per_use_case=prompts_per_use_case,
            dynamic=dynamic,
            data_extraction_use_cases=data_extraction_use_cases,
            get_project_module_name=self._get_project_module_name,
            build_task_url_with_seed=self._build_task_url_with_seed,
        )
        if generated_from_de_use_cases is not None:
            logger.info(f"[DATA_EXTRACTION] Generated {len(generated_from_de_use_cases)} DE tasks from dedicated DE use cases for project '{self.web_project.id}'")
            return generated_from_de_use_cases

        if data_extraction_use_cases is not None:
            web_use_cases = [uc for uc in self.web_project.use_cases if uc.name in data_extraction_use_cases]
            if not web_use_cases:
                logger.warning(f"No matching use cases found for data_extraction_use_cases: {data_extraction_use_cases}. Available: {[uc.name for uc in self.web_project.use_cases]}")
                return all_tasks
        elif use_cases:
            web_use_cases = [uc for uc in self.web_project.use_cases if uc.name in use_cases]
            if not web_use_cases:
                logger.warning(f"No matching use cases found for: {use_cases}. Available: {[uc.name for uc in self.web_project.use_cases]}")
                return all_tasks
        else:
            web_use_cases = self.web_project.use_cases

        for use_case in web_use_cases:
            try:
                tasks_for_use_case = await self.generate_tasks_for_use_case(
                    use_case,
                    number_of_prompts=prompts_per_use_case,
                    dynamic=dynamic,
                )
                all_tasks.extend(tasks_for_use_case)
            except Exception as e:
                logger.error(f"Error generating DE tasks for {use_case.name}: {e!s}")
                continue

        return all_tasks

    async def generate_tasks_for_use_case(
        self,
        use_case: UseCase,
        number_of_prompts: int = 1,
        dynamic: bool = True,
    ) -> list[Task]:
        tasks: list[Task] = []

        for _ in range(number_of_prompts):
            use_case.constraints = None
            task_url = self._build_task_url_with_seed(dynamic=dynamic)
            seed = self._resolve_seed(task_url) if dynamic else 1
            dataset: dict[str, list[dict]] = {}

            use_case_copy = copy.deepcopy(use_case)
            if hasattr(use_case, "generate_constraints_async"):
                dataset = await self._load_dataset(seed) or {}
                try:
                    await use_case_copy.generate_constraints_async(
                        task_url=task_url,
                        dataset=dataset,
                        test_types="data_extraction_only",
                    )
                except Exception as e:
                    logger.error(f"DE constraint generation failed for '{use_case_copy.name}': {e}")
                    continue

            if not use_case_copy.additional_prompt_info:
                use_case_copy.additional_prompt_info = f"GENERATE PROMPT LIKE: {use_case_copy.get_example_prompts_str()}"

            llm_prompt = build_data_extraction_generation_prompt(use_case_copy)
            if llm_prompt is None:
                logger.warning(f"No constraints generated for data-extraction use case '{use_case_copy.name}' (seed={seed}). Skipping iteration.")
                continue

            prompt_list = await self._call_llm_with_retry(llm_prompt)
            if not prompt_list:
                logger.warning(f"No DE prompts returned from LLM for use case '{use_case_copy.name}'")
                continue

            prompt_text = prompt_list[0]
            try:
                replace_kwargs: dict[str, Any] = {}
                if use_case_copy.replace_func:
                    sig = inspect.signature(use_case_copy.replace_func)
                    if "seed_value" in sig.parameters:
                        replace_kwargs["seed_value"] = seed
                    if "dataset" in sig.parameters:
                        if isinstance(dataset, dict) and dataset:
                            entity_list = next((v for v in dataset.values() if isinstance(v, list)), None)
                            replace_kwargs["dataset"] = entity_list
                        else:
                            replace_kwargs["dataset"] = dataset

                if hasattr(use_case_copy, "apply_replacements_async"):
                    replaced_prompt = await use_case_copy.apply_replacements_async(prompt_text, **replace_kwargs)
                else:
                    replaced_prompt = use_case_copy.apply_replacements(prompt_text, **replace_kwargs)

                task = Task(
                    web_project_id=self.web_project.id,
                    url=task_url,
                    prompt=replaced_prompt,
                    use_case=use_case_copy,
                )
                if dynamic:
                    task.assign_seed_to_url()
                tasks.append(task)
                use_case.constraints = None
            except Exception as ex:
                logger.error(f"Could not assemble DE Task for prompt '{prompt_text}': {ex!s}")

        random.shuffle(tasks)
        return tasks
