# -----------------------------------------------------------------------------
# use_cases.py
# -----------------------------------------------------------------------------
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddCommentEvent,
    # CompositeEvent  # si eventualmente necesitas el composite
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
from .replace_functions import login_replace_func, register_replace_func, replace_film_placeholders

###############################################################################
# REGISTRATION_USE_CASE
###############################################################################
REGISTRATION_USE_CASE = UseCase(
    name="User Registration",
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
    name="User Login",
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
    name="User Logout",
    description="The user logs out of the platform after logging in.",
    event=LogoutEvent,
    event_source_code=LogoutEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Login for the following username:<username> and password:<password>, then logout",
            "prompt_for_task_generation": "Login for the following username:<username> and password:<password>, then logout",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {},
                "reasoning": "This test verifies that the system can handle a login followed by logout instruction.",
            },
        },
        {
            "prompt": "Login with a specific username:<username> and password:<password>, then sign out from the system",
            "prompt_for_task_generation": "Login with a specific username:<username> and password:<password>, then sign out from the system",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {},
                "reasoning": "This test checks if the system recognizes 'sign out' as a logout action after login.",
            },
        },
        {
            "prompt": "Fill the Login Form with a specific username:<username> and password:<password>, once logged in, logout from my account",
            "prompt_for_task_generation": "Fill the Login Form with a specific username:<username> and password:<password>, once logged in, logout from my account",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {},
                "reasoning": "This test verifies logout detection after form-based login phrasing.",
            },
        },
        {
            "prompt": "Sign in to the website username:<username> and password:<password>, after that please log me out",
            "prompt_for_task_generation": "Sign in to the website username:<username> and password:<password>, after that please log me out",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {},
                "reasoning": "This test ensures logout is detected after 'sign in' terminology.",
            },
        },
        {
            "prompt": "Authenticate with username:<username> and password:<password>, then end my session",
            "prompt_for_task_generation": "Authenticate with username:<username> and password:<password>, then end my session",
            "test": {
                "type": "CheckEventTest",
                "event_name": "LOGOUT",
                "event_criteria": {},
                "reasoning": "This test checks if the system recognizes 'end my session' as a logout request.",
            },
        },
    ],
)
###############################################################################
# FILM_DETAIL_USE_CASE
###############################################################################
FILM_DETAIL_USE_CASE = UseCase(
    name="View Film Details",
    description="The user views the details of a specific movie, including director, year, genres, rating, duration, and cast.",
    event=FilmDetailEvent,
    event_source_code=FilmDetailEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
    examples=[
        {
            "prompt": "Show details for the movie The Matrix",
            "prompt_for_task_generation": "Show details for the movie <movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"name": {"value": "The Matrix", "operator": "equals"}},
                "reasoning": "This test ensures that when the user requests details for The Matrix, the correct movie name is captured.",
            },
        },
        {
            "prompt": "Show details for the movie Interstellar directed by Christopher Nolan",
            "prompt_for_task_generation": "Show details for the movie <movie> directed by <director>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"name": {"value": "Interestellar", "operator": "equals"}, "director": {"value": "Christopher Nolan", "operator": "equals"}},
                "reasoning": "Checks that when a user requests movie details with a director's name, both are captured.",
            },
        },
        {
            "prompt": "Show information about a movie released after 2005",
            "prompt_for_task_generation": "Show information about a movie released after <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"year": {"value": 2005, "operator": "greater_than"}},
                "reasoning": "Validates that the year criterion is correctly processed with a greater_than operator.",
            },
        },
        {
            "prompt": "Give me details on a movie with rating above 4.5",
            "prompt_for_task_generation": "Give me details on a movie with rating above <rating>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"rating": {"value": 4.5, "operator": "greater_equal"}},
                "reasoning": "Ensures that rating comparisons with greater_equal operator work correctly.",
            },
        },
        {
            "prompt": "I want to see details of a movie in the Sci-Fi genre",
            "prompt_for_task_generation": "I want to see details of a movie in the <genre> genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"genres": {"value": ["Sci-Fi"], "operator": "contains"}},
                "reasoning": "Checks if the genre is correctly matched using the contains operator for lists.",
            },
        },
        {
            "prompt": "What are some movies not directed by Christopher Nolan?",
            "prompt_for_task_generation": "What are some movies not directed by <director>?",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"director": {"value": "Christopher Nolan", "operator": "not_equals"}},
                "reasoning": "Tests the not_equals operator for excluding specific directors.",
            },
        },
        {
            "prompt": "Show me films with duration less than 150 minutes",
            "prompt_for_task_generation": "Show me films with duration less than <duration> minutes",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"duration": {"value": 150, "operator": "less_than"}},
                "reasoning": "Verifies that duration constraints with the less_than operator work properly.",
            },
        },
        {
            "prompt": "Find movies from the 90s",
            "prompt_for_task_generation": "Find movies from the <decade>s",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"year": {"value": [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999], "operator": "in_list"}},
                "reasoning": "Tests the in_list operator for finding movies in a specific decade.",
            },
        },
        {
            "prompt": "Show movies that are not in the Horror genre",
            "prompt_for_task_generation": "Show movies that are not in the <genre> genre",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILM_DETAIL",
                "event_criteria": {"genres": {"value": ["Horror"], "operator": "not_contains"}},
                "reasoning": "Tests the not_contains operator for excluding movies of a specific genre.",
            },
        },
    ],
)

###############################################################################
# SEARCH_FILM_USE_CASE
###############################################################################
SEARCH_FILM_USE_CASE = UseCase(
    name="Search Film",
    description="The user searches for a film using a query.",
    event=SearchFilmEvent,
    event_source_code=SearchFilmEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
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
                "event_criteria": {"query": {"value": "Interestellar", "operator": "equals"}},
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

ADD_FILM_USE_CASE = UseCase(
    name="Add Film",
    description="The user adds a new film to the system, specifying details such as name, director, year, genres, duration, and cast.",
    event=AddFilmEvent,
    event_source_code=AddFilmEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Add the movie 'The Grand Budapest Hotel' directed by 'Wes Anderson'",
            "prompt_for_task_generation": "Add the movie '<movie>' directed by '<director>'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {
                    "name": {"value": "The Grand Budapest Hotel", "operator": "equals"},
                    "director": {"value": "Wes Anderson", "operator": "equals"},
                },
                "reasoning": "Validates capturing movie name and director with exact match.",
            },
        },
        {
            "prompt": "Add the film 'Whiplash' released in 2014",
            "prompt_for_task_generation": "Add the film '<movie>' released in <year>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Whiplash", "operator": "equals"}, "year": {"value": 2014, "operator": "equals"}},
                "reasoning": "Checks if the event records the year correctly with exact match.",
            },
        },
        {
            "prompt": "Add the movie 'Spirited Away' with genres Animation, Fantasy and Adventure",
            "prompt_for_task_generation": "Add the movie '<movie>' with genres <genre>, <genre> and <genre>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Spirited Away", "operator": "equals"}, "genres": {"value": ["Animation", "Fantasy", "Adventure"], "operator": "contains"}},
                "reasoning": "Validates that multiple genres are captured in the event using contains operator.",
            },
        },
        {
            "prompt": "Add the movie 'Django Unchained' with a duration under 180 minutes",
            "prompt_for_task_generation": "Add the movie '<movie>' with a duration under <duration> minutes",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Django Unchained", "operator": "equals"}, "duration": {"value": 180, "operator": "less_than"}},
                "reasoning": "Ensures that the duration field is stored and properly compared with less_than operator.",
            },
        },
        {
            "prompt": "Add a movie 'Parasite' that is not in English",
            "prompt_for_task_generation": "Add a movie '<movie>' that is not in <language>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "Parasite", "operator": "equals"}, "language": {"value": "English", "operator": "not_equals"}},
                "reasoning": "Tests the not_equals operator for language field validation.",
            },
        },
        {
            "prompt": "Add a movie 'The Shining' from one of these directors: Kubrick, Spielberg, or Scorsese",
            "prompt_for_task_generation": "Add a movie '<movie>' from one of these directors: <director>, <director>, or <director>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {"name": {"value": "The Shining", "operator": "equals"}, "director": {"value": ["Kubrick", "Spielberg", "Scorsese"], "operator": "in_list"}},
                "reasoning": "Tests the in_list operator for validating that director is one of several options.",
            },
        },
        {
            "prompt": "Add a movie 'Amélie' with running time at least 120 minutes starring Audrey Tautou",
            "prompt_for_task_generation": "Add a movie '<movie>' with running time at least <duration> minutes starring <cast>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_FILM",
                "event_criteria": {
                    "name": {"value": "Amélie", "operator": "equals"},
                    "duration": {"value": 120, "operator": "greater_equal"},
                    "cast": {"value": "Audrey Tautou", "operator": "contains"},
                },
                "reasoning": "Checks both greater_equal operator for duration and contains operator for cast.",
            },
        },
    ],
)


###############################################################################
# EDIT_FILM_USE_CASE
###############################################################################
EDIT_FILM_USE_CASE = UseCase(
    name="Edit Film",
    description="The user edits an existing film, modifying one or more attributes such as name, director, year, genres, rating, duration, or cast.",
    event=EditFilmEvent,
    event_source_code=EditFilmEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
    examples=[
        {
            "prompt": "Update the director of 'The Matrix' to 'Lana Wachowski' and 'Lilly Wachowski'",
            "prompt_for_task_generation": "Update the director of <movie> to Lana Wachowski and Lilly Wachowski",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {
                    "name": {"value": "The Matrix"},
                    "director": {"value": ["Lana Wachowski", "Lilly Wachowski"]},
                },
                "reasoning": "Ensures the new directors are recorded as a list.",
            },
        },
        {
            "prompt": "Modify the release year of Pulp Fiction to 1994",
            "prompt_for_task_generation": "Modify the release year of <movie> to 1994",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "Pulp Fiction"}, "year": {"value": 1994}},
                "reasoning": "Ensures the new year is recorded.",
            },
        },
        {
            "prompt": "Add Drama to the genres of The Godfather",
            "prompt_for_task_generation": "Add 'Drama' to the genres of <movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "The Godfather"}, "genre": {"value": "Drama", "operator": "contains"}},
                "reasoning": "Verifies that the new genre is added.",
            },
        },
        {
            "prompt": "Change the rating of Inception to 4.8",
            "prompt_for_task_generation": "Change the rating of <movie> to 4.8",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "Inception"}, "rating": {"value": 4.8}},
                "reasoning": "Ensures the rating is updated correctly.",
            },
        },
        {
            "prompt": "Change the rating of Inception to 4.8 and change the movie name to 'Nope'",
            "prompt_for_task_generation": "Change the rating of <movie> to 3.2 and change the movie name to 'Nope'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "Nope"}, "rating": {"value": 3.2}},
                "reasoning": "Ensures the rating is updated correctly.",
            },
        },
        {
            "prompt": "Edit the duration of Avatar to 162 minutes",
            "prompt_for_task_generation": "Edit the duration of <movie> to 143 minutes",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {"name": {"value": "Avatar"}, "duration": {"value": 162}},
                "reasoning": "Ensures that the duration is updated.",
            },
        },
        {
            "prompt": "Modify the cast of Titanic to include Leonardo DiCaprio and Kate Winslet",
            "prompt_for_task_generation": "Modify the cast of <movie> to include 'Leonardo DiCaprio' and 'Kate Winslet'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_FILM",
                "event_criteria": {
                    "name": {"value": "Titanic"},
                    "cast": {"value": ["Leonardo DiCaprio", "Kate Winslet"], "operator": "contains"},
                },
                "reasoning": "Ensures the cast changes are properly logged.",
            },
        },
    ],
)

###############################################################################
# DELETE_FILM_USE_CASE
###############################################################################
DELETE_FILM_USE_CASE = UseCase(
    name="Delete Film",
    description="The user deletes a film from the system.",
    event=DeleteFilmEvent,
    event_source_code=DeleteFilmEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
    examples=[
        {
            "prompt": "Remove The Matrix from the database",
            "prompt_for_task_generation": "Remove '<movie> from the database",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "The Matrix"}},
                "reasoning": "Ensures that 'The Matrix' is correctly removed from the system.",
            },
        },
        {
            "prompt": "Erase all records of Pulp Fiction",
            "prompt_for_task_generation": "Erase all records of '<movie>",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Pulp Fiction"}},
                "reasoning": "Confirms that all records of 'Pulp Fiction' are deleted.",
            },
        },
        {
            "prompt": "Permanently delete The Godfather from the collection",
            "prompt_for_task_generation": "Permanently delete '<movie> from the collection",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "The Godfather"}},
                "reasoning": "Ensures 'The Godfather' is permanently removed from the system.",
            },
        },
        {
            "prompt": "Discard Titanic from the system",
            "prompt_for_task_generation": "Discard '<movie> from the system",
            "test": {
                "type": "CheckEventTest",
                "event_name": "DELETE_FILM",
                "event_criteria": {"name": {"value": "Titanic"}},
                "reasoning": "Ensures that 'Titanic' is discarded as expected.",
            },
        },
    ],
)

###############################################################################
# CONTACT_USE_CASE
###############################################################################
CONTACT_USE_CASE = UseCase(
    name="Send Contact Form",
    description="The user navigates to the contact form page, fills out fields, and submits the form successfully.",
    event=ContactEvent,
    event_source_code=ContactEvent.get_source_code_of_class(),
    examples=[
        # Comentados: también les agregamos la clave si tienen 'prompt'
        # {
        #     "prompt": "Send a contact form with the subject 'Test Subject'",
        #     "prompt_for_task_generation": "Send a contact form with the subject 'Test Subject'",
        #     "test": {
        #         "type": "CheckEventTest",
        #         "event_name": "CONTACT",
        #         "event_criteria": {
        #             "subject": {
        #                 "value": "Test Subject"
        #             }
        #         },
        #         "reasoning": "Verify that the contact form was submitted with the specified subject.",
        #     },
        # },
        # {
        #     "prompt": "Fill out the contact form and include 'Hello, I would like information about your services' in the message",
        #     "prompt_for_task_generation": "Fill out the contact form and include 'Hello, I would like information about your services' in the message",
        #     "test": {
        #         "type": "CheckEventTest",
        #         "event_name": "CONTACT",
        #         "event_criteria": {
        #             "message": {
        #                 "value": "Hello, I would like information about your services",
        #                 "operator": "contains"
        #             }
        #         },
        #         "reasoning": "Verify that the contact form was submitted with the specific message content.",
        #     },
        # },
        # {
        #     "prompt": "Complete the contact form using the email address 'test@example.com' and different value for field name :'jhon'",
        #     "prompt_for_task_generation": "Complete the contact form using the email address 'test@example.com' and different value for field name :'jhon'",
        #     "test": {
        #         "type": "CheckEventTest",
        #         "event_name": "CONTACT",
        #         "event_criteria": {
        #             "email": {
        #                 "value": "test@example.com"
        #             },
        #             "name": {
        #                 "value": "jhon",
        #                 "operator": "not_equals"
        #             }
        #         },
        #         "reasoning": "Verify that the contact form was submitted from the specified email address.",
        #     },
        # },
        # {
        #     "prompt": "Complete the contact form using the email address different to 'test@example.com'",
        #     "prompt_for_task_generation": "Complete the contact form using the email address different to 'test@example.com'",
        #     "test": {
        #         "type": "CheckEventTest",
        #         "event_name": "CONTACT",
        #         "event_criteria": {
        #             "email": {
        #                 "value": "test@example.com",
        #                 "operator": "not_equals"
        #             }
        #         },
        #         "reasoning": "Verify that the contact form was submitted from the specified email address.",
        #     },
        # },
        # {
        #     "prompt": "Send a contact form with subject 'Partnership Inquiry' and include the phrase 'potential collaboration' in your message",
        #     "prompt_for_task_generation": "Send a contact form with subject 'Partnership Inquiry' and include the phrase 'potential collaboration' in your message",
        #     "test": {
        #         "type": "CheckEventTest",
        #         "event_name": "CONTACT",
        #         "event_criteria": {
        #             "subject": {
        #                 "value": "Partnership Inquiry"
        #             },
        #             "message": {
        #                 "value": "potential collaboration",
        #                 "operator": "contains"
        #             }
        #         },
        #         "reasoning": "Verify that the contact form was submitted with both the specified subject and message content.",
        #     },
        # },
        # {
        #     "prompt": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and message 'Great website, I love the design'",
        #     "prompt_for_task_generation": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and message 'Great website, I love the design'",
        #     "test": {
        #         "type": "CheckEventTest",
        #         "event_name": "CONTACT",
        #         "event_criteria": {
        #             "name": {
        #                 "value": "John Smith"
        #             },
        #             "email": {
        #                 "value": "john@example.com"
        #             },
        #             "subject": {
        #                 "value": "Feedback"
        #             },
        #             "message": {
        #                 "value": "Great website, I love the design",
        #                 "operator": "contains"
        #             }
        #         },
        #         "reasoning": "Verify that the contact form was submitted with all fields matching the specified values.",
        #     },
        # },
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
EDIT_USER_PROFILE_USE_CASE = UseCase(
    name="Edit User Profile",
    description="The user updates their profile details such as name, email, bio, location, or favorite genres.",
    event=EditUserEvent,
    event_source_code=EditUserEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Change the username to 'MovieBuff99' and update the email to 'moviebuff99@example.com'",
            "prompt_for_task_generation": "Change the username to 'MovieBuff99' and update the email to 'moviebuff99@example.com'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "username": {"value": "MovieBuff99"},
                    "email": {"value": "moviebuff99@example.com"},
                    "changed_field": {"value": ["username", "email"]},
                },
                "reasoning": "Ensures that the username and email fields were correctly updated in the user profile.",
            },
        },
        {
            "prompt": "Update the bio to 'Passionate about indie films and classic cinema.'",
            "prompt_for_task_generation": "Update the bio to 'Passionate about indie films and classic cinema.'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "bio_contains": {"value": "Passionate about indie films and classic cinema."},
                    "changed_field": {"value": "bio"},
                },
                "reasoning": "Ensures that the updated bio contains the expected text.",
            },
        },
        {
            "prompt": "Add a new favorite genre 'Science Fiction'",
            "prompt_for_task_generation": "Add a new favorite genre 'Science Fiction'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "has_favorite_genre": {"value": "Science Fiction"},
                    "changed_field": {"value": "favorite_genres"},
                },
                "reasoning": "Ensures that the updated profile includes the specified favorite genre.",
            },
        },
        {
            "prompt": "Set the location to 'Los Angeles, CA' and add a profile picture",
            "prompt_for_task_generation": "Set the location to 'Los Angeles, CA' and add a profile picture",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "location": {"value": "Los Angeles, CA"},
                    "has_profile_pic": {"value": True},
                    "changed_field": {"value": ["location", "has_profile_pic"]},
                },
                "reasoning": "Ensures that the user's location was updated and they have a profile picture.",
            },
        },
        {
            "prompt": "Update the website link to 'https://cinemareviews.com'",
            "prompt_for_task_generation": "Update the website link to 'https://cinemareviews.com'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "has_website": {"value": True},
                    "changed_field": {"value": "website"},
                },
                "reasoning": "Checks if the website field was updated and a valid link was added.",
            },
        },
        {
            "prompt": "Modify the first name to 'John' and last name to 'Doe'",
            "prompt_for_task_generation": "Modify the first name to 'John' and last name to 'Doe'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "name_contains": {"value": "John"},
                    "changed_field": {"value": ["first_name", "last_name"]},
                },
                "reasoning": "Ensures that the first and last names were successfully changed.",
            },
        },
        {
            "prompt": "Change email to 'johndoe@newdomain.com' and remove the profile picture",
            "prompt_for_task_generation": "Change email to 'johndoe@newdomain.com' and remove the profile picture",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "email": {"value": "johndoe@newdomain.com"},
                    "has_profile_pic": {"value": False},
                    "changed_field": {"value": ["email", "has_profile_pic"]},
                },
                "reasoning": "Verifies that the email is updated and the profile picture is removed.",
            },
        },
        {
            "prompt": "Remove 'Horror' from the favorite genres",
            "prompt_for_task_generation": "Remove 'Horror' from the favorite genres",
            "test": {
                "type": "CheckEventTest",
                "event_name": "EDIT_USER",
                "event_criteria": {
                    "has_favorite_genre": {"value": "Horror"},
                    "changed_field": {"value": "favorite_genres"},
                },
                "reasoning": "Ensures that the removed genre no longer exists in the favorite genres list.",
            },
        },
    ],
)

###############################################################################
# FILTER_FILM_USE_CASE
###############################################################################
FILTER_FILM_USE_CASE = UseCase(
    name="Filter Films",
    description="The user applies filters to search for films by genre and/or year.",
    event=FilterFilmEvent,
    event_source_code=FilterFilmEvent.get_source_code_of_class(),
    examples=[
        {
            "prompt": "Filter movies released in the year 2014",
            "prompt_for_task_generation": "Filter movies released in the year 2014",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"year": {"value": 2014}, "has_year_filter": {"value": True}},
                "reasoning": "Ensures that filtering movies by the year 2014 correctly triggers the event.",
            },
        },
        {
            "prompt": "Find action movies",
            "prompt_for_task_generation": "Find action movies",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"genre_name": {"value": "Action"}, "has_genre_filter": {"value": True}},
                "reasoning": "Ensures that filtering movies by the 'Action' genre correctly triggers the event.",
            },
        },
        {
            "prompt": "Search for films from the year 2015 in the genre 'Comedy'",
            "prompt_for_task_generation": "Search for films from the year 2015 in the genre 'Comedy'",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {
                    "year": {"value": 2015},
                    "genre_name": {"value": "Comedy"},
                    "has_year_filter": {"value": True},
                    "has_genre_filter": {"value": True},
                },
                "reasoning": "Validates that filtering by both year and genre applies correctly.",
            },
        },
        {
            "prompt": "Show movies from 1999",
            "prompt_for_task_generation": "Show movies from 1999",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"year": {"value": 1999}, "has_year_filter": {"value": True}},
                "reasoning": "Ensures filtering by the year 1999 works independently.",
            },
        },
        {
            "prompt": "Show only Horror movies",
            "prompt_for_task_generation": "Show only Horror movies",
            "test": {
                "type": "CheckEventTest",
                "event_name": "FILTER_FILM",
                "event_criteria": {"genre_name": {"value": "Horror"}, "has_genre_filter": {"value": True}},
                "reasoning": "Ensures filtering by the genre 'Horror' works independently.",
            },
        },
    ],
)

###############################################################################
# ADD_COMMENT_USE_CASE
###############################################################################
ADD_COMMENT_USE_CASE = UseCase(
    name="Add Comment",
    description="The user adds a comment to a movie.",
    event=AddCommentEvent,
    event_source_code=AddCommentEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
    examples=[
        {
            "prompt": "Search the movie:Inception and add a comment: 'Amazing cinematography! The visuals were stunning.'",
            "prompt_for_task_generation": "Search the movie:<movie> and  add a comment: 'Amazing cinematography! The visuals were stunning.' ",
            "test": {
                "type": "CheckEventTest",
                "event_name": "ADD_COMMENT",
                "event_criteria": {
                    "content": {"value": "Amazing cinematography! The visuals were stunning."},
                    "movie_name": {"value": "Inception"},
                },
                "reasoning": "This test verifies that a positive comment on a movie is recorded correctly.",
            },
        },
        #     {
        #         "prompt": "Comment 'The character development was weak, but the action scenes were top-notch.' on Mad Max: Fury Road",
        #         "prompt_for_task_generation": "Comment 'The character development was weak, but the action scenes were top-notch.' on <movie>",
        #         "test": {
        #             "type": "CheckEventTest",
        #             "event_name": "ADD_COMMENT",
        #             "event_criteria": {
        #                 "content": {"value": "The character development was weak, but the action scenes were top-notch."},
        #                 "movie_name": {"value": "Mad Max: Fury Road"},
        #             },
        #             "reasoning": "This test ensures that a balanced critique is properly captured in the system.",
        #         },
        #     },
        #     {
        #         "prompt": "Leave a review: 'A thought-provoking masterpiece that keeps you guessing.' for The Prestige",
        #         "prompt_for_task_generation": "Leave a review: 'A thought-provoking masterpiece that keeps you guessing.' for <movie>",
        #         "test": {
        #             "type": "CheckEventTest",
        #             "event_name": "ADD_COMMENT",
        #             "event_criteria": {
        #                 "content": {"value": "A thought-provoking masterpiece that keeps you guessing."},
        #                 "movie_name": {"value": "The Prestige"},
        #             },
        #             "reasoning": "This test checks if a detailed review is correctly logged under the respective movie.",
        #         },
        #     },
        #     {
        #         "prompt": "Post a comment 'I didn't expect that plot twist! Totally mind-blowing.' under Fight Club",
        #         "prompt_for_task_generation": "Post a comment 'I didn't expect that plot twist! Totally mind-blowing.' under <movie>",
        #         "test": {
        #             "type": "CheckEventTest",
        #             "event_name": "ADD_COMMENT",
        #             "event_criteria": {
        #                 "content": {"value": "I didn't expect that plot twist! Totally mind-blowing."},
        #                 "movie_name": {"value": "Fight Club"},
        #             },
        #             "reasoning": "This test ensures that a reaction to a shocking plot twist is recorded correctly.",
        #         },
        #     },
        #     {
        #         "prompt": "Write a comment which contains word 'character' on the film The Conjuring",
        #         "prompt_for_task_generation": "Write a comment which contains word 'character' on the film <movie>",
        #         "test": {
        #             "type": "CheckEventTest",
        #             "event_name": "ADD_COMMENT",
        #             "event_criteria": {
        #                 "content": {"value": "Not a fan of horror movies, but this one kept me at the edge of my seat!"},
        #                 "movie_name": {"value": "The Conjuring"},
        #             },
        #             "reasoning": "This test confirms that feedback from a non-horror fan is correctly stored.",
        #         },
        #     },
        #     {
        #         "prompt": "Leave a review: 'The soundtrack was mesmerizing and added so much depth to the story.' for Interestellar. Commenter Name could not be 'John'",
        #         "prompt_for_task_generation": "Leave a review: 'The soundtrack was mesmerizing and added so much depth to the story.' for <movie>. Commenter Name could not be 'John'",
        #         "test": {
        #             "type": "CheckEventTest",
        #             "event_name": "ADD_COMMENT",
        #             "event_criteria": {
        #                 "content": {"value": "The soundtrack was mesmerizing and added so much depth to the story."},
        #                 "commenter_name": {"value": "John", "operator": "not_equals"},
        #                 "movie_name": {"value": "Interestellar"},
        #             },
        #             "reasoning": "This test verifies if a comment about the movie's soundtrack is accurately captured.",
        #         },
        #     },
        #     {
        #         "prompt": "Post a comment 'Too much CGI ruined the realism of the film.' under Jurassic World",
        #         "prompt_for_task_generation": "Post a comment 'Too much CGI ruined the realism of the film.' under  <movie>",
        #         "test": {
        #             "type": "CheckEventTest",
        #             "event_name": "ADD_COMMENT",
        #             "event_criteria": {
        #                 "content": {"value": "Too much CGI ruined the realism of the film."},
        #                 "movie_name": {"value": "Jurassic World"},
        #             },
        #             "reasoning": "This test ensures that criticism about CGI-heavy movies is properly logged.",
        #         },
        #     },
        #     {
        #         "prompt": "Write a comment 'Loved the chemistry between the lead actors. Perfect casting!' on the film La La Land",
        #         "prompt_for_task_generation": "Write a comment 'Loved the chemistry between the lead actors. Perfect casting!' on the film  <movie>",
        #         "test": {
        #             "type": "CheckEventTest",
        #             "event_name": "ADD_COMMENT",
        #             "event_criteria": {
        #                 "content": {"value": "Loved the chemistry between the lead actors. Perfect casting!"},
        #                 "movie_name": {"value": "La La Land"},
        #             },
        #             "reasoning": "This test checks whether romantic or chemistry-related feedback is recorded correctly.",
        #         },
        #     },
    ],
)

###############################################################################
# EJEMPLO DE CASO COMPUESTO (OPCIONAL)
# COMPOSITE_USE_CASE = UseCase(
#     name="Filter and View Movie",
#     ...
# )

###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    # REGISTRATION_USE_CASE,
    LOGIN_USE_CASE,
    LOGOUT_USE_CASE,  # Must be login-ed first
    # FILM_DETAIL_USE_CASE,
    # SEARCH_FILM_USE_CASE,
    # ADD_FILM_USE_CASE,
    # EDIT_FILM_USE_CASE,
    # DELETE_FILM_USE_CASE,
    # ADD_COMMENT_USE_CASE,
    # CONTACT_USE_CASE,
    EDIT_USER_PROFILE_USE_CASE,  # Must be login-ed first
    # FILTER_FILM_USE_CASE,
    # COMPOSITE_USE_CASE,  # si quisieras meterlo también
]
