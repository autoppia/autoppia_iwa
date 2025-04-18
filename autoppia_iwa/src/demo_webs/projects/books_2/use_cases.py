from autoppia_iwa.src.demo_webs.classes import UseCase

from .data import BOOKS_DATA
from .events import (
    AddBookEvent,
    AddCommentEvent,
    BookDetailEvent,
    ContactEvent,
    DeleteBookEvent,
    EditBookEvent,
    EditUserEvent,
    FilterBookEvent,
    LoginEvent,
    LogoutEvent,
    PurchaseBookEvent,
    RegistrationEvent,
    SearchBookEvent,
    ShoppingCartEvent,
)
from .generation_functions import (
    generate_add_book_constraints,
    generate_add_comment_constraints,
    generate_book_constraints,
    generate_book_filter_constraints,
    generate_contact_constraints,
    generate_edit_book_constraints,
    generate_edit_profile_constraints,
)
from .replace_functions import login_replace_func, register_replace_func, replace_book_placeholders

###############################################################################
# REGISTRATION_USE_CASE
###############################################################################
REGISTRATION_USE_CASE = UseCase(
    name="REGISTRATION",
    description="The user fills out the registration form and successfully creates a new account.",
    event=RegistrationEvent,
    event_source_code=RegistrationEvent.get_source_code_of_class(),
    replace_func=register_replace_func,
    examples=[
        {
            "prompt": "Register with the following username:<username>,email:<email> and password:<password>",
            "prompt_for_task_generation": "Register with the following username:<username>,email:<email> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "REGISTRATION",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test applies when the task requires a registration event with a specific username.",
            },
        },
        {
            "prompt": "Create a new account with username:<username>,email:<email> and password:<password>",
            "prompt_for_task_generation": "Create a new account with username:<username>,email:<email> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "REGISTRATION",
                "event_criteria": {"username": {"value": "<username>", "operator": "equals"}},
                "reasoning": "This test applies when the task requires registration with a specific username.",
            },
        },
        {
            "prompt": "Fill the registration form with username:<username>, email:<email> and password:<password>",
            "prompt_for_task_generation": "Fill the registration form with username:<username>, email:<email> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "REGISTRATION",
                "event_criteria": {"username": {"value": "<username>"}, "email": {"value": "<email>"}},
                "reasoning": "This test applies when the task requires registration with both username and email specified.",
            },
        },
        {
            "prompt": "Sign up for an account with username:<username>,email:<email> and password:<password>",
            "prompt_for_task_generation": "Sign up for an account with username:<username>,email:<email> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "REGISTRATION",
                "event_criteria": {"username": {"value": "<username>", "operator": "contains"}},
                "reasoning": "This test applies when the task requires registration with a specific username.",
            },
        },
    ],
)

###############################################################################
# LOGIN_USE_CASE
###############################################################################
LOGIN_USE_CASE = UseCase(
    name="LOGIN",
    description="The user fills out the login form and logs in successfully.",
    event=LoginEvent,
    event_source_code=LoginEvent.get_source_code_of_class(),
    replace_func=login_replace_func,
    examples=[
        {
            "prompt": "Login for the following username:<username> and password:<password>",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGIN",
                "event_criteria": {"username": {"value": "<username>", "operator": "equals"}},
                "reasoning": "This test applies when the task requires a login event.",
            },
        },
        {
            "prompt": "Login with a specific username:<username> and password:<password>",
            "prompt_for_task_generation": "Login with a specific username:<username> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGIN",
                "event_criteria": {"username": {"value": "<username>", "operator": "contains"}},
                "reasoning": "This test applies when the task requires a login event with username containing a specific value.",
            },
        },
        {
            "prompt": "Fill the Login Form with a specific username:<username> and password:<password>",
            "prompt_for_task_generation": "Fill the Login Form with a specific username:<username> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGIN",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test applies when the task requires a login event.",
            },
        },
        {
            "prompt": "Sign in to the website username:<username> and password:<password>",
            "prompt_for_task_generation": "Sign in to the website username:<username> and password:<password>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGIN",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test applies when the task requires a login event.",
            },
        },
    ],
)

###############################################################################
# LOGOUT_USE_CASE
###############################################################################
LOGOUT_USE_CASE = UseCase(
    name="LOGOUT",
    description="The user logs out of the platform after logging in.",
    event=LogoutEvent,
    event_source_code=LogoutEvent.get_source_code_of_class(),
    replace_func=login_replace_func,
    examples=[
        {
            "prompt": "Login for the following username:<username> and password:<password>, then logout",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>, then logout",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test verifies that the system can handle a login followed by logout instruction.",
            },
        },
        {
            "prompt": "Login with a specific username:<username> and password:<password>, then sign out from the system",
            "prompt_for_task_generation": "Login with a specific username:<username> and password:<password>, then sign out from the system",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test checks if the system recognizes 'sign out' as a logout action after login.",
            },
        },
        {
            "prompt": "Fill the Login Form with a specific username:<username> and password:<password>, once logged in, logout from my account",
            "prompt_for_task_generation": "Fill the Login Form with a specific username:<username> and password:<password>, once logged in, logout from my account",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test verifies logout detection after form-based login phrasing.",
            },
        },
        {
            "prompt": "Sign in to the website username:<username> and password:<password>, after that please log me out",
            "prompt_for_task_generation": "Sign in to the website username:<username> and password:<password>, after that please log me out",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test ensures logout is detected after 'sign in' terminology.",
            },
        },
        {
            "prompt": "Authenticate with username:<username> and password:<password>, then end my session",
            "prompt_for_task_generation": "Authenticate with username:<username> and password:<password>, then end my session",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {"username": {"value": "<username>"}},
                "reasoning": "This test checks if the system recognizes 'end my session' as a logout request.",
            },
        },
    ],
)


###############################################################################
# BOOK_DETAIL_USE_CASE
###############################################################################

BOOK_DETAIL_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to view details of a book (use phrases like "Show details for...", "Give me information about...")
4. Only use the books name defined below.

BOOKS NAMES:
{chr(10).join([n["name"] for n in BOOKS_DATA])}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Show me details about a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Show me details about a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Show me details about a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""

BOOK_DETAIL_USE_CASE = UseCase(
    name="BOOK_DETAIL",
    description="The user explicitly requests to navigate to or go to the details page of a specific book that meets certain criteria, where they can view information including author, year, genres, rating, page count, and characters.",
    event=BookDetailEvent,
    event_source_code=BookDetailEvent.get_source_code_of_class(),
    additional_prompt_info=BOOK_DETAIL_INFO,
    constraints_generator=generate_book_constraints,
    examples=[
        {
            "prompt": "Navigate to 'The Housemaid Is Watching' book page",
            "prompt_for_task_generation": "Navigate to <book> book page",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"name": {"value": "The Housemaid Is Watching", "operator": "equals"}},
                "reasoning": "Explicitly directs the system to navigate to 'The Housemaid Is Watching' book detail page.",
            },
        },
        {
            "prompt": "Go to the book details page for 'Art of Computer Programming, the, Volumes 1-4B, Boxed Set' by Donald Knuth",
            "prompt_for_task_generation": "Go to the book details page for <book> by <author>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"name": {"value": "Art of Computer Programming, the, Volumes 1-4B, Boxed Set", "operator": "equals"}, "author": {"value": "Donald Knuth", "operator": "equals"}},
                "reasoning": "Explicitly directs the system to go to the 'Art of Computer Programming, the, Volumes 1-4B, Boxed Set' book details page, using author as additional criteria.",
            },
        },
        {
            "prompt": "Navigate directly to a Science book page from 2022",
            "prompt_for_task_generation": "Navigate directly to a <genre> book page from <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"genres": {"value": ["Science"], "operator": "contains"}, "year": {"value": 2022, "operator": "equals"}},
                "reasoning": "Explicitly instructs the system to navigate to a book detail page that matches both genre and year criteria.",
            },
        },
        {
            "prompt": "Go directly to a book page with rating above 4.5",
            "prompt_for_task_generation": "Go directly to a book page with rating above <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"rating": {"value": 4.5, "operator": "greater_than"}},
                "reasoning": "Explicitly instructs the system to go to a book detail page for a highly-rated book that exceeds the specified rating.",
            },
        },
        {
            "prompt": "Take me directly to the 'Fourth Wing' book details page",
            "prompt_for_task_generation": "Take me directly to the <book> book details page",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"name": {"value": "Fourth Wing", "operator": "equals"}},
                "reasoning": "Explicitly requests direct navigation to the 'Fourth Wing' book detail page.",
            },
        },
        {
            "prompt": "Navigate to a 'Magazine' book page less than 1000 pages long",
            "prompt_for_task_generation": "Navigate to a <genre> book page less than <page_count> pages long",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"genres": {"value": ["Magazine"], "operator": "contains"}, "duration": {"value": 1000, "operator": "less_than"}},
                "reasoning": "Explicitly directs the system to navigate to a book detail page that matches both genre and page count criteria.",
            },
        },
        {
            "prompt": "Go to a book details page from the 2010s directed by 'Ron Larson'",
            "prompt_for_task_generation": "Go to a book details page from the <decade> directed by '<author>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"year": {"value": [2010, 2019], "operator": "between"}, "author": {"value": "Ron Larson", "operator": "contains"}},
                "reasoning": "Explicitly instructs the system to go to a book detail page matching both decade range and criteria.",
            },
        },
        {
            "prompt": "Navigate me to a 'Science' book page not written by 'Grant Morrison'",
            "prompt_for_task_generation": "Navigate me to a <genre> book page not written by <author>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"genres": {"value": ["Science"], "operator": "contains"}, "author": {"value": "Grant Morrison", "operator": "not_equals"}},
                "reasoning": "Explicitly directs the system to navigate to a Science book detail page excluding those by the specified author.",
            },
        },
        {
            "prompt": "Go directly to the highest-rated 'Lidia Matticchio Bastianich' book page",
            "prompt_for_task_generation": "Go directly to the highest-rated <author> book page",
            "test": {
                "type": "CheckEventTest",
                "event_name": "BOOK_DETAIL",
                "event_criteria": {"author": {"value": "Lidia Matticchio Bastianich", "operator": "equals"}, "rating": {"value": 4.0, "operator": "greater_equal"}},
                "reasoning": "Explicitly instructs the system to go directly to the book detail page of the highest-rated book by the specified author.",
            },
        },
    ],
)
###############################################################################
# SEARCH_BOOK_USE_CASE
###############################################################################
SEARCH_BOOK_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Make it EXPLICIT that this is a SEARCH for a book using clear terms such as:
   - "Search for..."
   - "Look for the book..."
   - "Find a book..."
   - "Look up a book..."
2. Avoid ambiguous phrases like "Show details" or "Give me information" that could be confused with other actions
3. Include ONLY the book title as part of the search
4. DO NOT include ANY constraints or conditions like author, year, genre, etc.

For example:
- CORRECT: "Search for the book 'A Breath of Snow and Ashes' in the database"
- CORRECT: "Look for the book 'Fourth Wing'"
- CORRECT: "Find books called The 'The Housemaid Is Watching'"
- INCORRECT: "Show me details about 'Fourth Wing'" (doesn't specify it's a search)
- INCORRECT: "Give me information on 'The Housemaid Is Watching'" (ambiguous, doesn't clearly indicate search)
- INCORRECT: "Search for 'A Breath of Snow and Ashes' NOT written by James Cameron" (includes constraints)
- INCORRECT: "Find a book called 'Dark Nights: Metal: Dark Knights Rising' released after 2018" (includes constraints)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL clearly indicating that it is a simple SEARCH with NO additional constraints.
"""

SEARCH_BOOK_USE_CASE = UseCase(
    name="SEARCH_BOOK",
    description="The user searches for a book using a query.",
    event=SearchBookEvent,
    event_source_code=SearchBookEvent.get_source_code_of_class(),
    replace_func=replace_book_placeholders,
    additional_prompt_info=SEARCH_BOOK_INFO,
    examples=[
        {
            "prompt": "Look for the book 'Lidia's Italian-American Kitchen'",
            "prompt_for_task_generation": "Look for the book '<book>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_BOOK",
                "event_criteria": {"query": {"value": "Lidia's Italian-American Kitchen"}},
                "reasoning": "This test applies when searching for a specific book title <book>",
            },
        },
        {
            "prompt": "Find a book called 'Programming Massively Parallel Processors' starring Al Pacino",
            "prompt_for_task_generation": "Find a book called '<book>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_BOOK",
                "event_criteria": {"query": {"value": "Programming Massively Parallel Processors", "operator": "equals"}},
                "reasoning": "This test applies when searching for the book <book>.",
            },
        },
        {
            "prompt": "Search for 'Elementary Statistics' in the book database",
            "prompt_for_task_generation": "Search for '<book>' in the book database",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_BOOK",
                "event_criteria": {"query": {"value": "Elementary Statistics", "operator": "equals"}},
                "reasoning": "This test applies when searching for the book <book>.",
            },
        },
        {
            "prompt": "Look up a book 'Dark Nights: Metal: Dark Knights Rising' featuring Uma Thurman",
            "prompt_for_task_generation": "Look up a book '<book>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_BOOK",
                "event_criteria": {"query": {"value": "Dark Nights: Metal: Dark Knights Rising"}},
                "reasoning": "This test applies when searching for <book>.",
            },
        },
        {
            "prompt": "Find a book called 'Case Files Family Medicine 5th Edition' with Leonardo DiCaprio on the cover",
            "prompt_for_task_generation": "Find a book called '<book>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_BOOK",
                "event_criteria": {"query": {"value": "Case Files Family Medicine 5th Edition", "operator": "equals"}},
                "reasoning": "This test applies when searching for the book <book>.",
            },
        },
    ],
)

###############################################################################
# ADD_BOOK_USE_CASE
###############################################################################
ADD_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to add or insert a book (use phrases like "Add...", "Insert...", "Register...", etc.).

For example, if the constraints are "year equals 2014 AND author equals 'Wes Anderson'":
- CORRECT: "Add a book whose year equals 2014 and that is authored by Wes Anderson."
- INCORRECT: "Add a book with a high rating" (you added an extra filter).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

ADD_BOOK_USE_CASE = UseCase(
    name="ADD_BOOK",
    description="The user adds a new book to the system, specifying details such as name, author, year, genres, page_count",
    event=AddBookEvent,
    event_source_code=AddBookEvent.get_source_code_of_class(),
    constraints_generator=generate_add_book_constraints,
    additional_prompt_info=ADD_BOOK_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add the book 'A Guide to the Good Life' authored by William B. Irvine",
            "prompt_for_task_generation": "Add the book '<book>' authored by '<author>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_BOOK",
                "event_criteria": {
                    "name": {"value": "A Guide to the Good Life", "operator": "equals"},
                    "author": {"value": "William B. Irvine", "operator": "equals"},
                },
                "reasoning": "Ensures that the book name and exact author match are recorded.",
            },
        },
        {
            "prompt": "Add the book 'AI Superpowers' released in 2018",
            "prompt_for_task_generation": "Add the book '<book>' released in <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_BOOK",
                "event_criteria": {
                    "name": {"value": "AI Superpowers", "operator": "equals"},
                    "year": {"value": 2018, "operator": "equals"},
                },
                "reasoning": "Tests if the correct release year is stored for the book.",
            },
        },
        {
            "prompt": "Add the book 'Sapiens: A Brief History of Humankind' with genres History and Anthropology",
            "prompt_for_task_generation": "Add the book '<book>' with genres <genre> and <genre>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_BOOK",
                "event_criteria": {
                    "name": {"value": "Sapiens: A Brief History of Humankind", "operator": "equals"},
                    "genres": {"value": ["History", "Anthropology"], "operator": "contains"},
                },
                "reasoning": "Validates the genre containment logic for multi-genre books.",
            },
        },
        {
            "prompt": "Add the book 'The Midnight Library' with a page_count under 320 pages",
            "prompt_for_task_generation": "Add the book '<book>' with a page_count under <page_count> pages",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_BOOK",
                "event_criteria": {
                    "name": {"value": "The Midnight Library", "operator": "equals"},
                    "page_count": {"value": 320, "operator": "less_than"},
                },
                "reasoning": "Checks that the book's page_count is handled with a less-than comparison.",
            },
        },
        {
            "prompt": "Add the book 'The Art of Learning' with rating not 4.8.",
            "prompt_for_task_generation": "Add the book '<book>' with rating not equal to <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_BOOK",
                "event_criteria": {
                    "name": {"value": "The Art of Learning", "operator": "equals"},
                    "rating": {"value": 4.8, "operator": "not_equals"},
                },
                "reasoning": "Tests exclusion by rating using the not_equals operator.",
            },
        },
        {
            "prompt": "Add the book 'The Practicing Mind' from one of these authors: Thomas M. Sterner, James Clear, or Ryan Holiday",
            "prompt_for_task_generation": "Add a book '<book>' from one of these authors: <author>, <author>, or <author>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_BOOK",
                "event_criteria": {
                    "name": {"value": "The Practicing Mind", "operator": "equals"},
                    "author": {"value": ["Thomas M. Sterner", "James Clear", "Ryan Holiday"], "operator": "in_list"},
                },
                "reasoning": "Validates that the author falls within an allowed set of names.",
            },
        },
        {
            "prompt": "Add the book 'Deep Work' with running time at least 450 pages authored by Cal Newport",
            "prompt_for_task_generation": "Add the book '<book>' with running time at least <page_count> pages authored by <author>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_BOOK",
                "event_criteria": {
                    "name": {"value": "Deep Work", "operator": "equals"},
                    "page_count": {"value": 450, "operator": "greater_equal"},
                    "author": {"value": "Cal Newport", "operator": "contains"},
                },
                "reasoning": "Validates the greater_equal condition on duration and inclusion of a author member.",
            },
        },
    ],
)

###############################################################################
# EDIT_BOOK_USE_CASE
###############################################################################
EDIT_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to edit or modify a book (use phrases like "Edit...", "Modify...", "Update...", "Change...", etc.).

For example, if the constraints are "year equals 2014 AND author contains 'e'":
- CORRECT: "Edit a book where the year equals 2014 and the author's name contains the letter 'e'."
- INCORRECT: "Edit a random book with a high rating" (you added an extra filter).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
EDIT_BOOK_USE_CASE = UseCase(
    name="EDIT_BOOK",
    description="The user edits an existing book, modifying one or more attributes such as name, author, year, genres, rating, page_count.",
    event=EditBookEvent,
    event_source_code=EditBookEvent.get_source_code_of_class(),
    replace_func=replace_book_placeholders,
    constraints_generator=generate_edit_book_constraints,
    additional_prompt_info=EDIT_BOOK_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Update the author of 'Lidia's Italian-American Kitchen' to Jamie Oliver",
            "prompt_for_task_generation": "Update the author of <book> to Jamie Oliver",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_BOOK",
                "event_criteria": {
                    "name": {"value": "Lidia's Italian-American Kitchen", "operator": "equals"},
                    "author": {"value": "Jamie Oliver", "operator": "equals"},
                },
                "reasoning": "Ensures the new author is recorded.",
            },
        },
        {
            "prompt": "Modify the release year of 'Programming Massively Parallel Processors' to 2023",
            "prompt_for_task_generation": "Modify the release year of <book> to 2023",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_BOOK",
                "event_criteria": {
                    "name": {"value": "Programming Massively Parallel Processors", "operator": "equals"},
                    "year": {"value": 2023, "operator": "equals"},
                },
                "reasoning": "Ensures the new year is recorded.",
            },
        },
        {
            "prompt": "Add 'Baking' to the genres of 'Lidia's Italian-American Kitchen'",
            "prompt_for_task_generation": "Add 'Baking' to the genres of <book>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_BOOK",
                "event_criteria": {
                    "name": {"value": "Lidia's Italian-American Kitchen", "operator": "equals"},
                    "genres": {"value": "Baking", "operator": "contains"},
                },
                "reasoning": "Verifies that the new genre is added.",
            },
        },
        {
            "prompt": "Change the rating of 'Elementary Statistics' to 4.9",
            "prompt_for_task_generation": "Change the rating of <book> to 4.9",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_BOOK",
                "event_criteria": {
                    "name": {"value": "Elementary Statistics", "operator": "equals"},
                    "rating": {"value": 4.9, "operator": "equals"},
                },
                "reasoning": "Ensures the rating is updated correctly.",
            },
        },
        {
            "prompt": "Edit the duration of 'A Breath of Snow and Ashes' to 1000 pages",
            "prompt_for_task_generation": "Edit the duration of <book> to 1000 pages",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_BOOK",
                "event_criteria": {
                    "name": {"value": "A Breath of Snow and Ashes", "operator": "equals"},
                    "duration": {"value": 1000, "operator": "equals"},
                },
                "reasoning": "Ensures that the duration is updated.",
            },
        },
        {
            "prompt": "Modify the author of 'Dark Nights: Metal: Dark Knights Rising' to include Neil Gaiman",
            "prompt_for_task_generation": "Modify the author of <book> to include 'Neil Gaiman'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_BOOK",
                "event_criteria": {
                    "name": {"value": "Dark Nights: Metal: Dark Knights Rising", "operator": "equals"},
                    "author": {"value": "Neil Gaiman", "operator": "contains"},
                },
                "reasoning": "Ensures the author changes are properly logged.",
            },
        },
    ],
)
###############################################################################
# DELETE_BOOK_USE_CASE
###############################################################################
DELETE_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to delete or remove a book (use phrases like "Remove...", "Delete...", "Erase...", "Discard...").

For example, if the constraints are "year greater_than 2014 AND genres contains Sci-Fi":
- CORRECT: "Delete a book whose year is greater than 2014 and that belongs to the Sci-Fi genre."
- INCORRECT: "Delete a book from 2015 with a high rating" (you added an extra filter).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

DELETE_BOOK_USE_CASE = UseCase(
    name="DELETE_BOOK",
    description="The user deletes a book from the system.",
    event=DeleteBookEvent,
    event_source_code=DeleteBookEvent.get_source_code_of_class(),
    additional_prompt_info=DELETE_BOOK_ADDITIONAL_PROMPT_INFO,
    constraints_generator=generate_book_constraints,
    examples=[
        {
            "prompt": "Remove 'Programming Massively Parallel Processors', a book released after 2021, from the database",
            "prompt_for_task_generation": "Remove '<book>' that was released after <year> from the database",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "Programming Massively Parallel Processors", "operator": "equals"},
                    "year": {"value": 2021, "operator": "greater_than"},
                },
                "reasoning": "Ensures the book is deleted and its release year is greater than 2021.",
            },
        },
        {
            "prompt": "Erase all records of 'Dark Nights: Metal: Dark Knights Rising', a book not authored by Stephen King",
            "prompt_for_task_generation": "Erase all records of '<book>' not authored by <author>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "Dark Nights: Metal: Dark Knights Rising", "operator": "equals"},
                    "author": {"value": "Stephen King", "operator": "not_equals"},
                },
                "reasoning": "Confirms deletion and verifies the author is not Stephen King.",
            },
        },
        {
            "prompt": "Permanently delete 'Ettinger's Textbook of Veterinary Internal Medicine', which has a duration greater than 2000 pages",
            "prompt_for_task_generation": "Permanently delete '<book>' with duration greater than <duration> pages",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "Ettinger's Textbook of Veterinary Internal Medicine", "operator": "equals"},
                    "duration": {"value": 2000, "operator": "greater_than"},
                },
                "reasoning": "Ensures the book is removed and its page count exceeds 2000.",
            },
        },
        {
            "prompt": "Discard 'Case Files Family Medicine 5th Edition', a book with a rating less than 4.6",
            "prompt_for_task_generation": "Discard '<book>' with rating less than <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "Case Files Family Medicine 5th Edition", "operator": "equals"},
                    "rating": {"value": 4.6, "operator": "less_than"},
                },
                "reasoning": "Verifies deletion and checks the rating is below 4.6.",
            },
        },
        {
            "prompt": "Remove 'A Breath of Snow and Ashes', a historical fiction book released before 2010",
            "prompt_for_task_generation": "Remove a <genre> book called '<book>' released before <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "A Breath of Snow and Ashes", "operator": "equals"},
                    "genres": {"value": ["Magazine"], "operator": "contains"},
                    "year": {"value": 2010, "operator": "less_than"},
                },
                "reasoning": "Checks deletion and validates genre/release year.",
            },
        },
        {
            "prompt": "Erase the education book that is not authored by Donald Knuth",
            "prompt_for_task_generation": "Erase a <genre> book not authored by <author>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "genres": {"value": ["Education"], "operator": "contains"},
                    "author": {"value": "Donald Knuth", "operator": "not_equals"},
                },
                "reasoning": "Ensures deletion of an education book not by Knuth.",
            },
        },
        {
            "prompt": "Permanently delete a book authored by 'Diana Gabaldon' that was released after 2000",
            "prompt_for_task_generation": "Permanently delete a book with author containing <author> and released after <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "author": {"value": "Diana Gabaldon", "operator": "contains"},
                    "year": {"value": 2000, "operator": "greater_than"},
                },
                "reasoning": "Verifies deletion of a post-2000 book featuring Diana Gabaldon.",
            },
        },
        {
            "prompt": "Discard 'Fourth Wing', a book with a rating greater than 4.5",
            "prompt_for_task_generation": "Discard '<book>' with rating greater than <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "Fourth Wing", "operator": "equals"},
                    "rating": {"value": 4.5, "operator": "greater_than"},
                },
                "reasoning": "Ensures deletion and checks rating exceeds 4.5.",
            },
        },
        {
            "prompt": "Remove 'The Housemaid Is Watching', ensuring it was released before 2025",
            "prompt_for_task_generation": "Remove '<book>' ensuring it was released before <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "The Housemaid Is Watching", "operator": "equals"},
                    "year": {"value": 2025, "operator": "less_than"},
                },
                "reasoning": "Verifies deletion and release year is before 2025.",
            },
        },
        {
            "prompt": "Erase all records of 'Art of Computer Programming', a book that does not belong to the Romance genre",
            "prompt_for_task_generation": "Erase all records of '<book>' that does not belong to the <genre> genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_BOOK",
                "event_criteria": {
                    "name": {"value": "Art of Computer Programming, the, Volumes 1-4B, Boxed Set", "operator": "equals"},
                    "genres": {"value": ["Romance"], "operator": "not_contains"},
                },
                "reasoning": "Confirms deletion and genre exclusion.",
            },
        },
    ],
)


###############################################################################
# CONTACT_USE_CASE
###############################################################################

CONTACT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
3. Be phrased as a request to fill or submit the contact form (e.g., "Fill out the contact form...", "Submit a contact form...", "Go to the contact page and send a form...").

For example, if the constraints are "name not_equals John AND message contains 'services'":
- CORRECT: "Fill out the contact form with a name not_equals John and a message that contains 'services'."
- INCORRECT: "Fill out the form with name = John" (contradice not_equals John)
- INCORRECT: "Fill out the form and mention your budget" (agrega un constraint que NO está en la lista)

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
CONTACT_USE_CASE = UseCase(
    name="CONTACT",
    description="The user navigates to the contact form page, fills out fields, and submits the form successfully.",
    event=ContactEvent,
    event_source_code=ContactEvent.get_source_code_of_class(),
    constraints_generator=generate_contact_constraints,
    additional_prompt_info=CONTACT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Send a contact form with the subject 'Test Subject'",
            "prompt_for_task_generation": "Send a contact form with the subject 'Test Subject'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CONTACT",
                "event_criteria": {"subject": {"value": "Test Subject"}},
                "reasoning": "Verify that the contact form was submitted with the specified subject.",
            },
        },
        {
            "prompt": "Fill out the contact form and include 'Hello, I would like information about your services' in the message",
            "prompt_for_task_generation": "Fill out the contact form and include 'Hello, I would like information about your services' in the message",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CONTACT",
                "event_criteria": {"message": {"value": "Hello, I would like information about your services", "operator": "contains"}},
                "reasoning": "Verify that the contact form was submitted with the specific message content.",
            },
        },
        {
            "prompt": "Complete the contact form using the email address 'test@example.com' and different value for field name :'jhon'",
            "prompt_for_task_generation": "Complete the contact form using the email address 'test@example.com' and different value for field name :'jhon'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CONTACT",
                "event_criteria": {"email": {"value": "test@example.com"}, "name": {"value": "jhon", "operator": "not_equals"}},
                "reasoning": "Verify that the contact form was submitted from the specified email address.",
            },
        },
        {
            "prompt": "Complete the contact form using the email address different to 'test@example.com'",
            "prompt_for_task_generation": "Complete the contact form using the email address different to 'test@example.com'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CONTACT",
                "event_criteria": {"email": {"value": "test@example.com", "operator": "not_equals"}},
                "reasoning": "Verify that the contact form was submitted from the specified email address.",
            },
        },
        {
            "prompt": "Send a contact form with subject 'Partnership Inquiry' and include the phrase 'potential collaboration' in your message",
            "prompt_for_task_generation": "Send a contact form with subject 'Partnership Inquiry' and include the phrase 'potential collaboration' in your message",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CONTACT",
                "event_criteria": {"subject": {"value": "Partnership Inquiry"}, "message": {"value": "potential collaboration", "operator": "contains"}},
                "reasoning": "Verify that the contact form was submitted with both the specified subject and message content.",
            },
        },
        {
            "prompt": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and message 'Great website, I love the design'",
            "prompt_for_task_generation": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and message 'Great website, I love the design'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CONTACT",
                "event_criteria": {
                    "name": {"value": "John Smith"},
                    "email": {"value": "john@example.com"},
                    "subject": {"value": "Feedback"},
                    "message": {"value": "Great website, I love the design", "operator": "contains"},
                },
                "reasoning": "Verify that the contact form was submitted with all fields matching the specified values.",
            },
        },
        {
            "prompt": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and cannot contains any 'e'",
            "prompt_for_task_generation": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and cannot contains any 'e'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "CONTACT",
                "event_criteria": {
                    "name": {"value": "John Smith"},
                    "email": {"value": "john@example.com"},
                    "subject": {"value": "Feedback"},
                    "message": {"value": "e", "operator": "not_contains"},
                },
                "reasoning": "Verify that the contact form was submitted with all fields matching the specified values, and the message does NOT contain 'e'.",
            },
        },
    ],
)
###############################################################################
# EDIT_USER_PROFILE_USE_CASE
###############################################################################
EDIT_PROFILE_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Begin with "Login for the following username:<username> and password:<password>".
4. Be phrased as a request to edit or modify a user profile (use phrases like "Edit...", "Modify...", "Update...", "Change...", etc.).

For example, if the constraints are "username equals 'bookfan' AND password equals 'pass123' AND bio contains 'bookworm'":
- CORRECT: "Login for the following username:bookfan and password:pass123. Edit your profile to update your bio to include the word 'bookworm'."
- INCORRECT: "Edit a profile to change the website" (missing login information and specific constraints).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

EDIT_USER_PROFILE_USE_CASE = UseCase(
    name="EDIT_PROFILE",
    description="The user edits their profile, modifying one or more attributes such as first name, last name, bio, location, website, or favorite genres. Username and email cannot be edited.",
    event=EditUserEvent,
    event_source_code=EditUserEvent.get_source_code_of_class(),
    replace_func=login_replace_func,
    constraints_generator=generate_edit_profile_constraints,
    additional_prompt_info=EDIT_PROFILE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Login for the following username:user1 and password:pass123. Update your first name to John.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Update your first name to <first_name>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "user1", "operator": "equals"},
                    "first_name": {"value": "John", "operator": "equals"},
                },
                "reasoning": "Ensures the new first name is recorded.",
            },
        },
        {
            "prompt": "Login for the following username:bookfan and password:pass456. Modify your bio to include your passion for bookworm.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Modify your bio to include <bio_content>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "bookfan", "operator": "equals"},
                    "bio": {"value": "bookworm", "operator": "contains"},
                },
                "reasoning": "Ensures the new bio content is recorded.",
            },
        },
        {
            "prompt": "Login for the following username:booklover and password:pass789. Change your location to New York, USA.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Change your location to <location>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "booklover", "operator": "equals"},
                    "location": {"value": "New York, USA", "operator": "equals"},
                },
                "reasoning": "Ensures the location is updated.",
            },
        },
        {
            "prompt": "Login for the following username:cinephile and password:pass321. Edit your website to https://mybookblog.example.com.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Edit your website to <website>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "cinephile", "operator": "equals"},
                    "website": {"value": "https://mybookblog.example.com", "operator": "equals"},
                },
                "reasoning": "Ensures the website is updated.",
            },
        },
        {
            "prompt": "Login for the following username:author101 and password:pass654. Update your favorite genre to Science.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Update your favorite genre to <genre>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "author101", "operator": "equals"},
                    "favorite_genres": {"value": "Science", "operator": "equals"},
                },
                "reasoning": "Ensures the favorite genre is updated.",
            },
        },
        {
            "prompt": "Login for the following username:producer and password:pass987. Change your last name to Smith.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Change your last name to <last_name>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "producer", "operator": "equals"},
                    "last_name": {"value": "Smith", "operator": "equals"},
                },
                "reasoning": "Ensures the last name is updated.",
            },
        },
    ],
)

###############################################################################
# FILTER_BOOK_USE_CASE
###############################################################################
FILTER_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Include the word "Filter" (or "filtering", "filtered", "filters") explicitly in the prompt.
4. Be phrased as a request to filter or browse books (e.g., "Filter...", "Show only...", "Display...", "Browse...", etc.).
5. Use ONLY the allowed genres and years from the lists below.

ALLOWED YEARS:
2024, 2023, 2022, 2020, 2019, 2018, 2005, 2001

ALLOWED GENRES:
"Children", "Cooking", "Culture", "Education", "History", "Magazine", "Music", "Romance", "Science", "Story"

For example, if the constraints are "genre_name equals 'Culture' AND year equals 2020":
- CORRECT: "Filter for 'Culture' books released in 2020."
- CORRECT: "Browse books from 2020 in the 'Culture' genre."
- INCORRECT: "Search for 'Culture' books from the 20s" (uses vague year and incorrect phrasing).
- INCORRECT: "Show all 'Culture' books" (missing the year constraint if both are provided).
- INCORRECT: "Filter for Mystery books" (Mystery is not in the allowed genre list).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

FILTER_BOOK_USE_CASE = UseCase(
    name="FILTER_BOOK",
    description="The user applies filters to search for books by genre and/or year. Includes Filter in the prompt",
    event=FilterBookEvent,
    event_source_code=FilterBookEvent.get_source_code_of_class(),
    constraints_generator=generate_book_filter_constraints,
    additional_prompt_info=FILTER_BOOK_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Filter books released in the year 2005",
            "prompt_for_task_generation": "Filter books released in the year 2005",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_BOOK",
                "event_criteria": {"year": 2005},
                "reasoning": "Ensures that filtering books by the year 1994 correctly triggers the event.",
            },
        },
        {
            "prompt": "Filter for Action books",
            "prompt_for_task_generation": "Filter for Action books",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_BOOK",
                "event_criteria": {"genre_name": "Action"},
                "reasoning": "Ensures that searching for 'Action' genre books correctly triggers the event.",
            },
        },
        {
            "prompt": "Browse books from 2019 in the Story genre",
            "prompt_for_task_generation": "Browse books from 2019 in the Story genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_BOOK",
                "event_criteria": {"year": 2019, "genre_name": "Story"},
                "reasoning": "Validates that filtering by both year and genre applies correctly.",
            },
        },
        {
            "prompt": "Filter Screen books from 2022",
            "prompt_for_task_generation": "Filter Screen books from 2022",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_BOOK",
                "event_criteria": {"year": 2022},
                "reasoning": "Ensures screening books by the year 2022 works independently.",
            },
        },
        {
            "prompt": "Filter book list to Education genre",
            "prompt_for_task_generation": "Filter book list to Education genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_BOOK",
                "event_criteria": {"genre_name": "Education"},
                "reasoning": "Ensures refining books by the 'Education' genre works independently.",
            },
        },
    ],
)

###############################################################################
# ADD_COMMENT_USE_CASE
###############################################################################
ADD_COMMENT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
3. Be phrased as a request to add a comment to a book (use phrases like "Add a comment...", "Write a review...", "Post a comment...", "Leave feedback...").
4. If the constraints include the 'content' field (e.g., content contains or content not_contains), the prompt MUST refer specifically to the comment **content or message**, using expressions like "a comment whose content...", "a review whose message...", etc., and NOT just a vague instruction".
For example, if the constraints are "book_name contains 'Fourth Win' AND content not_contains 'boring'":
- CORRECT: "Add a comment to a book that contains 'Fourth Win' with a review that does NOT contain the word 'boring'."
- INCORRECT: "Write a comment about any book" (missing specific constraints)
- INCORRECT: "Post a review that includes extra unnecessary details" (adding constraints not specified)

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
ADD_COMMENT_USE_CASE = UseCase(
    name="ADD_COMMENT",
    description="The user adds a comment to a book.",
    event=AddCommentEvent,
    event_source_code=AddCommentEvent.get_source_code_of_class(),
    constraints_generator=generate_add_comment_constraints,
    additional_prompt_info=ADD_COMMENT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Navigate to a book and add a comment about 'Fourth Win'",
            "prompt_for_task_generation": "Navigate to <book> and add a comment",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"book_name": {"value": "Fourth Win", "operator": "equals"}},
                "reasoning": "Verifies adding a comment to a specific book.",
            },
        },
        {
            "prompt": "Write a review for a book, ensuring the commenter is not John",
            "prompt_for_task_generation": "Write a review for <book>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"commenter_name": {"value": "John", "operator": "not_equals"}},
                "reasoning": "Ensures comment can be added with name constraint.",
            },
        },
        {
            "prompt": "Post a comment containing the word 'masterpiece'",
            "prompt_for_task_generation": "Post a comment for <book>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"content": {"value": "masterpiece", "operator": "contains"}},
                "reasoning": "Validates comment generation with specific content.",
            },
        },
        {
            "prompt": "Add a comment for a book not called The Matrix by someone other than John",
            "prompt_for_task_generation": "Add a comment for <book>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"book_name": {"value": "The Matrix", "operator": "not_equals"}, "commenter_name": {"value": "John", "operator": "not_equals"}},
                "reasoning": "Checks multiple constraints for comment addition.",
            },
        },
        {
            "prompt": "Write a detailed review with specific book, content, and commenter constraints",
            "prompt_for_task_generation": "Write a review for <book>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {
                    "book_name": {"value": "Elementary Statistics", "operator": "equals"},
                    "content": {"value": "boring", "operator": "not_contains"},
                    "commenter_name": {"value": "David", "operator": "not_equals"},
                },
                "reasoning": "Demonstrates complex constraint combinations for comment generation.",
            },
        },
    ],
)

SHOPPING_CART_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
3. Be phrased as a request to add/remove/view items in the shopping cart (e.g., "Add to cart...", "Remove from cart...", "View cart...", "Update cart...").
4. Explicitly mention the shopping cart in the prompt (e.g., "shopping cart", "cart").
5. If constraints include book_name or quantity, they MUST be referenced directly in the prompt.

For example, if the constraints are "book_name equals 'Inception' AND quantity equals 2":
- CORRECT: "Add 2 copies of Inception to the shopping cart."
- CORRECT: "Update the cart to include 2 Inception books."
- INCORRECT: "Put some books in the cart" (missing specific constraints).
- INCORRECT: "Add Inception to my list" (doesn't mention cart).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

SHOPPING_CART_USE_CASE = UseCase(
    name="SHOPPING_CART",
    description="The user interacts with the shopping cart by adding, removing, or viewing items.",
    event=ShoppingCartEvent,
    event_source_code=ShoppingCartEvent.get_source_code_of_class(),
    # constraints_generator=generate_shopping_cart_constraints,
    additional_prompt_info=SHOPPING_CART_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add the book 'Fourth Win' to the shopping cart",
            "prompt_for_task_generation": "Add the book '<book>' to the shopping cart",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SHOPPING_CART",
                "event_criteria": {"book_name": {"value": "Fourth Win", "operator": "equals"}},
                "reasoning": "Ensures that a book with a specific name can be added to the shopping cart.",
            },
        },
        {
            "prompt": "Place 'Elementary Statistics' in the cart",
            "prompt_for_task_generation": "Place '<book>' in the cart",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SHOPPING_CART",
                "event_criteria": {"book_name": {"value": "Elementary Statistics", "operator": "equals"}},
                "reasoning": "Tests another phrasing for adding a book to the cart.",
            },
        },
        {
            "prompt": "Add 'Dark Nights: Metal: Dark Knights Rising' to basket",
            "prompt_for_task_generation": "Add '<book>' to basket",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SHOPPING_CART",
                "event_criteria": {"book_name": {"value": "Dark Nights: Metal: Dark Knights Rising", "operator": "equals"}},
                "reasoning": "Verifies alternative synonym usage for shopping cart.",
            },
        },
    ],
)


PURCHASE_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
3. Be phrased as a request to purchase books (e.g., "Purchase...", "Buy...", "Checkout...", "Complete order...").
4. Explicitly mention the purchase/checkout action in the prompt.
5. If constraints include payment_method or shipping_address, they MUST be referenced directly.

For example, if constraints are "payment_method equals 'Credit Card'":
- CORRECT: "Purchase my cart items with Credit Card payment."
- CORRECT: "Checkout using Credit Card."
- INCORRECT: "Buy my books" (missing payment method constraint).
- INCORRECT: "Complete purchase with unspecified details" (vague).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

PURCHASE_BOOK_USE_CASE = UseCase(
    name="PURCHASE_BOOK",
    description="The user completes a purchase of items in the shopping cart.",
    event=PurchaseBookEvent,
    event_source_code=PurchaseBookEvent.get_source_code_of_class(),
    replace_func=replace_book_placeholders,
    # constraints_generator=generate_purchase_book_constraints,
    additional_prompt_info=PURCHASE_BOOK_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Purchase the book titled 'Dark Nights: Metal: Dark Knights Rising'",
            "prompt_for_task_generation": "Purchase the book titled <book>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PURCHASE_BOOK",
                "event_criteria": {"book_name": {"value": "Dark Nights: Metal: Dark Knights Rising", "operator": "equals"}},
                "reasoning": "Ensures the book 'Dark Nights: Metal: Dark Knights Rising' is purchased directly.",
            },
        },
        {
            "prompt": "Checkout with 'Elementary Statistics'",
            "prompt_for_task_generation": "Checkout with <book>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PURCHASE_BOOK",
                "event_criteria": {"book_name": {"value": "Elementary Statistics", "operator": "equals"}},
                "reasoning": "Validates that the checkout process includes the right book.",
            },
        },
        {
            "prompt": "Buy the book 'Fourth Win' now",
            "prompt_for_task_generation": "Buy the book <book> now",
            "test": {
                "type": "CheckEventTest",
                "event_name": "PURCHASE_BOOK",
                "event_criteria": {"book_name": {"value": "Fourth Win", "operator": "equals"}},
                "reasoning": "Tests a direct instruction to purchase a book.",
            },
        },
    ],
)

###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    # ===== TESTED =====
    # REGISTRATION_USE_CASE,
    # SEARCH_BOOK_USE_CASE,
    # FILTER_BOOK_USE_CASE,
    # CONTACT_USE_CASE,
    # ===== PENDING =====
    # LOGIN_USE_CASE,
    # LOGOUT_USE_CASE,   # Requires Login first
    ADD_BOOK_USE_CASE,  # Requires Login first
    # EDIT_BOOK_USE_CASE,   # Requires Login first + Book registered on that User id
    # DELETE_BOOK_USE_CASE,   # Requires Login first
    # BOOK_DETAIL_USE_CASE,   # Requires BOOK ID
    # ADD_COMMENT_USE_CASE,   # Requires BOOK ID
    # SHOPPING_CART_USE_CASE,   # Requires Login first
    # PURCHASE_BOOK_USE_CASE,   # Requires Login first
    # EDIT_USER_PROFILE_USE_CASE,   # Requires Login first
]
