"""
prompts.py
"""

GLOBAL_TASK_GENERATION_PROMPT = """
We are creating synthetic prompts for a specific web project and we have manually created a list of Use Cases that represent this web project functionality.
You are going to receive information of this web project and a specific usecase
and you are in charge or generating variants of prompts for that use case.

## Use Case Information
- Name: {use_case_name}
- Description: {use_case_description}

##Examples:
{prompt_examples}


## Response Format
The response should be a list with lenght {number_of_prompts} of strings, each string being a prompt:
[
  "Search for a Movie called 'Interestellar'",
  "Submit the contact form with my information"
]
"""
