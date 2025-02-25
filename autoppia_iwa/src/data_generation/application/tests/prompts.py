# file: prompts.py

TEST_CONTEXT_PROMPT = """
Context on what we are doing:
The Infinite Web Arena (IWA) is an autonomous web agent evaluation framework that overcomes traditional benchmarking limitations by leveraging generative AI and synthetic data to create a scalable testing environment. It enables continuous assessment of web agents in novel scenarios without human intervention.

Key Features of IWA:

- **Autonomous Task Generation:** Utilizes large language models (LLMs) to generate tasks and validation criteria, eliminating the need for human task designers.
- **Comprehensive Testing Methodology:** Manages both frontend and backend environments to evaluate web agent behavior across multiple layers.

  - **Frontend Tests:** Include DOM analysis, network activity monitoring, visual verification, and browser event tracking.
  - **Backend Tests:** Encompass event tracking, state validation, process flow confirmation, and custom event utilization.

### Example Use Case:

1. **Task Generation:** Assigns the task *"Purchase a red dress for under $10,"* with tests verifying a `Purchase()` event where the item is *"red dress"* and the price is less than $10.
2. **Agent Execution:** The agent navigates the site, searches for the product, applies filters, and completes the purchase.
3. **Validation:** Confirms the correct item selection, adherence to price constraints, and successful purchase completion.

By developing skills in controlled settings, agents trained with IWA can effectively navigate complex DOM structures, handle dynamic content, and adapt to diverse website architectures, making them proficient in real-world web environments.
"""

TEST_GENERATION_PER_CLASS_SYSTEM_PROMPT = """
You are a test-generation expert responsible for generating test definitions for our web agents benchmark. 
Our goal is to confirm whether the agent truly completed the user task by checking relevant conditions.

We have a specific test class named: {test_class_name}

Below is the Pydantic (or equivalent) JSON schema describing the fields for {test_class_name}:
{schema_json}

Given the following context:
- Task Prompt: {task_prompt}
- Success Criteria: {success_criteria}
- Truncated HTML (if available):
{truncated_html}
- Screenshot description (if available):
{screenshot_desc}
- Interactive elements (if available):
{interactive_elements}
- Domain/Project analysis (if available):
{domain_analysis}

### Instructions
1. Determine if the test class **{test_class_name}** is relevant for verifying the success criteria. 
   - If **not** relevant, return: `[]` (an empty JSON array).

2. If **{test_class_name}** is relevant, return a strictly valid JSON array with exactly ONE object that adheres to the schema above. 
   - **Do not** include any extra keys that are not in the schema.
   - **Do not** rename or omit the fields that the schema requires.
   - The `type` field **must** be exactly "{test_class_name}".
   - You can fill out the fields with the minimal necessary info to make the test meaningful.

3. Return ONLY valid JSON and nothing else. NO explanations, NO markdown code blocks, NO comments.

Example of valid response format:
[
  {{
    "type": "{test_class_name}",
    "parameter1": "value1",
    "parameter2": "value2"
  }}
]

Example if not relevant:
[]
"""

FILTER_PROMPT = """ 
You are an expert at validating and filtering test cases for web automation. 
Be thorough but conservative in filtering - only remove tests if there's a clear reason.

For each test, evaluate:

Accuracy: For frontend tests, do the keywords actually appear in the HTML? If not , the test is invalid.
Domain Relevance: For backend tests, do URLs / events match the current domain?
Redundancy: Is this test redundant given other tests? (e.g., backend tests may supersede frontend tests)
Success Criteria Alignment: Does this test genuinely validate the task's success criteria?
Return a JSON object containing:

"valid_tests": an array of valid tests after filtering
"filtering_decisions": an array of decisions(kept or removed) with a short explanation
Example format:

json
{
    "valid_tests": [],
    "filtering_decisions": [
        {
            "test": {"type": "frontend", "keywords": ["example"]},
            "kept": false,
            "reason": "Keywords not found in HTML"
        }
    ]
}
"""
