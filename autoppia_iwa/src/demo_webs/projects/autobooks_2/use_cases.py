from autoppia_iwa.src.demo_webs.classes import UseCase

from .data_utils import fetch_data
from .events import (
    AddBookEvent,
    AddCommentEvent,
    AddToCartBookEvent,
    AddToReadingListEvent,
    BookDetailEvent,
    ContactEvent,
    DeleteBookEvent,
    EditBookEvent,
    EditUserEvent,
    FilterBookEvent,
    LoginEvent,
    LogoutEvent,
    OpenPreviewEvent,
    PurchaseBookEvent,
    RegistrationEvent,
    RemoveFromCartBookEvent,
    RemoveFromReadingListEvent,
    SearchBookEvent,
    ShareBookEvent,
    ViewCartBookEvent,
)
from .generation_functions import (
    generate_add_book_constraints,
    generate_add_comment_constraints,
    generate_book_constraints,
    generate_book_details_constraints,
    generate_book_filter_constraints,
    generate_contact_constraints,
    generate_delete_book_constraints,
    generate_edit_book_constraints,
    generate_edit_profile_constraints,
    generate_login_constraints,
    generate_logout_constraints,
    generate_registration_constraints,
    generate_search_book_constraints,
)
from .replace_functions import register_replace_func, replace_book_placeholders


async def _get_books_data_for_prompts(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """Fetch books data from API for use in prompt generation."""
    return await fetch_data(seed_value=seed_value, count=count)


def _generate_book_names_list(books_data: list[dict]) -> str:
    """Generate a newline-separated list of book names from books data."""
    if not books_data:
        return "No books available"
    return "\n".join([book.get("name", "") for book in books_data if book.get("name")])


def _generate_allowed_years_list(books_data: list[dict]) -> list[int]:
    """Generate a list of unique years from books data."""
    if not books_data:
        return []
    return sorted({book.get("year") for book in books_data if book.get("year") is not None})


def _generate_allowed_genres_list(books_data: list[dict]) -> list[str]:
    """Generate a list of unique genres from books data."""
    if not books_data:
        return []
    genres = set()
    for book in books_data:
        book_genres = book.get("genres", [])
        if isinstance(book_genres, list):
            genres.update(book_genres)
        elif isinstance(book_genres, str):
            genres.add(book_genres)
    return sorted(genres)


###############################################################################
# REGISTRATION_USE_CASE
###############################################################################
REGISTRATION_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Be sure to add instruction to register using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
2. Only phrase it like: "Register with the following username:<username>,email:<email> and password:<password>" etc
3. Avoid mentioning anything other than mentioned above.
All email must finish with @gmail.com, so pay attention to the constraints.
ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

REGISTRATION_USE_CASE = UseCase(
    name="REGISTRATION_BOOK",
    description="The user fills out the registration form and successfully creates a new account.",
    event=RegistrationEvent,
    event_source_code=RegistrationEvent.get_source_code_of_class(),
    replace_func=register_replace_func,
    constraints_generator=generate_registration_constraints,
    additional_prompt_info=REGISTRATION_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Register with the following username:<username>,email:<email> and password:<password>",
            "prompt_for_task_generation": "Register with the following username:<username>,email:<email> and password:<password>",
        },
        {
            "prompt": "Create a new account with username:<username>,email:<email> and password:<password>",
            "prompt_for_task_generation": "Create a new account with username:<username>,email:<email> and password:<password>",
        },
        {
            "prompt": "Fill the registration form with username:<username>, email:<email> and password:<password>",
            "prompt_for_task_generation": "Fill the registration form with username:<username>, email:<email> and password:<password>",
        },
    ],
)

###############################################################################
# LOGIN_USE_CASE
###############################################################################

LOGIN_USE_CASE = UseCase(
    name="LOGIN_BOOK",
    description="The user fills out the login form and logs in successfully.",
    event=LoginEvent,
    event_source_code=LoginEvent.get_source_code_of_class(),
    # replace_func not needed - credentials remain as placeholders until evaluation
    constraints_generator=generate_login_constraints,
    examples=[
        {
            "prompt": "Login for the following username:<username> and password:<password>",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>",
        },
        {
            "prompt": "Login with a specific username:<username> and password:<password>",
            "prompt_for_task_generation": "Login with a specific username:<username> and password:<password>",
        },
        {
            "prompt": "Fill the Login Form with a specific username:<username> and password:<password>",
            "prompt_for_task_generation": "Fill the Login Form with a specific username:<username> and password:<password>",
        },
        {
            "prompt": "Sign in to the website username:<username> and password:<password>",
            "prompt_for_task_generation": "Sign in to the website username:<username> and password:<password>",
        },
    ],
)

###############################################################################
# LOGOUT_USE_CASE
###############################################################################

LOGOUT_USE_CASE = UseCase(
    name="LOGOUT_BOOK",
    description="The user logs out of the platform after logging in.",
    event=LogoutEvent,
    event_source_code=LogoutEvent.get_source_code_of_class(),
    # replace_func not needed - credentials remain as placeholders until evaluation
    constraints_generator=generate_logout_constraints,
    examples=[
        {
            "prompt": "Login for the following username:<username> and password:<password>, then logout",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>, then logout",
        },
        {
            "prompt": "Login with a specific username:<username> and password:<password>, then sign out from the system",
            "prompt_for_task_generation": "Login with a specific username:<username> and password:<password>, then sign out from the system",
        },
        {
            "prompt": "Fill the Login Form with a specific username:<username> and password:<password>, once logged in, logout from my account",
            "prompt_for_task_generation": "Fill the Login Form with a specific username:<username> and password:<password>, once logged in, logout from my account",
        },
        {
            "prompt": "Sign in to the website username:<username> and password:<password>, after that please log me out",
            "prompt_for_task_generation": "Sign in to the website username:<username> and password:<password>, after that please log me out",
        },
        {
            "prompt": "Authenticate with username:<username> and password:<password>, then end my session",
            "prompt_for_task_generation": "Authenticate with username:<username> and password:<password>, then end my session",
        },
    ],
)


###############################################################################
# BOOK_DETAIL_USE_CASE
###############################################################################


def _get_book_detail_info(books_data: list[dict]) -> str:
    """Generate book detail info dynamically from API data."""
    book_names = _generate_book_names_list(books_data)
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **view details** of a book (use phrases like "Show details for...", "Navigate to the details page for...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{book_names}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Show me details about a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Show me details about a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Show me details about a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


BOOK_DETAIL_INFO_TEMPLATE = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **view details** of a book (use phrases like "Show details for...", "Navigate to the details page for...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{BOOKS_NAMES_PLACEHOLDER}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Show me details about a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Show me details about a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Show me details about a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""

BOOK_DETAIL_USE_CASE = UseCase(
    name="BOOK_DETAIL",
    description="The user explicitly requests to navigate to or go to the details page of a specific book that meets certain criteria, "
    "where they can view information including author, year, genres, rating, page count, and characters.",
    event=BookDetailEvent,
    event_source_code=BookDetailEvent.get_source_code_of_class(),
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_book_details_constraints,
    examples=[
        {
            "prompt": "First, authenticate with username '<username>' and password '<password>'. Then, navigate to the book details page where the name is equal to 'The Housemaid Is Watching'.",
            "prompt_for_task_generation": "First, authenticate with username '<username>' and password '<password>'. Then, navigate to the book details page where the name is equal to <book>.",
        },
        {
            "prompt": "Login with username '<username>' and password '<password>'. Go to the book details page for the book where the author is equal to 'Donald Knuth'.",
            "prompt_for_task_generation": "Login with username '<username>' and password '<password>'. Go to the book details page for the book where the author is equal to <author>.",
        },
        {
            "prompt": "Sign in as '<username>' with password '<password>'. Navigate directly to a Science book page where the year is equal to 2022.",
            "prompt_for_task_generation": "Sign in as '<username>' with password '<password>'. Navigate directly to a <genre> book page where the year is equal to <year>.",
        },
        {
            "prompt": "Go directly to a book page with rating above 4.5",
            "prompt_for_task_generation": "Go directly to a book page with rating above <rating>",
        },
        {
            "prompt": "Take me directly to the 'Fourth Wing' book details page",
            "prompt_for_task_generation": "Take me directly to the <book> book details page",
        },
        {
            "prompt": "Navigate to a 'Magazine' book page less than 1000 pages long",
            "prompt_for_task_generation": "Navigate to a <genre> book page less than <page_count> pages long",
        },
        {
            "prompt": "Go to a book details page from the 2010s directed by 'Ron Larson'",
            "prompt_for_task_generation": "Go to a book details page from the <decade> directed by '<author>'",
        },
        {
            "prompt": "Navigate me to a 'Science' book page not written by 'Grant Morrison'",
            "prompt_for_task_generation": "Navigate me to a <genre> book page not written by <author>",
        },
        {
            "prompt": "Go directly to the highest-rated 'Lidia Matticchio Bastianich' book page",
            "prompt_for_task_generation": "Go directly to the highest-rated <author> book page",
        },
    ],
)


def _get_share_book_info(books_data: list[dict]) -> str:
    """Generate share book info dynamically from API data."""
    book_names = _generate_book_names_list(books_data)
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **share** a book (use phrases like "Share details for...", "Share the book...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{book_names}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Share details about a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Share details about a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Share details about a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


SHARE_BOOK_INFO_TEMPLATE = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **share** a book (use phrases like "Share details for...", "Share the book...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{BOOKS_NAMES_PLACEHOLDER}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Share details about a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Share details about a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Share details about a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""

SHARE_BOOK_USE_CASE = UseCase(
    name="SHARE_BOOK",
    description="The user explicitly requests to share a specific book that meets certain criteria, "
    "where they can view information including author, year, genres, rating, page count, and characters.",
    event=ShareBookEvent,
    event_source_code=BookDetailEvent.get_source_code_of_class(),
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_book_details_constraints,
    examples=[
        {
            "prompt": "First, authenticate with username '<username>' and password '<password>'. Then, share the book where the title is equal to 'The Housemaid Is Watching'.",
            "prompt_for_task_generation": "First, authenticate with username '<username>' and password '<password>'. Then, share the book where the title is equal to <book>.",
        },
        {
            "prompt": "Login with username '<username>' and password '<password>'. Share book details for the book where the author is equal to 'Donald Knuth'.",
            "prompt_for_task_generation": "Login with username '<username>' and password '<password>'. Share book details for the book where the author is equal to <author>.",
        },
        {
            "prompt": "Sign in as '<username>' with password '<password>'. Share the Science book where the year is equal to 2022.",
            "prompt_for_task_generation": "Sign in as '<username>' with password '<password>'. Share the <genre> book where the year is equal to <year>.",
        },
        {
            "prompt": "Share book with rating above 4.5",
            "prompt_for_task_generation": "Share book with rating above <rating>",
        },
        {
            "prompt": "Share 'Fourth Wing' book details",
            "prompt_for_task_generation": "Share <book> book details",
        },
        {
            "prompt": "Share 'Magazine' book less than 1000 pages long",
            "prompt_for_task_generation": "Share <genre> book less than <page_count> pages long",
        },
        {
            "prompt": "Share book details from the 2010s directed by 'Ron Larson'",
            "prompt_for_task_generation": "Share book details from the <decade> directed by '<author>'",
        },
        {
            "prompt": "Share 'Science' book not written by 'Grant Morrison'",
            "prompt_for_task_generation": "Share <genre> book not written by <author>",
        },
        {
            "prompt": "Share highest-rated 'Lidia Matticchio Bastianich' book",
            "prompt_for_task_generation": "Share highest-rated <author> book",
        },
    ],
)


def _get_open_preview_info(books_data: list[dict]) -> str:
    """Generate open preview info dynamically from API data."""
    book_names = _generate_book_names_list(books_data)
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **open preview** of a book (use phrases like "Open preview of...", "Show preview for...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{book_names}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Open preview for a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Open preview for a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Open preview for a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


OPEN_PREVIEW_INFO_TEMPLATE = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **open preview** of a book (use phrases like "Open preview of...", "Show preview for...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{BOOKS_NAMES_PLACEHOLDER}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Open preview for a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Open preview for a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Open preview for a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""

OPEN_PREVIEW_USE_CASE = UseCase(
    name="OPEN_PREVIEW",
    description="The user explicitly requests to open preview of a specific book that meets certain criteria, "
    "where they can view information including author, year, genres, rating, page count, and characters.",
    event=OpenPreviewEvent,
    event_source_code=OpenPreviewEvent.get_source_code_of_class(),
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_book_details_constraints,
    examples=[
        {
            "prompt": "First, authenticate with username '<username>' and password '<password>'. Then, open preview of the book where the title is equal to 'The Housemaid Is Watching'.",
            "prompt_for_task_generation": "First, authenticate with username '<username>' and password '<password>'. Then, open preview of the book where the title is equal to <book>.",
        },
        {
            "prompt": "Login with username '<username>' and password '<password>'. Open preview for the book where the author is equal to 'Donald Knuth'.",
            "prompt_for_task_generation": "Login with username '<username>' and password '<password>'. Open preview for the book where the author is equal to <author>.",
        },
        {
            "prompt": "Sign in as '<username>' with password '<password>'. Open preview of the Science book where the year is equal to 2022.",
            "prompt_for_task_generation": "Sign in as '<username>' with password '<password>'. Open preview of the <genre> book where the year is equal to <year>.",
        },
        {
            "prompt": "Open preview of book with rating above 4.5",
            "prompt_for_task_generation": "Open preview of book with rating above <rating>",
        },
        {
            "prompt": "Open preview of 'Fourth Wing' book",
            "prompt_for_task_generation": "Open preview of <book> book",
        },
        {
            "prompt": "Open preview of 'Magazine' book less than 1000 pages long",
            "prompt_for_task_generation": "Open preview of <genre> book less than <page_count> pages long",
        },
        {
            "prompt": "Open preview of book from the 2010s directed by 'Ron Larson'",
            "prompt_for_task_generation": "Open preview of book from the <decade> directed by '<author>'",
        },
        {
            "prompt": "Open preview of 'Science' book not written by 'Grant Morrison'",
            "prompt_for_task_generation": "Open preview of <genre> book not written by <author>",
        },
        {
            "prompt": "Open preview of highest-rated 'Lidia Matticchio Bastianich' book",
            "prompt_for_task_generation": "Open preview of highest-rated <author> book",
        },
    ],
)


def _get_add_to_reading_list_info(books_data: list[dict]) -> str:
    """Generate add to reading list info dynamically from API data."""
    book_names = _generate_book_names_list(books_data)
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **add to reading list** (use phrases like "Add to reading list...", "Add the book to my list...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{book_names}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Add to reading list a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Add to reading list a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Add to reading list a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


ADD_TO_READING_LIST_INFO_TEMPLATE = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **add to reading list** (use phrases like "Add to reading list...", "Add the book to my list...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{BOOKS_NAMES_PLACEHOLDER}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Add to reading list a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Add to reading list a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Add to reading list a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""

ADD_TO_READING_LIST_USE_CASE = UseCase(
    name="ADD_TO_READING_LIST",
    description="The user explicitly requests to add a specific book to list book that meets certain criteria, "
    "where they can view information including author, year, genres, rating, page count, and characters.",
    event=AddToReadingListEvent,
    event_source_code=AddToReadingListEvent.get_source_code_of_class(),
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_book_details_constraints,
    examples=[
        {
            "prompt": "First, authenticate with username '<username>' and password '<password>'. Then, add to reading list the book where the title is equal to 'The Housemaid Is Watching'.",
            "prompt_for_task_generation": "First, authenticate with username '<username>' and password '<password>'. Then, add to reading list the book where the title is equal to <book>.",
        },
        {
            "prompt": "Login with username '<username>' and password '<password>'. Add to reading list the book where the author is equal to 'Donald Knuth'.",
            "prompt_for_task_generation": "Login with username '<username>' and password '<password>'. Add to reading list the book where the author is equal to <author>.",
        },
        {
            "prompt": "Sign in as '<username>' with password '<password>'. Add to reading list a Science book where the year is equal to 2022.",
            "prompt_for_task_generation": "Sign in as '<username>' with password '<password>'. Add to reading list a <genre> book where the year is equal to <year>.",
        },
        {
            "prompt": "Add to reading list a book with rating above 4.5",
            "prompt_for_task_generation": "Add to reading list a book with rating above <rating>",
        },
        {
            "prompt": "Add to reading list a 'Fourth Wing' book",
            "prompt_for_task_generation": "Add to reading list a <book> book",
        },
        {
            "prompt": "Add to reading list a 'Magazine' book less than 1000 pages long",
            "prompt_for_task_generation": "Add to reading list a <genre> book less than <page_count> pages long",
        },
        {
            "prompt": "Add to reading list a book from the 2010s directed by 'Ron Larson'",
            "prompt_for_task_generation": "Add to reading list a book from the <decade> directed by '<author>'",
        },
        {
            "prompt": "Add to reading list a 'Science' book not written by 'Grant Morrison'",
            "prompt_for_task_generation": "Add to reading list a <genre> book not written by <author>",
        },
        {
            "prompt": "Add to reading list a highest-rated 'Lidia Matticchio Bastianich' book",
            "prompt_for_task_generation": "Add to reading list a highest-rated <author> book",
        },
    ],
)


def _get_remove_from_reading_list_info(books_data: list[dict]) -> str:
    """Generate remove from reading list info dynamically from API data."""
    book_names = _generate_book_names_list(books_data)
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to **remove from reading list** (use phrases like "Remove from reading list...", "Delete from reading list..." etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
5. Use the word 'NOT' if the constraint is 'not_equals' or 'not_contains'.
6. Use terms like 'greater than', 'less than', 'at least', 'no more than' to explicitly represent numeric operators (greater_than, less_than, greater_equal, less_equal).
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'. If it is 'not_equals', use 'not equal'.
8. Only use the books name defined below.

BOOKS NAMES:
{book_names}

For example, if the constraints are "author not_equals Diana Gabaldon AND year greater_than 2004":
- CORRECT: "Remove from reading list a book not written by Diana Gabaldon that was published after 2004"
- INCORRECT: "Remove from reading list a book written by Christopher Nolan" (you added a random author, and missed the year constraint)
- INCORRECT: "Remove from reading list a book not written by Diana Gabaldon that was published after 2004 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


REMOVE_FROM_READING_LIST_USE_CASE = UseCase(
    name="REMOVE_FROM_READING_LIST",
    description="The user explicitly requests to remove a specific book from reading list that meets certain criteria.",
    event=RemoveFromReadingListEvent,
    event_source_code=RemoveFromReadingListEvent.get_source_code_of_class(),
    additional_prompt_info=None,
    constraints_generator=generate_book_details_constraints,
    examples=[
        {
            "prompt": "First, authenticate with username '<username>' and password '<password>'. Then, remove from reading list the book where the title is equal to 'The Housemaid Is Watching'.",
            "prompt_for_task_generation": "First, authenticate with username '<username>' and password '<password>'. Then, remove from reading list the book where the title is equal to <book>.",
        },
        {
            "prompt": "Login with username '<username>' and password '<password>'. Remove from reading list the book where the author is equal to 'Donald Knuth'.",
            "prompt_for_task_generation": "Login with username '<username>' and password '<password>'. Remove from reading list the book where the author is equal to <author>.",
        },
        {
            "prompt": "Sign in as '<username>' with password '<password>'. Remove from reading list a Science book where the year is equal to 2022.",
            "prompt_for_task_generation": "Sign in as '<username>' with password '<password>'. Remove from reading list a <genre> book where the year is equal to <year>.",
        },
        {
            "prompt": "Login with username '<username>' and password '<password>'. Remove from reading list a book with rating above 4.5",
            "prompt_for_task_generation": "Login with username '<username>' and password '<password>'. Remove from reading list a book with rating above <rating>",
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
3. Include ONLY the book title as part of the search. Use the value EXACTLY as it appears in the constraints.
4. DO NOT include ANY constraints or conditions like author, year, genre, etc.
5. PAY ATTENTION to the operators. Use the word 'NOT' if the constraint is 'not_equals'.
For example:
- CORRECT: "Search for the book 'A Breath of Snow and Ashes' in the database"
- CORRECT: "Look for a book that is NOT 'Fourth Wing'" (if constraint is query not_equals Fourth Wing)
- CORRECT: "Find books called The 'The Housemaid Is Watching'"
- INCORRECT: "Show me details about 'Fourth Wing'" (doesn't specify it's a search)
- INCORRECT: "Give me information on 'The Housemaid Is Watching'" (ambiguous, doesn't clearly indicate search)
- INCORRECT: "Search for 'A Breath of Snow and Ashes' NOT written by James Cameron" (includes constraints from other fields)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL clearly indicating that it is a simple SEARCH with NO additional constraints.
"""

SEARCH_BOOK_USE_CASE = UseCase(
    name="SEARCH_BOOK",
    description="The user searches for a book using a query.",
    event=SearchBookEvent,
    event_source_code=SearchBookEvent.get_source_code_of_class(),
    replace_func=replace_book_placeholders,
    constraints_generator=generate_search_book_constraints,
    additional_prompt_info=SEARCH_BOOK_INFO,
    examples=[
        {
            "prompt": "Look for the book 'Lidia's Italian-American Kitchen'",
            "prompt_for_task_generation": "Look for the book '<book>'",
        },
        {
            "prompt": "Find a book called 'Programming Massively Parallel Processors' starring Al Pacino",
            "prompt_for_task_generation": "Find a book called '<book>'",
        },
        {
            "prompt": "Search for 'Elementary Statistics' in the book database",
            "prompt_for_task_generation": "Search for '<book>' in the book database",
        },
        {
            "prompt": "Look up a book 'Dark Nights: Metal: Dark Knights Rising' featuring Uma Thurman",
            "prompt_for_task_generation": "Look up a book '<book>'",
        },
        {
            "prompt": "Find a book called 'Case Files Family Medicine 5th Edition' with Leonardo DiCaprio on the cover",
            "prompt_for_task_generation": "Find a book called '<book>'",
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
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
Examples include: "First, authenticate with...", "Initiate session using...", "After successful login with...", "Once logged in as...", etc. Followed by the book addition request.
5. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.

For example, if the constraints are "year equals 2014 AND author equals 'Wes Anderson'":

CORRECT:
"First, authenticate with username '<username>' and password '<password>'. Then, add a book whose year equals 2014 and that is authored by 'Wes Anderson'."

INCORRECT:
- Using different username/password values.
- Using placeholders other than the exact provided ones.
- Rewriting 'Wes Anderson' differently.
- Changing 2014 to another year.
- Adding extra filters.

If you specify the name of the book, then do NOT specify the author or year — only use the book name.

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria and EXACT field values.
"""


ADD_BOOK_USE_CASE = UseCase(
    name="ADD_BOOK",
    description="The user adds a new book to the system, specifying details such as name, author, year, genres, page_count",
    event=AddBookEvent,
    event_source_code=AddBookEvent.get_source_code_of_class(),
    constraints_generator=generate_add_book_constraints,
    # replace_func not needed - credentials remain as placeholders until evaluation
    additional_prompt_info=ADD_BOOK_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "First, authenticate with username '<username>' and password '<password>'. Then, add the book 'A Guide to the Good Life' authored by 'William B. Irvine'",
            "prompt_for_task_generation": "First, authenticate with username '<username>' and password '<password>'. Then, add the book '<book>' authored by '<author>'",
        },
        {
            "prompt": "Initiate session using '<username>' as the username and '<password>' as the secret. Then, add the book 'AI Superpowers' released in 2018",
            "prompt_for_task_generation": "Initiate session using '<username>' as the username and '<password>' as the secret. Then, add the book '<book>' released in <year>",
        },
        {
            "prompt": "After successful login with '<username>' and '<password>', add the book 'Sapiens: A Brief History of Humankind' with genres History and Anthropology",
            "prompt_for_task_generation": "After successful login with '<username>' and '<password>', add the book '<book>' with genres <genre> and <genre>",
        },
        {
            "prompt": "Once logged in as '<username>' with the password '<password>', add the book 'The Midnight Library' with a page_count under 320 pages",
            "prompt_for_task_generation": "Once logged in as '<username>' with the password '<password>', add the book '<book>' with a page_count under <page_count> pages",
        },
        {
            "prompt": "Having authenticated with '<username>' and '<password>', add the book 'The Art of Learning' with rating not 4.8.",
            "prompt_for_task_generation": "Having authenticated with '<username>' and '<password>', add the book '<book>' with rating not equal to <rating>",
        },
        {
            "prompt": "Upon logging in with username '<username>' and the secret '<password>', add the book 'The Practicing Mind' from one of these authors: 'Thomas M. Sterner', 'James Clear', or 'Ryan Holiday'",
            "prompt_for_task_generation": "Upon logging in with username '<username>' and the secret '<password>', add a book '<book>' from one of these authors: '<author>', '<author>', or '<author>'",
        },
        {
            "prompt": "With credentials '<username>' and '<password>' successfully entered, add the book 'Deep Work' with running time at least 450 pages authored by 'Cal Newport'",
            "prompt_for_task_generation": "With credentials '<username>' and '<password>' successfully entered, add the book '<book>' with running time at least <page_count> pages authored by '<author>'",
        },
    ],
)

###############################################################################
# EDIT_BOOK_USE_CASE
###############################################################################
EDIT_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:

1. Include ALL edit constraints mentioned above — not just some of them.
2. Include ONLY the edit constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to edit or modify a book (use phrases like "Edit...", "Modify...", "Update...", "Change...", etc.).
4. Begin with a creative instruction to log in using username '<username>' and password '<password> (**strictly** containing both the username and password placeholders)'.
Examples include: "First, authenticate with...", "Initiate session using...", "After successful login with...", "Once logged in as...", etc. Followed by the book addition request.
5. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.

STRICT FIELD USAGE RULE:

- The username and password MUST appear exactly as provided in the LOGIN sentence only.
- Do NOT repeat username or password inside the edit constraint description unless they are explicitly part of the edit constraints.
- Only include fields that are explicitly defined as edit constraints.
- Every constraint value MUST be copied EXACTLY as given.
- Do NOT rewrite, transform, infer, replace, generalize, or suggest alternative values.
- Do NOT introduce placeholders other than the exact provided values.
- Do NOT add additional filtering criteria beyond what is specified.

IMPORTANT DISTINCTION:

- Login credentials are for authentication only.
- Edit constraints define which book should be modified.
- Do NOT mix authentication fields into the edit filtering unless explicitly instructed.

For example, if the constraints are:
"year equals 2014 AND author contains 'e'"

CORRECT:
"First, authenticate with username '<username>' and password '<password>'. Then, edit your book where the year equals 2014 and the author contains 'e'."

INCORRECT:
- Adding extra filters such as rating or genre.
- Rewriting constraint values.
- Repeating username or password inside the edit condition.
- Editing a random or unspecified book.

ALL prompts must follow this structure exactly, with varied phrasing but identical constraint logic and EXACT field values.
"""
EDIT_BOOK_USE_CASE = UseCase(
    name="EDIT_BOOK",
    description="The user edits an existing book, modifying one or more attributes such as author, year, genres, rating, or page_count.",
    event=EditBookEvent,
    event_source_code=EditBookEvent.get_source_code_of_class(),
    replace_func=replace_book_placeholders,
    constraints_generator=generate_edit_book_constraints,
    additional_prompt_info=EDIT_BOOK_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Sign in with username: <username> and password: <password>. After that, update the author of your book to Jamie Oliver.",
            "prompt_for_task_generation": "Sign in with username: <username> and password: <password>. After that, update the author of <your_book> to Jamie Oliver.",
        },
        {
            "prompt": "First, log into your account with username: <username>, password: <password>. Then, modify the release year of your book to 2023.",
            "prompt_for_task_generation": "First, log into your account with username: <username>, password: <password>. Then, modify the release year of <your_book> to 2023.",
        },
        {
            "prompt": "Access your account by entering username: <username> and password: <password>. Once logged in, add 'Baking' to the genres of your book.",
            "prompt_for_task_generation": "Access your account by entering username: <username> and password: <password>. Once logged in, add 'Baking' to the genres of <your_book>.",
        },
        {
            "prompt": "Using username: <username> and password: <password>, sign into the platform. Then change the rating of your book to 4.9.",
            "prompt_for_task_generation": "Using username: <username> and password: <password>, sign into the platform. Then change the rating of <your_book> to 4.9.",
        },
        {
            "prompt": "Authenticate yourself with username <username> and password <password>. After logging in, edit the page_count of your book to 1000 pages.",
            "prompt_for_task_generation": "Authenticate yourself with username <username> and password <password>. After logging in, edit the page_count of <your_book> to 1000 pages.",
        },
        {
            "prompt": "Login credentials: username <username>, password <password>. Sign in first and then modify the author of your book to include Neil Gaiman.",
            "prompt_for_task_generation": "Login credentials: username <username>, password <password>. Sign in first and then modify the author of <your_book> to include 'Neil Gaiman'.",
        },
    ],
)
###############################################################################
# DELETE_BOOK_USE_CASE
###############################################################################
DELETE_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:

1. Include ALL deletion constraints mentioned above — not just some of them.
2. Include ONLY the deletion constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to delete or remove a book (use phrases like "Remove...", "Delete...", "Erase...", "Discard...").
4. The user is only allowed to delete books they have added. Use terms like 'your book' or 'user-registered book' in the final prompt.
5. Begin with a creative instruction to log in using username '<username>' and password '<password>'.

STRICT FIELD USAGE RULE:

- The username and password MUST appear exactly as provided in the LOGIN sentence only.
- Do NOT repeat username or password inside the delete constraint description unless they are explicitly part of the deletion constraints.
- Only include fields that are explicitly defined as deletion constraints.
- If "id" is a deletion constraint, include it exactly as given.
- Do NOT automatically include username or password as deletion filters unless they are explicitly stated as deletion constraints.
- Do NOT rewrite, transform, infer, or replace any provided field values.
- Every constraint value must be copied verbatim.

IMPORTANT DISTINCTION:
- Login credentials are for authentication only.
- Deletion constraints describe which book to delete.
- Do NOT mix authentication fields into deletion filtering unless explicitly instructed.

For example, if the deletion constraint is:
"id equals '<web_agent_id>'"

CORRECT:
"First, authenticate with username '<username>' and password '<password>'. Then, delete your book whose id equals '<web_agent_id>'."

INCORRECT:
- Adding username or password as deletion filters.
- Repeating login credentials inside the delete description.
- Adding extra constraints like rating or year.

ALL prompts must follow this structure exactly, with varied phrasing but identical constraint logic and EXACT field values.
"""


DELETE_BOOK_USE_CASE = UseCase(
    name="DELETE_BOOK",
    description="The user deletes a book from the system.",
    event=DeleteBookEvent,
    event_source_code=DeleteBookEvent.get_source_code_of_class(),
    additional_prompt_info=DELETE_BOOK_ADDITIONAL_PROMPT_INFO,
    constraints_generator=generate_delete_book_constraints,
    examples=[
        {
            "prompt": "Log in with username: <username>, password: <password> and remove '<your_book>'.",
            "prompt_for_task_generation": "Log in with username: <username>, password: <password> and remove '<your_book>'.",
        },
        {
            "prompt": "After logging in with username: <username> and password: <password>, erase all records of '<your_book>'.",
            "prompt_for_task_generation": "After logging in with username: <username> and password: <password>, erase all records of '<your_book>'.",
        },
        {
            "prompt": "Log in with username: <username>, password: <password> and permanently delete '<your_book>'.",
            "prompt_for_task_generation": "Log in with username: <username>, password: <password> and permanently delete '<your_book>'.",
        },
        {
            "prompt": "Sign into your account where username: <username>, password: <password> and discard '<your_book>'.",
            "prompt_for_task_generation": "Sign into your account where username: <username>, password: <password> and discard '<your_book>'.",
        },
        {
            "prompt": "Initiate a session with username: <username> and password: <password>, then remove '<your_book>'.",
            "prompt_for_task_generation": "Initiate a session with username: <username> and password: <password>, then remove '<your_book>'.",
        },
        {
            "prompt": "Once logged in as username: <username> and password: <password>, delete '<your_book>'.",
            "prompt_for_task_generation": "Once logged in as username: <username> and password: <password>, delete '<your_book>'.",
        },
        {
            "prompt": "Begin by signing in with username <username> and password <password>. Then, delete '<your_book>'.",
            "prompt_for_task_generation": "Begin by signing in with username <username> and password <password>. Then, delete '<your_book>'.",
        },
        {
            "prompt": "First, log into the system with username: <username>, password: <password>, then discard '<your_book>'.",
            "prompt_for_task_generation": "First, log into the system with username: <username>, password: <password>, then discard '<your_book>'.",
        },
        {
            "prompt": "Authenticate yourself with username <username> and password <password>. Then, remove '<your_book>'.",
            "prompt_for_task_generation": "Authenticate yourself with username <username> and password <password>. Then, remove '<your_book>'.",
        },
        {
            "prompt": "Using your credentials username: <username>, password: <password>, sign in and erase all records of '<your_book>'.",
            "prompt_for_task_generation": "Using your credentials username: <username>, password: <password>, sign in and erase all records of '<your_book>'.",
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
4. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.
"""
CONTACT_USE_CASE = UseCase(
    name="CONTACT_BOOK",
    description="The user navigates to the contact form page, fills out fields, and submits the form successfully.",
    event=ContactEvent,
    event_source_code=ContactEvent.get_source_code_of_class(),
    constraints_generator=generate_contact_constraints,
    additional_prompt_info=CONTACT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Send a contact form with the subject 'Test Subject'",
            "prompt_for_task_generation": "Send a contact form with the subject 'Test Subject'",
        },
        {
            "prompt": "Fill out the contact form and include 'Hello, I would like information about your services' in the message",
            "prompt_for_task_generation": "Fill out the contact form and include 'Hello, I would like information about your services' in the message",
        },
        {
            "prompt": "Complete the contact form using the email address 'test@example.com' and different value for field name :'jhon'",
            "prompt_for_task_generation": "Complete the contact form using the email address 'test@example.com' and different value for field name :'jhon'",
        },
        {
            "prompt": "Complete the contact form using the email address different to 'test@example.com'",
            "prompt_for_task_generation": "Complete the contact form using the email address different to 'test@example.com'",
        },
        {
            "prompt": "Send a contact form with subject 'Partnership Inquiry' and include the phrase 'potential collaboration' in your message",
            "prompt_for_task_generation": "Send a contact form with subject 'Partnership Inquiry' and include the phrase 'potential collaboration' in your message",
        },
        {
            "prompt": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and message 'Great website, I love the design'",
            "prompt_for_task_generation": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and message 'Great website, I love the design'",
        },
        {
            "prompt": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and cannot contains any 'e'",
            "prompt_for_task_generation": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and cannot contains any 'e'",
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
3. Begin with "Login for the following username:<username> and password:<password> (**strictly** containing both the username and password placeholders)".
4. Be phrased as a request to edit or modify a user profile (use phrases like "Edit...", "Modify...", "Update...", "Change...", etc.).

For example, if the constraints are "username equals 'bookfan' AND password equals 'pass123' AND bio contains 'bookworm'":
- CORRECT: "Login for the following username:bookfan and password:pass123. Edit your profile to update your bio to include the word 'bookworm'."
- INCORRECT: "Edit a profile to change the website" (missing login information and specific constraints).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
5. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.
"""

EDIT_USER_PROFILE_USE_CASE = UseCase(
    name="EDIT_USER_BOOK",
    description="The user edits their profile, modifying one or more attributes such as first name, last name, bio, location, website, or favorite genres. Username and email cannot be edited.",
    event=EditUserEvent,
    event_source_code=EditUserEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_profile_constraints,
    additional_prompt_info=EDIT_PROFILE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Login for the following username equal to user1 and password equal to pass123. Update your first name so it is equal to John.",
            "prompt_for_task_generation": "Login for the following username equal to <username> and password equal to <password>. Update your first name so it is equal to <first_name>.",
        },
        {
            "prompt": "Login for the following username:user1 and password:pass123.Modify your profile to include the word 'cinema' in your first name and ensure that your website does NOT contain 'https://cinephileworld.example.org'.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Modify your profile to include the word 'cinema' in your <first_name> and ensure that your website does NOT contain <website>.",
        },
        {
            "prompt": "Login for the following username equal to bookfan and password equal to pass456. Modify your bio to include your passion for bookworm.",
            "prompt_for_task_generation": "Login for the following username equal to <username> and password equal to <password>. Modify your bio to include <bio_content>.",
        },
        {
            "prompt": "Login for the following username equal to booklover and password equal to pass789. Change your location so it is equal to New York, USA.",
            "prompt_for_task_generation": "Login for the following username equal to <username> and password equal to <password>. Change your location so it is equal to <location>.",
        },
        {
            "prompt": "Login for the following username:cinephile and password:pass321. Edit your website to https://mybookblog.example.com.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Edit your website to <website>.",
        },
        {
            "prompt": "Login for the following username:author101 and password:pass654. Update your favorite genre to Science.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Update your favorite genre to <genre>.",
        },
        {
            "prompt": "Login for the following username:producer and password:pass987. Change your last name to Smith.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Change your last name to <last_name>.",
        },
    ],
)


###############################################################################
# FILTER_BOOK_USE_CASE
###############################################################################
def _get_filter_book_info(books_data: list[dict]) -> str:
    """Generate filter book info dynamically from API data."""
    allowed_years = _generate_allowed_years_list(books_data)
    allowed_genres = _generate_allowed_genres_list(books_data)
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Include the word "Filter" (or "filtering", "filtered", "filters") explicitly in the prompt.
4. Be phrased as a request to filter or browse books (e.g., "Filter...", "Show only...", etc.).
5. Use ONLY the allowed genres and years from the lists below.

ALLOWED YEARS:
{allowed_years}

ALLOWED GENRES:
{allowed_genres}
For example, if the constraints are "genre_name equals 'Culture' AND year equals 2020":
- CORRECT: "Filter for 'Culture' books released in 2020."
- CORRECT: "Browse books from 2020 in the 'Culture' genre."
- INCORRECT: "Search for 'Culture' books from the 20s" (uses vague year and incorrect phrasing).
- INCORRECT: "Show all 'Culture' books" (missing the year constraint if both are provided).
- INCORRECT: "Filter for Mystery books" (Mystery is not in the allowed genre list).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
6. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.
"""


FILTER_BOOK_ADDITIONAL_PROMPT_INFO_TEMPLATE = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Include the word "Filter" (or "filtering", "filtered", "filters") explicitly in the prompt.
4. Be phrased as a request to filter or browse books (e.g., "Filter...", "Show only...", etc.).
5. Use ONLY the allowed genres and years from the lists below.

ALLOWED YEARS:
{ALLOWED_YEARS_PLACEHOLDER}

ALLOWED GENRES:
{ALLOWED_GENRES_PLACEHOLDER}
For example, if the constraints are "genre_name equals 'Culture' AND year equals 2020":
- CORRECT: "Filter for 'Culture' books released in 2020."
- CORRECT: "Browse books from 2020 in the 'Culture' genre."
- INCORRECT: "Search for 'Culture' books from the 20s" (uses vague year and incorrect phrasing).
- INCORRECT: "Show all 'Culture' books" (missing the year constraint if both are provided).
- INCORRECT: "Filter for Mystery books" (Mystery is not in the allowed genre list).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
6. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.
"""

FILTER_BOOK_USE_CASE = UseCase(
    name="FILTER_BOOK",
    description="The user applies filters to search for books by genre and/or year. Includes Filter in the prompt",
    event=FilterBookEvent,
    event_source_code=FilterBookEvent.get_source_code_of_class(),
    constraints_generator=generate_book_filter_constraints,
    additional_prompt_info=None,  # Will be populated dynamically from API
    examples=[
        {
            "prompt": "Filter books released in the year 2005",
            "prompt_for_task_generation": "Filter books released in the year 2005",
        },
        {
            "prompt": "Filter for Action books",
            "prompt_for_task_generation": "Filter for Action books",
        },
        {
            "prompt": "Browse books from 2019 in the Story genre",
            "prompt_for_task_generation": "Browse books from 2019 in the Story genre",
        },
        {
            "prompt": "Filter Screen books from 2022",
            "prompt_for_task_generation": "Filter Screen books from 2022",
        },
        {
            "prompt": "Filter book list to Education genre",
            "prompt_for_task_generation": "Filter book list to Education genre",
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
4. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.
5. If the constraints include the 'content' field (e.g., content contains or content not_contains), the prompt MUST refer specifically to the comment **content or message**, using expressions like "a comment whose content...", "a review whose message...", etc., and NOT just a vague instruction".
For example, if the constraints are "book_name contains 'Fourth Win' AND content not_contains 'boring'":
- CORRECT: "Add a comment to a book that contains 'Fourth Win' with a review that does NOT contain the word 'boring'."
- INCORRECT: "Write a comment about any book" (missing specific constraints)
- INCORRECT: "Post a review that includes extra unnecessary details" (adding constraints not specified)
6. Value Preservation: Use the exact field values as they are provided in the constraints. Do NOT attempt to correct spelling, rephrase, or normalize any entries.
7. Quoting of Values: Enclose the value of the comment's content AND the commenter's name within **single quotation*** marks.

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

ADD_COMMENT_USE_CASE = UseCase(
    name="ADD_COMMENT_BOOK",
    description="The user adds a comment to a book.",
    event=AddCommentEvent,
    event_source_code=AddCommentEvent.get_source_code_of_class(),
    constraints_generator=generate_add_comment_constraints,
    additional_prompt_info=ADD_COMMENT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Navigate to a book 'Fourth Win' and add a comment 'beautiful book'.",
            "prompt_for_task_generation": "Navigate to a book '<book>' and add a comment '<comment>'.",
        },
        {
            "prompt": "Write a review for a book, ensuring the commenter is not 'John'.",
            "prompt_for_task_generation": "Write a review for a book, ensuring the commenter is not '<commenter>'.",
        },
        {
            "prompt": "Post a comment containing the word 'masterpiece'.",
            "prompt_for_task_generation": "Post a comment containing the word '<comment>'.",
        },
        {
            "prompt": "Add a comment for a book not called The Matrix by someone other than 'John'.",
            "prompt_for_task_generation": "Add a comment for a book not called '<book>' by someone other than '<commenter>'.",
        },
        {
            "prompt": "Write a detailed review for the book 'Elementary Statistics' with a comment that does NOT contain the word 'boring' and ensuring the commenter is not 'David'.",
            "prompt_for_task_generation": "Write a detailed review for the book '<book>' with a comment that does NOT contain the word '<content>' and ensuring the commenter is not '<commenter>'.",
        },
    ],
)

# SHOPPING_CART_ADDITIONAL_PROMPT_INFO = """
# CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
# 1. Include ALL constraints mentioned above — not just some of them.
# 2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
# 3. Be phrased as a request to add/remove/view items in the shopping cart (e.g., "Add to cart...", "Remove from cart...", "View cart...").
# 4. Explicitly mention the shopping cart in the prompt (e.g., "shopping cart", "cart").
# 5. If constraints include book_name or quantity, they MUST be referenced directly in the prompt.
# 6. Begin with a creative instruction to log in using username '<username>' and password '<password>' (**strictly** containing both the username and password placeholders).
# Examples include: "First, authenticate with...", "Initiate session using...", "After successful login with...", "Once logged in as...", etc. Followed by the book addition request.
# 7. Only add a book into the shopping cart, do not include anything like "remove 'The Housemaid' from the shopping cart "...
#
# For example, if the constraints are "book_name equals 'Inception' AND quantity equals 2":
# - CORRECT: "Add 2 copies of Inception to the shopping cart."
# - CORRECT: "Update the cart to include 2 Inception books."
# - INCORRECT: "Put some books in the cart" (missing specific constraints).
# - INCORRECT: "Add Inception to my list" (doesn't mention cart).
#
# ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
# """
#
# SHOPPING_CART_USE_CASE = UseCase(
#     name="SHOPPING_CART",
#     description="The user interacts with the shopping cart by adding, removing, or viewing items.",
#     event=ShoppingCartEvent,
#     event_source_code=ShoppingCartEvent.get_source_code_of_class(),
#     constraints_generator=generate_book_constraints,
#     additional_prompt_info=SHOPPING_CART_ADDITIONAL_PROMPT_INFO,
#     replace_func=replace_book_placeholders,
#     examples=[
#         {
#             "prompt": "Login with username: <username> and password: <password>. After logging in, add 'Fourth Win' to your shopping cart.",
#             "prompt_for_task_generation": "Login with username: <username> and password: <password>. After logging in, add '<book>' to your shopping cart.",
#         },
#         {
#             "prompt": "First sign in with username: <username> and password: <password>. Then place a book with page count greater than or equal to 704, with genre 'Education' into your shopping cart.",
#             "prompt_for_task_generation": "First sign in with username: <username> and password: <password>. Then place a book with page_count greater than or equal to <page_count>, with genre '<genre>' into your shopping cart.",
#         },
#         {
#             "prompt": "Authenticate using username: <username> and password: <password>. After that, add a 'Comics' genre book with less than 400 pages to your shopping cart.",
#             "prompt_for_task_generation": "Authenticate using username: <username> and password: <password>. After that, add a '<genre>' genre book with less than <page_count> pages to your shopping cart.",
#         },
#     ],
# )


VIEW_CART_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
3. Be phrased as a request to view the shopping cart (e.g., "View cart...", "Show cart...", "Display cart...").
4. Explicitly mention the shopping cart in the prompt (e.g., "shopping cart", "cart").
5. Begin with a creative instruction to log in using username '<username>' and password '<password>' (**strictly** containing both the username and password placeholders).
Examples include: "First, authenticate with...", "Initiate session using...", "After successful login with...", "Once logged in as...", etc.

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

VIEW_CART_BOOK_USE_CASE = UseCase(
    name="VIEW_CART_BOOK",
    description="The user views the shopping cart to see items added.",
    event=ViewCartBookEvent,
    event_source_code=ViewCartBookEvent.get_source_code_of_class(),
    constraints_generator=None,
    additional_prompt_info=VIEW_CART_BOOK_ADDITIONAL_PROMPT_INFO,
    replace_func=replace_book_placeholders,
    examples=[
        {
            "prompt": "Login with username: <username> and password: <password>. After logging in, view your shopping cart.",
            "prompt_for_task_generation": "Login with username: <username> and password: <password>. After logging in, view your shopping cart.",
        },
        {
            "prompt": "First sign in with username: <username> and password: <password>. Then display your shopping cart.",
            "prompt_for_task_generation": "First sign in with username: <username> and password: <password>. Then display your shopping cart.",
        },
    ],
)


ADD_TO_CART_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
3. Be phrased as a request to add items to the shopping cart (e.g., "Add to cart...", "Add book to cart...").
4. Explicitly mention the shopping cart in the prompt (e.g., "shopping cart", "cart").
5. If constraints include book_name or quantity, they MUST be referenced directly in the prompt.
6. Begin with a creative instruction to log in using username '<username>' and password '<password>' (**strictly** containing both the username and password placeholders).
Examples include: "First, authenticate with...", "Initiate session using...", "After successful login with...", "Once logged in as...", etc. Followed by the book addition request.
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.

For example, if the constraints are "book_name equals 'Inception' AND quantity equals 2":
- CORRECT: "Add 2 copies of Inception to the shopping cart."
- CORRECT: "Update the cart to include 2 Inception books."
- INCORRECT: "Put some books in the cart" (missing specific constraints).
- INCORRECT: "Add Inception to my list" (doesn't mention cart).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

ADD_TO_CART_BOOK_USE_CASE = UseCase(
    name="ADD_TO_CART_BOOK",
    description="The user adds a book to the shopping cart.",
    event=AddToCartBookEvent,
    event_source_code=AddToCartBookEvent.get_source_code_of_class(),
    constraints_generator=generate_book_constraints,
    additional_prompt_info=ADD_TO_CART_BOOK_ADDITIONAL_PROMPT_INFO,
    replace_func=replace_book_placeholders,
    examples=[
        {
            "prompt": "Login with the username equal to <username> and password equal to <password>. After logging in, add the book where the title is equal to 'Fourth Win' to your shopping cart.",
            "prompt_for_task_generation": "Login with the username equal to <username> and password equal to <password>. After logging in, add the book where the title is equal to <book> to your shopping cart.",
        },
        {
            "prompt": "First sign in using username equal to <username> and password equal to <password>. Then place a book with page count greater than or equal to 704, with genre equal to 'Education' into your shopping cart.",
            "prompt_for_task_generation": "First sign in using username equal to <username> and password equal to <password>. Then place a book with page_count greater than or equal to <page_count>, with genre equal to <genre> into your shopping cart.",
        },
    ],
)


REMOVE_FROM_CART_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions.
3. Be phrased as a request to remove items from the shopping cart (e.g., "Remove from cart...", "Delete from cart...", "Remove book from cart...").
4. Explicitly mention the shopping cart in the prompt (e.g., "shopping cart", "cart").
5. If constraints include book_name, they MUST be referenced directly in the prompt.
6. Begin with a creative instruction to log in using username '<username>' and password '<password>' (**strictly** containing both the username and password placeholders).
Examples include: "First, authenticate with...", "Initiate session using...", "After successful login with...", "Once logged in as...", etc. Followed by the removal request.
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.

For example, if the constraints are "book_name equals 'Inception'":
- CORRECT: "Remove Inception from the shopping cart."
- CORRECT: "Delete Inception from your cart."
- INCORRECT: "Remove some books from the cart" (missing specific constraints).
- INCORRECT: "Remove Inception from my list" (doesn't mention cart).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

REMOVE_FROM_CART_BOOK_USE_CASE = UseCase(
    name="REMOVE_FROM_CART_BOOK",
    description="The user removes a book from the shopping cart.",
    event=RemoveFromCartBookEvent,
    event_source_code=RemoveFromCartBookEvent.get_source_code_of_class(),
    constraints_generator=generate_book_constraints,
    additional_prompt_info=REMOVE_FROM_CART_BOOK_ADDITIONAL_PROMPT_INFO,
    replace_func=replace_book_placeholders,
    examples=[
        {
            "prompt": "Login with the username equal to <username> and password equal to <password>. After logging in, remove the book where the title is equal to 'Fourth Win' from your shopping cart.",
            "prompt_for_task_generation": "Login with the username equal to <username> and password equal to <password>. After logging in, remove the book where the title is equal to <book> from your shopping cart.",
        },
        {
            "prompt": "First sign in using username equal to <username> and password equal to <password>. Then remove the book with genre equal to 'Education' from your shopping cart.",
            "prompt_for_task_generation": "First sign in using username equal to <username> and password equal to <password>. Then remove the book with genre equal to <genre> from your shopping cart.",
        },
    ],
)


PURCHASE_BOOK_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other fields or conditions. Use the values EXACTLY as they appear (do not shorten or modify them).
3. Be phrased as a request to purchase books (e.g., "Purchase...", "Buy...").
4. Explicitly mention the purchase/checkout action in the prompt.
5. If constraints include payment_method or shipping_address, they MUST be referenced directly.
6. Begin with a creative instruction to log in using username '<username>' and password '<password>' (**strictly** containing both the username and password placeholders).
Examples include: "First, authenticate with...", "Initiate session using...", "After successful login with...", "Once logged in as...", etc. Followed by the book addition request.
7. If the constraint contains a field that must be equal to a value, you **must** explicitly mention the word 'equal'.

1. Include ALL purchase constraints mentioned above — not just some of them.
2. Include ONLY the purchase constraints mentioned above — do not add any other fields, filters, or conditions.
3. Be phrased clearly as a request to purchase or buy book(s) (use phrases like "Purchase...", "Buy...", "Proceed to checkout...", etc.).
4. Explicitly mention the purchase or checkout action in the prompt.
5. If constraints include fields such as payment_method or shipping_address, they MUST be referenced exactly as provided.
6. Begin with a creative instruction to log in using username '<username>' and password '<password>'.

STRICT FIELD USAGE RULE:

- The username and password MUST appear exactly as provided in the LOGIN sentence only.
- Do NOT repeat username or password inside the purchase constraint description unless they are explicitly part of the purchase constraints.
- Only include fields that are explicitly defined as purchase constraints.
- Every constraint value MUST be copied EXACTLY as given.
- Do NOT rewrite, transform, infer, generalize, substitute, or suggest alternative values.
- Do NOT introduce new placeholders.
- Do NOT add extra filters such as rating, genre, author, etc., unless explicitly specified.

IMPORTANT DISTINCTION:

- Login credentials are for authentication only.
- Purchase constraints define which book(s) to buy and under what purchase conditions.
- Do NOT mix authentication fields into purchase filtering unless explicitly instructed.

Example (structure illustration only):
If the constraints include:
"title equals 'Dune' AND payment_method equals 'Credit Card'"

CORRECT:
"First, authenticate with username '<username>' and password '<password>'. Then, purchase the book whose title equals 'Dune' using payment_method equals 'Credit Card'."

INCORRECT:
- Rewriting 'Credit Card' as 'card payment'.
- Adding extra filters such as rating.
- Repeating login credentials inside purchase conditions.
- Changing any provided constraint value.

ALL prompts must follow this structure exactly, with varied phrasing but identical constraint logic and EXACT field values.
"""

PURCHASE_BOOK_USE_CASE = UseCase(
    name="PURCHASE_BOOK",
    description="The user completes a purchase of items in the shopping cart.",
    event=PurchaseBookEvent,
    event_source_code=PurchaseBookEvent.get_source_code_of_class(),
    replace_func=replace_book_placeholders,
    constraints_generator=generate_book_constraints,
    additional_prompt_info=PURCHASE_BOOK_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "First, authenticate with username equal to <username> and password equal to <password>. After successful login, purchase the book where the title is equal to 'The Housemaid Is Watching' and the year is equal to 2024.",
            "prompt_for_task_generation": "First, authenticate with username equal to <username> and password equal to <password>. After successful login, purchase the book where the title is equal to <book> and the year is equal to <year>.",
        },
        {
            "prompt": "Initiate session using username equal to <username> and password equal to <password>. Once logged in, checkout with the book where the title is equal to 'Elementary Statistics' and its price is less than $100.",
            "prompt_for_task_generation": "Initiate session using username equal to <username> and password equal to <password>. Once logged in, checkout with the book where the title is equal to <book> and its price is less than <price>.",
        },
        {
            "prompt": "Sign in with username equal to <username> and password equal to <password>. Then complete buying the order for a book where the genre is equal to 'History' and it was released in 2019.",
            "prompt_for_task_generation": "Sign in with username equal to <username> and password equal to <password>. Then complete the order for a book where the genre is equal to <genre> and it was released in <year>.",
        },
    ],
)


###############################################################################
# DYNAMIC PROMPT INFO UPDATER
###############################################################################
async def update_use_cases_prompt_info(
    seed_value: int | None = None,
    dataset: list[dict] | None = None,
    count: int | None = 50,
):
    """
    Update use cases' additional_prompt_info with data from API.
    This should be called before generating tasks to ensure prompt info uses current API data.
    """
    books_data = dataset
    if books_data is None:
        books_data = await _get_books_data_for_prompts(seed_value=seed_value, count=count or 50)
    if books_data is None:
        return

    # Update use cases that need book data
    BOOK_DETAIL_USE_CASE.additional_prompt_info = _get_book_detail_info(books_data)
    SHARE_BOOK_USE_CASE.additional_prompt_info = _get_share_book_info(books_data)
    OPEN_PREVIEW_USE_CASE.additional_prompt_info = _get_open_preview_info(books_data)
    ADD_TO_READING_LIST_USE_CASE.additional_prompt_info = _get_add_to_reading_list_info(books_data)
    REMOVE_FROM_READING_LIST_USE_CASE.additional_prompt_info = _get_remove_from_reading_list_info(books_data)
    FILTER_BOOK_USE_CASE.additional_prompt_info = _get_filter_book_info(books_data)


###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    REGISTRATION_USE_CASE,
    SEARCH_BOOK_USE_CASE,
    FILTER_BOOK_USE_CASE,
    CONTACT_USE_CASE,
    LOGIN_USE_CASE,
    LOGOUT_USE_CASE,
    DELETE_BOOK_USE_CASE,
    ADD_BOOK_USE_CASE,
    ADD_COMMENT_USE_CASE,
    EDIT_USER_PROFILE_USE_CASE,
    BOOK_DETAIL_USE_CASE,
    EDIT_BOOK_USE_CASE,
    PURCHASE_BOOK_USE_CASE,
    SHARE_BOOK_USE_CASE,
    OPEN_PREVIEW_USE_CASE,
    ADD_TO_READING_LIST_USE_CASE,
    REMOVE_FROM_READING_LIST_USE_CASE,
    VIEW_CART_BOOK_USE_CASE,
    ADD_TO_CART_BOOK_USE_CASE,
    REMOVE_FROM_CART_BOOK_USE_CASE,
]
