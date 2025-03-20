# Assuming these are imported from your events module
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import LoginEvent
from .replace_functions import login_replace_func

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
    #     name="View Film Details",
    #     description="The user views the details of a specific movie, including information such as the director, year, genres, rating, duration, and cast.",
    #     event=FilmDetailEvent,
    #     event_source_code=FilmDetailEvent.get_source_code_of_class(),
    #     replace_func=view_film_detail_replace_func,
    #     examples=[
    #         {
    #             "prompt": "Show details for the movie <movie_name>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "<movie_name>"},
    #                 "reasoning": "This test ensures that when the user requests details for a specific movie, the correct movie name is captured in the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Show details for the movie <movie_name> directed by <director>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "<movie_name>", "director": "<director>"},
    #                 "reasoning": "This test ensures that when a user requests movie details with a director's name, the event captures the correct movie and director information.",
    #             },
    #         },
    #         {
    #             "prompt": "Show information about the movie <movie_name> released in <year>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "<movie_name>", "year": "<year>"},
    #                 "reasoning": "This test validates that the event correctly records the movie's name and release year when viewing film details.",
    #             },
    #         },
    #         {
    #             "prompt": "Give me details on <movie_name> including its rating",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "<movie_name>", "rating": True},
    #                 "reasoning": "This test ensures that when a user specifically requests movie details including the rating, the event captures and records the rating information.",
    #             },
    #         },
    #         {
    #             "prompt": "I want to see details of <movie_name> and its genre",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "<movie_name>", "genre": True},
    #                 "reasoning": "This test checks if the movie genre is correctly included when a user asks for movie details including genre information.",
    #             },
    #         },
    #         {
    #             "prompt": "What is the duration of <movie_name>?",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "<movie_name>", "duration": True},
    #                 "reasoning": "This test ensures that when a user requests the duration of a movie, the event logs the duration field correctly.",
    #             },
    #         },
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
    #     description="The user adds a new film to the system, specifying details such as name, director, year, genres, rating, duration, and cast.",
    #     event=AddFilmEvent,
    #     event_source_code=AddFilmEvent.get_source_code_of_class(),
    #     replace_func=add_film_replace_func,
    #     examples=[
    #         {
    #             "prompt": "Add a new film called <movie_name>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "<movie_name>"},
    #                 "reasoning": "This test ensures that when a user adds a film, the correct movie name is captured in the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the movie <movie_name> directed by <director>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "<movie_name>", "director": "<director>"},
    #                 "reasoning": "This test validates that when a user specifies a director while adding a film, the event correctly captures the movie name and director.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the film <movie_name> released in <year>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "<movie_name>", "year": "<year>"},
    #                 "reasoning": "This test checks if the event records the movie name and release year correctly when a user provides them.",
    #             },
    #         },
    #         {
    #             "prompt": "Add a movie named <movie_name> with a rating of <rating>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "<movie_name>", "rating": "<rating>"},
    #                 "reasoning": "This test ensures that when a user specifies a rating for a movie, the event correctly records the rating information.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the movie <movie_name> with the genre <genre>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "<movie_name>", "genre": "<genre>"},
    #                 "reasoning": "This test validates that when a user specifies a genre while adding a movie, the event includes the genre information.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the movie <movie_name> with a duration of <duration> minutes",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "<movie_name>", "duration": "<duration>"},
    #                 "reasoning": "This test ensures that when a user provides a duration while adding a movie, the event correctly logs the duration information.",
    #             },
    #         },
    #         {
    #             "prompt": "Add a movie <movie_name> starring <cast>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "<movie_name>", "cast": "<cast>"},
    #                 "reasoning": "This test ensures that when a user specifies the cast while adding a movie, the event captures and records the cast details.",
    #             },
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Edit Film",
    #     description="The user edits an existing film in the system, updating details such as name, director, year, genres, rating, duration, and cast.",
    #     event=EditFilmEvent,
    #     event_source_code=EditFilmEvent.get_source_code_of_class(),
    #     replace_func=edit_film_replace_func,
    #     examples=[
    #         {
    #             "prompt": "Change the name of the movie with ID <movie_id> to <new_movie_name>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": "<movie_id>", "name": "<new_movie_name>", "changed_field": "name"},
    #                 "reasoning": "This test ensures that when a user updates a movie's name, the event correctly captures the change.",
    #             },
    #         },
    #         {
    #             "prompt": "Update the director of the film with ID <movie_id> to <new_director>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": "<movie_id>", "director": "<new_director>", "changed_field": "director"},
    #                 "reasoning": "This test verifies that when a user modifies the director of a film, the event properly records the update.",
    #             },
    #         },
    #         {
    #             "prompt": "Modify the release year of the movie with ID <movie_id> to <new_year>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": "<movie_id>", "year": "<new_year>", "changed_field": "year"},
    #                 "reasoning": "This test checks if the event accurately reflects a change in the release year of a film.",
    #             },
    #         },
    #         {
    #             "prompt": "Change the rating of the film with ID <movie_id> to <new_rating>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": "<movie_id>", "rating": "<new_rating>", "changed_field": "rating"},
    #                 "reasoning": "This test ensures that updating a film's rating is correctly captured in the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Update the genre of the movie with ID <movie_id> to <new_genre>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": "<movie_id>", "genre": "<new_genre>", "changed_field": "genre"},
    #                 "reasoning": "This test validates that changes to a film's genre are reflected accurately in the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Edit the duration of the film with ID <movie_id> to <new_duration> minutes",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": "<movie_id>", "duration": "<new_duration>", "changed_field": "duration"},
    #                 "reasoning": "This test checks if the event correctly records changes to the film duration.",
    #             },
    #         },
    #         {
    #             "prompt": "Update the cast of the movie with ID <movie_id> to <new_cast>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": "<movie_id>", "cast": "<new_cast>", "changed_field": "cast"},
    #                 "reasoning": "This test ensures that modifications to a film's cast are properly recorded.",
    #             },
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
    # UseCase(
    #     name="Filter Films",
    #     description="The user applies filters to search for films by genre and/or year.",
    #     event=FilterFilmEvent,
    #     event_source_code=FilterFilmEvent.get_source_code_of_class(),
    #     replace_func=filter_film_replace_func,
    #     examples=[
    #         {
    #             "prompt": "Filter movies released in the year <year>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"year": "<year>", "has_year_filter": True},
    #                 "reasoning": "This test applies when the task requires filtering movies by a specific release year.",
    #             },
    #         },
    #         {
    #             "prompt": "Find action movies",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"genre_name": "Action", "has_genre_filter": True},
    #                 "reasoning": "This test applies when the task requires filtering movies by the 'Action' genre.",
    #             },
    #         },
    #         {
    #             "prompt": "Search for films from the year <year> in the genre <genre>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"year": "<year>", "genre_name": "<genre>", "has_year_filter": True, "has_genre_filter": True},
    #                 "reasoning": "This test applies when the task requires filtering movies by both year and genre.",
    #             },
    #         },
    #         {
    #             "prompt": "Show movies from <year>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"year": "<year>", "has_year_filter": True},
    #                 "reasoning": "This test ensures that filtering by year correctly applies the given criteria.",
    #             },
    #         },
    #         {
    #             "prompt": "Show only <genre> movies",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"genre_name": "<genre>", "has_genre_filter": True},
    #                 "reasoning": "This test verifies that filtering by genre works as expected.",
    #             },
    #         },
    #         {
    #             "prompt": "Show details for the movie <movie_name>",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"genre_name": "<movie_name>"},
    #                 "reasoning": "This test ensures that accessing a movie's details works correctly.",
    #             },
    #         },
    #     ],
    # ),
]
