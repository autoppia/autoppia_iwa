# Assuming these are imported from your events module
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import LoginEvent, RegistrationEvent, SearchFilmEvent
from .replace_functions import login_replace_func, register_replace_func

# Create the use cases directly using the UseCase constructor
USE_CASES = [
    UseCase(
        name="User Registration",
        description="The user fills out the registration form and successfully creates a new account.",
        event=RegistrationEvent,
        event_source_code=RegistrationEvent.get_source_code_of_class(),
        replace_func=register_replace_func,
        examples=[
            {
                "prompt": "Register with the following username:<username>,email:<email> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "REGISTRATION",
                    "criteria": {"username": "<username>"},
                    "reasoning": "This test applies when the task requires a registration event with a specific username.",
                },
            },
            {
                "prompt": "Create a new account with username:<username>,email:<email> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "REGISTRATION",
                    "criteria": {"username": "<username>"},
                    "reasoning": "This test applies when the task requires registration with a specific username.",
                },
            },
            {
                "prompt": "Fill the registration form with username:<username>, email:<email> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "REGISTRATION",
                    "criteria": {"username": "<username>", "email": "<email>"},
                    "reasoning": "This test applies when the task requires registration with both username and email specified.",
                },
            },
            {
                "prompt": "Sign up for an account with username:<username>,email:<email> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "REGISTRATION",
                    "criteria": {"username": "<username>"},
                    "reasoning": "This test applies when the task requires registration with a specific username.",
                },
            },
        ],
    ),
    UseCase(
        name="User Login",
        description="The user fills out the login form and logs in successfully.",
        event=LoginEvent,
        event_source_code=LoginEvent.get_source_code_of_class(),
        replace_func=login_replace_func,
        examples=[
            {
                "prompt": "Login for the following username:<username>  and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "LOGIN",
                    "criteria": {"username": "<username>"},
                    "reasoning": "This test applies when the task requires a login event.",
                },
            },
            {
                "prompt": "Login with a specific username:<username>  and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "LOGIN",
                    "criteria": {"username": "<username>"},
                    "reasoning": "This test applies when the task requires a login event.",
                },
            },
            {
                "prompt": "Fill the Login Form with a specific username:<username> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "LOGIN",
                    "criteria": {"username": "<username>"},
                    "reasoning": "This test applies when the task requires a login event.",
                },
            },
            {
                "prompt": "Sign in to the website username:<username> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "username": "<username>",
                    "event_name": "LOGIN",
                    "criteria": {"username": "<username>"},
                    "reasoning": "This test applies when the task requires a login event.",
                },
            },
        ],
    ),
    # UseCase(
    #     name="User Logout",
    #     description="The user logs out of the platform.",
    #     event=LogoutEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "LogoutEvent", "criteria": {}, "code": LogoutEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Film Detail View",
    #     description="The user views the details page of a film.",
    #     event=FilmDetailEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "FilmDetailEvent", "criteria": {}, "code": FilmDetailEvent.get_source_code_of_class()},
    #     ],
    # ),
    UseCase(
        name="Search Film",
        description="The user searches for a film using a query.",
        event=SearchFilmEvent,
        event_source_code=SearchFilmEvent.get_source_code_of_class(),
        examples=[
            {
                "prompt": "Search for the movie 'Pulp Fiction'",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "SEARCH_FILM",
                    "criteria": {"query": "Pulp Fiction"},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Pulp Fiction'.",
                },
            },
            {
                "prompt": "Find a movie called 'Forrest Gump'",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "SEARCH_FILM",
                    "criteria": {"query": "Forrest Gump"},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Forrest Gump'.",
                },
            },
            {
                "prompt": "Search for 'Goodfellas' in the movie database",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "SEARCH_FILM",
                    "criteria": {"query": "Goodfellas"},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Goodfellas'.",
                },
            },
            {
                "prompt": "Look up the movie 'Interestellar'",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "SEARCH_FILM",
                    "criteria": {"query": "Interestellar"},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Interestellar'.",
                },
            },
        ],
    ),
    # # UseCase(
    #     name="Add Film",
    #     description="The user adds a new film to the system.",
    #     event=AddFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "AddFilmEvent", "criteria": {}, "code": AddFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Edit Film",
    #     description="The user edits the details of an existing film.",
    #     event=EditFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "EditFilmEvent", "criteria": {}, "code": EditFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Delete Film",
    #     description="The user deletes a film from the system.",
    #     event=DeleteFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "DeleteFilmEvent", "criteria": {}, "code": DeleteFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Add Comment",
    #     description="The user adds a comment to a film.",
    #     event=AddCommentEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "AddCommentEvent", "criteria": {}, "code": AddCommentEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Contact Form Submission",
    #     description="The user submits a contact form.",
    #     event=ContactEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "ContactEvent", "criteria": {}, "code": ContactEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Edit User Profile",
    #     description="The user edits their profile details.",
    #     event=EditUserEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "EditUserEvent", "criteria": {}, "code": EditUserEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Filter Films",
    #     description="The user applies filters to search for films by genre and/or year.",
    #     event=FilterFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "FilterFilmEvent", "criteria": {}, "code": FilterFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
]
