from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue, validate_criterion

# =============================================================================
#                            USER EVENTS
# =============================================================================


class RegistrationEvent(Event):
    """Event triggered when a user registration is completed"""

    event_name: str = "REGISTRATION"
    username: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating registration events"""

        username: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this registration event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.username is not None:
            return validate_criterion(self.username, criteria.username)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "RegistrationEvent":
        """
        Parse a registration event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        username = data.get("username", "")
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class LoginEvent(Event):
    """Event triggered when a user logs in"""

    event_name: str = "LOGIN"
    username: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating login events"""

        username: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this login event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.username is not None:
            return validate_criterion(self.username, criteria.username)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "LoginEvent":
        """
        Parse a login event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        username = data.get("username", "")
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class LogoutEvent(Event):
    """Event triggered when a user logs out"""

    event_name: str = "LOGOUT"
    username: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating logout events"""

        username: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this logout event meets the criteria.
        """
        if not criteria:
            return True
        return not (criteria.username is not None and not validate_criterion(self.username, criteria.username))

    @classmethod
    def parse(cls, backend_event: dict[str, Any]) -> "LogoutEvent":
        """
        Parse a logout event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get("data", {})
        username = data.get("username", "")
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class EditUserEvent(Event):
    """Event triggered when a user edits their profile"""

    event_name: str = "EDIT_USER"

    user_id: int | None = None
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str
    profile_id: int | None = None
    bio: str | None = None
    location: str | None = None
    website: str | None = None
    has_profile_pic: bool = False
    favorite_genres: list[str] = Field(default_factory=list)
    previous_values: dict[str, Any] = Field(default_factory=dict)

    class ValidationCriteria(BaseModel):
        """Criteria for validating edit user events"""

        username: str | CriterionValue | None = None
        email: str | CriterionValue | None = None
        name_contains: str | CriterionValue | None = None  # For first or last name
        location: str | CriterionValue | None = None
        bio_contains: str | CriterionValue | None = None
        has_profile_pic: bool | CriterionValue | None = None
        has_favorite_genre: str | CriterionValue | None = None
        has_website: bool | CriterionValue | None = None
        changed_field: str | list[str] | CriterionValue | None = None

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

        # Validate username
        if criteria.username is not None and not validate_criterion(self.username, criteria.username):
            return False

        # Validate email
        if criteria.email is not None and not validate_criterion(self.email, criteria.email):
            return False

        # Validate name contains (check both first and last name)
        if criteria.name_contains is not None:
            full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
            if isinstance(criteria.name_contains, str):
                if criteria.name_contains.lower() not in full_name.lower():
                    return False
            else:
                # Using operator
                if criteria.name_contains.operator == ComparisonOperator.CONTAINS:
                    if criteria.name_contains.value.lower() not in full_name.lower():
                        return False
                elif criteria.name_contains.operator == ComparisonOperator.EQUALS and criteria.name_contains.value.lower() != full_name.lower():
                    return False

        # Validate location
        if criteria.location is not None:
            if self.location is None:
                return False
            if not validate_criterion(self.location, criteria.location):
                return False

        # Validate bio contains
        if criteria.bio_contains is not None:
            if self.bio is None:
                return False
            if isinstance(criteria.bio_contains, str) and criteria.bio_contains.lower() not in self.bio.lower():
                return False
            else:
                # Using operator
                if criteria.bio_contains.operator == ComparisonOperator.CONTAINS and criteria.bio_contains.value.lower() not in self.bio.lower():
                    return False

        # Validate has_profile_pic
        if criteria.has_profile_pic is not None and not validate_criterion(self.has_profile_pic, criteria.has_profile_pic):
            return False

        # Validate has_favorite_genre
        if criteria.has_favorite_genre is not None:
            if isinstance(criteria.has_favorite_genre, str):
                if not any(criteria.has_favorite_genre.lower() in genre.lower() for genre in self.favorite_genres):
                    return False
            else:
                # Using operator
                if criteria.has_favorite_genre.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.has_favorite_genre.value.lower() in genre.lower() for genre in self.favorite_genres):
                        return False
                elif criteria.has_favorite_genre.operator == ComparisonOperator.EQUALS and not any(criteria.has_favorite_genre.value.lower() == genre.lower() for genre in self.favorite_genres):
                    return False

        # Validate has_website
        if criteria.has_website is not None:
            has_website = self.website is not None and self.website != ""
            if not validate_criterion(has_website, criteria.has_website):
                return False

        # Validate changed_field
        if criteria.changed_field is not None:
            # Determine what fields were changed
            changed_fields = []
            for field, value in self.previous_values.items():
                current_value = getattr(self, field, None)
                if current_value != value:
                    changed_fields.append(field)

            if isinstance(criteria.changed_field, str):
                if criteria.changed_field not in changed_fields:
                    return False
            elif isinstance(criteria.changed_field, list):
                if not any(field in changed_fields for field in criteria.changed_field):
                    return False
            else:
                # Using operator
                if criteria.changed_field.operator == ComparisonOperator.IN_LIST:
                    if not any(field in criteria.changed_field.value for field in changed_fields):
                        return False
                elif criteria.changed_field.operator == ComparisonOperator.EQUALS and criteria.changed_field.value not in changed_fields:
                    return False

        return True

    @classmethod
    def parse(cls, backend_event: dict[str, Any]) -> "EditUserEvent":
        """
        Parse an edit user event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            EditUserEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract data
        data = backend_event.get("data", {})

        # Extract favorite genres as a list of strings
        favorite_genres = []
        if "favorite_genres" in data and isinstance(data["favorite_genres"], list):
            favorite_genres = [genre.get("name", "") for genre in data["favorite_genres"] if isinstance(genre, dict) and "name" in genre]

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            profile_id=data.get("profile_id"),
            bio=data.get("bio"),
            location=data.get("location"),
            website=data.get("website"),
            has_profile_pic=data.get("has_profile_pic", False),
            favorite_genres=favorite_genres,
            previous_values=data.get("previous_values", {}),
        )


# =============================================================================
#                           FILM EVENTS
# =============================================================================


class FilmDetailEvent(Event):
    """Event triggered when a film detail page is viewed"""

    event_name: str = "FILM_DETAILS"

    movie_id: int
    movie_name: str
    movie_director: str | None = None
    movie_year: int | None = None
    movie_genres: list[str] = Field(default_factory=list)
    movie_rating: float | None = None
    movie_duration: int | None = None
    movie_cast: str | None = None

    class ValidationCriteria(BaseModel):
        """
        Validation criteria for FilmDetailEvent.
        Supports both simple values and advanced criteria with operators.
        """

        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        director: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        duration: int | CriterionValue | None = None

        class Config:
            title = "Film Detail Validation"
            description = "Validates that a film detail page was viewed with specific attributes"

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate this FilmDetailEvent against the criteria.
        """
        if not criteria:
            return True
        if criteria.name is not None and not validate_criterion(self.movie_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.movie_genres):
                    return False
            else:
                if criteria.genre.operator == ComparisonOperator.EQUALS:
                    if not any(criteria.genre.value.lower() == genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.genre.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.genre.value] for genre in self.movie_genres):
                        return False
        if criteria.director is not None and not validate_criterion(self.movie_director, criteria.director):
            return False
        if criteria.year is not None and not validate_criterion(self.movie_year, criteria.year):
            return False
        if criteria.rating is not None and not validate_criterion(self.movie_rating, criteria.rating):
            return False
        return not (criteria.duration is not None and not validate_criterion(self.movie_duration, criteria.duration))

    @classmethod
    def parse(cls, backend_event: dict[str, Any]) -> "FilmDetailEvent":
        """
        Parse a film detail event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get("data", {})
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            movie_id=data.get("id", 0),
            movie_name=data.get("name", ""),
            movie_director=data.get("director", ""),
            movie_year=data.get("year"),
            movie_genres=genres,
            movie_rating=data.get("rating"),
            movie_duration=data.get("duration"),
            movie_cast=data.get("cast", ""),
        )


class AddFilmEvent(Event):
    """Event triggered when a user adds a new film"""

    event_name: str = "ADD_FILM"

    movie_id: int
    movie_name: str
    movie_director: str | None = None
    movie_year: int | None = None
    movie_genres: list[str] = Field(default_factory=list)
    movie_rating: float | None = None
    movie_duration: int | None = None
    movie_cast: str | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating add film events"""

        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        director: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        duration: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this add film event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.name is not None and not validate_criterion(self.movie_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.movie_genres):
                    return False
            else:
                if criteria.genre.operator == ComparisonOperator.EQUALS:
                    if not any(criteria.genre.value.lower() == genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.genre.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.genre.value] for genre in self.movie_genres):
                        return False
        if criteria.director is not None and not validate_criterion(self.movie_director, criteria.director):
            return False
        if criteria.year is not None and not validate_criterion(self.movie_year, criteria.year):
            return False
        if criteria.rating is not None and not validate_criterion(self.movie_rating, criteria.rating):
            return False
        return not (criteria.duration is not None and not validate_criterion(self.movie_duration, criteria.duration))

    @classmethod
    def parse(cls, backend_event: dict[str, Any]) -> "AddFilmEvent":
        """
        Parse an add film event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get("data", {})
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            movie_id=data.get("id", 0),
            movie_name=data.get("name", ""),
            movie_director=data.get("director", ""),
            movie_year=data.get("year"),
            movie_genres=genres,
            movie_rating=data.get("rating"),
            movie_duration=data.get("duration"),
            movie_cast=data.get("cast", ""),
        )


class EditFilmEvent(Event):
    """Event triggered when a user edits an existing film"""

    event_name: str = "EDIT_FILM"

    movie_id: int
    movie_name: str
    movie_director: str | None = None
    movie_year: int | None = None
    movie_genres: list[str] = Field(default_factory=list)
    movie_rating: float | None = None
    movie_duration: int | None = None
    movie_cast: str | None = None
    previous_values: dict[str, Any] = Field(default_factory=dict)
    changed_fields: list[str] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        """Criteria for validating edit film events"""

        movie_id: int | CriterionValue | None = None
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        director: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        # Check if a specific field was changed
        changed_field: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this edit film event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.movie_id is not None and not validate_criterion(self.movie_id, criteria.movie_id):
            return False
        if criteria.name is not None and not validate_criterion(self.movie_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.movie_genres):
                    return False
            else:
                if criteria.genre.operator == ComparisonOperator.EQUALS:
                    if not any(criteria.genre.value.lower() == genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.genre.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.genre.value] for genre in self.movie_genres):
                        return False
        if criteria.director is not None and not validate_criterion(self.movie_director, criteria.director):
            return False
        if criteria.year is not None and not validate_criterion(self.movie_year, criteria.year):
            return False
        if criteria.rating is not None and not validate_criterion(self.movie_rating, criteria.rating):
            return False
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
    def parse(cls, backend_event: dict[str, Any]) -> "EditFilmEvent":
        """
        Parse an edit film event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get("data", {})
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        previous_values = data.get("previous_values", {})
        changed_fields = data.get("changed_fields", [])
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            movie_id=data.get("id", 0),
            movie_name=data.get("name", ""),
            movie_director=data.get("director", ""),
            movie_year=data.get("year"),
            movie_genres=genres,
            movie_rating=data.get("rating"),
            movie_duration=data.get("duration"),
            movie_cast=data.get("cast", ""),
            previous_values=previous_values,
            changed_fields=changed_fields,
        )


class DeleteFilmEvent(Event):
    """Event triggered when a user deletes a film"""

    event_name: str = "DELETE_FILM"

    movie_id: int
    movie_name: str
    movie_director: str | None = None
    movie_year: int | None = None
    movie_genres: list[str] = Field(default_factory=list)
    movie_rating: float | None = None
    movie_duration: int | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating delete film events"""

        movie_id: int | CriterionValue | None = None
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        director: str | CriterionValue | None = None
        year: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this delete film event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.movie_id is not None and not validate_criterion(self.movie_id, criteria.movie_id):
            return False
        if criteria.name is not None and not validate_criterion(self.movie_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str) and not any(criteria.genre.lower() in genre.lower() for genre in self.movie_genres):
                return False
            else:
                if (
                    (criteria.genre.operator == ComparisonOperator.EQUALS and not any(criteria.genre.value.lower() == genre.lower() for genre in self.movie_genres))
                    or (criteria.genre.operator == ComparisonOperator.CONTAINS and not any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres))
                    or (criteria.genre.operator == ComparisonOperator.NOT_CONTAINS and any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres))
                    or (
                        criteria.genre.operator == ComparisonOperator.IN_LIST
                        and not any(genre.lower() in [v.lower() if isinstance(v, str) else v for v in criteria.genre.value] for genre in self.movie_genres)
                    )
                ):
                    return False
        if criteria.director is not None and not validate_criterion(self.movie_director, criteria.director):
            return False
        return not (criteria.year is not None and not validate_criterion(self.movie_year, criteria.year))

    @classmethod
    def parse(cls, backend_event: dict[str, Any]) -> "DeleteFilmEvent":
        """
        Parse a delete film event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get("data", {})
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            movie_id=data.get("id", 0),
            movie_name=data.get("name", ""),
            movie_director=data.get("director", ""),
            movie_year=data.get("year"),
            movie_genres=genres,
            movie_rating=data.get("rating"),
            movie_duration=data.get("duration"),
        )


class SearchFilmEvent(Event):
    """Event triggered when a user searches for a film"""

    event_name: str = "SEARCH_FILM"

    query: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating search film events"""

        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this search event meets the criteria.
        """
        if not criteria:
            return True

        if criteria.query is not None:
            result = validate_criterion(self.query, criteria.query)
            return result

        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchFilmEvent":
        """
        Parse a search film event from backend data.
        """

        base_event = Event.parse(backend_event)
        data = backend_event.data
        query = data.get("query")
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, query=query)


class AddCommentEvent(Event):
    """Event triggered when a user adds a comment to a film"""

    event_name: str = "ADD_COMMENT"

    commenter_name: str
    content: str
    movie_id: int
    movie_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating add comment events"""

        content_contains: str | CriterionValue | None = None
        commenter_name: str | CriterionValue | None = None
        movie_id: int | CriterionValue | None = None
        movie_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this add comment event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.content_contains is not None and not validate_criterion(
            self.content,
            CriterionValue(value=criteria.content_contains.value if isinstance(criteria.content_contains, CriterionValue) else criteria.content_contains, operator=ComparisonOperator.CONTAINS),
        ):
            return False
        if criteria.commenter_name is not None and not validate_criterion(self.commenter_name, criteria.commenter_name):
            return False
        if criteria.movie_id is not None and not validate_criterion(self.movie_id, criteria.movie_id):
            return False
        return not (criteria.movie_name is not None and not validate_criterion(self.movie_name, criteria.movie_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddCommentEvent":
        """
        Parse an add comment event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = base_event.get("data", {})
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
        """
        Validate if this contact event meets the criteria
        """
        if not criteria:
            return True

        # Validate all fields using the centralized validate_criterion function
        if criteria.name is not None and not validate_criterion(self.name, criteria.name):
            return False

        if criteria.email is not None and not validate_criterion(self.email, criteria.email):
            return False

        if criteria.subject is not None and not validate_criterion(self.subject, criteria.subject):
            return False

        return not (criteria.message is not None and not validate_criterion(self.message, criteria.message))

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

        # Extract data
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


class FilterFilmEvent(Event):
    """Event triggered when a user filters films by genre and/or year"""

    event_name: str = "FILTER_FILM"

    genre_id: int | None = None
    genre_name: str | None = None
    year: int | None = None
    filters_applied: dict[str, bool] = Field(default_factory=dict)

    class ValidationCriteria(BaseModel):
        """Criteria for validating filter film events"""

        genre_id: int | CriterionValue | None = None
        genre_name: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        has_genre_filter: bool | None = None
        has_year_filter: bool | None = None

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

        # Validate genre_id
        if criteria.genre_id is not None:
            if self.genre_id is None:
                return False
            if not validate_criterion(self.genre_id, criteria.genre_id):
                return False

        # Validate genre_name
        if criteria.genre_name is not None:
            if self.genre_name is None:
                return False
            if not validate_criterion(self.genre_name, criteria.genre_name):
                return False

        # Validate year
        if criteria.year is not None:
            if self.year is None:
                return False
            if not validate_criterion(self.year, criteria.year):
                return False

        # Validate has_genre_filter
        if criteria.has_genre_filter is not None:
            has_genre = self.filters_applied.get("genre", False)
            if has_genre != criteria.has_genre_filter:
                return False

        # Validate has_year_filter
        if criteria.has_year_filter is not None:
            has_year = self.filters_applied.get("year", False)
            if has_year != criteria.has_year_filter:
                return False

        return True

    @classmethod
    def parse(cls, backend_event: dict[str, Any]) -> "FilterFilmEvent":
        """
        Parse a filter film event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            FilterFilmEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract data
        data = backend_event.get("data", {})
        genre_data = data.get("genre", {})

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            genre_id=genre_data.get("id") if genre_data else None,
            genre_name=genre_data.get("name") if genre_data else None,
            year=data.get("year"),
            filters_applied=data.get("filters_applied", {}),
        )


# TODO: No sensible, Need to come-up with a new approach
# class CompositeEvent(Event):
#     """Event triggered when a user performs multiple actions in sequence"""
#
#     event_name: str = "COMPOSITE_EVENT"
#     events: list[Event] = Field(default_factory=list)
#
#     class ValidationCriteria(BaseModel):
#         """Criteria for validating composite events"""
#
#         event_criteria: list[dict[str, Any]] = []
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         """
#         Validate if this composite event meets the criteria for all sub-events.
#
#         Args:
#             criteria: Optional validation criteria for each event
#
#         Returns:
#             True if all criteria are met, False otherwise
#         """
#         if not criteria or not criteria.event_criteria:
#             return True
#
#         if len(self.events) != len(criteria.event_criteria):
#             return False  # Ensure criteria match the number of events
#
#         return all(event._validate_criteria(event.__class__.ValidationCriteria(**event_criteria)) for event, event_criteria in zip(self.events, criteria.event_criteria, strict=False))
#
#     @classmethod
#     def parse(cls, backend_event: dict[str, Any]) -> "CompositeEvent":
#         """
#         Parse a composite event from backend data
#
#         Args:
#             backend_event: Event data from the backend API
#
#         Returns:
#             CompositeEvent object populated with data from the backend event
#         """
#         base_event = super().parse(backend_event)
#         event_data = backend_event.get("events", [])
#
#         parsed_events = []
#         for event_dict in event_data:
#             event_class = BACKEND_EVENT_TYPES.get(event_dict.get("event_name"))  # Dynamically get event class
#             if event_class:
#                 parsed_events.append(event_class.parse(event_dict))
#
#         return cls(
#             event_name=base_event.event_name,
#             timestamp=base_event.timestamp,
#             web_agent_id=base_event.web_agent_id,
#             user_id=base_event.user_id,
#             events=parsed_events,
#         )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================


EVENTS = [RegistrationEvent, LoginEvent, LogoutEvent, FilmDetailEvent, SearchFilmEvent, AddFilmEvent, EditFilmEvent, DeleteFilmEvent, AddCommentEvent, ContactEvent, EditUserEvent, FilterFilmEvent]

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
}

# =============================================================================
#                          EXAMPLE USAGE
# =============================================================================
"""
# Example 1: Basic validation for a login event
login_criteria = LoginEvent.ValidationCriteria(
    username="testuser"
)

# Example 2: Advanced login validation with operators
login_criteria_advanced = LoginEvent.ValidationCriteria(
    username=CriterionValue(
        value="testuser",
        operator=ComparisonOperator.EQUALS
    )
)

# Example 3: Movie with rating ≥ 8.0 and runtime < 120 minutes
movie_criteria = FilmDetailEvent.ValidationCriteria(
    rating=CriterionValue(value=8.0, operator=ComparisonOperator.GREATER_EQUAL),
    duration=CriterionValue(value=120, operator=ComparisonOperator.LESS_THAN)
)

# Example 4: Comedy movie directed by Spielberg after 2000
movie_criteria2 = FilmDetailEvent.ValidationCriteria(
    genre="comedy",
    director="Spielberg",
    year=CriterionValue(value=2000, operator=ComparisonOperator.GREATER_THAN)
)
"""
