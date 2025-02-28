# file: prompts.py

TEST_GENERATION_PROMPT = """
You are a specialized test engineer tasked with generating validation tests for our web agent benchmark framework. These tests will execute after each agent action, examining browser snapshots to determine if the agent has successfully completed the required task.

## Task Information
- Task Description: {task_prompt}
- Success Requirements: {success_criteria}

## Context
- Current Page HTML (truncated): {truncated_html}
- Visual State Description: {screenshot_desc}
- Available Interactive Elements: {interactive_elements}
- Domain/Project Context: {domain_analysis}

## Test Classes
{test_classes_info}


## Instructions
1. For each test class, evaluate whether it is appropriate for verifying the success criteria for this task. If not do not include that test class.
2. For each relevant test class, create ONE test object that:
   - Strictly adheres to the provided schema
   - Contains ONLY fields defined in the schema (no additional keys)
   - Sets the `type` field to exactly the test class name
   - Provides meaningful values for all required fields that will effectively validate task completion
3. Your response must ONLY contain valid JSON array of tests (no explanations, markdown, or comments)
4. The test should successfully evaluates the completion of the task in an objective and deterministic way. 
5. Avoid including tests that validate the same thing. Prioritize keeping CheckEvents tests in case you have to delete 1 to avoid duplication. 
6. Try not to make up things and when creating the test attrs like substring for the FindInHTMl test.

## Response Format
Return an array of test objects, one for each relevant test class:
[
  {{
    "type": "TestClassName1",
    ...other required and optional fields...
  }},
  {{
    "type": "TestClassName2",
    ...other required and optional fields...
  }}
]
"""

TEST_FILTERING_PROMPT = """
You are a test analyzer for web automation testing. Review the tests below and decide which ones to keep.

TASK CONTEXT:
- Task Prompt: {task_prompt}
- Success Criteria: {success_criteria}

TESTS TO REVIEW:
{tests_json}

GUIDELINES:
1. Backend tests (CheckEventTest, CheckPageViewEventTest) are preferred over frontend tests or checkUrl tests as they are more reliable. Only in case they try to validate the same thing.
2. Intelligent judgment tests (JudgeBaseOnHTML, JudgeBaseOnScreenshot) are useful for complex criteria
3. Avoid keeping tests that check for the same thing in different ways
4. Prioritize tests that directly verify the success criteria
5. Aim to keep 1-3 high-quality tests in total
6. Delete tests that make up parameters like making up event_names in CheckEventTest, or making up keywords in FindInHtmlTest.
7. Judge Tests like JudgeBaseOnHTML or JudgeBaseOnScreenshot should be use if all the other tests do not validate completely the task or there are no more tests. This are fallback tests.

RESPOND WITH A JSON ARRAY of decisions, one for each test, like this:
[
  {{
    "index": 0,
    "keep": true,
    "reason": "High quality backend test that verifies core success criteria"
  }},
  {{
    "index": 1,
    "keep": false,
    "reason": "Redundant with test #0 which is more reliable"
  }}
]

For EACH test in the input, include a decision object with:
- "index": The original index of the test
- "keep": true/false decision
- "reason": Brief explanation of your decision

Return ONLY the JSON array, no additional text.

Extra Class-Specific Data:
{extra_data}
"""
