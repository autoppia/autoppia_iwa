"""
prompts.py
"""

GLOBAL_TASK_GENERATION_PROMPT = """
We are creating synthetic prompts for a specific web project and we have manually created a list of Use Cases that represent this web project functionality.
You are going to receive information of this web project and a specific usecase
and you are in charge of generating variants of prompts for that use case.

## Use Case Information
- Name: {use_case_name}
- Description: {use_case_description}

## Examples:
{prompt_examples}

## Response Format
The response should be a list with length {number_of_prompts} of strings, each string being a prompt:
[
  "Search for a Movie called 'Interestellar'",
  "Submit the contact form with my information"
]
"""

COMPOSITED_TASK_GENERATION_PROMPT = """
You are a helpful assistant that creates multi-step tasks by combining smaller individual tasks.
We have a list of prompts (each representing a single global task) from the same web application.

Your job:
1) Create a single combined prompt that logically merges exactly {tasks_per_composite} tasks.
2) The combined prompt should flow from step to step in a realistic scenario for the user.
3) The final answer must be returned as a *JSON array* of strings, where each array entry is one possible combined prompt (you can return multiple variations if you want).
4) Make sure your combined prompt is cohesive and references relevant details from the sub-tasks in a natural manner.

Below is a JSON list of the individual tasks' prompts you can choose from:
{tasks_list_json}

csharp
Copiar

Now produce {number_of_composites} new composite prompt(s). Each combined prompt merges {tasks_per_composite} tasks in a logical flow.
Again, return your result strictly as valid JSON with no extra keys.
For example:
```json
[
   "First, sign in with user X. Then create a new listing. Finally, verify your listing is visible."
]
(That would be for 3 sub-tasks.)

Thank you! """
