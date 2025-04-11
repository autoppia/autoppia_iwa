from autoppia_iwa.src.demo_webs.classes import UseCase

from .data import MOVIES_DATA
from .events import (
    AddCommentEvent,
    AddFilmEvent,
    ContactEvent,
    DeleteFilmEvent,
    EditFilmEvent,
    EditUserEvent,
    FilmDetailEvent,
    FilterFilmEvent,
    LoginEvent,
    LogoutEvent,
    RegistrationEvent,
    SearchFilmEvent,
)
from .generation_functions import (
    generate_add_comment_constraints,
    generate_add_film_constraints,
    generate_contact_constraints,
    generate_edit_film_constraints,
    generate_edit_profile_constraints,
    generate_film_constraints,
    generate_film_filter_constraints,
)
from .replace_functions import login_replace_func, register_replace_func, replace_film_placeholders

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
# FILM_DETAIL_USE_CASE
###############################################################################

FILM_DETAIL_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above - not just some of them
2. Include ONLY the constraints mentioned above - do not add any other criteria
3. Be phrased as a request to view details of a movie (use phrases like "Show film details for...", "Give me film details about...")
4. Only use the movies name defined below.

MOVIES NAMES:
{chr(10).join([n["name"] for n in MOVIES_DATA])}

For example, if the constraints are "director not_equals Robert Zemeckis AND year greater_than 2010":
- CORRECT: "Show me details about a movie not directed by Robert Zemeckis that was released after 2010"
- INCORRECT: "Show me details about a movie directed by Christopher Nolan" (you added a random director, and missing the year constraint)
- INCORRECT: "Show me details about a movie not directed by Robert Zemeckis that was released after 2010 with a high rating" (adding an extra constraint about rating)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""
FILM_DETAIL_USE_CASE = UseCase(
    name="FILM_DETAIL",
    description="The user explicitly requests to navigate to or go to the details page of a specific movie that meets certain criteria, where they can view information including director, year, genres, rating, duration, and cast.",
    event=FilmDetailEvent,
    event_source_code=FilmDetailEvent.get_source_code_of_class(),
    additional_prompt_info=FILM_DETAIL_INFO,
    constraints_generator=generate_film_constraints,
    examples=[
        {
            "prompt": "Navigate to The Matrix movie page",
            "prompt_for_task_generation": "Navigate to <movie> movie page",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"name": {"value": "The Matrix", "operator": "equals"}},
                "reasoning": "Explicitly directs the system to navigate to The Matrix film detail page.",
            },
        },
        {
            "prompt": "Go to the film details page for Interstellar by Christopher Nolan",
            "prompt_for_task_generation": "Go to the film details page for <movie> by <director>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"name": {"value": "Interstellar", "operator": "equals"}, "director": {"value": "Christopher Nolan", "operator": "equals"}},
                "reasoning": "Explicitly directs the system to go to the Interstellar film details page, using director as additional criteria.",
            },
        },
        {
            "prompt": "Navigate directly to a sci-fi movie page from 2010",
            "prompt_for_task_generation": "Navigate directly to a <genre> movie page from <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"genres": {"value": ["Sci-Fi"], "operator": "contains"}, "year": {"value": 2010, "operator": "equals"}},
                "reasoning": "Explicitly instructs the system to navigate to a film detail page that matches both genre and year criteria.",
            },
        },
        {
            "prompt": "Go directly to a movie page with rating above 4.5",
            "prompt_for_task_generation": "Go directly to a movie page with rating above <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"rating": {"value": 4.5, "operator": "greater_than"}},
                "reasoning": "Explicitly instructs the system to go to a film detail page for a highly-rated movie that exceeds the specified rating.",
            },
        },
        {
            "prompt": "Take me directly to the Pulp Fiction film details page",
            "prompt_for_task_generation": "Take me directly to the <movie> film details page",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"name": {"value": "Pulp Fiction", "operator": "equals"}},
                "reasoning": "Explicitly requests direct navigation to the Pulp Fiction film detail page.",
            },
        },
        {
            "prompt": "Navigate to a comedy film page less than 100 minutes long",
            "prompt_for_task_generation": "Navigate to a <genre> film page less than <duration> minutes long",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"genres": {"value": ["Comedy"], "operator": "contains"}, "duration": {"value": 100, "operator": "less_than"}},
                "reasoning": "Explicitly directs the system to navigate to a film detail page that matches both genre and duration criteria.",
            },
        },
        {
            "prompt": "Go to a film details page from the 90s with Al Pacino",
            "prompt_for_task_generation": "Go to a film details page from the <decade>s with <actor>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"year": {"value": [1990, 1999], "operator": "between"}, "cast": {"value": "Al Pacino", "operator": "contains"}},
                "reasoning": "Explicitly instructs the system to go to a film detail page matching both decade range and cast member criteria.",
            },
        },
        {
            "prompt": "Navigate me to a horror movie page not directed by Wes Craven",
            "prompt_for_task_generation": "Navigate me to a <genre> movie page not directed by <director>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"genres": {"value": ["Horror"], "operator": "contains"}, "director": {"value": "Wes Craven", "operator": "not_equals"}},
                "reasoning": "Explicitly directs the system to navigate to a horror film detail page excluding those by the specified director.",
            },
        },
        {
            "prompt": "Go directly to the highest-rated James Cameron film page",
            "prompt_for_task_generation": "Go directly to the highest-rated <director> film page",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"director": {"value": "James Cameron", "operator": "equals"}, "rating": {"value": 0, "operator": "sort_desc"}},
                "reasoning": "Explicitly instructs the system to go directly to the film detail page of the highest-rated film by the specified director.",
            },
        },
    ],
)
###############################################################################
# SEARCH_FILM_USE_CASE
###############################################################################
SEARCH_FILM_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Make it EXPLICIT that this is a SEARCH for a movie using clear terms such as:
   - "Search for..."
   - "Look for the film..."
   - "Find a movie..."
   - "Look up a movie..."
2. Avoid ambiguous phrases like "Show details" or "Give me information" that could be confused with other actions
3. Include ONLY the movie title as part of the search
4. DO NOT include ANY constraints or conditions like director, year, genre, etc.

For example:
- CORRECT: "Search for the movie Inception in the database"
- CORRECT: "Look for the film Titanic"
- CORRECT: "Find movies called The Matrix"
- INCORRECT: "Show me details about Inception" (doesn't specify it's a search)
- INCORRECT: "Give me information on Titanic" (ambiguous, doesn't clearly indicate search)
- INCORRECT: "Search for Titanic NOT directed by James Cameron" (includes constraints)
- INCORRECT: "Find a movie called Inception released after 2010" (includes constraints)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL clearly indicating that it is a simple SEARCH with NO additional constraints.
"""

SEARCH_FILM_USE_CASE = UseCase(
    name="SEARCH_FILM",
    description="The user searches for a film using a query.",
    event=SearchFilmEvent,
    event_source_code=SearchFilmEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
    additional_prompt_info=SEARCH_FILM_INFO,
    examples=[
        {
            "prompt": "Look for the film 'The Shawshank Redemption'",
            "prompt_for_task_generation": "Look for the film '<movie>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_FILM",
                "event_criteria": {"query": {"value": "The Shawshank Redemption"}},
                "reasoning": "This test applies when searching for a specific film title <movie>",
            },
        },
        {
            "prompt": "Find a movie called 'Forrest Gump'",
            "prompt_for_task_generation": "Find a movie called '<movie>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_FILM",
                "event_criteria": {"query": {"value": "Forrest Gump", "operator": "equals"}},
                "reasoning": "This test applies when searching for the film <movie>.",
            },
        },
        {
            "prompt": "Search for Interestellar in the movie database",
            "prompt_for_task_generation": "Search for '<movie>' in the movie database",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_FILM",
                "event_criteria": {"query": {"value": "ar", "operator": "equals"}},
                "reasoning": "This test applies when searching for the film <movie>.",
            },
        },
        {
            "prompt": "Look up a movie 'The Dark Knight'",
            "prompt_for_task_generation": "Look up a movie '<movie>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "SEARCH_FILM",
                "event_criteria": {"query": {"value": "The Dark Knight"}},
                "reasoning": "This test applies when searching for <movie>.",
            },
        },
    ],
)

###############################################################################
# ADD_FILM_USE_CASE
###############################################################################
ADD_FILM_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to add or insert a film (use phrases like "Add...", "Insert...", "Register...", etc.).

For example, if the constraints are "year equals 2014 AND director equals 'Wes Anderson'":
- CORRECT: "Add a film whose year equals 2014 and that is directed by Wes Anderson."
- INCORRECT: "Add a film with a high rating" (you added an extra filter).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

ADD_FILM_USE_CASE = UseCase(
    name="ADD_FILM",
    description="The user adds a new film to the system, specifying details such as name, director, year, genres, duration, language, and cast.",
    event=AddFilmEvent,
    event_source_code=AddFilmEvent.get_source_code_of_class(),
    constraints_generator=generate_add_film_constraints,
    additional_prompt_info=ADD_FILM_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add the movie 'The Grand Budapest Hotel' directed by 'Wes Anderson'",
            "prompt_for_task_generation": "Add the movie '<movie>' directed by '<director>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "The Grand Budapest Hotel", "operator": "equals"}, "director": {"value": "Wes Anderson", "operator": "equals"}},
                "reasoning": "Validates that the film's name and director are captured with an exact match.",
            },
        },
        {
            "prompt": "Add the film 'Whiplash' released in 2014",
            "prompt_for_task_generation": "Add the film '<movie>' released in <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Whiplash", "operator": "equals"}, "year": {"value": 2014, "operator": "equals"}},
                "reasoning": "Checks that the film's release year is recorded correctly.",
            },
        },
        {
            "prompt": "Add the movie 'Spirited Away' with genres Animation, Fantasy, and Adventure",
            "prompt_for_task_generation": "Add the movie '<movie>' with genres <genre>, <genre> and <genre>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Spirited Away", "operator": "equals"}, "genres": {"value": ["Animation", "Fantasy", "Adventure"], "operator": "contains"}},
                "reasoning": "Validates that multiple genres are captured correctly using the contains operator.",
            },
        },
        {
            "prompt": "Add the movie 'Django Unchained' with a duration under 180 minutes",
            "prompt_for_task_generation": "Add the movie '<movie>' with a duration under <duration> minutes",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Django Unchained", "operator": "equals"}, "duration": {"value": 180, "operator": "less_than"}},
                "reasoning": "Ensures that the film's duration is stored and compared correctly using the less_than operator.",
            },
        },
        {
            "prompt": "Add a movie 'Parasite' that is not in English",
            "prompt_for_task_generation": "Add a movie '<movie>' that is not in <language>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Parasite", "operator": "equals"}, "language": {"value": "English", "operator": "not_equals"}},
                "reasoning": "Tests the not_equals operator for the language field, ensuring that the film's language is different from English.",
            },
        },
        {
            "prompt": "Add a movie 'The Shining' from one of these directors: Kubrick, Spielberg, or Scorsese",
            "prompt_for_task_generation": "Add a movie '<movie>' from one of these directors: <director>, <director>, or <director>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "The Shining", "operator": "equals"}, "director": {"value": ["Kubrick", "Spielberg", "Scorsese"], "operator": "in_list"}},
                "reasoning": "Validates that the director is one of the allowed options using the in_list operator.",
            },
        },
        {
            "prompt": "Add the movie 'Amélie' with running time at least 120 minutes starring Audrey Tautou",
            "prompt_for_task_generation": "Add the movie '<movie>' with running time at least <duration> minutes starring <cast>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {
                    "name": {"value": "Amélie", "operator": "equals"},
                    "duration": {"value": 120, "operator": "greater_equal"},
                    "cast": {"value": "Audrey Tautou", "operator": "contains"},
                },
                "reasoning": "Checks that the film's duration meets the minimum requirement and that the cast includes Audrey Tautou.",
            },
        },
    ],
)

###############################################################################
# EDIT_FILM_USE_CASE
###############################################################################
EDIT_FILM_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to edit or modify a film (use phrases like "Edit...", "Modify...", "Update...", "Change...", etc.).

For example, if the constraints are "year equals 2014 AND director contains 'e'":
- CORRECT: "Edit a film where the year equals 2014 and the director's name contains the letter 'e'."
- INCORRECT: "Edit a random film with a high rating" (you added an extra filter).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
EDIT_FILM_USE_CASE = UseCase(
    name="EDIT_FILM",
    description="The user edits an existing film, modifying one or more attributes such as name, director, year, genres, rating, duration, or cast.",
    event=EditFilmEvent,
    event_source_code=EditFilmEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
    constraints_generator=generate_edit_film_constraints,
    additional_prompt_info=EDIT_FILM_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Update the director of The Matrix to Christopher Nolan",
            "prompt_for_task_generation": "Update the director of <movie> to Christopher Nolan",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {
                    "name": {"value": "The Matrix", "operator": "equals"},
                    "director": {"value": "Christopher Nolan", "operator": "equals"},
                },
                "reasoning": "Ensures the new director is recorded.",
            },
        },
        {
            "prompt": "Modify the release year of Pulp Fiction to 1994",
            "prompt_for_task_generation": "Modify the release year of <movie> to 1994",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "Pulp Fiction", "operator": "equals"}, "year": {"value": 1994, "operator": "equals"}},
                "reasoning": "Ensures the new year is recorded.",
            },
        },
        {
            "prompt": "Add Sci-Fi to the genres of Inception",
            "prompt_for_task_generation": "Add 'Sci-Fi' to the genres of <movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "Inception", "operator": "equals"}, "genre": {"value": "Sci-Fi", "operator": "contains"}},
                "reasoning": "Verifies that the new genre is added.",
            },
        },
        {
            "prompt": "Change the rating of Interstellar to 4.8",
            "prompt_for_task_generation": "Change the rating of <movie> to 4.8",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "Interestellar", "operator": "equals"}, "rating": {"value": 4.8, "operator": "equals"}},
                "reasoning": "Ensures the rating is updated correctly.",
            },
        },
        {
            "prompt": "Edit the duration of The Godfather to 175 minutes",
            "prompt_for_task_generation": "Edit the duration of <movie> to 175 minutes",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "The Godfather", "operator": "equals"}, "duration": {"value": 175, "operator": "equals"}},
                "reasoning": "Ensures that the duration is updated.",
            },
        },
        {
            "prompt": "Modify the cast of The Shawshank Redemption to include Morgan Freeman",
            "prompt_for_task_generation": "Modify the cast of <movie> to include 'Morgan Freeman'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {
                    "name": {"value": "The Shawshank Redemption", "operator": "equals"},
                    "cast": {"value": "Morgan Freeman", "operator": "contains"},
                },
                "reasoning": "Ensures the cast changes are properly logged.",
            },
        },
    ],
)
###############################################################################
# DELETE_FILM_USE_CASE
###############################################################################
DELETE_FILM_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Be phrased as a request to delete or remove a film (use phrases like "Remove...", "Delete...", "Erase...", "Discard...").

For example, if the constraints are "year greater_than 2014 AND genres contains Sci-Fi":
- CORRECT: "Delete a film whose year is greater than 2014 and that belongs to the Sci-Fi genre."
- INCORRECT: "Delete a film from 2015 with a high rating" (you added an extra filter).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

DELETE_FILM_USE_CASE = UseCase(
    name="DELETE_FILM",
    description="The user deletes a film from the system.",
    event=DeleteFilmEvent,
    event_source_code=DeleteFilmEvent.get_source_code_of_class(),
    additional_prompt_info=DELETE_FILM_ADDITIONAL_PROMPT_INFO,
    constraints_generator=generate_film_constraints,
    examples=[
        {
            "prompt": "Remove The Matrix, a film released after 2014, from the database",
            "prompt_for_task_generation": "Remove '<movie>' that was released after <year> from the database",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "The Matrix", "operator": "equals"}, "year": {"value": 2014, "operator": "greater_than"}},
                "reasoning": "Ensures that 'The Matrix' is deleted and that its release year is greater than 2014.",
            },
        },
        {
            "prompt": "Erase all records of Pulp Fiction, a film not directed by Quentin Tarantino",
            "prompt_for_task_generation": "Erase all records of '<movie>' not directed by <director>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Pulp Fiction", "operator": "equals"}, "director": {"value": "Quentin Tarantino", "operator": "not_equals"}},
                "reasoning": "Confirms that 'Pulp Fiction' is deleted and verifies that the film's director is not Quentin Tarantino.",
            },
        },
        {
            "prompt": "Permanently delete The Godfather, which has a duration greater than 175 minutes",
            "prompt_for_task_generation": "Permanently delete '<movie>' with duration greater than <duration> minutes",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "The Godfather", "operator": "equals"}, "duration": {"value": 175, "operator": "greater_than"}},
                "reasoning": "Ensures that 'The Godfather' is permanently removed and that its duration exceeds 175 minutes.",
            },
        },
        {
            "prompt": "Discard Titanic, a film with a rating less than 7.0, from the system",
            "prompt_for_task_generation": "Discard '<movie>' with rating less than <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Titanic", "operator": "equals"}, "rating": {"value": 7.0, "operator": "less_than"}},
                "reasoning": "Verifies that 'Titanic' is discarded and its rating is below 7.0.",
            },
        },
        {
            "prompt": "Remove Airplane!, a comedy film released before 1980, from the records",
            "prompt_for_task_generation": "Remove a <genre> film called '<movie>' released before <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Airplane!", "operator": "equals"}, "genres": {"value": ["Comedy"], "operator": "contains"}, "year": {"value": 1980, "operator": "less_than"}},
                "reasoning": "Checks that 'Airplane!' is removed and meets the genre and release year criteria.",
            },
        },
        {
            "prompt": "Erase the horror film that is not directed by Wes Craven",
            "prompt_for_task_generation": "Erase a <genre> film not directed by <director>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"genres": {"value": ["Horror"], "operator": "contains"}, "director": {"value": "Wes Craven", "operator": "not_equals"}},
                "reasoning": "Ensures deletion of a horror film and verifies that it is not directed by Wes Craven.",
            },
        },
        {
            "prompt": "Permanently delete a film featuring Robert De Niro that was released after 2000",
            "prompt_for_task_generation": "Permanently delete a film with cast containing <actor> and released after <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"cast": {"value": "Robert De Niro", "operator": "contains"}, "year": {"value": 2000, "operator": "greater_than"}},
                "reasoning": "Verifies that the film to be deleted features Robert De Niro and was released after the year 2000.",
            },
        },
        {
            "prompt": "Discard Inception, a film with a rating greater than 8.0, from the system",
            "prompt_for_task_generation": "Discard '<movie>' with rating greater than <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Inception", "operator": "equals"}, "rating": {"value": 8.0, "operator": "greater_than"}},
                "reasoning": "Ensures that 'Inception' is discarded and its rating exceeds 8.0.",
            },
        },
        {
            "prompt": "Remove Gladiator, ensuring it was released before 2000",
            "prompt_for_task_generation": "Remove '<movie>' ensuring it was released before <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Gladiator", "operator": "equals"}, "year": {"value": 2000, "operator": "less_than"}},
                "reasoning": "Verifies that 'Gladiator' is removed and that its release year is before 2000.",
            },
        },
        {
            "prompt": "Erase all records of Avatar, a film that does not belong to the Action genre",
            "prompt_for_task_generation": "Erase all records of '<movie>' that does not belong to the <genre> genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Avatar", "operator": "equals"}, "genres": {"value": ["Action"], "operator": "not_contains"}},
                "reasoning": "Checks that 'Avatar' is erased and confirms that it does not belong to the Action genre.",
            },
        },
        {
            "prompt": "Delete a film whose year is in the list [1999, 1972, 1990]",
            "prompt_for_task_generation": "Delete a film whose year is in the list [<year1>, <year2>, <year3>]",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"year": {"value": [1999, 1972, 1990], "operator": "in_list"}},
                "reasoning": "Verifies that the film's release year is one of the specific years mentioned in the list: 1999, 1972, or 1990.",
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

For example, if the constraints are "username equals 'filmfan' AND password equals 'pass123' AND bio contains 'cinema'":
- CORRECT: "Login for the following username:filmfan and password:pass123. Edit your profile to update your bio to include the word 'cinema'."
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
            "prompt": "Login for the following username:filmfan and password:pass456. Modify your bio to include your passion for cinema.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Modify your bio to include <bio_content>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "filmfan", "operator": "equals"},
                    "bio": {"value": "cinema", "operator": "contains"},
                },
                "reasoning": "Ensures the new bio content is recorded.",
            },
        },
        {
            "prompt": "Login for the following username:movielover and password:pass789. Change your location to New York, USA.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Change your location to <location>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "movielover", "operator": "equals"},
                    "location": {"value": "New York, USA", "operator": "equals"},
                },
                "reasoning": "Ensures the location is updated.",
            },
        },
        {
            "prompt": "Login for the following username:cinephile and password:pass321. Edit your website to https://myfilmblog.example.com.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Edit your website to <website>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "cinephile", "operator": "equals"},
                    "website": {"value": "https://myfilmblog.example.com", "operator": "equals"},
                },
                "reasoning": "Ensures the website is updated.",
            },
        },
        {
            "prompt": "Login for the following username:director101 and password:pass654. Update your favorite genre to Sci-Fi.",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>. Update your favorite genre to <genre>.",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_PROFILE",
                "event_criteria": {
                    "username": {"value": "director101", "operator": "equals"},
                    "favorite_genres": {"value": "Sci-Fi", "operator": "equals"},
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
# FILTER_FILM_USE_CASE
###############################################################################
FILTER_FILM_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above — not just some of them.
2. Include ONLY the constraints mentioned above — do not add any other criteria or filters.
3. Include the word "Filter" (or "filtering", "filtered", "filters") explicitly in the prompt.
4. Be phrased as a request to filter or browse films (e.g., "Filter...", "Show only...", etc.).
5. Use ONLY the allowed genres and years from the lists below.

ALLOWED YEARS:
1972, 1990, 1994, 1999, 2001, 2008, 2010, 2014

ALLOWED GENRES:
"Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"

For example, if the constraints are "genre_name equals 'Action' AND year equals 1999":
- CORRECT: "Filter for Action movies released in 1999."
- CORRECT: "Browse films from 1999 in the Action genre."
- INCORRECT: "Search for Action films from the 90s" (uses vague year and incorrect phrasing).
- INCORRECT: "Show all Action films" (missing the year constraint if both are provided).
- INCORRECT: "Filter for Mystery movies" (Mystery is not in the allowed genre list).

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

FILTER_FILM_USE_CASE = UseCase(
    name="FILTER_FILM",
    description="The user applies filters to search for films by genre and/or year. Includes Filter in the prompt",
    event=FilterFilmEvent,
    event_source_code=FilterFilmEvent.get_source_code_of_class(),
    constraints_generator=generate_film_filter_constraints,
    additional_prompt_info=FILTER_FILM_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Filter movies released in the year 1994",
            "prompt_for_task_generation": "Filter movies released in the year 1994",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"year": 1994},
                "reasoning": "Ensures that filtering movies by the year 1994 correctly triggers the event.",
            },
        },
        {
            "prompt": "Filter for Action movies",
            "prompt_for_task_generation": "Filter for Action movies",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"genre_name": "Action"},
                "reasoning": "Ensures that searching for 'Action' genre movies correctly triggers the event.",
            },
        },
        {
            "prompt": "Browse films from 2010 in the Drama genre",
            "prompt_for_task_generation": "Browse films from 2010 in the Drama genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"year": 2010, "genre_name": "Drama"},
                "reasoning": "Validates that filtering by both year and genre applies correctly.",
            },
        },
        {
            "prompt": "Filter Screen movies from 1999",
            "prompt_for_task_generation": "Filter Screen movies from 1999",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"year": 1999},
                "reasoning": "Ensures screening movies by the year 1999 works independently.",
            },
        },
        {
            "prompt": "Filter movie list to Sci-Fi genre",
            "prompt_for_task_generation": "Filter movie list to Sci-Fi genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"genre_name": "Sci-Fi"},
                "reasoning": "Ensures refining movies by the 'Sci-Fi' genre works independently.",
            },
        },
    ],
)

###############################################################################
# ADD_COMMENT_USE_CASE
###############################################################################
ADD_COMMENT_ADDITIONAL_PROMPT_INFO = """
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. **Mention EXACTLY the constraints** for movie_name, commenter_name, or content, **using the same words** as the constraints.
   - If the constraint is movie_name = 'Inception', you must say: "Add a comment to a movie whose name EQUALS 'Inception'."
   - If the constraint is commenter_name contains 'John', you must say: "Ensure the commenter's name CONTAINS 'John'."
   - If the constraint is content not_contains 'boring', you must say: "Ensure the comment's content does NOT contain 'boring'."
   - Avoid ambiguous or vague phrases like "emotionally powerful," "true cinematic experience," or "redefines the genre." Instead, **only** use literal constraints from the system.

2. **Do NOT** introduce or interpret subjective phrases like "sets a new standard," "redefines the genre," "true cinematic experience," "is emotionally powerful," etc.
   - If such a phrase appears in a constraint, rewrite it explicitly as content = "the exact substring" or content not_contains "the exact substring," or omit it if it doesn't map to an operator.

3. The prompt MUST be phrased as a direct request to add or post a comment (e.g. "Add a comment...", "Write a review...", "Leave feedback...").
   - If the constraint says commenter_name = 'Tom', you must say "Ensure the commenter's name EQUALS 'Tom'."

4. If there's a constraint about `movie_name`, you must specify it: "Add a comment to a movie whose name [operator] 'XYZ'."
   - If there's no constraint about movie_name, the prompt can simply say "Add a comment to a movie."

5. If there's a constraint about `commenter_name`, you must reference the person posting the comment, e.g., "a comment from someone whose name CONTAINS 'John'."
   - If there's no constraint, do not invent one.

6. If there's a constraint about `content`, you must explicitly say "a comment whose content [operator] 'XYZ'."
   - e.g. "a comment whose content NOT_CONTAINS 'boring'."

7. **Use field values exactly as provided.** Do not correct spelling or reword.
   - If the system says the movie_name is 'Interestellar', do NOT change it to 'Interstellar'.
   - If the system says commenter_name not_equals 'Michael', you must keep 'Michael' exactly.

8. **No extraneous constraints**: Do not add extra conditions like "with a rating of X", "mention your budget," etc. If it's not in the constraint, it must not appear.

EXAMPLE of a correct prompt if the constraints are:
- movie_name not_equals 'The Matrix'
- commenter_name contains 'John'
- content not_contains 'boring'

CORRECT:
"Add a comment to a movie whose name does NOT EQUAL 'The Matrix', with a commenter's name that CONTAINS 'John', and the comment content that does NOT CONTAIN 'boring'."

INCORRECT (vague, missing details, or extra):
- "Post a review for a film that is not The Matrix about an amazing experience" (vague and missing actual content constraint).
- "Add a comment to any movie" (omits constraints).
- "Write a comment that does not mention the word 'boring' but also do not mention 'bad acting' either" (extra constraint not in the system).

ALL prompts must follow this structure, phrasing each constraint EXACTLY, and only the constraints that were specified.
"""
ADD_COMMENT_USE_CASE = UseCase(
    name="ADD_COMMENT",
    description="The user adds a comment to a movie.",
    event=AddCommentEvent,
    event_source_code=AddCommentEvent.get_source_code_of_class(),
    constraints_generator=generate_add_comment_constraints,
    additional_prompt_info=ADD_COMMENT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Navigate to a movie and add a comment about Inception",
            "prompt_for_task_generation": "Navigate to <movie> and add a comment",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"movie_name": {"value": "Inception", "operator": "equals"}},
                "reasoning": "Verifies adding a comment to a specific movie.",
            },
        },
        {
            "prompt": "Write a review for a movie, ensuring the commenter is not John",
            "prompt_for_task_generation": "Write a review for <movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"commenter_name": {"value": "John", "operator": "not_equals"}},
                "reasoning": "Ensures comment can be added with name constraint.",
            },
        },
        {
            "prompt": "Post a comment containing the word 'masterpiece'",
            "prompt_for_task_generation": "Post a comment for <movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"content": {"value": "masterpiece", "operator": "contains"}},
                "reasoning": "Validates comment generation with specific content.",
            },
        },
        {
            "prompt": "Add a comment for a movie not called The Matrix by someone other than John",
            "prompt_for_task_generation": "Add a comment for <movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {"movie_name": {"value": "The Matrix", "operator": "not_equals"}, "commenter_name": {"value": "John", "operator": "not_equals"}},
                "reasoning": "Checks multiple constraints for comment addition.",
            },
        },
        {
            "prompt": "Write a detailed review with specific movie, content, and commenter constraints",
            "prompt_for_task_generation": "Write a review for <movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {
                    "movie_name": {"value": "Interstellar", "operator": "equals"},
                    "content": {"value": "boring", "operator": "not_contains"},
                    "commenter_name": {"value": "David", "operator": "not_equals"},
                },
                "reasoning": "Demonstrates complex constraint combinations for comment generation.",
            },
        },
    ],
)

###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    EDIT_FILM_USE_CASE,
    FILM_DETAIL_USE_CASE,
    ADD_FILM_USE_CASE,
    EDIT_USER_PROFILE_USE_CASE,
    CONTACT_USE_CASE,
    LOGIN_USE_CASE,
    REGISTRATION_USE_CASE,
    SEARCH_FILM_USE_CASE,
    LOGOUT_USE_CASE,
    FILTER_FILM_USE_CASE,
    DELETE_FILM_USE_CASE,
    ADD_COMMENT_USE_CASE,
]
