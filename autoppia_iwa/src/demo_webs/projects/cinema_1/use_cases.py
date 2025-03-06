# Assuming these are imported from your events module
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import RegistrationEvent

# Create the use cases directly using the UseCase constructor
USE_CASES = [
    UseCase(
        name="User Registration",
        description="The user fills out the registration form and successfully creates a new account.",
        prompt_template="Register a new user",
        prompt_examples=["Fill out the registration form and register", "Register a new user", "Create a new account"],
        event=RegistrationEvent,
        event_source_code=RegistrationEvent.get_source_code_of_class(),
        examples=[
            (
                "Register with any username",
                {
                    "type": "CheckEventTest",
                    "event_name": "RegistrationEvent",
                    "criteria": {},
                    "reasoning": "This test applies when the task requires a registration event without specifying a username.",
                },
            ),
            (
                "Register with a specific username",
                {
                    "type": "CheckEventTest",
                    "event_name": "RegistrationEvent",
                    "criteria": {"username": "<THE USERNAME SPECIFIED ON PROMPT IF SPECIFIED>"},
                    "reasoning": "This test applies when the task requires registration with a specific username provided in the prompt.",
                },
            ),
            (
                "Register with a specific email",
                {
                    "type": "CheckEventTest",
                    "event_name": "RegistrationEvent",
                    "criteria": {"email": "<THE EMAIL SPECIFIED ON PROMPT IF SPECIFIED>"},
                    "reasoning": "This test applies when the task requires registration with a specific email provided in the prompt.",
                },
            ),
            (
                "Register with a specific password",
                {
                    "type": "CheckEventTest",
                    "event_name": "RegistrationEvent",
                    "criteria": {"password": "<THE PASSWORD SPECIFIED ON PROMPT IF SPECIFIED>"},
                    "reasoning": "This test applies when the task requires registration with a specific password provided in the prompt.",
                },
            ),
            (
                "Register with a specific username and password",
                {
                    "type": "CheckEventTest",
                    "event_name": "RegistrationEvent",
                    "criteria": {"username": "<THE USERNAME SPECIFIED ON PROMPT IF SPECIFIED>", "password": "<THE PASSWORD SPECIFIED ON PROMPT IF SPECIFIED>"},
                    "reasoning": "This test applies when the task requires registration with both a specific username and password provided in the prompt.",
                },
            ),
        ],
    ),
    # UseCase(
    #     name="User Login",
    #     description="The user fills out the login form and logs in successfully.",
    #     prompt_template="Log in",
    #     prompt_examples=["Log in with a user account", "Sign in with your account", "Fill out the login form and sign in"],
    #     event=LoginEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "LoginEvent", "criteria": {}, "code": LoginEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="User Logout",
    #     description="The user logs out of the platform.",
    #     prompt_template="Log out",
    #     prompt_examples=["Log out from the platform", "Sign out of your account", "Click the logout button"],
    #     event=LogoutEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "LogoutEvent", "criteria": {}, "code": LogoutEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Film Detail View",
    #     description="The user views the details page of a film.",
    #     prompt_template="View film details for {film_id}",
    #     prompt_examples=["Display the details of a selected film", "Open the detail page for a specific film"],
    #     event=FilmDetailEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "FilmDetailEvent", "criteria": {}, "code": FilmDetailEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Search Film",
    #     description="The user searches for a film using a query.",
    #     prompt_template="Search for a film with {query}",
    #     prompt_examples=["Search for a film by name", "Find a film by keyword", "Search for a film"],
    #     event=SearchFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "SearchFilmEvent", "criteria": {}, "code": SearchFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Add Film",
    #     description="The user adds a new film to the system.",
    #     prompt_template="Add a new film",
    #     prompt_examples=["Submit new film details", "Add a film entry", "Create a new film record"],
    #     event=AddFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "AddFilmEvent", "criteria": {}, "code": AddFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Edit Film",
    #     description="The user edits the details of an existing film.",
    #     prompt_template="Edit film details for {film_id}",
    #     prompt_examples=["Update film information", "Modify film details", "Edit the film record"],
    #     event=EditFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "EditFilmEvent", "criteria": {}, "code": EditFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Delete Film",
    #     description="The user deletes a film from the system.",
    #     prompt_template="Delete film with {film_id}",
    #     prompt_examples=["Remove a film from the collection", "Delete a film record", "Erase film data"],
    #     event=DeleteFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "DeleteFilmEvent", "criteria": {}, "code": DeleteFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Add Comment",
    #     description="The user adds a comment to a film.",
    #     prompt_template="Add a comment to film {film_id}",
    #     prompt_examples=["Leave a comment on a film", "Comment on a movie", "Submit a comment for a film"],
    #     event=AddCommentEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "AddCommentEvent", "criteria": {}, "code": AddCommentEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Contact Form Submission",
    #     description="The user submits a contact form.",
    #     prompt_template="Submit a contact message",
    #     prompt_examples=["Fill out the contact form", "Send a message via the contact form", "Contact support"],
    #     event=ContactEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "ContactEvent", "criteria": {}, "code": ContactEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Edit User Profile",
    #     description="The user edits their profile details.",
    #     prompt_template="Edit user profile",
    #     prompt_examples=["Update your profile information", "Change account details", "Modify user profile data"],
    #     event=EditUserEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "EditUserEvent", "criteria": {}, "code": EditUserEvent.get_source_code_of_class()},
    #     ],
    # ),
    # UseCase(
    #     name="Filter Films",
    #     description="The user applies filters to search for films by genre and/or year.",
    #     prompt_template="Filter films with {filters}",
    #     prompt_examples=["Apply filters to film search", "Filter films by genre and year", "Search films with specific filters"],
    #     event=FilterFilmEvent,
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "FilterFilmEvent", "criteria": {}, "code": FilterFilmEvent.get_source_code_of_class()},
    #     ],
    # ),
]
