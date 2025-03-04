# prompts.py

GLOBAL_TASK_GENERATION_PROMPT = """
# Task Generation Request

## Use Case Information
- Name: {use_case_name}
- Description: {use_case_description}
- Success Criteria: {success_criteria}

## Domain-Specific Examples:
{examples_str}

## Validation Requirements:
This task must create an event that satisfies these validation criteria:
{validation_schema}

## Instructions
Generate {num_prompts} realistic, specific user tasks for the "{use_case_name}" use case.
Each task should be something a real user would want to do on this website.
Make tasks specific with real examples, not generic placeholders.
Each task must have clear success criteria that can be verified.

## Required Format
Respond ONLY with a JSON array of task objects. Each object should have:
- "prompt": Clear user instruction for what to do
- "success_criteria": Specific condition that indicates task success

Example format:
[
  {{
    "prompt": "Search for 'Inception' movie and view its details page",
    "success_criteria": "The movie details page for 'Inception' is displayed"
  }}
]
"""
