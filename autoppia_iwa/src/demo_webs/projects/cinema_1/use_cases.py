# Assuming these are imported from your events module
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import FilterFilmEvent

# Create the use cases directly using the UseCase constructor
USE_CASES = [
    # UseCase(
    #     name="User Registration",
    #     description="The user fills out the registration form and successfully creates a new account.",
    #     event=RegistrationEvent,
    #     event_source_code=RegistrationEvent.get_source_code_of_class(),
    #     replace_func=register_replace_func,
    #     examples=[
    #         {
    #             "prompt": "Register with the following username:<username>,email:<email> and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "REGISTRATION",
    #                 "criteria": {"username": "<username>"},
    #                 "reasoning": "This test applies when the task requires a registration event with a specific username.",
    #             },
    #         },
    #         {
    #             "prompt": "Create a new account with username:<username>,email:<email> and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "REGISTRATION",
    #                 "criteria": {"username": "<username>"},
    #                 "reasoning": "This test applies when the task requires registration with a specific username.",
    #             },
    #         },
    #         {
    #             "prompt": "Fill the registration form with username:<username>, email:<email> and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "REGISTRATION",
    #                 "criteria": {"username": "<username>", "email": "<email>"},
    #                 "reasoning": "This test applies when the task requires registration with both username and email specified.",
    #             },
    #         },
    #         {
    #             "prompt": "Sign up for an account with username:<username>,email:<email> and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "REGISTRATION",
    #                 "criteria": {"username": "<username>"},
    #                 "reasoning": "This test applies when the task requires registration with a specific username.",
    #             },
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="User Login",
    #     description="The user fills out the login form and logs in successfully.",
    #     event=LoginEvent,
    #     event_source_code=LoginEvent.get_source_code_of_class(),
    #     replace_func=login_replace_func,
    #     examples=[
    #         {
    #             "prompt": "Login for the following username:<username>  and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "LOGIN",
    #                 "criteria": {"username": "<username>"},
    #                 "reasoning": "This test applies when the task requires a login event.",
    #             },
    #         },
    #         {
    #             "prompt": "Login with a specific username:<username>  and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "LOGIN",
    #                 "criteria": {"username": "<username>"},
    #                 "reasoning": "This test applies when the task requires a login event.",
    #             },
    #         },
    #         {
    #             "prompt": "Fill the Login Form with a specific username:<username> and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "LOGIN",
    #                 "criteria": {"username": "<username>"},
    #                 "reasoning": "This test applies when the task requires a login event.",
    #             },
    #         },
    #         {
    #             "prompt": "Sign in to the website username:<username> and password:<password>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "username": "<username>",
    #                 "event_name": "LOGIN",
    #                 "criteria": {"username": "<username>"},
    #                 "reasoning": "This test applies when the task requires a login event.",
    #             },
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="User Logout",
    #     description="The user logs out of the platform.",
    #     event=LogoutEvent,
    #     event_source_code=LogoutEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "LogoutEvent",
    #             "criteria": {},
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Film Detail View",
    #     description="The user views the details page of a film.",
    #     event=FilmDetailEvent,
    #     event_source_code=FilmDetailEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "FilmDetailEvent",
    #             "criteria": {},
    #         }
    #     ],
    # ),
    # UseCase(
    #     name="Search Film",
    #     description="The user searches for a film using a query.",
    #     event=SearchFilmEvent,
    #     event_source_code=SearchFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Search for the movie 'Pulp Fiction'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "SEARCH_FILM",
    #                 "criteria": {"query": "Pulp Fiction"},
    #                 "reasoning": "This test applies when the task requires searching for a specific film title 'Pulp Fiction'.",
    #             },
    #         },
    #         {
    #             "prompt": "Find a movie called 'Forrest Gump'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "SEARCH_FILM",
    #                 "criteria": {"query": "Forrest Gump"},
    #                 "reasoning": "This test applies when the task requires searching for a specific film title 'Forrest Gump'.",
    #             },
    #         },
    #         {
    #             "prompt": "Search for 'Goodfellas' in the movie database",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "SEARCH_FILM",
    #                 "criteria": {"query": "Goodfellas"},
    #                 "reasoning": "This test applies when the task requires searching for a specific film title 'Goodfellas'.",
    #             },
    #         },
    #         {
    #             "prompt": "Look up the movie 'Interestellar'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "SEARCH_FILM",
    #                 "criteria": {"query": "Interestellar"},
    #                 "reasoning": "This test applies when the task requires searching for a specific film title 'Interestellar'.",
    #             },
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Add Film",
    #     description="The user adds a new film to the system.",
    #     event=AddFilmEvent,
    #     event_source_code=AddFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "AddFilmEvent",
    #             "criteria": {},
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Edit Film",
    #     description="The user edits the details of an existing film.",
    #     event=EditFilmEvent,
    #     event_source_code=EditFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "EditFilmEvent",
    #             "criteria": {},
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Delete Film",
    #     description="The user deletes a film from the system.",
    #     event=DeleteFilmEvent,
    #     event_source_code=DeleteFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "DeleteFilmEvent",
    #             "criteria": {},
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Add Comment",
    #     description="The user adds a comment to a film.",
    #     event=AddCommentEvent,
    #     event_source_code=AddCommentEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "AddCommentEvent",
    #             "criteria": {},
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Contact Form Submission",
    #     description="The user submits a contact form.",
    #     event=ContactEvent,
    #     event_source_code=ContactEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "ContactEvent",
    #             "criteria": {},
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Edit User Profile",
    #     description="The user edits their profile details.",
    #     event=EditUserEvent,
    #     event_source_code=EditFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "type": "CheckEventTest",
    #             "event_name": "EditUserEvent",
    #             "criteria": {},
    #         },
    #     ],
    # ),
    UseCase(
        name="Filter Films",
        description="The user applies filters to search for films by genre and/or year.",
        event=FilterFilmEvent,
        event_source_code=FilterFilmEvent.get_source_code_of_class(),
        examples=[
            {
                "prompt": "Filter movies released in the year <year>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "FILTER_FILM",
                    "criteria": {"year": "<year>", "has_year_filter": True},
                    "reasoning": "This test applies when the task requires filtering movies by a specific release year.",
                },
            },
            {
                "prompt": "Find action movies",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "FILTER_FILM",
                    "criteria": {"genre_name": "Action", "has_genre_filter": True},
                    "reasoning": "This test applies when the task requires filtering movies by the 'Action' genre.",
                },
            },
            {
                "prompt": "Search for films from the year <year> in the genre <genre>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "FILTER_FILM",
                    "criteria": {"year": "<year>", "genre_name": "<genre>", "has_year_filter": True, "has_genre_filter": True},
                    "reasoning": "This test applies when the task requires filtering movies by both year and genre.",
                },
            },
            {
                "prompt": "Show movies from <year>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "FILTER_FILM",
                    "criteria": {"year": "<year>", "has_year_filter": True},
                    "reasoning": "This test ensures that filtering by year correctly applies the given criteria.",
                },
            },
            {
                "prompt": "Show only <genre> movies",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "FILTER_FILM",
                    "criteria": {"genre_name": "<genre>", "has_genre_filter": True},
                    "reasoning": "This test verifies that filtering by genre works as expected.",
                },
            },
            {
                "prompt": "Show details for the movie <movie_name>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "FILTER_FILM",
                    "criteria": {"genre_name": "<movie_name>"},
                    "reasoning": "This test ensures that accessing a movie's details works correctly.",
                },
            },
        ],
    ),
]
