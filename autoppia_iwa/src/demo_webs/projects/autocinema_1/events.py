from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue, validate_criterion

# =============================================================================
#                            HELPER FUNCTIONS
# =============================================================================


def parse_genres_from_data(data: dict, key: str = "genres") -> list[str]:
    """
    Extract genre names from backend event data.
    Handles both list of strings and list of dicts with 'name' key.

    Args:
        data: Backend event data dictionary
        key: Key to look for in data (default: "genres")

    Returns:
        List of genre names as strings
    """
    genres = []
    if key in data and isinstance(data[key], list):
        for genre_item in data[key]:
            if isinstance(genre_item, dict) and "name" in genre_item:
                genres.append(genre_item["name"])
            elif isinstance(genre_item, str):
                genres.append(genre_item)
    return genres


def validate_genre_criteria(
    movie_genres: list[str],
    criteria_genre: str | CriterionValue | None,
) -> bool:
    """
    Validate genre criteria against a list of movie genres.

    Args:
        movie_genres: List of genre names from the movie
        criteria_genre: Genre criteria (string, CriterionValue, or None)

    Returns:
        True if criteria is met, False otherwise
    """
    if criteria_genre is None:
        return True

    if isinstance(criteria_genre, str):
        return any(criteria_genre.lower() in genre.lower() for genre in movie_genres)

    # Handle CriterionValue
    operator = criteria_genre.operator
    value = criteria_genre.value

    if operator == ComparisonOperator.EQUALS:
        return any(value.lower() == genre.lower() for genre in movie_genres)
    elif operator == ComparisonOperator.CONTAINS:
        return any(value.lower() in genre.lower() for genre in movie_genres)
    elif operator == ComparisonOperator.NOT_CONTAINS:
        return not any(value.lower() in genre.lower() for genre in movie_genres)
    elif operator == ComparisonOperator.IN_LIST:
        if not isinstance(value, list):
            return False
        return any(genre.lower() in [v.lower() for v in value] for genre in movie_genres)
    elif operator == ComparisonOperator.NOT_IN_LIST:
        if not isinstance(value, list):
            return False
        return not any(genre.lower() in [v.lower() for v in value] for genre in movie_genres)

    return False


# =============================================================================
#                            BASE EVENT CLASSES
# =============================================================================


class UserEvent(Event, BaseEventValidator):
    """Base class for events that involve a username"""

    event_name: str = "BASE_USER_EVENT"
    username: str

    class ValidationCriteria(BaseModel):
        """Base validation criteria for user events"""

        username: str | CriterionValue | None = None

    def _validate_username(self, criteria: ValidationCriteria | None) -> bool:
        """Validate username criteria"""
        if criteria is None:
            return True
        return self._validate_field(self.username, criteria.username)

    @classmethod
    def _extract_username(cls, data: dict) -> str:
        """Extract username from backend event data"""
        return data.get("username", "")


class FilmEvent(Event, BaseEventValidator):
    """Base class for film-related events with common fields and validation"""

    event_name: str = "BASE_FILM_EVENT"

    movie_id: int
    movie_name: str
    movie_director: str | None = None
    movie_year: int | None = None
    movie_genres: list[str] = Field(default_factory=list)
    movie_rating: float | None = None
    movie_duration: int | None = None
    movie_cast: str | None = None

    class ValidationCriteria(BaseModel):
        """Base validation criteria for film events"""

        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        director: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        duration: int | CriterionValue | None = None

    def _validate_film_criteria(self, criteria: ValidationCriteria | None) -> bool:
        """Validate common film-related criteria"""
        if criteria is None:
            return True

        # Use BaseEventValidator for simple field validations
        if criteria.name is not None and not self._validate_field(self.movie_name, criteria.name):
            return False
        # Genre validation requires special handling for lists
        if criteria.genre is not None and not validate_genre_criteria(self.movie_genres, criteria.genre):
            return False
        if criteria.director is not None and not self._validate_field(self.movie_director, criteria.director):
            return False
        if criteria.year is not None and not self._validate_field(self.movie_year, criteria.year):
            return False
        if criteria.rating is not None and not self._validate_field(self.movie_rating, criteria.rating):
            return False
        return not (criteria.duration is not None and not self._validate_field(self.movie_duration, criteria.duration))

    @classmethod
    def _extract_film_data(cls, data: dict) -> dict[str, Any]:
        """Extract common film data from backend event"""
        genres = parse_genres_from_data(data, "genres")
        return {
            "movie_id": data.get("id", 0),
            "movie_name": data.get("name", ""),
            "movie_director": data.get("director", ""),
            "movie_year": data.get("year"),
            "movie_genres": genres,
            "movie_rating": data.get("rating"),
            "movie_duration": data.get("duration"),
            "movie_cast": data.get("cast", ""),
        }


# =============================================================================
#                            USER EVENTS
# =============================================================================


class RegistrationEvent(UserEvent):
    """Event triggered when a user registration is completed"""

    event_name: str = "REGISTRATION"

    def _validate_criteria(self, criteria: UserEvent.ValidationCriteria | None = None) -> bool:
        """Validate if this registration event meets the criteria."""
        return self._validate_username(criteria)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "RegistrationEvent":
        """Parse a registration event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        username = UserEvent._extract_username(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=username,
        )


class LoginEvent(UserEvent):
    """Event triggered when a user logs in"""

    event_name: str = "LOGIN"

    def _validate_criteria(self, criteria: UserEvent.ValidationCriteria | None = None) -> bool:
        """Validate if this login event meets the criteria."""
        return self._validate_username(criteria)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "LoginEvent":
        """Parse a login event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        username = UserEvent._extract_username(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=username,
        )


class LogoutEvent(UserEvent):
    """Event triggered when a user logs out"""

    event_name: str = "LOGOUT"

    def _validate_criteria(self, criteria: UserEvent.ValidationCriteria | None = None) -> bool:
        """Validate if this logout event meets the criteria."""
        return self._validate_username(criteria)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "LogoutEvent":
        """Parse a logout event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        username = UserEvent._extract_username(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=username,
        )


class EditUserEvent(UserEvent):
    """Event triggered when a user edits their profile"""

    event_name: str = "EDIT_USER"
    first_name: str | None = None
    last_name: str | None = None
    email: str
    bio: str | None = None
    location: str | None = None
    website: str | None = None
    profile_id: int | None = None
    has_profile_pic: bool = False
    favorite_genres: list[str] = Field(default_factory=list)
    previous_values: dict[str, Any] = Field(default_factory=dict)

    class ValidationCriteria(UserEvent.ValidationCriteria):
        """Criteria for validating edit user events"""

        first_name: str | CriterionValue | None = None
        last_name: str | CriterionValue | None = None
        bio: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        website: str | CriterionValue | None = None
        favorite_genres: str | list[str] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this edit user event meets the criteria

        Args:
            criteria: Optional validation criteria to check against

        Returns:
            True if criteria is met or not provided, False otherwise
        """
        if not criteria:
            return True

        # Validate username using base class method
        if not self._validate_username(criteria):
            return False

        # Validate simple fields using BaseEventValidator
        field_validations = [
            (criteria.first_name, self.first_name),
            (criteria.last_name, self.last_name),
            (criteria.bio, self.bio),
            (criteria.location, self.location),
            (criteria.website, self.website),
        ]
        for criterion_value, field_value in field_validations:
            if criterion_value is not None and not self._validate_field(field_value, criterion_value):
                return False

        # Validate favorite_genres using the shared helper
        return not (criteria.favorite_genres is not None and not validate_genre_criteria(self.favorite_genres, criteria.favorite_genres))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "EditUserEvent":
        """
        Parse an edit user event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            EditUserEvent object populated with data from the backend event
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data

        # Extract favorite genres using helper function
        favorite_genres = parse_genres_from_data(data, "favorite_genres")

        # Handle previous_values properly
        previous_values = data.get("previous_values", {})

        # Process previous_values favorite_genres if present
        if "favorite_genres" in previous_values and isinstance(previous_values["favorite_genres"], list) and not all(isinstance(item, str) for item in previous_values["favorite_genres"]):
            # If it's a list of objects, extract the names
            previous_values["favorite_genres"] = [item["name"] if isinstance(item, dict) and "name" in item else str(item) for item in previous_values["favorite_genres"]]

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=UserEvent._extract_username(data),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email", ""),
            bio=data.get("bio"),
            location=data.get("location"),
            website=data.get("website"),
            favorite_genres=favorite_genres,
            previous_values=previous_values,
        )


# =============================================================================
#                           FILM EVENTS
# =============================================================================


class FilmDetailEvent(FilmEvent):
    """Event triggered when a film detail page is viewed"""

    event_name: str = "FILM_DETAIL"

    class ValidationCriteria(FilmEvent.ValidationCriteria):
        """
        Validation criteria for FilmDetailEvent.
        Supports both simple values and advanced criteria with operators.
        """

        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate this FilmDetailEvent against the criteria."""
        return self._validate_film_criteria(criteria)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilmDetailEvent":
        """Parse a film detail event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        film_data = FilmEvent._extract_film_data(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **film_data,
        )


class AddToWatchlistEvent(FilmDetailEvent):
    event_name: str = "ADD_TO_WATCHLIST"


class AddProductToWatchlistEvent(FilmDetailEvent):
    """Event triggered when a user adds a specific film to a watchlist-like collection."""

    event_name: str = "ADD_PRODUCT_TO_WATCHLIST"


class RateFilmEvent(FilmEvent):
    """Event triggered when a user rates a film."""

    event_name: str = "RATE_FILM"
    new_rating: float | None = None

    class ValidationCriteria(FilmEvent.ValidationCriteria):
        rating_value: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.rating_value is not None and not self._validate_field(self.new_rating, criteria.rating_value):
            return False
        return self._validate_film_criteria(criteria)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "RateFilmEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        film_data = FilmEvent._extract_film_data(data)
        rating_value = data.get("new_rating", data.get("rating"))
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            new_rating=rating_value,
            **film_data,
        )


class RemoveFromWatchlistEvent(FilmDetailEvent):
    """Event triggered when a user removes a film from a watchlist."""

    event_name: str = "REMOVE_FROM_WATCHLIST"


class ShareFilmEvent(FilmDetailEvent):
    event_name: str = "SHARE_MOVIE"


class WatchTrailer(FilmDetailEvent):
    event_name: str = "WATCH_TRAILER"


class AddFilmEvent(FilmEvent):
    """Event triggered when a user adds a new film"""

    event_name: str = "ADD_FILM"

    class ValidationCriteria(FilmEvent.ValidationCriteria):
        """Criteria for validating add film events"""

        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate if this add film event meets the criteria."""
        return self._validate_film_criteria(criteria)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AddFilmEvent":
        """Parse an add film event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        film_data = FilmEvent._extract_film_data(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **film_data,
        )


class EditFilmEvent(FilmEvent):
    """Event triggered when a user edits an existing film"""

    event_name: str = "EDIT_FILM"
    previous_values: dict[str, Any] = Field(default_factory=dict)
    changed_fields: list[str] = Field(default_factory=list)

    class ValidationCriteria(FilmEvent.ValidationCriteria):
        """Criteria for validating edit film events"""

        movie_id: int | CriterionValue | None = None
        changed_field: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate if this edit film event meets the criteria."""
        if not criteria:
            return True

        # Validate movie_id using BaseEventValidator
        if criteria.movie_id is not None and not self._validate_field(self.movie_id, criteria.movie_id):
            return False

        # Validate common film criteria
        if not self._validate_film_criteria(criteria):
            return False

        # Validate changed_field
        if criteria.changed_field is not None:
            if isinstance(criteria.changed_field, str):
                if criteria.changed_field not in self.changed_fields:
                    return False
            else:
                if criteria.changed_field.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.changed_field.value, list):
                        return False
                    if not any(field in criteria.changed_field.value for field in self.changed_fields):
                        return False
                elif criteria.changed_field.operator == ComparisonOperator.EQUALS:
                    if criteria.changed_field.value not in self.changed_fields:
                        return False

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "EditFilmEvent":
        """Parse an edit film event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        film_data = FilmEvent._extract_film_data(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            previous_values=data.get("previous_values", {}),
            changed_fields=data.get("changed_fields", []),
            **film_data,
        )


class DeleteFilmEvent(FilmEvent):
    """Event triggered when a user deletes a film"""

    event_name: str = "DELETE_FILM"

    class ValidationCriteria(FilmEvent.ValidationCriteria):
        """Criteria for validating delete film events"""

        movie_id: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate if this delete film event meets the criteria."""
        if not criteria:
            return True

        # Validate movie_id using BaseEventValidator
        if criteria.movie_id is not None and not self._validate_field(self.movie_id, criteria.movie_id):
            return False

        # Validate common film criteria (name, genre, director, year)
        # Note: rating and duration are not validated for delete events
        if criteria.name is not None and not self._validate_field(self.movie_name, criteria.name):
            return False
        if criteria.genre is not None and not validate_genre_criteria(self.movie_genres, criteria.genre):
            return False
        if criteria.director is not None and not self._validate_field(self.movie_director, criteria.director):
            return False
        return not (criteria.year is not None and not self._validate_field(self.movie_year, criteria.year))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DeleteFilmEvent":
        """Parse a delete film event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        film_data = FilmEvent._extract_film_data(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **film_data,
        )


class SearchFilmEvent(Event, BaseEventValidator):
    """Event triggered when a user searches for a film"""

    event_name: str = "SEARCH_FILM"
    query: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating search film events"""

        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate if this search event meets the criteria."""
        if not criteria:
            return True
        return self._validate_field(self.query, criteria.query)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchFilmEvent":
        """Parse a search film event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=data.get("query", ""),
        )


class AddCommentEvent(Event):
    """Event triggered when a user adds a comment to a film"""

    event_name: str = "ADD_COMMENT"
    commenter_name: str
    content: str
    movie_id: int
    movie_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating add comment events"""

        content: str | CriterionValue | None = None
        commenter_name: str | CriterionValue | None = None
        movie_id: int | CriterionValue | None = None
        movie_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate if this add comment event meets the criteria."""
        if not criteria:
            return True

        field_validations = [
            (criteria.content, self.content),
            (criteria.commenter_name, self.commenter_name),
            (criteria.movie_id, self.movie_id),
            (criteria.movie_name, self.movie_name),
        ]

        return all(not (criterion_value is not None and not validate_criterion(field_value, criterion_value)) for criterion_value, field_value in field_validations)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddCommentEvent":
        """Parse an add comment event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        movie_data = data.get("movie", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            commenter_name=data.get("name", ""),
            content=data.get("content", ""),
            movie_id=movie_data.get("id", 0),
            movie_name=movie_data.get("name", ""),
        )


# =============================================================================
#                     CONTACT
# =============================================================================


class ContactEvent(Event):
    """Event triggered when a user submits a contact form"""

    event_name: str = "CONTACT"
    name: str
    email: str
    subject: str
    message: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating contact events"""

        name: str | CriterionValue | None = None
        email: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        message: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate if this contact event meets the criteria."""
        if not criteria:
            return True

        field_validations = [
            (criteria.name, self.name),
            (criteria.email, self.email),
            (criteria.subject, self.subject),
            (criteria.message, self.message),
        ]

        return all(not (criterion_value is not None and not validate_criterion(field_value, criterion_value)) for criterion_value, field_value in field_validations)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ContactEvent":
        """
        Parse a contact event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            ContactEvent object populated with data from the backend event
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("name", ""),
            email=data.get("email", ""),
            subject=data.get("subject", ""),
            message=data.get("message", ""),
        )


class FilterFilmEvent(Event, BaseEventValidator):
    """Event triggered when a user filters films by genre and/or year"""

    event_name: str = "FILTER_FILM"
    genre_name: str | None = None
    year: int | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating filter film events"""

        genre_name: str | CriterionValue | None = None
        year: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this filter film event meets the criteria

        Args:
            criteria: Optional validation criteria to check against

        Returns:
            True if criteria is met or not provided, False otherwise
        """
        if not criteria:
            return True

        # Validate genre_name using BaseEventValidator
        if criteria.genre_name is not None and (self.genre_name is None or not self._validate_field(self.genre_name, criteria.genre_name)):
            return False

        # Validate year using BaseEventValidator
        return not (criteria.year is not None and (self.year is None or not self._validate_field(self.year, criteria.year)))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterFilmEvent":
        """
        Parse a filter film event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            FilterFilmEvent object populated with data from the backend event
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genre_data = data.get("genre", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            genre_name=genre_data.get("name") if genre_data else None,
            year=data.get("year"),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================


EVENTS = [
    RegistrationEvent,
    LoginEvent,
    LogoutEvent,
    FilmDetailEvent,
    SearchFilmEvent,
    AddFilmEvent,
    EditFilmEvent,
    DeleteFilmEvent,
    AddCommentEvent,
    ContactEvent,
    EditUserEvent,
    FilterFilmEvent,
    WatchTrailer,
    ShareFilmEvent,
    AddToWatchlistEvent,
    AddProductToWatchlistEvent,
    RateFilmEvent,
    RemoveFromWatchlistEvent,
]

BACKEND_EVENT_TYPES = {
    "LOGIN": LoginEvent,
    "LOGOUT": LogoutEvent,
    "REGISTRATION": RegistrationEvent,
    "EDIT_USER": EditUserEvent,
    "FILM_DETAIL": FilmDetailEvent,
    "SEARCH_FILM": SearchFilmEvent,
    "ADD_FILM": AddFilmEvent,
    "EDIT_FILM": EditFilmEvent,
    "DELETE_FILM": DeleteFilmEvent,
    "ADD_COMMENT": AddCommentEvent,
    "CONTACT": ContactEvent,
    "FILTER_FILM": FilterFilmEvent,
    "ADD_TO_WATCHLIST": AddToWatchlistEvent,
    "ADD_PRODUCT_TO_WATCHLIST": AddProductToWatchlistEvent,
    "RATE_FILM": RateFilmEvent,
    "REMOVE_FROM_WATCHLIST": RemoveFromWatchlistEvent,
    "SHARE_MOVIE": ShareFilmEvent,
    "WATCH_TRAILER": WatchTrailer,
}
