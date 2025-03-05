# prompts.py

USE_CASE_TEST_GENERATION_PROMPT = """
You are an AI assistant that generates automated tests for a specific use case in JSON format.
Below is the context you have:

- **Use Case Name**: {use_case_name}
- **Use Case Description**: {use_case_description}
- **Task Prompt**: {task_prompt}

- **Example Tests for this Use Case** (these are typical tests or checks we often do):
{use_case_test_examples}

- **Event Code** (if this use case corresponds to a particular event that gets emitted, here is the relevant code snippet):
{event_code}

- **Partial/Truncated HTML** (this is the HTML relevant to the page where the task occurs):
{html}

- **Screenshot Description** (a textual description of the page or screenshot):
{screenshot_desc}

- **Interactive Elements** (JSON array describing forms, buttons, links, etc., extracted from HTML):
{interactive_elements}

Your job:
1. Propose a list of tests that ensure this task was completed successfully **with respect to the described use case**.
2. Return the tests **exclusively** in the form of a **valid JSON array** of objects (no markdown, no extra fields).
3. Each test object **must** have at least:
   - a `"type"` key (e.g. `"CheckEventTest"`, `"CheckUrlTest"`, `"FindInHtmlTest"`, etc.),
   - any additional fields that the chosen test type requires (e.g., `"event_name"`, `"criteria"`, `"code"`, `"selector"`, etc.)

Important:
- Do **not** wrap your JSON in markdown or include any extra commentary.
- Do **not** output anything except the JSON array.

Example format:

[
  {
    "type": "CheckEventTest",
    "event_name": "RegistrationEvent",
    "criteria": {},
    "code": "function or snippet here"
  },
  {
    "type": "FindInHtmlTest",
    "selector": "input[name='username']",
    "expected_value": "some default"
  }
]

Now, **generate the JSON array of test definitions**.
"""
