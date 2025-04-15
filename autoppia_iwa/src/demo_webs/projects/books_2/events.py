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
    def parse(cls, backend_event: "BackendEvent") -> "LogoutEvent":
        """
        Parse a logout event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        username = data.get("username", "")
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class EditUserEvent(Event):
    """Event triggered when a user edits their profile"""

    event_name: str = "EDIT_USER"
    username: str
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

    class ValidationCriteria(BaseModel):
        """Criteria for validating edit user events"""

        username: str | CriterionValue | None = None
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

        # Validate first_name
        if criteria.username is not None and not validate_criterion(self.username, criteria.username):
            return False

        if criteria.first_name is not None and not validate_criterion(self.first_name, criteria.first_name):
            return False

        # Validate last_name
        if criteria.last_name is not None and not validate_criterion(self.last_name, criteria.last_name):
            return False

        # Validate bio
        if criteria.bio is not None and not validate_criterion(self.bio, criteria.bio):
            return False

        # Validate location
        if criteria.location is not None and not validate_criterion(self.location, criteria.location):
            return False

        # Validate website
        if criteria.website is not None and not validate_criterion(self.website, criteria.website):
            return False

        # Validate favorite_genres
        if criteria.favorite_genres is not None:
            if isinstance(criteria.favorite_genres, str):
                # Check if any genre contains the string
                if not any(criteria.favorite_genres.lower() in genre.lower() for genre in self.favorite_genres):
                    return False
            elif isinstance(criteria.favorite_genres, list):
                # Check if any genre in the list matches
                if not any(genre in self.favorite_genres for genre in criteria.favorite_genres):
                    return False
            else:
                # Using operator
                if criteria.favorite_genres.operator == ComparisonOperator.EQUALS:
                    # For EQUALS, match the exact genre
                    if not any(criteria.favorite_genres.value.lower() == genre.lower() for genre in self.favorite_genres):
                        return False
                elif criteria.favorite_genres.operator == ComparisonOperator.CONTAINS:
                    # For CONTAINS, check if any genre contains the substring
                    if not any(criteria.favorite_genres.value.lower() in genre.lower() for genre in self.favorite_genres):
                        return False
                elif criteria.favorite_genres.operator == ComparisonOperator.NOT_CONTAINS:
                    # For NOT_CONTAINS, check that no genre contains the substring
                    if any(criteria.favorite_genres.value.lower() in genre.lower() for genre in self.favorite_genres):
                        return False
                elif criteria.favorite_genres.operator == ComparisonOperator.IN_LIST:
                    # For IN_LIST, check if any genre is in the provided list
                    if not isinstance(criteria.favorite_genres.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.favorite_genres.value] for genre in self.favorite_genres):
                        return False

        return True

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

        # Get the data directly from the backend event
        # Based on the provided example format
        data = backend_event.data

        # Extract favorite genres from the complex format
        favorite_genres = []
        if "favorite_genres" in data and isinstance(data["favorite_genres"], list):
            for genre_item in data["favorite_genres"]:
                if isinstance(genre_item, dict) and "name" in genre_item:
                    favorite_genres.append(genre_item["name"])
                elif isinstance(genre_item, str):
                    favorite_genres.append(genre_item)

        # Handle previous_values properly
        previous_values = data.get("previous_values", {})

        # Process previous_values favorite_genres if present
        if "favorite_genres" in previous_values and isinstance(previous_values["favorite_genres"], list):
            # If it's already a list of strings, keep it
            if all(isinstance(item, str) for item in previous_values["favorite_genres"]):
                pass
            # If it's a list of objects, extract the names
            else:
                previous_values["favorite_genres"] = [item["name"] if isinstance(item, dict) and "name" in item else str(item) for item in previous_values["favorite_genres"]]

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            username=data.get("username"),
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
#                           BOOK EVENTS
# =============================================================================


class BookDetailEvent(Event):
    """Event triggered when a book detail page is viewed"""

    event_name: str = "BOOK_DETAIL"

    book_id: int
    book_name: str
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None
    book_cast: str | None = None

    class ValidationCriteria(BaseModel):
        """
        Validation criteria for BookDetailEvent.
        Supports both simple values and advanced criteria with operators.
        """

        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        duration: int | CriterionValue | None = None

        class Config:
            title = "Book Detail Validation"
            description = "Validates that a book detail page was viewed with specific attributes"

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate this BookDetailEvent against the criteria.
        """
        if not criteria:
            return True
        if criteria.name is not None and not validate_criterion(self.book_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                    return False
            else:
                if criteria.genre.operator == ComparisonOperator.EQUALS:
                    if not any(criteria.genre.value.lower() == genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.genre.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.genre.value] for genre in self.book_genres):
                        return False
        if criteria.author is not None and not validate_criterion(self.book_author, criteria.author):
            return False
        if criteria.year is not None and not validate_criterion(self.book_year, criteria.year):
            return False
        if criteria.rating is not None and not validate_criterion(self.book_rating, criteria.rating):
            return False
        return not (criteria.duration is not None and not validate_criterion(self.book_pages, criteria.duration))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookDetailEvent":
        """
        Parse a book detail event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_id=data.get("id", 0),
            book_name=data.get("name", ""),
            book_author=data.get("director", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=data.get("duration"),
            book_cast=data.get("cast", ""),
        )


class AddBookEvent(Event):
    """Event triggered when a user adds a new book"""

    event_name: str = "ADD_BOOK"

    book_id: int
    book_name: str
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None
    book_cast: str | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating add book events"""

        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        duration: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this add book event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.name is not None and not validate_criterion(self.book_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                    return False
            else:
                if criteria.genre.operator == ComparisonOperator.EQUALS:
                    if not any(criteria.genre.value.lower() == genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.genre.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.genre.value] for genre in self.book_genres):
                        return False
        if criteria.author is not None and not validate_criterion(self.book_author, criteria.author):
            return False
        if criteria.year is not None and not validate_criterion(self.book_year, criteria.year):
            return False
        if criteria.rating is not None and not validate_criterion(self.book_rating, criteria.rating):
            return False
        return not (criteria.duration is not None and not validate_criterion(self.book_pages, criteria.duration))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AddBookEvent":
        """
        Parse an add book event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_id=data.get("id", 0),
            book_name=data.get("name", ""),
            book_author=data.get("director", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=data.get("duration"),
            book_cast=data.get("cast", ""),
        )


class EditBookEvent(Event):
    """Event triggered when a user edits an existing book"""

    event_name: str = "EDIT_BOOK"

    book_id: int
    book_name: str
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None
    book_cast: str | None = None
    previous_values: dict[str, Any] = Field(default_factory=dict)
    changed_fields: list[str] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        """Criteria for validating edit book events"""

        book_id: int | CriterionValue | None = None
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        # Check if a specific field was changed
        changed_field: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this edit book event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.book_id is not None and not validate_criterion(self.book_id, criteria.book_id):
            return False
        if criteria.name is not None and not validate_criterion(self.book_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                    return False
            else:
                if criteria.genre.operator == ComparisonOperator.EQUALS:
                    if not any(criteria.genre.value.lower() == genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.genre.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.genre.value] for genre in self.book_genres):
                        return False
        if criteria.author is not None and not validate_criterion(self.book_author, criteria.author):
            return False
        if criteria.year is not None and not validate_criterion(self.book_year, criteria.year):
            return False
        if criteria.rating is not None and not validate_criterion(self.book_rating, criteria.rating):
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
    def parse(cls, backend_event: "BackendEvent") -> "EditBookEvent":
        """
        Parse an edit book event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = []

            for genre in data["genres"]:
                if isinstance(genre, dict):
                    if "name" in genre:
                        genre_name = genre.get("name", "")
                        genres.append(genre_name)
                elif isinstance(genre, str):
                    genres.append(genre)

        previous_values = data.get("previous_values", {})
        changed_fields = data.get("changed_fields", [])
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_id=data.get("id", 0),
            book_name=data.get("name", ""),
            book_author=data.get("director", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=data.get("duration"),
            book_cast=data.get("cast", ""),
            previous_values=previous_values,
            changed_fields=changed_fields,
        )


class DeleteBookEvent(Event):
    """Event triggered when a user deletes a book"""

    event_name: str = "DELETE_BOOK"

    book_id: int
    book_name: str
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating delete book events"""

        book_id: int | CriterionValue | None = None
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this delete book event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.book_id is not None and not validate_criterion(self.book_id, criteria.book_id):
            return False
        if criteria.name is not None and not validate_criterion(self.book_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str) and not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                return False
            else:
                if (
                    (criteria.genre.operator == ComparisonOperator.EQUALS and not any(criteria.genre.value.lower() == genre.lower() for genre in self.book_genres))
                    or (criteria.genre.operator == ComparisonOperator.CONTAINS and not any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres))
                    or (criteria.genre.operator == ComparisonOperator.NOT_CONTAINS and any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres))
                    or (
                        criteria.genre.operator == ComparisonOperator.IN_LIST
                        and not any(genre.lower() in [v.lower() if isinstance(v, str) else v for v in criteria.genre.value] for genre in self.book_genres)
                    )
                ):
                    return False
        if criteria.author is not None and not validate_criterion(self.book_author, criteria.author):
            return False
        return not (criteria.year is not None and not validate_criterion(self.book_year, criteria.year))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DeleteBookEvent":
        """
        Parse a delete book event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_id=data.get("id", 0),
            book_name=data.get("name", ""),
            book_author=data.get("director", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=data.get("duration"),
        )


class SearchBookEvent(Event):
    """Event triggered when a user searches for a book"""

    event_name: str = "SEARCH_BOOK"

    query: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating search book events"""

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
    def parse(cls, backend_event: BackendEvent) -> "SearchBookEvent":
        """
        Parse a search book event from backend data.
        """

        base_event = Event.parse(backend_event)
        data = backend_event.data
        query = data.get("query")
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, query=query)


class AddCommentEvent(Event):
    """Event triggered when a user adds a comment to a book"""

    event_name: str = "ADD_COMMENT"

    commenter_name: str
    content: str
    book_id: int
    book_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating add comment events"""

        content: str | CriterionValue | None = None
        commenter_name: str | CriterionValue | None = None
        book_id: int | CriterionValue | None = None
        book_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this add comment event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.content is not None and not validate_criterion(self.content, criteria.content):
            return False
        if criteria.commenter_name is not None and not validate_criterion(self.commenter_name, criteria.commenter_name):
            return False
        if criteria.book_id is not None and not validate_criterion(self.book_id, criteria.book_id):
            return False
        return not (criteria.book_name is not None and not validate_criterion(self.book_name, criteria.book_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddCommentEvent":
        """
        Parse an add comment event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        book_data = data.get("book", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            commenter_name=data.get("name", ""),
            content=data.get("content", ""),
            book_id=book_data.get("id", 0),
            book_name=book_data.get("name", ""),
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


class FilterBookEvent(Event):
    """Event triggered when a user filters books by genre and/or year"""

    event_name: str = "FILTER_BOOK"
    genre_name: str | None = None
    year: int | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating filter book events"""

        genre_name: str | CriterionValue | None = None
        year: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this filter book event meets the criteria
        Args:
            criteria: Optional validation criteria to check against
        Returns:
            True if criteria is met or not provided, False otherwise
        """
        if not criteria:
            return True

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

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterBookEvent":
        """
        Parse a filter book event from backend data
        Args:
            backend_event: Event data from the backend API
        Returns:
            FilterBookEvent object populated with data from the backend event
        """
        base_event = Event.parse(backend_event)

        # Extract data
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


class PurchaseBookEvent(Event):
    """Event triggered when a user purchases a book"""

    event_name: str = "PURCHASE_BOOK"

    book_id: int
    book_name: str
    price: float
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating purchase book events"""

        book_id: int | CriterionValue | None = None
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        price: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this purchase book event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.book_id is not None and not validate_criterion(self.book_id, criteria.book_id):
            return False
        if criteria.name is not None and not validate_criterion(self.book_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str) and not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                return False
            else:
                if (
                    (criteria.genre.operator == ComparisonOperator.EQUALS and not any(criteria.genre.value.lower() == genre.lower() for genre in self.book_genres))
                    or (criteria.genre.operator == ComparisonOperator.CONTAINS and not any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres))
                    or (criteria.genre.operator == ComparisonOperator.NOT_CONTAINS and any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres))
                    or (
                        criteria.genre.operator == ComparisonOperator.IN_LIST
                        and not any(genre.lower() in [v.lower() if isinstance(v, str) else v for v in criteria.genre.value] for genre in self.book_genres)
                    )
                ):
                    return False
        if criteria.author is not None and not validate_criterion(self.book_author, criteria.author):
            return False
        if criteria.price is not None and not validate_criterion(self.price, criteria.price):
            return False
        return not (criteria.year is not None and not validate_criterion(self.book_year, criteria.year))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "PurchaseBookEvent":
        """
        Parse a purchase book event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_id=data.get("id", 0),
            book_name=data.get("name", ""),
            price=data.get("price", 0.0),
            book_author=data.get("director", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=data.get("duration"),
        )


class ShoppingCartEvent(Event):
    """Event triggered when a user adds a book to shopping cart"""

    event_name: str = "SHOPPING_CART"

    book_id: int
    book_name: str
    price: float
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating shopping cart events"""

        book_id: int | CriterionValue | None = None
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        price: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this shopping cart event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.book_id is not None and not validate_criterion(self.book_id, criteria.book_id):
            return False
        if criteria.name is not None and not validate_criterion(self.book_name, criteria.name):
            return False
        if criteria.genre is not None:
            if isinstance(criteria.genre, str) and not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                return False
            else:
                if (
                    (criteria.genre.operator == ComparisonOperator.EQUALS and not any(criteria.genre.value.lower() == genre.lower() for genre in self.book_genres))
                    or (criteria.genre.operator == ComparisonOperator.CONTAINS and not any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres))
                    or (criteria.genre.operator == ComparisonOperator.NOT_CONTAINS and any(criteria.genre.value.lower() in genre.lower() for genre in self.book_genres))
                    or (
                        criteria.genre.operator == ComparisonOperator.IN_LIST
                        and not any(genre.lower() in [v.lower() if isinstance(v, str) else v for v in criteria.genre.value] for genre in self.book_genres)
                    )
                ):
                    return False
        if criteria.author is not None and not validate_criterion(self.book_author, criteria.author):
            return False
        if criteria.price is not None and not validate_criterion(self.price, criteria.price):
            return False
        return not (criteria.year is not None and not validate_criterion(self.book_year, criteria.year))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ShoppingCartEvent":
        """
        Parse a shopping cart event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [genre.get("name", "") for genre in data["genres"] if isinstance(genre, dict) and "name" in genre]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_id=data.get("id", 0),
            book_name=data.get("name", ""),
            price=data.get("price", 0.0),
            book_author=data.get("director", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=data.get("duration"),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================


EVENTS = [
    RegistrationEvent,
    LoginEvent,
    LogoutEvent,
    BookDetailEvent,
    SearchBookEvent,
    AddBookEvent,
    EditBookEvent,
    DeleteBookEvent,
    AddCommentEvent,
    ContactEvent,
    EditUserEvent,
    FilterBookEvent,
    ShoppingCartEvent,
    PurchaseBookEvent,
]

BACKEND_EVENT_TYPES = {
    "LOGIN": LoginEvent,
    "LOGOUT": LogoutEvent,
    "REGISTRATION": RegistrationEvent,
    "EDIT_USER": EditUserEvent,
    "BOOK_DETAIL": BookDetailEvent,
    "SEARCH_book": SearchBookEvent,
    "ADD_BOOK": AddBookEvent,
    "EDIT_BOOK": EditBookEvent,
    "DELETE_BOOK": DeleteBookEvent,
    "ADD_COMMENT": AddCommentEvent,
    "CONTACT": ContactEvent,
    "FILTER_BOOK": FilterBookEvent,
    "SHOPPING_CART": ShoppingCartEvent,
    "PURCHASE_BOOK": PurchaseBookEvent,
}
