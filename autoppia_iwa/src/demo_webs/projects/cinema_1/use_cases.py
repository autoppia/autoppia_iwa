# Assuming these are imported from your events module
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import LoginEvent, RegistrationEvent

# Create the use cases directly using the UseCase constructor
USE_CASES = [
    UseCase(
        name="Registration",
        description="User fill the registration form and registers successfully.",
        prompt_template="Register a new user",
        prompt_examples=["Fill the registration form and register", "Register a new user", "create a new account"],
        event=RegistrationEvent,
        test_examples=[
            {"type": "CheckEventTest", "event_name": "RegistrationEvent", "event_criteria": {}, "code": RegistrationEvent.code()},  # No special criteria needed
        ],
    ),
    UseCase(
        name="Login",
        description="User fill the login form and logins successfully.",
        prompt_template="Login",
        prompt_examples=["Log in with a user", "sign in with your account", "Fill the login form and Sign In"],
        event=LoginEvent,
        test_examples=[
            {"type": "CheckEventTest", "event_name": "LoginEvent", "event_criteria": {}, "code": LoginEvent.code()},  # No special criteria needed
        ],
    ),
    UseCase(
        name="Logout",
        description="User fill the login form and logins successfully.",
        prompt_template="Logout",
        prompt_examples=["Log out from the platform", "sign out with your account", "Click on the logout button"],
        event=LoginEvent,
        test_examples=[
            {"type": "CheckEventTest", "event_name": "LoginEvent", "event_criteria": {}, "code": LoginEvent.code()},  # No special criteria needed
        ],
    ),
    # UseCase(
    #     name="Search film",
    #     description="Task is successful when there is an event of type 'FilmDetailEvent' emitted with the correct movie associated",
    #     prompt_template="Search for a film with {filters} and open its detail page",
    #     prompt_examples=[""],
    #     event=FilmDetailEvent,
    #     models=[Movie],
    #     test_examples=[
    #         {"type": "CheckEventTest", "event_name": "FilmDetailEvent", "validation_schema": FilmDetailEvent.ValidationCriteria.model_json_schema(), "code": FilmDetailEvent.code()},
    #     ],
    # ),
]
