# Assuming these are imported from your events module
from autoppia_iwa.src.demo_webs.classes import UseCase
from autoppia_iwa.src.demo_webs.projects.cinema_1.replace_functions import login_replace_func, register_replace_func

from .events import LoginEvent, RegistrationEvent, SearchFilmEvent

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
                    "event_name": "REGISTRATION",
                    "event_criteria": {"username": {"value": "<username>"}},
                    "reasoning": "This test applies when the task requires a registration event with a specific username.",
                },
            },
            {
                "prompt": "Create a new account with username:<username>,email:<email> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "REGISTRATION",
                    "event_criteria": {"username": {"value": "<username>", "operator": "equals"}},
                    "reasoning": "This test applies when the task requires registration with a specific username.",
                },
            },
            {
                "prompt": "Fill the registration form with username:<username>, email:<email> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "REGISTRATION",
                    "event_criteria": {"username": {"value": "<username>"}, "email": {"value": "<email>"}},
                    "reasoning": "This test applies when the task requires registration with both username and email specified.",
                },
            },
            {
                "prompt": "Sign up for an account with username:<username>,email:<email> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "REGISTRATION",
                    "event_criteria": {"username": {"value": "<username>", "operator": "contains"}},
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
                "prompt": "Login for the following username:<username> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "LOGIN",
                    "event_criteria": {"username": {"value": "<username>", "operator": "equals"}},
                    "reasoning": "This test applies when the task requires a login event.",
                },
            },
            {
                "prompt": "Login with a specific username:<username> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "LOGIN",
                    "event_criteria": {"username": {"value": "<username>", "operator": "contains"}},
                    "reasoning": "This test applies when the task requires a login event with username containing a specific value.",
                },
            },
            {
                "prompt": "Fill the Login Form with a specific username:<username> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "LOGIN",
                    "event_criteria": {"username": {"value": "<username>"}},
                    "reasoning": "This test applies when the task requires a login event.",
                },
            },
            {
                "prompt": "Sign in to the website username:<username> and password:<password>",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "LOGIN",
                    "event_criteria": {"username": {"value": "<username>"}},
                    "reasoning": "This test applies when the task requires a login event.",
                },
            },
        ],
    ),
    # # UseCase(
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
    #     examples=[
    #         {
    #             "prompt": "Show details for the movie The Matrix",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "The Matrix"},
    #                 "reasoning": "This test ensures that when the user requests details for a specific movie, the correct movie name is captured in the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Show details for the movie Interstellar directed by Christopher Nolan",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "Interstellar", "director": "Christopher Nolan"},
    #                 "reasoning": "This test ensures that when a user requests movie details with a director's name, the event captures the correct movie and director information.",
    #             },
    #         },
    #         {
    #             "prompt": "Show information about the movie Parasite released in 2019",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "Parasite", "year": 2019},
    #                 "reasoning": "This test validates that the event correctly records the movie's name and release year when viewing film details.",
    #             },
    #         },
    #         {
    #             "prompt": "Give me details on The Godfather including its rating",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "The Godfather", "rating": "9.2"},
    #                 "reasoning": "This test ensures that when a user specifically requests movie details including the rating, the event captures and records the rating information.",
    #             },
    #         },
    #         {
    #             "prompt": "I want to see details of Blade Runner 2049 and its genre",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "Blade Runner 2049", "genre": "Sci-Fi"},
    #                 "reasoning": "This test checks if the movie genre is correctly included when a user asks for movie details including genre information.",
    #             },
    #         },
    #         {
    #             "prompt": "What is the duration of Fight Club?",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILM_DETAILS",
    #                 "criteria": {"name": "Fight Club", "duration": "139 min"},
    #                 "reasoning": "This test ensures that when a user requests the duration of a movie, the event logs the duration field correctly.",
    #             },
    #         },
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
                    "event_criteria": {"query": {"value": "Pulp Fiction"}},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Pulp Fiction'.",
                },
            },
            {
                "prompt": "Find a movie called 'Forrest Gump'",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "SEARCH_FILM",
                    "event_criteria": {"query": {"value": "Forrest Gump", "operator": "equals"}},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Forrest Gump'.",
                },
            },
            {
                "prompt": "Search for 'Goodfellas' in the movie database",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "SEARCH_FILM",
                    "event_criteria": {"query": {"value": "Goodfellas", "operator": "equals"}},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Goodfellas'.",
                },
            },
            {
                "prompt": "Look up the movie 'Interestellar'",
                "test": {
                    "type": "CheckEventTest",
                    "event_name": "SEARCH_FILM",
                    "event_criteria": {"query": {"value": "Interestellar"}},
                    "reasoning": "This test applies when the task requires searching for a specific film title 'Interestellar'.",
                },
            },
        ],
    ),
    # # UseCase(
    #     name="Add Film",
    #     description="The user adds a new film to the system, specifying details such as name, director, year, genres, rating, duration, and cast.",
    #     event=AddFilmEvent,
    #     event_source_code=AddFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Add a new film called Inception",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "Inception"},
    #                 "reasoning": "This test ensures that when a user adds a film, the correct movie name is captured in the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the movie The Grand Budapest Hotel directed by Wes Anderson",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "The Grand Budapest Hotel", "director": "Wes Anderson"},
    #                 "reasoning": "This test validates that when a user specifies a director while adding a film, the event correctly captures the movie name and director.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the film Whiplash released in 2014",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "Whiplash", "year": 2014},
    #                 "reasoning": "This test checks if the event records the movie name and release year correctly when a user provides them.",
    #             },
    #         },
    #         {
    #             "prompt": "Add a movie named Mad Max: Fury Road with a rating of 8.1",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "Mad Max: Fury Road", "rating": 8.1},
    #                 "reasoning": "This test ensures that when a user specifies a rating for a movie, the event correctly records the rating information.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the movie Spirited Away with the genres Animation, Fantasy",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "Spirited Away", "genre": ["Animation", "Fantasy"]},
    #                 "reasoning": "This test validates that when a user specifies genres while adding a movie, the event includes the genre information.",
    #             },
    #         },
    #         {
    #             "prompt": "Add the movie Django Unchained with a duration of 165 minutes",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "Django Unchained", "duration": 165},
    #                 "reasoning": "This test ensures that when a user provides a duration while adding a movie, the event correctly logs the duration information.",
    #             },
    #         },
    #         {
    #             "prompt": "Add a movie The Dark Knight starring Christian Bale, Heath Ledger, and Aaron Eckhart",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_FILM",
    #                 "criteria": {"name": "The Dark Knight", "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"]},
    #                 "reasoning": "This test ensures that when a user specifies the cast while adding a movie, the event captures and records the cast details.",
    #             },
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Edit Film",
    #     description="The user edits an existing film, modifying one or more attributes such as name, director, year, genres, rating, duration, or cast.",
    #     event=EditFilmEvent,
    #     event_source_code=EditFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Change the name of the movie with ID 101 to Interstellar",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"movie_id": 101, "name": "Interstellar", "changed_field": "movie_name"},
    #                 "reasoning": "This test ensures that when a user edits a movie name, the event correctly captures the movie ID and new name while tracking the changed field.",
    #             },
    #         },
    #         {
    #             "prompt": "Update the director of The Matrix to Lana Wachowski and Lilly Wachowski",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"name": "The Matrix", "director": "Lana Wachowski, Lilly Wachowski", "changed_field": "movie_director"},
    #                 "reasoning": "This test ensures that when a user updates the director of a movie, the event logs the correct movie name and new director details while noting the changed field.",
    #             },
    #         },
    #         {
    #             "prompt": "Modify the release year of Pulp Fiction to 1994",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"name": "Pulp Fiction", "year": 1994, "changed_field": "movie_year"},
    #                 "reasoning": "This test ensures that when a user modifies the release year, the event correctly records the new year and the changed field.",
    #             },
    #         },
    #         {
    #             "prompt": "Add Drama to the genres of The Godfather",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"name": "The Godfather", "genre": "Drama", "changed_field": "movie_genres"},
    #                 "reasoning": "This test verifies that when a genre is added, the event properly captures the movie name, new genre, and updated field.",
    #             },
    #         },
    #         {
    #             "prompt": "Change the rating of Inception to 8.8",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"name": "Inception", "rating": 8.8, "changed_field": "movie_rating"},
    #                 "reasoning": "This test ensures that when a user updates the rating, the event correctly records the new rating and the changed field.",
    #             },
    #         },
    #         {
    #             "prompt": "Edit the duration of Avatar to 162 minutes",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"name": "Avatar", "movie_duration": 162, "changed_field": "movie_duration"},
    #                 "reasoning": "This test ensures that the event captures the updated duration of the movie correctly.",
    #             },
    #         },
    #         {
    #             "prompt": "Modify the cast of Titanic to include Leonardo DiCaprio and Kate Winslet",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_FILM",
    #                 "criteria": {"name": "Titanic", "movie_cast": "Leonardo DiCaprio, Kate Winslet", "changed_field": "movie_cast"},
    #                 "reasoning": "This test ensures that changes to the cast are properly logged with the new cast details and the updated field.",
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
    #     description="The user adds a comment to a movie.",
    #     event=AddCommentEvent,
    #     event_source_code=AddCommentEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Add a comment: 'Amazing cinematography! The visuals were stunning.' to the movie Inception",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "Amazing cinematography! The visuals were stunning.", "movie_name": "Inception"},
    #                 "reasoning": "This test verifies that a positive comment on a movie is recorded correctly.",
    #             },
    #         },
    #         {
    #             "prompt": "Comment 'The character development was weak, but the action scenes were top-notch.' on Mad Max: Fury Road",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "The character development was weak, but the action scenes were top-notch.", "movie_name": "Mad Max: Fury Road"},
    #                 "reasoning": "This test ensures that a balanced critique is properly captured in the system.",
    #             },
    #         },
    #         {
    #             "prompt": "Leave a review: 'A thought-provoking masterpiece that keeps you guessing.' for The Prestige",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "A thought-provoking masterpiece that keeps you guessing.", "movie_name": "The Prestige"},
    #                 "reasoning": "This test checks if a detailed review is correctly logged under the respective movie.",
    #             },
    #         },
    #         {
    #             "prompt": "Post a comment 'I didn't expect that plot twist! Totally mind-blowing.' under Fight Club",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "I didn't expect that plot twist! Totally mind-blowing.", "movie_name": "Fight Club"},
    #                 "reasoning": "This test ensures that a reaction to a shocking plot twist is recorded correctly.",
    #             },
    #         },
    #         {
    #             "prompt": "Write a comment 'Not a fan of horror movies, but this one kept me at the edge of my seat!' on the film The Conjuring",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "Not a fan of horror movies, but this one kept me at the edge of my seat!", "movie_name": "The Conjuring"},
    #                 "reasoning": "This test confirms that feedback from a non-horror fan is correctly stored.",
    #             },
    #         },
    #         {
    #             "prompt": "Leave a review: 'The soundtrack was mesmerizing and added so much depth to the story.' for Interstellar",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "The soundtrack was mesmerizing and added so much depth to the story.", "movie_name": "Interstellar"},
    #                 "reasoning": "This test verifies if a comment about the movie's soundtrack is accurately captured.",
    #             },
    #         },
    #         {
    #             "prompt": "Post a comment 'Too much CGI ruined the realism of the film.' under Jurassic World",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "Too much CGI ruined the realism of the film.", "movie_name": "Jurassic World"},
    #                 "reasoning": "This test ensures that criticism about CGI-heavy movies is properly logged.",
    #             },
    #         },
    #         {
    #             "prompt": "Write a comment 'Loved the chemistry between the lead actors. Perfect casting!' on the film La La Land",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "ADD_COMMENT",
    #                 "criteria": {"content_contains": "Loved the chemistry between the lead actors. Perfect casting!", "movie_name": "La La Land"},
    #                 "reasoning": "This test checks whether romantic or chemistry-related feedback is recorded correctly.",
    #             },
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Send Contact Form",
    #     description="The user navigates to the contact form page, fills out fields, and submits the form successfully.",
    #     event=ContactEvent,
    #     event_source_code=ContactEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Send a contact form with the subject 'Test Subject'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "CONTACT",
    #                 "event_criteria": {"subject": "Test Subject"},
    #                 "description": "Verify that the contact form was submitted with the specified subject.",
    #             },
    #         },
    #         {
    #             "prompt": "Fill out the contact form and include 'Hello, I would like information about your services' in the message",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "CONTACT",
    #                 "event_criteria": {"message": {"value": "Hello, I would like information about your services", "operator": "contains"}},
    #                 "description": "Verify that the contact form was submitted with the specific message content.",
    #             },
    #         },
    #         # Example 3: Check for specific email
    #         {
    #             "prompt": "Complete the contact form using the email address 'test@example.com'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "CONTACT",
    #                 "event_criteria": {"email": "test@example.com"},
    #                 "description": "Verify that the contact form was submitted from the specified email address.",
    #             },
    #         },
    #         # Example 4: Check for both subject and message
    #         {
    #             "prompt": "Send a contact form with subject 'Partnership Inquiry' and include the phrase 'potential collaboration' in your message",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "CONTACT",
    #                 "event_criteria": {"subject": "Partnership Inquiry", "message": {"value": "potential collaboration", "operator": "contains"}},
    #                 "description": "Verify that the contact form was submitted with both the specified subject and message content.",
    #             },
    #         },
    #         # Example 5: Complete form with all fields
    #         {
    #             "prompt": "Go to the contact page and submit a form with name 'John Smith', email 'john@example.com', subject 'Feedback', and message 'Great website, I love the design'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "CONTACT",
    #                 "event_criteria": {"name": "John Smith", "email": "john@example.com", "subject": "Feedback", "message": {"value": "Great website, I love the design", "operator": "contains"}},
    #                 "description": "Verify that the contact form was submitted with all fields matching the specified values.",
    #             },
    #         },
    #     ],
    # )
    # UseCase(
    #     name="Edit User Profile",
    #     description="The user updates their profile details such as name, email, bio, location, or favorite genres.",
    #     event=EditUserEvent,
    #     event_source_code=EditUserEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Change the username to 'MovieBuff99' and update the email to 'moviebuff99@example.com'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"username": "MovieBuff99", "email": "moviebuff99@example.com", "changed_field": ["username", "email"]},
    #                 "reasoning": "Ensures that the username and email fields were correctly updated in the user profile.",
    #             },
    #         },
    #         {
    #             "prompt": "Update the bio to 'Passionate about indie films and classic cinema.'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"bio_contains": "Passionate about indie films and classic cinema.", "changed_field": "bio"},
    #                 "reasoning": "Ensures that the updated bio contains the expected text.",
    #             },
    #         },
    #         {
    #             "prompt": "Add a new favorite genre 'Science Fiction'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"has_favorite_genre": "Science Fiction", "changed_field": "favorite_genres"},
    #                 "reasoning": "Ensures that the updated profile includes the specified favorite genre.",
    #             },
    #         },
    #         {
    #             "prompt": "Set the location to 'Los Angeles, CA' and add a profile picture",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"location": "Los Angeles, CA", "has_profile_pic": True, "changed_field": ["location", "has_profile_pic"]},
    #                 "reasoning": "Ensures that the user's location was updated and they have a profile picture.",
    #             },
    #         },
    #         {
    #             "prompt": "Update the website link to 'https://cinemareviews.com'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"has_website": True, "changed_field": "website"},
    #                 "reasoning": "Checks if the website field was updated and a valid link was added.",
    #             },
    #         },
    #         {
    #             "prompt": "Modify the first name to 'John' and last name to 'Doe'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"name_contains": "John", "changed_field": ["first_name", "last_name"]},
    #                 "reasoning": "Ensures that the first and last names were successfully changed.",
    #             },
    #         },
    #         {
    #             "prompt": "Change email to 'johndoe@newdomain.com' and remove the profile picture",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"email": "johndoe@newdomain.com", "has_profile_pic": False, "changed_field": ["email", "has_profile_pic"]},
    #                 "reasoning": "Verifies that the email is updated and the profile picture is removed.",
    #             },
    #         },
    #         {
    #             "prompt": "Remove 'Horror' from the favorite genres",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "EDIT_USER",
    #                 "criteria": {"has_favorite_genre": "Horror", "changed_field": "favorite_genres"},
    #                 "reasoning": "Ensures that the removed genre no longer exists in the favorite genres list.",
    #             },
    #         },
    #     ],
    # ),
    # UseCase(
    #     name="Filter Films",
    #     description="The user applies filters to search for films by genre and/or year.",
    #     event=FilterFilmEvent,
    #     event_source_code=FilterFilmEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Filter movies released in the year 2020",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"year": 2020, "has_year_filter": True},
    #                 "reasoning": "Ensures that filtering movies by the year 2020 correctly triggers the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Find action movies",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"genre_name": "Action", "has_genre_filter": True},
    #                 "reasoning": "Ensures that filtering movies by the 'Action' genre correctly triggers the event.",
    #             },
    #         },
    #         {
    #             "prompt": "Search for films from the year 2015 in the genre 'Comedy'",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {
    #                     "year": 2015,
    #                     "genre_name": "Comedy",
    #                     "has_year_filter": True,
    #                     "has_genre_filter": True,
    #                 },
    #                 "reasoning": "Validates that filtering by both year (2015) and genre ('Comedy') applies correctly.",
    #             },
    #         },
    #         {
    #             "prompt": "Show movies from 1999",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"year": 1999, "has_year_filter": True},
    #                 "reasoning": "Ensures filtering by the year 1999 works independently.",
    #             },
    #         },
    #         {
    #             "prompt": "Show only Horror movies",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "FILTER_FILM",
    #                 "criteria": {"genre_name": "Horror", "has_genre_filter": True},
    #                 "reasoning": "Ensures filtering by the genre 'Horror' works independently.",
    #             },
    #         },
    #     ],
    # ),
    # TODO: No sensible, Need to come-up with a new approach
    # UseCase(
    #     name="Filter and View Movie",
    #     description="User filters movies by genre and year, then views details of a selected movie.",
    #     event=CompositeEvent,
    #     event_source_code=CompositeEvent.get_source_code_of_class(),
    #     examples=[
    #         {
    #             "prompt": "Find Action movies from 2020, then view details of 'Inception'.",
    #             "test": {
    #                 "type": "CheckEventTest",
    #                 "event_name": "COMPOSITE_EVENT",
    #                 "criteria": {
    #                     "event_criteria": [
    #                         {
    #                             "event_name": "FILTER_FILM",
    #                             "genre_name": "Action",
    #                             "year": 2020,
    #                             "has_genre_filter": True,
    #                             "has_year_filter": True,
    #                         },
    #                         {"event_name": "FILM_DETAILS", "movie_name": "Inception"},
    #                     ]
    #                 },
    #                 "reasoning": "This test ensures that filtering by genre and year happens before viewing a specific movie.",
    #             },
    #         }
    #     ],
    # )
]
