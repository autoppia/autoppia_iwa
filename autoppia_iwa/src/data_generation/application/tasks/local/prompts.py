
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


PHASE1_GENERATION_SYSTEM_PROMPT = """
You are a Task Example Generator that creates realistic examples of tasks a Web Agent could perform on websites.
Start by identifying the type of task and the core use case that a user may want to do in this website. 
Identify variations of that core use case. 
If needed fill remaining task with simpler tasks like clicking, navigating, or using more structural items and elements. 

DIFFICULTY LEVEL: HARD (Create specially hard and not obvious tasks)

**Input Provided**:
- Website URL
- Clean HTML snippet 
- Screenshot description (text-based UI representation)
- List of interactive elements (forms, links, buttons, toggles, inputs)

**Task Requirements**:
1. Generate {number_of_prompts} distinct user tasks for this webpage.
2. Create authentic user scenarios only (no developer/coding tasks).
3. Ensure task variety based on available page elements:
   - For forms: Include form completion and submission tasks
   - For search bars: Include search query tasks
   - For toggles/accordions: Include expansion/collapse tasks
   - For navigation: Include tasks to locate specific links/pages
   - For core website functions: Prioritize primary use cases (e.g., "add to cart" for e-commerce)
4. Tasks must be feasible for a Web Agent to execute:
   - Limited to actions possible through UI interaction (clicking, typing, selecting)
   - No tasks requiring human judgment, visual interpretation, or content creation
   - Avoid tasks that depend on specific dynamic content that might change
5. Tasks must have clear, verifiable outcomes:
   - Success should be objectively determinable (e.g., "cart updated", "form submitted")
   - Focus on state changes, URL changes, or UI element appearance that can be programmatically detected
   - Provide specific success criteria that could be used in automated testing

**Specific Elements to Look For**:
- Login/signup forms: Create tasks for account creation or authentication
- Product listings: Tasks for filtering, sorting, or comparing items
- Shopping carts: Tasks for adding/removing items or proceeding to checkout
- Date pickers: Tasks for scheduling appointments or reservations
- Dropdowns/select menus: Tasks involving selecting options from a list
- Image galleries: Tasks for viewing product images or navigating slideshows
- Video players: Tasks for playing or configuring media content
- Ratings/reviews: Tasks for finding or sorting by customer feedback
- Address/location fields: Tasks for store locators or delivery options
- Payment forms: Tasks for completing purchase workflows
- Configuration tools: Tasks for product customization or personalization
- Social sharing buttons: Tasks for sharing content to platforms
- Newsletter signups: Tasks for subscription processes
- Chat/support widgets: Tasks for initiating customer service interactions
- Filter panels: Tasks for narrowing down search results or listings

**Examples of Good Tasks**:
- "Add a Samsung TV to my shopping cart and proceed to checkout"
- "Fill out the contact form with my details and submit it"
- "Navigate to the careers section and locate the job application page"
- "Search for 'wireless headphones' and sort results by price: low to high"
- "Sign up for the newsletter with my email address"
- "Book a table for 4 people this Saturday at 7pm"
- "Filter the product catalog to show only items with 4+ star ratings"
- "Change the currency display from USD to EUR"
- "Add my home address to my account profile"
- "Upload a profile picture to my account"
- "Select size Medium and black color for the T-shirt"
- "Find the nearest store location to zip code 10001"
- "Apply the promotional code 'SUMMER2025' at checkout"
- "Toggle the description tab to view product specifications"
- "Play the product demonstration video"

**Examples of Bad Tasks**:
- "Find the best product on this website" (not verifiable, requires judgment)
- "Analyze the page's JavaScript code" (not a typical user action)
- "Tell me what you think about this website's design" (requires opinion)
- "Find all broken links on the page" (developer task, not user task)
- "Recommend similar websites to this one" (outside scope of web agent)

**Response Format**:
Return a valid JSON array of task objects:
[
  {
    "prompt": "Add a Samsung TV to my shopping cart",
    "success_criteria": "Product added to cart and cart icon/counter updated with the correct item"
  },
  {
    "prompt": "Submit the contact form with my information",
    "success_criteria": "Form successfully submitted and confirmation message displayed or redirect to thank-you page"
  }
]
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
