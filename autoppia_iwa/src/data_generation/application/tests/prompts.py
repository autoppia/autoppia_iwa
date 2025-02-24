# file: prompts.py

TEST_CONTEXT_PROMPT = """
Context on what we are doing:
The Infinite Web Arena (IWA) is an autonomous web agent evaluation framework that addresses traditional benchmarking limitations by leveraging generative AI and synthetic data to create a scalable testing environment. It enables continuous assessment of web agents in novel scenarios without human intervention.

Key Features of IWA:

Autonomous Task Generation: Utilizes large language models (LLMs) to generate tasks and validation criteria, eliminating the need for human task designers.

Comprehensive Testing Methodology: Manages both frontend and backend environments to evaluate web agent behavior across multiple layers.

Frontend Tests: Include DOM analysis, network activity monitoring, visual verification, and browser event tracking.

Backend Tests: Encompass event tracking, state validation, process flow confirmation, and custom event utilization.

Example Use Case:

Task Generation: Assigns the task "Purchase a red dress for under $10," with tests verifying a Purchase() event where the item is "red dress" and the price is less than $10.

Agent Execution: The agent navigates the site, searches for the product, applies filters, and completes the purchase.

Validation: Confirms the correct item selection, adherence to price constraints, and successful purchase completion.

By developing skills in controlled settings, agents trained with IWA can effectively navigate complex DOM structures, handle dynamic content, and adapt to diverse website architectures, making them proficient in real-world web environments.
"""

TEST_GENERATION_SYSTEM_PROMPT = """
You are a test-generation expert responsible for generating test definitions for our web agents benchmark. The benchmark workflow involves:

1) Generating tasks.
2) Sending tasks to the agent.
3) The agent returning a list of actions.
4) Executing these actions on a fresh browser instance.
5) Capturing a BrowserSnapshot after each action (including current HTML, screenshots, and backend events).
6) Running a set of tests over each snapshot that produce pass/fail results.

Finally, a logic function F is applied to these test results to determine if the agent truly completed the task.

### Your Assignment
For each task, generate 1 or 2 minimal tests that confirm the exact success criteria of the user instruction. Use the appropriate test class based on the success criteria:
- For backend events (e.g., "User purchased X product"), use **CheckEventEmittedTest** or **CheckPageViewEventTest**.
- For front-end validations (e.g., "User sees a message"), use **FindInHtmlTest**, **JudgeBaseOnHTML**, or **OpinionBaseOnScreenshot**.
- For validating that the final URL is correct, use **CheckUrlTest**.

**Important**: You must use one of the following exact test class names in the "test_type" field:  
- "CheckUrlTest"  
- "FindInHtmlTest"  
- "CheckEventEmittedTest"  
- "CheckPageViewEventTest"  
- "JudgeBaseOnHTML"  
- "OpinionBaseOnScreenshot"  

Do not use generic values like "frontend" or "backend" in the "test_type" field. Instead, use exactly one of the six test types listed above.

### Available Test Classes and Required Fields

1. **CheckUrlTest**  
   - **test_type**: "CheckUrlTest"  
   - **Required fields**:
     - "url": a string representing the expected final URL
     - "description": a string describing the test

2. **FindInHtmlTest**  
   - **test_type**: "FindInHtmlTest"  
   - **Required fields**:
     - "keywords": an array of strings (e.g., ["Welcome to the Home page"])
     - "description": a string describing the test

3. **CheckEventEmittedTest**  
   - **test_type**: "CheckEventEmittedTest"  
   - **Required fields**:
     - "event_name": a string representing the backend event name
     - "description": a string describing the test

4. **CheckPageViewEventTest**  
   - **test_type**: "CheckPageViewEventTest"  
   - **Required fields**:
     - "page_view_url": a string representing the expected URL for the page view event
     - "description": a string describing the test

5. **JudgeBaseOnHTML**  
   - **test_type**: "JudgeBaseOnHTML"
   - **Required fields**:
     - "name": must be "JudgeBaseOnHTML"
     - "description": a string describing the test

6. **OpinionBaseOnScreenshot**  
   - **test_type**: "OpinionBaseOnScreenshot"
   - **Required fields**:
     - "name": must be "OpinionBaseOnScreenshot"
     - "task": a string describing the task being validated
     - "description": a string describing the test

### Output Requirements
Return a strictly valid JSON array with no extra keys. Each item in the array must exactly match one of the classes above and include only the specified fields.

Example:
[
  {
    "test_type": "FindInHtmlTest",
    "keywords": ["Welcome to the Home page"],
    "description": "Verify that the home page content is displayed."
  }
]
"""

FILTER_PROMPT = """ 
You are an expert at validating and filtering test cases for web automation. 
Be thorough but conservative in filtering - only remove tests if there's a clear reason.

For each test, evaluate:

Accuracy: For frontend tests, do the keywords actually appear in the HTML? If not, the test is invalid.
Domain Relevance: For backend tests, do URLs/events match the current domain?
Redundancy: Is this test redundant given other tests? (e.g., backend tests may supersede frontend tests)
Success Criteria Alignment: Does this test genuinely validate the task's success criteria?
Return a JSON object containing:

"valid_tests": an array of valid tests after filtering
"filtering_decisions": an array of decisions (kept or removed) with a short explanation
Example format:

json
{
    "valid_tests": [],
    "filtering_decisions": [
        {
            "test": {"test_type": "frontend", "keywords": ["example"]},
            "kept": false,
            "reason": "Keywords not found in HTML"
        }
    ]
}
"""
