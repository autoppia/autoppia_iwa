# Assuming these are imported from your events module
from autoppia_iwa.src.demo_webs.classes import UseCase
from autoppia_iwa.src.demo_webs.projects.cinema_1.models import Movie

from .events import FilmDetailEvent, RegistrationEvent

# Create the use cases directly using the UseCase constructor
USE_CASES = [
    UseCase(
        name="Registration",
        prompt_template="Fill registration form and register",
        event=RegistrationEvent,
        success_criteria="Task is successful if the user is actually registered",
        test_examples=[
            {"type": "CheckEventTest", "event_name": "RegistrationEvent", "event_criteria": {}, "code": RegistrationEvent.code()},  # No special criteria needed
        ],
    ),
    UseCase(
        name="Search film",
        prompt_template="Search for a film with {filters} and open its detail page",
        event=FilmDetailEvent,
        models=[Movie],
        success_criteria="Task is successful when there is an event of type 'FilmDetailEvent' emitted with the correct movie associated",
        test_examples=[
            {"type": "CheckEventTest", "event_name": "FilmDetailEvent", "validation_schema": FilmDetailEvent.ValidationCriteria.model_json_schema(), "code": FilmDetailEvent.code()},
        ],
    ),
]
