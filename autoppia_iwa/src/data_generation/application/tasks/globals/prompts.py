"""
prompts.py
This file defines the prompt template used by the GlobalTaskGenerationPipeline for LLM calls.
"""

GLOBAL_TASK_GENERATION_PROMPT = """
# Global Task Generation Request

## Use Case Information
- Name: {use_case_name}
- Description: {use_case_description}
- Success Criteria: {success_criteria}

## Random Generated Instances:
{random_generated_instances_str}

## Instructions
Generate {num_prompts} realistic, specific user tasks for the "{use_case_name}" use case.
Each task should be something a real user would want to do on this website.
Make tasks specific with real examples, not generic placeholders.
Each task must have clear success criteria that can be verified.

The response should look exactly like this:
[
  {{
    "prompt": "Add a Samsung TV to my shopping cart",
    "success_criteria": "Product added to cart and cart icon/counter updated with the correct item"
  }},
  {{
    "prompt": "Submit the contact form with my information",
    "success_criteria": "Form successfully submitted and confirmation message displayed or redirect to thank-you page"
  }}
]
"""
