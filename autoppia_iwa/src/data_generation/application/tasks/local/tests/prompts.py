# file: prompts.py
TEST_GENERATION_PROMPT = """
You are a specialized test engineer tasked with generating validation tests for our web agent benchmark framework. These tests will execute after each agent action, examining browser snapshots to determine if the agent has successfully completed the required task.

## Task Information
- Task Description: {task_prompt}
- Success Requirements: {success_criteria}

## Context
- Current Page URL: {current_url}
- Current Page HTML (truncated): {truncated_html}
- Visual State Description: {screenshot_desc}
- Available Interactive Elements: {interactive_elements}

## Available Backend Events
{events}

## Test Classes
{test_classes_info}

## Instructions on deciding which tests to use and its arguments
1. For each test class, evaluate whether it is appropriate for verifying the success criteria for this task.
2. You can just use 1 test of each type.
3. Each test should objectively and deterministically evaluate the completion of the task
4. Avoid creating tests that validate the same thing; prioritize CheckEventTest in case of duplication
5. Do not create a lot of FindInHTML tests. If you want to use this test use it wisely and in moderation.
6. Do not use any event_name not in the 'Available Backend Events' list

#Instruction on output format
1. YOU MUST OUTPUT ONLY THE JSON ARRAY WITH NO ADDITIONAL TEXT OR FORMATTING.
   - Strictly adheres to the provided schema
   - Contains ONLY fields defined in the schema (no additional keys)
   - Sets the `type` field to exactly the test class name
   - Provides meaningful values for all required fields that will effectively validate task completion
2. YOUR RESPONSE MUST BE A VALID JSON ARRAY ONLY. Do not include code blocks, markdown formatting, explanations, or any text outside the JSON array

## Response Format Examples

For a login task, appropriate tests might look like this exact format:

[
  {{
    "type": "CheckUrlTest",
    "url": "http://localhost:8000/dashboard",
  }},
  {{
    "type": "FindInHtmlTest",
    "substring": "Welcome back",
  }},
  {{
    "type": "CheckEventTest",
    "event_name": "login_success",
  }}
]

For a job application task, appropriate tests might look like this exact format:

[
  {{
    "type": "CheckUrlTest",
    "url": "http://localhost:8000/application-confirmation",
  }},
  {{
    "type": "FindInHtmlTest",
    "substring": "Application submitted successfully",
  }},
  {{
    "type": "CheckEventTest",
    "event_name": "application_submitted",
  }}
]

CRITICAL REQUIREMENTS:
1. Return ONLY the raw JSON array without any backticks, code blocks, or markdown
2. Do not include any text before or after the JSON array
3. The JSON must start with '[' and end with ']'
4. Do not use indentation or newlines different from the examples above
5. Include only test classes that are relevant to the specific task
6. Ensure each test has a clear, descriptive "description" field
"""
