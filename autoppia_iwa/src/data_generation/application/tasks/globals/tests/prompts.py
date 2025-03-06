# prompts.py

CHECK_EVENT_TEST_GENERATION_PROMPT = """
You are an AI assistant that generates automated tests for a single use case in JSON format.
Here are the important details:

- **Use Case**: "{use_case_name}"
  - Description: "{use_case_description}"
  - We have manually curated test examples for this use case (see below).
  - If relevant, the event code snippet for this use case is shown further below.

- **Task Prompt**: 
{task_prompt}

- **Use Case Test Examples** (manually assigned):
{use_case_test_examples}

- **Event Code** (if any):
{event_code}

- **Partial HTML** (truncated for brevity):
{truncated_html}

- **Screenshot Description**:
{screenshot_desc}

- **Interactive Elements** (JSON array):
{interactive_elements}

**Only test type** to generate: `CheckEventTest`
Each test object must be in the form:
{
  "type": "CheckEventTest",
  "event_name": "NameOfEventClass",
  "event_criteria": { ... },
  "description": "Optional human-readable note"
}

**Your job**: 
1. Generate a JSON array of **one or more** `CheckEventTest` objects that validate this task’s success under the described use case. 
2. Reference or adapt the "test_examples" if useful, but ensure correctness given the dynamic info in the prompt, HTML, or event code.
3. **Output only** a JSON array with no extra keys or commentary. 
4. Do not wrap the JSON in Markdown. 

Example final structure (no commentary, just JSON):

[
  {
    "type": "CheckEventTest",
    "event_name": "MyEvent",
    "event_criteria": { "expected_field": "someValue" },
    "description": "Ensure MyEvent is triggered with correct data"
  }
]
"""
