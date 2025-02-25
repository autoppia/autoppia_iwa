
LOCAL_TASKS_CONTEXT_PROMPT = """
Context: 
You are responsible for generating, refining, and validating single-page user tasks for a website through a structured, multi-phase process. This process is inspired by advanced autonomous evaluation frameworks like Infinite Web Arena (IWA) and consists of the following phases:

1. Draft Generation
   - **What:** Create initial task drafts using generative AI techniques to simulate realistic user interactions (e.g., navigation, search, filtering, and transactions) on a single-page interface.
   - **Why:** To generate a diverse set of scenarios that challenge web agents by mimicking dynamic, real-world website behaviors.
   - **How:** Leverage meta-programming and LLMs to produce a broad range of tasks that cover both common and edge-case interactions.

2. Feasibility & Success Criteria Filtering
   - **What:** Evaluate each task draft against predefined feasibility metrics and success criteria.
   - **Why:** To ensure that every task is executable within a real browser environment and that success can be objectively measured through both frontend (DOM analysis, network monitoring, visual verification) and backend (event tracking, state validation) tests.
   - **How:** Automatically filter out tasks that do not meet the criteria, refining the list to include only those with clear, testable outcomes.

3. Concept and Off-Topic Filtering
   - **What:** Review the refined tasks for conceptual coherence and alignment with the website’s objectives.
   - **Why:** To eliminate tasks that are off-topic or that fail to contribute meaningfully to evaluating user-agent interactions, ensuring the focus remains on realistic and valuable web scenarios.
   - **How:** Apply logical checks and thematic filtering to validate that each task contributes to a robust, scalable evaluation framework, similar to how IWA continuously introduces novel challenges to prevent overfitting and memorization.

Overall, your role is to create high-quality, executable tasks that:
- Reflect the complexities of modern web environments.
- Are grounded in both synthetic generation and logical validation.
- Provide clear, measurable outcomes for autonomous testing.
"""


# -----------------------------------------------------------------------------
# [MODIFIED] Enhanced Phase 1 prompt with instructions for more variety:
# -----------------------------------------------------------------------------
PHASE1_GENERATION_SYSTEM_PROMPT = """
We are on Phase 1: Task Prompts Generation
You are a local tasks generator for a website page. Local mean you generate tasks that can be complete within this website. 
You will be provided with:
 - Url of the website
 - A 'clean_html' snippet.
 - A 'screenshot_description' (done by a ML model that parses the UI into text for you to 'see')
 - A list of 'interactive_elements' (forms, links, buttons, toggles, inputs) so you can filter better whats important on the DOM.

**Requirements**:
1. Generate 6 user tasks for this page. 
2. Each task must be a real user scenario (no developer or code editing steps). Should be something a user may ask a 'Web Agent' to do on behalf of him.
3. Enforce variety:
   - If there is at least one form, create a task that fills and submits the form.
   - If there's a search bar, create a task that performs a search.
   - If toggles/accordions exist, create a task to toggle or expand them.
   - Asking to find a way to go to 'X' other url. 
   - Completing the core use-cases that website is for. For example, if we are in a ecommerce product page, adding to cart is the obvious use case. 

4. Each task must be testable:
   - "prompt": brief user instruction
   - "success_criteria": how we know the user succeeded
5. Return valid JSON array:
[
  {
    "prompt": "...",
    "success_criteria": "..."
  },
  ...
]
6. Do not include task like testing the functionality itself or developers stuff. this is for Users who want to automate or who want help when using the website.
7. Do not create tasks about 'knowledge' or finding info as we dont have a way to know in later phases if that task was completed. This include subjective tasks or opinions. 
This can be part of a more general task bun never the whole purpose. So, in summary, avoid fact checking, subjective, opinionated tast. 

Be sure each prompt references actual, existing elements from the snippet or 'interactive_elements'. 
Be sure the task is relevant to the contect the website is is. Do not ask ecommerce related task in wikipedia. 
"""

PHASE2_FEASIBILITY_FILTER_PROMPT = """
We are in Phase 2: Feasibility Filter.
Remove tasks referencing elements that definitely do not exist 
in 'clean_html' or the 'interactive_elements'.
If a task might be referencing something that partially matches 
(e.g., a form with name 'search_form' vs 'searchForm'), keep it.

#Output format:
Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove","reason":"..."},
  ...
]
"""

PHASE2_SUCCESS_CRITERIA_FILTER_PROMPT = """
We Are in Phase 2: Success Criteria Filtering. 
Remove tasks with vague or missing success criteria.
Success Criterial should be enough to verify if the Web Agent who will be in charge of completing this charge has actually completed it. 
So it cant be abstract or subjective. 

#Output format:
Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove"},
  ...
]
"""

PHASE2_CONCEPT_FILTER_PROMPT = """
We Are in Phase 2: Contextual and concept Filtering
You need to Remove off-topic, dev-oriented task, task unrelated to what the website is about tasks. 
For example, if the task is about buying a product but we are in Wikipedia.com its unrelated and should be removed.
#Output format:
Return JSON:
[
  {"prompt": "...","success_criteria": "...","decision":"keep" or "remove"},
  ...
]
"""
