# -----------------------------------------------------------------------------
# use_cases.py
# -----------------------------------------------------------------------------
from autoppia_iwa.src.demo_webs.classes import UseCase

from .data_utils import fetch_movies_data
from .events import (
    AddCommentEvent,
    AddFilmEvent,
    AddToWatchlistEvent,
    ContactEvent,
    DeleteFilmEvent,
    EditFilmEvent,
    EditUserEvent,
    FilmDetailEvent,
    FilterFilmEvent,
    LoginEvent,
    LogoutEvent,
    RegistrationEvent,
    RemoveFromWatchlistEvent,
    SearchFilmEvent,
    ShareFilmEvent,
    WatchTrailer,
)
from .generation_functions import (
    generate_add_comment_constraints,
    generate_add_film_constraints,
    generate_add_to_watchlist_constraints,
    generate_contact_constraints,
    generate_delete_film_constraints,
    generate_edit_film_constraints,
    generate_edit_profile_constraints,
    generate_film_detail_constraints,
    generate_film_filter_constraints,
    generate_login_constraints,
    generate_logout_constraints,
    generate_registration_constraints,
    generate_remove_from_watchlist_constraints,
    generate_search_film_constraints,
    generate_share_film_constraints,
    generate_watch_trailer_constraints,
)
from .replace_functions import login_and_film_replace_func, login_replace_func, register_replace_func, replace_film_placeholders

STRICT_COPY_INSTRUCTION = "CRITICAL: Copy values EXACTLY as provided in the constraints. Do NOT correct typos, do NOT remove numbers, do NOT truncate or summarize strings, and do NOT 'clean up' names or titles (e.g., if constraint is 'Sofia 4', write 'Sofia 4', NOT 'Sofia'; if it is 'ng', write 'ng', NOT 'an')."


async def _get_movies_data_for_prompts(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """Fetch movies data from API for use in prompt generation."""
    return await fetch_movies_data(seed_value=seed_value, count=count)


def _generate_movie_names_list(movies_data: list[dict]) -> str:
    """Generate a newline-separated list of movie names from movies data."""
    if not movies_data:
        return "No movies available"
    return "\n".join([movie.get("name", "") for movie in movies_data if movie.get("name")])


def _generate_allowed_years_list(movies_data: list[dict]) -> list[int]:
    """Generate a list of unique years from movies data."""
    if not movies_data:
        return []
    return sorted(list(set(movie.get("year") for movie in movies_data if movie.get("year") is not None)))


def _generate_allowed_genres_list(movies_data: list[dict]) -> list[str]:
    """Generate a list of unique genres from movies data."""
    if not movies_data:
        return []
    genres = set()
    for movie in movies_data:
        movie_genres = movie.get("genres", [])
        if isinstance(movie_genres, list):
            genres.update(movie_genres)
        elif isinstance(movie_genres, str):
            genres.add(movie_genres)
    return sorted(list(genres))


###############################################################################
# REGISTRATION_USE_CASE
###############################################################################
REGISTRATION_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (username, email, and password).
2. Explicitly include instruction to register using username equals 'signup_username', email equals 'signup_email' and password equals 'signup_password' (**strictly** containing these identifiers).
3. Be phrased as a request to register or create a new account (e.g., "Please register using...", "Create an account with...", "Sign up using...").
4. {STRICT_COPY_INSTRUCTION}

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
REGISTRATION_USE_CASE = UseCase(
    name="REGISTRATION",
    description="The user fills out the registration form and successfully creates a new account.",
    event=RegistrationEvent,
    event_source_code=RegistrationEvent.get_source_code_of_class(),
    replace_func=register_replace_func,
    constraints_generator=generate_registration_constraints,
    additional_prompt_info=REGISTRATION_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Register where username equals signup_username, email equals signup_email and password equals signup_password",
            "prompt_for_task_generation": "Register where username equals signup_username, email equals signup_email and password equals signup_password",
        },
        {
            "prompt": "Create a new account where username equals signup_username, email equals signup_email and password equals signup_password",
            "prompt_for_task_generation": "Create a new account where username equals signup_username, email equals signup_email and password equals signup_password",
        },
        {
            "prompt": "Fill the registration form where username equals signup_username, email equals signup_email and password equals signup_password",
            "prompt_for_task_generation": "Fill the registration form where username equals signup_username, email equals signup_email and password equals signup_password",
        },
        {
            "prompt": "Sign up for an account where username equals signup_username, email equals signup_email and password equals signup_password",
            "prompt_for_task_generation": "Sign up for an account where username equals signup_username, email equals signup_email and password equals signup_password",
        },
    ],
)

###############################################################################
# LOGIN_USE_CASE
###############################################################################
LOGIN_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include instruction to login using username equals '<username>' and password equals '<password> (**strictly** containing both the username and password placeholders)'.
2. Be phrased as a request to login or sign in.
3. {STRICT_COPY_INSTRUCTION}

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
LOGIN_USE_CASE = UseCase(
    name="LOGIN",
    description="The user fills out the login form and logs in successfully.",
    event=LoginEvent,
    event_source_code=LoginEvent.get_source_code_of_class(),
    replace_func=login_replace_func,
    constraints_generator=generate_login_constraints,
    additional_prompt_info=LOGIN_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Login where username equals <username> and password equals <password>",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>",
        },
        {
            "prompt": "Login with a specific username equals <username> and password equals <password>",
            "prompt_for_task_generation": "Login with a specific username equals <username> and password equals <password>",
        },
        {
            "prompt": "Fill the Login Form where username equals <username> and password equals <password>",
            "prompt_for_task_generation": "Fill the Login Form where username equals <username> and password equals <password>",
        },
        {
            "prompt": "Sign in to the website where username equals <username> and password equals <password>",
            "prompt_for_task_generation": "Sign in to the website where username equals <username> and password equals <password>",
        },
    ],
)

###############################################################################
# LOGOUT_USE_CASE
###############################################################################
LOGOUT_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include instruction to login using username equals '<username>' and password equals '<password> (**strictly** containing both the username and password placeholders)'.
2. Be phrased as a request to login and then logout.
3. {STRICT_COPY_INSTRUCTION}

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""
LOGOUT_USE_CASE = UseCase(
    name="LOGOUT",
    description="The user logs out of the platform after logging in.",
    event=LogoutEvent,
    event_source_code=LogoutEvent.get_source_code_of_class(),
    replace_func=login_replace_func,
    constraints_generator=generate_logout_constraints,
    additional_prompt_info=LOGOUT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Login where username equals <username> and password equals <password>, then logout",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>, then logout",
        },
        {
            "prompt": "Login with a specific username equals <username> and password equals <password>, then sign out from the system",
            "prompt_for_task_generation": "Login with a specific username equals <username> and password equals <password>, then sign out from the system",
        },
        {
            "prompt": "Fill the Login Form where username equals <username> and password equals <password>, once logged in, logout from my account",
            "prompt_for_task_generation": "Fill the Login Form where username equals <username> and password equals <password>, once logged in, logout from my account",
        },
        {
            "prompt": "Sign in to the website where username equals <username> and password equals <password>, after that please log me out",
            "prompt_for_task_generation": "Sign in to the website where username equals <username> and password equals <password>, after that please log me out",
        },
        {
            "prompt": "Authenticate where username equals <username> and password equals <password>, then end my session",
            "prompt_for_task_generation": "Authenticate where username equals <username> and password equals <password>, then end my session",
        },
    ],
)

###############################################################################
# FILM_DETAIL_USE_CASE
###############################################################################


def _get_film_detail_info(movies_data: list[dict]) -> str:
    """Generate film detail info dynamically from API data."""
    _generate_movie_names_list(movies_data)
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (field, operator, and value).
2. Include ONLY the constraints mentioned above - do not add any other criteria.
3. Be phrased as a request to **view details** of a movie (e.g., "Show details for...", "Navigate to the details page for...", "Go to the film page for...").
4. {STRICT_COPY_INSTRUCTION}

For example, if the constraints are "director not_equals Robert Zemeckis AND year greater_than 2010":
- CORRECT: "Show me details about a movie not directed by Robert Zemeckis that was released after 2010"
- INCORRECT: "Show me details about a movie directed by Christopher Nolan" (you added a random director, and missing the year constraint)
- INCORRECT: "Show me details about a movie released after 2010 with a high rating" (adding an extra constraint about rating and missing director)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


FILM_DETAIL_USE_CASE = UseCase(
    name="FILM_DETAIL",
    description="The user explicitly requests to navigate to or go to the details page of a specific movie that meets certain criteria, where they can view information including director, year, genres, rating, duration, and cast.",
    event=FilmDetailEvent,
    event_source_code=FilmDetailEvent.get_source_code_of_class(),
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_film_detail_constraints,
    examples=[
        {
            "prompt": "Navigate to The Matrix movie page",
            "prompt_for_task_generation": "Navigate to <movie> movie page",
        },
        {
            "prompt": "Go to the film details page for Interstellar by Christopher Nolan",
            "prompt_for_task_generation": "Go to the film details page for <movie> by <director>",
        },
        {
            "prompt": "Navigate directly to a sci-fi movie page from 2010",
            "prompt_for_task_generation": "Navigate directly to a <genre> movie page from <year>",
        },
        {
            "prompt": "Go directly to a movie page with rating above 4.5",
            "prompt_for_task_generation": "Go directly to a movie page with rating above <rating>",
        },
        {
            "prompt": "Take me directly to the Pulp Fiction film details page",
            "prompt_for_task_generation": "Take me directly to the <movie> film details page",
        },
        {
            "prompt": "Navigate to a comedy film page less than 100 minutes long",
            "prompt_for_task_generation": "Navigate to a <genre> film page less than <duration> minutes long",
        },
        {
            "prompt": "Go to a film details page from the 90s with Al Pacino",
            "prompt_for_task_generation": "Go to a film details page from the <decade>s with <actor>",
        },
        {
            "prompt": "Navigate me to a horror movie page not directed by Wes Craven",
            "prompt_for_task_generation": "Navigate me to a <genre> movie page not directed by <director>",
        },
        {
            "prompt": "Go directly to the highest-rated James Cameron film page",
            "prompt_for_task_generation": "Go directly to the highest-rated <director> film page",
        },
    ],
)


def _get_add_to_watchlist_info(movies_data: list[dict]) -> str:
    """Generate add to watchlist / remove from watchlist info dynamically from API data (auth required)."""
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with a login instruction using username equals <username> and password equals <password> (exact constraint values).
2. Include ALL constraints mentioned above (field, operator, and value).
3. Include ONLY the constraints mentioned above - do not add any other criteria.
4. Be phrased as a request to **add to watchlist or wishlist** (or **remove from watchlist**) of a movie (e.g., "Add to wishlist...", "Remove from watchlist...").
5. {STRICT_COPY_INSTRUCTION}

For example: "Login with username equals <username> and password equals <password>. Add to wishlist a movie whose name contains 'ng' and that has a rating greater than 3.8."
ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


ADD_TO_WATCHLIST_USE_CASE = UseCase(
    name="ADD_TO_WATCHLIST",
    description="The user explicitly requests to add a film into wishlist of a specific movie that meets certain criteria, where they can view information including director, year, genres, rating, duration, and cast.",
    event=AddToWatchlistEvent,
    event_source_code=AddToWatchlistEvent.get_source_code_of_class(),
    replace_func=login_and_film_replace_func,
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_add_to_watchlist_constraints,
    examples=[
        {
            "prompt": "Add to wishlist The Matrix movie",
            "prompt_for_task_generation": "Add to wishlist <movie> movie",
        },
        {
            "prompt": "Add to wishlist Interstellar by Christopher Nolan",
            "prompt_for_task_generation": "Add to wishlist <movie> by <director>",
        },
        {
            "prompt": "Add to wishlist sci-fi movie from 2010",
            "prompt_for_task_generation": "Add to wishlist <genre> movie from <year>",
        },
        {
            "prompt": "Add to wishlist movie with rating above 4.5",
            "prompt_for_task_generation": "Add to wishlist a movie with rating above <rating>",
        },
        {
            "prompt": "Add to wishlist Pulp Fiction film",
            "prompt_for_task_generation": "Add to wishlist <movie> film",
        },
        {
            "prompt": "Add to wishlist a comedy film less than 100 minutes long",
            "prompt_for_task_generation": "Add to wishlist a <genre> film less than <duration> minutes long",
        },
        {
            "prompt": "Add to wishlist a film from the 90s with Al Pacino",
            "prompt_for_task_generation": "Add to wishlist a film from the <decade>s with <actor>",
        },
        {
            "prompt": "Add to wishlist a horror movie not directed by Wes Craven",
            "prompt_for_task_generation": "Add to wishlist a <genre> movie not directed by <director>",
        },
        {
            "prompt": "Add to wishlist a highest-rated James Cameron film",
            "prompt_for_task_generation": "Add to wishlist a highest-rated <director> film",
        },
    ],
)


REMOVE_FROM_WATCHLIST_USE_CASE = UseCase(
    name="REMOVE_FROM_WATCHLIST",
    description="Remove a film from the watchlist using the provided constraints (used to validate removal events).",
    event=RemoveFromWatchlistEvent,
    event_source_code=RemoveFromWatchlistEvent.get_source_code_of_class(),
    replace_func=login_and_film_replace_func,
    additional_prompt_info=None,  # populated dynamically
    constraints_generator=generate_remove_from_watchlist_constraints,
    examples=[
        {
            "prompt": "Remove the film '<movie>' from the watchlist",
            "prompt_for_task_generation": "Remove the film '<movie>' from the watchlist",
        },
        {
            "prompt": "Remove a <genre> movie directed by <director> from the watchlist",
            "prompt_for_task_generation": "Remove a <genre> movie directed by <director> from the watchlist",
        },
        {
            "prompt": "Remove any movie released before <year> from the watchlist",
            "prompt_for_task_generation": "Remove any movie released before <year> from the watchlist",
        },
    ],
)


def _get_share_film_info(movies_data: list[dict]) -> str:
    """Generate share film info dynamically from API data."""
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (field, operator, and value).
2. Include ONLY the constraints mentioned above - do not add any other criteria.
3. Be phrased as a request to **share a movie** (e.g., "Share this movie...", "I want to share the film...", "Send the film info...").
4. {STRICT_COPY_INSTRUCTION}

For example, if the constraints are "director equals 'James Cameron' AND rating greater_than 4.0":
- CORRECT: "Share a movie directed by James Cameron with a rating higher than 4.0"
- INCORRECT: "Share the details of Titanic" (missing constraints)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


SHARE_FILM_USE_CASE = UseCase(
    name="SHARE_MOVIE",
    description="The user requests to share a specific movie that meets certain criteria, where they can view information including director, year, genres, rating, duration, and cast.",
    event=ShareFilmEvent,
    event_source_code=ShareFilmEvent.get_source_code_of_class(),
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_share_film_constraints,
    examples=[
        {
            "prompt": "Share The Matrix movie",
            "prompt_for_task_generation": "Share <movie> movie",
        },
        {
            "prompt": "Share Interstellar by Christopher Nolan",
            "prompt_for_task_generation": "Share <movie> by <director>",
        },
        {
            "prompt": "Share sci-fi movie from 2010",
            "prompt_for_task_generation": "Share <genre> movie from <year>",
        },
        {
            "prompt": "Share movie with rating above 4.5",
            "prompt_for_task_generation": "Share movie with rating above <rating>",
        },
        {
            "prompt": "Share Pulp Fiction film details",
            "prompt_for_task_generation": "Share <movie> film details",
        },
        {
            "prompt": "Share comedy film less than 100 minutes long",
            "prompt_for_task_generation": "Share <genre> film less than <duration> minutes long",
        },
        {
            "prompt": "Share film details from the 90s with Al Pacino",
            "prompt_for_task_generation": "Share film details from the <decade>s with <actor>",
        },
        {
            "prompt": "Share horror movie not directed by Wes Craven",
            "prompt_for_task_generation": "Share <genre> movie not directed by <director>",
        },
        {
            "prompt": "Share highest-rated James Cameron film",
            "prompt_for_task_generation": "Share highest-rated <director> film",
        },
    ],
)


def _get_watch_trailer_info(movies_data: list[dict]) -> str:
    """Generate watch trailer info dynamically from API data."""
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (field, operator, and value).
2. Include ONLY the constraints mentioned above - do not add any other criteria.
3. Be phrased as a request to **watch the trailer** of a movie (e.g., "Watch trailer for...", "Play the trailer of...", "View the trailer for...").
4. {STRICT_COPY_INSTRUCTION}

For example, if the constraints are "director not_equals Robert Zemeckis AND year greater_than 2010":
- CORRECT: "Watch the trailer for a movie not directed by Robert Zemeckis produced after 2010"
- INCORRECT: "Watch the trailer for Titanic" (missing constraints)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


WATCH_TRAILER_USE_CASE = UseCase(
    name="WATCH_TRAILER",
    description="The user requests to watch the trailer of a specific movie that meets certain criteria, where they can view information including director, year, genres, rating, duration, and cast.",
    event=WatchTrailer,
    event_source_code=WatchTrailer.get_source_code_of_class(),
    additional_prompt_info=None,  # Will be populated dynamically from API
    constraints_generator=generate_watch_trailer_constraints,
    examples=[
        {
            "prompt": "Watch the trailer for The Matrix movie",
            "prompt_for_task_generation": "Watch the trailer for <movie> movie",
        },
        {
            "prompt": "Play the trailer of Interstellar by Christopher Nolan",
            "prompt_for_task_generation": "Play the trailer of <movie> by <director>",
        },
        {
            "prompt": "Watch the trailer for a sci-fi movie from 2010",
            "prompt_for_task_generation": "Watch the trailer for a <genre> movie from <year>",
        },
        {
            "prompt": "View the trailer for a movie with rating above 4.5",
            "prompt_for_task_generation": "View the trailer for a movie with rating above <rating>",
        },
        {
            "prompt": "Watch the trailer for Pulp Fiction film",
            "prompt_for_task_generation": "Watch the trailer for <movie> film",
        },
        {
            "prompt": "Play the trailer of a comedy film less than 100 minutes long",
            "prompt_for_task_generation": "Play the trailer of a <genre> film less than <duration> minutes long",
        },
        {
            "prompt": "Watch the trailer for a film from the 90s with Al Pacino",
            "prompt_for_task_generation": "Watch the trailer for a film from the <decade>s with <actor>",
        },
        {
            "prompt": "View the trailer for a horror movie not directed by Wes Craven",
            "prompt_for_task_generation": "View the trailer for a <genre> movie not directed by <director>",
        },
        {
            "prompt": "Watch the trailer for the highest-rated James Cameron film",
            "prompt_for_task_generation": "Watch the trailer for the highest-rated <director> film",
        },
    ],
)
###############################################################################
# SEARCH_FILM_USE_CASE
###############################################################################
SEARCH_FILM_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Make it EXPLICIT that this is a SEARCH for a movie using clear terms (e.g., "Search for...", "Find a movie...").
2. DO NOT include ANY constraints other than the movie title ('query' field).
3. {STRICT_COPY_INSTRUCTION}

For example:
- CORRECT: "Search for the movie 'Inception'"
- INCORRECT: "Show me details about Inception" (doesn't specify it's a search)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL clearly indicating that it is a simple SEARCH.
"""

SEARCH_FILM_USE_CASE = UseCase(
    name="SEARCH_FILM",
    description="The user searches for a film using a query.",
    event=SearchFilmEvent,
    event_source_code=SearchFilmEvent.get_source_code_of_class(),
    replace_func=replace_film_placeholders,
    constraints_generator=generate_search_film_constraints,
    additional_prompt_info=SEARCH_FILM_INFO,
    examples=[
        {
            "prompt": "Look for the film 'The Shawshank Redemption'",
            "prompt_for_task_generation": "Look for the film '<movie>'",
        },
        {
            "prompt": "Find a movie not called 'Forrest Gump'",
            "prompt_for_task_generation": "Find a movie not called '<movie>'",
        },
        {
            "prompt": "Search for Interestellar in the movie database",
            "prompt_for_task_generation": "Search for '<movie>' in the movie database",
        },
        {
            "prompt": "Look up a movie different from'The Dark Knight'",
            "prompt_for_task_generation": "Look up a movie different from'<movie>'",
        },
    ],
)

###############################################################################
# ADD_FILM_USE_CASE
###############################################################################
ADD_FILM_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with a login instruction using username equals <username> and password equals <password> (exact constraint values).
2. Include ALL constraints mentioned above (field, operator, and value).
3. Include ONLY the constraints mentioned above - do not add any other criteria.
4. Be phrased as a request to add or insert a film (e.g., "Add the movie...", "Insert a new film...", "Register a movie...").
5. {STRICT_COPY_INSTRUCTION}

For example: "Login with username equals <username> and password equals <password>. Add a film whose year equals 2014 and that is directed by Wes Anderson."
ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

ADD_FILM_USE_CASE = UseCase(
    name="ADD_FILM",
    description="The user adds a new film to the system, specifying details such as name, director, year, genres, duration, language, and cast.",
    event=AddFilmEvent,
    event_source_code=AddFilmEvent.get_source_code_of_class(),
    replace_func=login_and_film_replace_func,
    constraints_generator=generate_add_film_constraints,
    additional_prompt_info=ADD_FILM_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add the movie 'The Grand Budapest Hotel' directed by 'Wes Anderson'",
            "prompt_for_task_generation": "Add the movie '<movie>' directed by '<director>'",
        },
        {
            "prompt": "Add the film 'Whiplash' released in 2014",
            "prompt_for_task_generation": "Add the film '<movie>' released in <year>",
        },
        {
            "prompt": "Add the movie 'Spirited Away' with genres Animation, Fantasy, and Adventure",
            "prompt_for_task_generation": "Add the movie '<movie>' with genres <genre>, <genre> and <genre>",
        },
        {
            "prompt": "Add the movie 'Django Unchained' with a duration under 180 minutes",
            "prompt_for_task_generation": "Add the movie '<movie>' with a duration under <duration> minutes",
        },
        {
            "prompt": "Add a movie 'Parasite' that is not in English",
            "prompt_for_task_generation": "Add a movie '<movie>' that is not in <language>",
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
        },
    ],
)

###############################################################################
# EDIT_FILM_USE_CASE
###############################################################################
EDIT_FILM_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Begin with a login instruction using username equals <username> and password equals <password> (exact constraint values).
2. Include ALL constraints mentioned above (field, operator, and value).
3. Explicitly mention the field names (name, director, year, genres, rating, duration, cast). For 'genres', you can also use 'genre' in singular.
4. Use clear operator indicators (e.g., "equals", "contains", "greater than", "less than"). DO NOT use ambiguous words like "including" for a CONTAINS operator; use "contains" instead.
5. Include ONLY the constraints mentioned above - do not add any other criteria.
6. Be phrased as a request to edit or modify a film (e.g., "Edit...", "Update the film...", "Modify...").
7. {STRICT_COPY_INSTRUCTION}

For example: "Login with username equals <username> and password equals <password>. Update the movie where name equals 'The Matrix', set the year equals 1999 and ensure the director contains 'Wachowskis'."
ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria and mentioning the field names.
"""
EDIT_FILM_USE_CASE = UseCase(
    name="EDIT_FILM",
    description="The user edits an existing film, modifying one or more attributes such as name, director, year, genres, rating, duration, or cast.",
    event=EditFilmEvent,
    event_source_code=EditFilmEvent.get_source_code_of_class(),
    replace_func=login_and_film_replace_func,
    constraints_generator=generate_edit_film_constraints,
    additional_prompt_info=EDIT_FILM_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Update the director of The Matrix to Christopher Nolan",
            "prompt_for_task_generation": "Update the director of <movie> to Christopher Nolan",
        },
        {
            "prompt": "Modify the release year of Pulp Fiction to 1994",
            "prompt_for_task_generation": "Modify the release year of <movie> to 1994",
        },
        {
            "prompt": "Add Sci-Fi to the genres of Inception",
            "prompt_for_task_generation": "Add 'Sci-Fi' to the genres of <movie>",
        },
        {
            "prompt": "Change the rating of Interstellar to 4.8",
            "prompt_for_task_generation": "Change the rating of <movie> to 4.8",
        },
        {
            "prompt": "Edit the duration of The Godfather to 175 minutes",
            "prompt_for_task_generation": "Edit the duration of <movie> to 175 minutes",
        },
        {
            "prompt": "Modify the cast of The Shawshank Redemption to include Morgan Freeman",
            "prompt_for_task_generation": "Modify the cast of <movie> to include 'Morgan Freeman'",
        },
    ],
)
###############################################################################
# DELETE_FILM_USE_CASE
###############################################################################
DELETE_FILM_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (field, operator, and value).
2. Include ONLY the constraints mentioned above - do not add any other criteria.
3. Be phrased as a request to delete or remove a film (e.g., "Remove the film...", "Delete...", "Erase...").
4. {STRICT_COPY_INSTRUCTION}

For example, if the constraints are "year greater_than 2014 AND genres contains 'Sci-Fi'":
- CORRECT: "Delete a film whose year is greater than 2014 and that belongs to the 'Sci-Fi' genre."
- INCORRECT: "Delete a film from 2015 with a high rating" (wrong constraints)

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria.
"""

DELETE_FILM_USE_CASE = UseCase(
    name="DELETE_FILM",
    description="The user deletes a film from the system.",
    event=DeleteFilmEvent,
    event_source_code=DeleteFilmEvent.get_source_code_of_class(),
    additional_prompt_info=DELETE_FILM_ADDITIONAL_PROMPT_INFO,
    constraints_generator=generate_delete_film_constraints,
    examples=[
        {
            "prompt": "Remove The Matrix, a film released after 2014, from the database",
            "prompt_for_task_generation": "Remove '<movie>' that was released after <year> from the database",
        },
        {
            "prompt": "Erase all records of Pulp Fiction, a film not directed by Quentin Tarantino",
            "prompt_for_task_generation": "Erase all records of '<movie>' not directed by <director>",
        },
        {
            "prompt": "Permanently delete The Godfather, which has a duration greater than 175 minutes",
            "prompt_for_task_generation": "Permanently delete '<movie>' with duration greater than <duration> minutes",
        },
        {
            "prompt": "Discard Titanic, a film with a rating less than 7.0, from the system",
            "prompt_for_task_generation": "Discard '<movie>' with rating less than <rating>",
        },
        {
            "prompt": "Remove Airplane!, a comedy film released before 1980, from the records",
            "prompt_for_task_generation": "Remove a <genre> film called '<movie>' released before <year>",
        },
        {
            "prompt": "Erase the horror film that is not directed by Wes Craven",
            "prompt_for_task_generation": "Erase a <genre> film not directed by <director>",
        },
        {
            "prompt": "Permanently delete a film featuring Robert De Niro that was released after 2000",
            "prompt_for_task_generation": "Permanently delete a film with cast containing <actor> and released after <year>",
        },
        {
            "prompt": "Discard Inception, a film with a rating greater than 8.0, from the system",
            "prompt_for_task_generation": "Discard '<movie>' with rating greater than <rating>",
        },
        {
            "prompt": "Remove Gladiator, ensuring it was released before 2000",
            "prompt_for_task_generation": "Remove '<movie>' ensuring it was released before <year>",
        },
        {
            "prompt": "Erase all records of Avatar, a film that does not belong to the Action genre",
            "prompt_for_task_generation": "Erase all records of '<movie>' that does not belong to the <genre> genre",
        },
    ],
)


###############################################################################
# CONTACT_USE_CASE
###############################################################################

CONTACT_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (field, operator, and value).
2. Include ONLY the constraints mentioned above - do not add any other fields.
3. Be phrased as a request to fill or submit the contact form (e.g., "Fill out the contact form...", "Submit feedback...").
4. {STRICT_COPY_INSTRUCTION}

For example, if the constraints are "name not_equals 'John' AND message contains 'services'":
- CORRECT: "Fill out the contact form with a name NOT 'John' and a message that contains 'services'."
- INCORRECT: "Fill out the form with name = John" (contradicts constraint)

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
EDIT_PROFILE_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints — every field (username, password, first_name, last_name, bio, location, website, favorite_genres) that appears in the constraints MUST be explicitly mentioned in the prompt with its exact value and operator.
2. Use clear operator indicators (e.g., "equals", "contains"). For ComparisonOperator.CONTAINS, use the word "contains" explicitly (e.g., "website contains 'filmcritics'"). DO NOT use ambiguous words like "include" or "contains the word".
3. Use the EXACT constraint values in the prompt — do NOT replace them with placeholders like <username> or <password>. If the constraint says "username equals <web_agent_id>", the prompt must contain "<web_agent_id>". If it says "password equals password123", the prompt must contain "password123".
4. Begin with a login instruction that states username and password using their exact constraint values (e.g. "Login with username equals <web_agent_id> and password equals password123").
5. Then add an edit-profile instruction that explicitly mentions each remaining constraint field and its exact value and operator.
6. {STRICT_COPY_INSTRUCTION}

Example: constraints "username equals <web_agent_id>, password equals pass456, website contains 'filmcritics', bio contains 'cinema'":
- CORRECT: "Login with username equals <web_agent_id> and password equals pass456. Edit your profile: ensure your website contains 'filmcritics' and your bio contains 'cinema'."
- INCORRECT: "Login and edit your profile." (missing exact values).

ALL prompts must mention every constraint field and use EXACTLY the values and operators from the constraints.
"""

EDIT_USER_PROFILE_USE_CASE = UseCase(
    name="EDIT_USER",
    description="The user edits their profile, modifying one or more attributes such as first name, last name, bio, location, website, or favorite genres. Username and email cannot be edited.",
    event=EditUserEvent,
    event_source_code=EditUserEvent.get_source_code_of_class(),
    replace_func=login_replace_func,
    constraints_generator=generate_edit_profile_constraints,
    additional_prompt_info=EDIT_PROFILE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Login where username equals user1 and password equals pass123. Update your first name to John.",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>. Update your first name to <first_name>.",
        },
        {
            "prompt": "Login where username equals filmfan and password equals pass456. Modify your bio to include your passion for cinema.",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>. Modify your bio to include <bio_content>.",
        },
        {
            "prompt": "Login where username equals movielover and password equals pass789. Change your location to New York, USA.",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>. Change your location to <location>.",
        },
        {
            "prompt": "Login where username equals cinephile and password equals pass321. Edit your website to https://myfilmblog.example.com.",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>. Edit your website to <website>.",
        },
        {
            "prompt": "Login where username equals director101 and password equals pass654. Update your favorite genre to Sci-Fi.",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>. Update your favorite genre to <genre>.",
        },
        {
            "prompt": "Login where username equals producer and password equals pass987. Change your last name to Smith.",
            "prompt_for_task_generation": "Login where username equals <username> and password equals <password>. Change your last name to <last_name>.",
        },
        {
            "prompt": "Login where username equals user<web_agent_id> and password equals password123. Modify your profile to ensure that your location does NOT contain 'a' and that your website contains 'https://cinephileworld.example.org'",
            "prompt_for_task_generation": "Login where username equals user<web_agent_id> and password equals password123. Modify your profile to ensure that your location does NOT contain 'a' and that your website contains <website>",
        },
    ],
)


###############################################################################
# FILTER_FILM_USE_CASE
###############################################################################
def _get_filter_film_info(movies_data: list[dict]) -> str:
    """Generate filter film info dynamically from API data."""
    return f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (field, operator, and value).
2. Include ONLY the constraints mentioned above - do not add any other criteria.
3. Be phrased as a request to filter or browse films (e.g., "Filter...", "Show only...", "Display...", "Browse...").
4. {STRICT_COPY_INSTRUCTION}

For example, if the constraints are "genres equals 'Action' AND year equals 1999":
- CORRECT: "Filter for Action movies released in 1999"
- CORRECT: "Browse films from 1999 in the Action genre."
- INCORRECT: "Show all Action films" (missing year)

ALL prompts must follow this pattern exactly, each phrased slightly differently but ALL containing EXACTLY the same constraint criteria.
"""


FILTER_FILM_USE_CASE = UseCase(
    name="FILTER_FILM",
    description="The user applies filters to search for films by genre and/or year. Includes Filter in the prompt",
    event=FilterFilmEvent,
    event_source_code=FilterFilmEvent.get_source_code_of_class(),
    constraints_generator=generate_film_filter_constraints,
    additional_prompt_info=None,  # Will be populated dynamically from API
    examples=[
        {
            "prompt": "Filter movies released in the year 1994",
            "prompt_for_task_generation": "Filter movies released in the year 1994",
        },
        {
            "prompt": "Filter for Action movies",
            "prompt_for_task_generation": "Filter for Action movies",
        },
        {
            "prompt": "Browse films from 2010 in the Drama genre",
            "prompt_for_task_generation": "Browse films from 2010 in the Drama genre",
        },
        {
            "prompt": "Filter Screen movies from 1999",
            "prompt_for_task_generation": "Filter Screen movies from 1999",
        },
        {
            "prompt": "Filter movie list to Sci-Fi genre",
            "prompt_for_task_generation": "Filter movie list to Sci-Fi genre",
        },
    ],
)

###############################################################################
# ADD_COMMENT_USE_CASE
###############################################################################
ADD_COMMENT_ADDITIONAL_PROMPT_INFO = f"""
CRITICAL REQUIREMENT: EVERY prompt you generate MUST:
1. Include ALL constraints mentioned above (field, operator, and value).
2. Explicitly mention the field names (movie_name, commenter_name, content). For movie_name, you can use "movie_name" or "movie name".
3. Include ONLY the constraints mentioned above - do not add any other fields.
4. Be phrased as a request to add a comment to a movie (e.g., "Add a comment...", "Post a review...").
5. {STRICT_COPY_INSTRUCTION}

For example, if the constraints are "movie_name contains 'Inception' AND content not_contains 'boring'":
- CORRECT: "Add a comment to the movie_name that contains 'Inception' with a content that does NOT contain the word 'boring'."
- CORRECT: "Post a review for the movie name 'Inception' where the content does NOT have 'boring'."
- INCORRECT: "Write a comment about any movie" (missing specific constraints)

ALL prompts must follow this pattern exactly, each phrased slightly differently but containing EXACTLY the same constraint criteria and mentioning the field names.
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
        },
        {
            "prompt": "Write a review for a movie, ensuring the commenter is not John",
            "prompt_for_task_generation": "Write a review for <movie>",
        },
        {
            "prompt": "Post a comment containing the word 'masterpiece'",
            "prompt_for_task_generation": "Post a comment for <movie>",
        },
        {
            "prompt": "Add a comment for a movie not called The Matrix by someone other than John",
            "prompt_for_task_generation": "Add a comment for <movie>",
        },
        {
            "prompt": "Write a detailed review with specific movie, content, and commenter constraints",
            "prompt_for_task_generation": "Write a review for <movie>",
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
    movies_data = dataset
    if movies_data is None:
        movies_data = await _get_movies_data_for_prompts(seed_value=seed_value, count=count or 50)
    if movies_data is None:
        return

    # Update use cases that need movie data
    FILM_DETAIL_USE_CASE.additional_prompt_info = _get_film_detail_info(movies_data)
    ADD_TO_WATCHLIST_USE_CASE.additional_prompt_info = _get_add_to_watchlist_info(movies_data)
    REMOVE_FROM_WATCHLIST_USE_CASE.additional_prompt_info = _get_add_to_watchlist_info(movies_data)
    SHARE_FILM_USE_CASE.additional_prompt_info = _get_share_film_info(movies_data)
    WATCH_TRAILER_USE_CASE.additional_prompt_info = _get_watch_trailer_info(movies_data)
    FILTER_FILM_USE_CASE.additional_prompt_info = _get_filter_film_info(movies_data)


###############################################################################
# FINAL LIST: ALL_USE_CASES
###############################################################################
ALL_USE_CASES = [
    FILM_DETAIL_USE_CASE,
    LOGIN_USE_CASE,
    DELETE_FILM_USE_CASE,
    LOGOUT_USE_CASE,
    FILTER_FILM_USE_CASE,
    SEARCH_FILM_USE_CASE,
    CONTACT_USE_CASE,
    REGISTRATION_USE_CASE,
    ADD_COMMENT_USE_CASE,
    EDIT_FILM_USE_CASE,
    ADD_FILM_USE_CASE,
    EDIT_USER_PROFILE_USE_CASE,
    ADD_TO_WATCHLIST_USE_CASE,
    REMOVE_FROM_WATCHLIST_USE_CASE,
    SHARE_FILM_USE_CASE,
    WATCH_TRAILER_USE_CASE,
]
