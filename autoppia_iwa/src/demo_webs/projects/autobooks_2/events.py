from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue


# Helpers
def _extract_genres(data: dict, key: str = "genres") -> list[str]:
    genres: list[str] = []
    if key in data and isinstance(data[key], list):
        for item in data[key]:
            if isinstance(item, dict):
                if "name" in item:
                    genres.append(str(item.get("name", "")))
            elif isinstance(item, str):
                genres.append(item)
    return genres


def _get_author(data: dict) -> str:
    # Accept either "author" or legacy "director"
    return data.get("author", data.get("director", "")) or ""


def _get_pages(data: dict) -> Any:
    # Accept either "pages" or legacy "duration"
    return data.get("pages", data.get("duration"))


def _matches_list_criteria(values: list[str], crit: CriterionValue, negate: bool = False) -> bool:
    # crit.value can be a str or list; normalize to list of lowercase strings
    val = crit.value
    if isinstance(val, str):
        val_list = [val.lower()]
    elif isinstance(val, list):
        val_list = [str(v).lower() for v in val]
    else:
        return False

    value_lower = [v.lower() for v in values]
    if crit.operator == ComparisonOperator.IN_LIST:
        match = any(v in val_list for v in value_lower)
    elif crit.operator == ComparisonOperator.NOT_IN_LIST:
        match = not any(v in val_list for v in value_lower)
    elif crit.operator == ComparisonOperator.EQUALS:
        match = any(v == val_list[0] for v in value_lower)
    elif crit.operator == ComparisonOperator.NOT_EQUALS:
        match = not any(v == val_list[0] for v in value_lower)
    elif crit.operator == ComparisonOperator.CONTAINS:
        match = any(any(p in v for v in value_lower) for p in val_list)
    elif crit.operator == ComparisonOperator.NOT_CONTAINS:
        match = not any(any(p in v for v in value_lower) for p in val_list)
    else:
        match = False

    return not match if negate else match


# =============================================================================
#                            USER EVENTS
# =============================================================================


class BaseUserEvent(Event, BaseEventValidator):
    event_name: str = "BASE_USER_EVENT"
    username: str

    class ValidationCriteria(BaseModel):
        username: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.username, criteria.username)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BaseUserEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=data.get("username", ""))


class RegistrationEvent(BaseUserEvent):
    """Event triggered when a user registration is completed"""

    event_name: str = "REGISTRATION_BOOK"


class LoginEvent(BaseUserEvent):
    """Event triggered when a user logs in"""

    event_name: str = "LOGIN_BOOK"


class LogoutEvent(BaseUserEvent):
    """Event triggered when a user logs out"""

    event_name: str = "LOGOUT_BOOK"


class EditUserEvent(Event, BaseEventValidator):
    """Event triggered when a user edits their profile"""

    event_name: str = "EDIT_USER_BOOK"
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    location: str | None = None
    website: str | None = None
    favorite_genres: list[str] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        """Criteria for validating edit user events"""

        first_name: str | CriterionValue | None = None
        last_name: str | CriterionValue | None = None
        bio: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        website: str | CriterionValue | None = None
        favorite_genres: str | list[str] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        # Validate favorite_genres
        if criteria.favorite_genres is not None:
            fv = self.favorite_genres
            crit = criteria.favorite_genres

            if isinstance(crit, str):
                if not any(crit.lower() in g.lower() for g in fv):
                    return False
            elif isinstance(crit, list):
                lower_vals = [str(v).lower() for v in crit]
                if not any(g.lower() in lower_vals for g in fv):
                    return False
            elif isinstance(crit, CriterionValue):
                negate = crit.operator in (
                    ComparisonOperator.NOT_IN_LIST,
                    ComparisonOperator.NOT_CONTAINS,
                    ComparisonOperator.NOT_EQUALS,
                )
                if not _matches_list_criteria(fv, crit, negate=negate):
                    return False

        return all(
            [
                self._validate_field(self.first_name, criteria.first_name),
                self._validate_field(self.last_name, criteria.last_name),
                self._validate_field(self.bio, criteria.bio),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.website, criteria.website),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "EditUserEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data

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
        if "favorite_genres" in previous_values and isinstance(previous_values["favorite_genres"], list) and not all(isinstance(item, str) for item in previous_values["favorite_genres"]):
            # If it's not a list of strings, extract the names from objects
            previous_values["favorite_genres"] = [item["name"] if isinstance(item, dict) and "name" in item else str(item) for item in previous_values["favorite_genres"]]

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            bio=data.get("bio"),
            location=data.get("location"),
            website=data.get("website"),
            favorite_genres=favorite_genres,
        )


# =============================================================================
#                           BOOK EVENTS
# =============================================================================


class BookDetailEvent(Event, BaseEventValidator):
    """Event triggered when a book detail page is viewed"""

    event_name: str = "BOOK_DETAIL"

    book_name: str
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                    return False
            else:
                crit = criteria.genre
                if crit.operator == ComparisonOperator.EQUALS:
                    if not any(crit.value.lower() == genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.CONTAINS:
                    if not any(crit.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(crit.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(crit.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in crit.value] for genre in self.book_genres):
                        return False
        return all(
            [
                self._validate_field(self.book_name, criteria.name),
                self._validate_field(self.book_rating, criteria.rating),
                self._validate_field(self.book_year, criteria.year),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookDetailEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = _extract_genres(data, "genres")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_name=data.get("name", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
        )


class ShareBookEvent(BookDetailEvent):
    """Event triggered when a book shared"""

    event_name: str = "SHARE_BOOK"


class OpenPreviewEvent(BookDetailEvent):
    """Event triggered when a book opened"""

    event_name: str = "OPEN_PREVIEW"


class AddToReadingListEvent(BookDetailEvent):
    """Event triggered when a book added to reading list"""

    event_name: str = "ADD_TO_READING_LIST"


class RemoveFromReadingListEvent(BookDetailEvent):
    """Event triggered when a book removed from reading list"""

    event_name: str = "REMOVE_FROM_READING_LIST"


class AddBookEvent(Event, BaseEventValidator):
    """Event triggered when a user adds a new book"""

    event_name: str = "ADD_BOOK"

    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None

    class ValidationCriteria(BaseModel):
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        pages: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                    return False
            else:
                crit = criteria.genre
                if crit.operator == ComparisonOperator.EQUALS:
                    if not any(crit.value.lower() == genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.CONTAINS:
                    if not any(crit.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(crit.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(crit.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in crit.value] for genre in self.book_genres):
                        return False

        return all(
            [
                self._validate_field(self.book_author, criteria.author),
                self._validate_field(self.book_year, criteria.year),
                self._validate_field(self.book_rating, criteria.rating),
                self._validate_field(self.book_pages, criteria.pages),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AddBookEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = _extract_genres(data, "genres")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_author=_get_author(data),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=_get_pages(data),
        )


class EditBookEvent(Event, BaseEventValidator):
    """Event triggered when a user edits an existing book"""

    event_name: str = "EDIT_BOOK"

    book_name: str
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None
    previous_values: dict[str, Any] = Field(default_factory=dict)
    changed_fields: list[str] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        changed_field: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.genre is not None:
            if isinstance(criteria.genre, str):
                if not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                    return False
            else:
                crit = criteria.genre
                if crit.operator == ComparisonOperator.EQUALS:
                    if not any(crit.value.lower() == genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.CONTAINS:
                    if not any(crit.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(crit.value.lower() in genre.lower() for genre in self.book_genres):
                        return False
                elif crit.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(crit.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in crit.value] for genre in self.book_genres):
                        return False
        if criteria.changed_field is not None:
            if isinstance(criteria.changed_field, str):
                if criteria.changed_field not in self.changed_fields:
                    return False
            else:
                crit = criteria.changed_field
                if crit.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(crit.value, list):
                        return False
                    if not any(field in crit.value for field in self.changed_fields):
                        return False
                elif crit.operator == ComparisonOperator.EQUALS:
                    if crit.value not in self.changed_fields:
                        return False
        return all(
            [
                self._validate_field(self.book_name, criteria.name),
                self._validate_field(self.book_author, criteria.author),
                self._validate_field(self.book_year, criteria.year),
                self._validate_field(self.book_rating, criteria.rating),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "EditBookEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = _extract_genres(data, "genres")

        previous_values = data.get("previous_values", {})
        changed = data.get("changed_fields", []) or []

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_name=data.get("name", ""),
            book_author=_get_author(data),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=_get_pages(data),
            previous_values=previous_values,
            changed_fields=list(changed),
        )


class DeleteBookEvent(Event, BaseEventValidator):
    """Event triggered when a user deletes a book"""

    event_name: str = "DELETE_BOOK"

    book_name: str
    book_author: str | None = None
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None
    book_pages: int | None = None

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        year: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.genre is not None:
            if isinstance(criteria.genre, str) and not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                return False
            else:
                crit = criteria.genre
                if (
                    (crit.operator == ComparisonOperator.EQUALS and not any(crit.value.lower() == genre.lower() for genre in self.book_genres))
                    or (crit.operator == ComparisonOperator.CONTAINS and not any(crit.value.lower() in genre.lower() for genre in self.book_genres))
                    or (crit.operator == ComparisonOperator.NOT_CONTAINS and any(crit.value.lower() in genre.lower() for genre in self.book_genres))
                    or (crit.operator == ComparisonOperator.IN_LIST and not any(genre.lower() in [str(v).lower() for v in crit.value] for genre in self.book_genres))
                ):
                    return False
        return all(
            [
                self._validate_field(self.book_name, criteria.name),
                self._validate_field(self.book_author, criteria.author),
                self._validate_field(self.book_year, criteria.year),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DeleteBookEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = _extract_genres(data, "genres")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_name=data.get("name", ""),
            book_author=_get_author(data),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
            book_pages=_get_pages(data),
        )


class SearchBookEvent(Event, BaseEventValidator):
    """Event triggered when a user searches for a book"""

    event_name: str = "SEARCH_BOOK"

    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return self._validate_field(self.query, criteria.query)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchBookEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, query=data.get("query"))


class AddCommentEvent(Event, BaseEventValidator):
    """Event triggered when a user adds a comment to a book"""

    event_name: str = "ADD_COMMENT_BOOK"

    commenter_name: str
    content: str
    book_name: str

    class ValidationCriteria(BaseModel):
        content: str | CriterionValue | None = None
        commenter_name: str | CriterionValue | None = None
        book_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.commenter_name, criteria.commenter_name),
                self._validate_field(self.content, criteria.content),
                self._validate_field(self.book_name, criteria.book_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddCommentEvent":
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
            book_name=book_data.get("name", ""),
        )


# =============================================================================
#                     CONTACT
# =============================================================================


class ContactEvent(Event, BaseEventValidator):
    """Event triggered when a user submits a contact form"""

    event_name: str = "CONTACT_BOOK"

    name: str
    email: str
    subject: str
    message: str

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        email: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        message: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.email, criteria.email),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.message, criteria.message),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ContactEvent":
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


class FilterBookEvent(Event, BaseEventValidator):
    """Event triggered when a user filters books by genre and/or year"""

    event_name: str = "FILTER_BOOK"
    genre_name: str | None = None
    year: int | None = None

    class ValidationCriteria(BaseModel):
        genre_name: str | CriterionValue | None = None
        year: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.genre_name, criteria.genre_name),
                self._validate_field(self.year, criteria.year),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterBookEvent":
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


class PurchaseBookEvent(Event, BaseEventValidator):
    """Event triggered when a user purchases a book"""

    event_name: str = "PURCHASE_BOOK"

    book_name: str
    book_year: int | None = None
    book_genres: list[str] = Field(default_factory=list)
    book_rating: float | None = None

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        genre: str | CriterionValue | None = None
        year: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.genre is not None:
            if isinstance(criteria.genre, str) and not any(criteria.genre.lower() in genre.lower() for genre in self.book_genres):
                return False
            else:
                crit = criteria.genre
                if (
                    (crit.operator == ComparisonOperator.EQUALS and not any(crit.value.lower() == genre.lower() for genre in self.book_genres))
                    or (crit.operator == ComparisonOperator.CONTAINS and not any(crit.value.lower() in genre.lower() for genre in self.book_genres))
                    or (crit.operator == ComparisonOperator.NOT_CONTAINS and any(crit.value.lower() in genre.lower() for genre in self.book_genres))
                    or (crit.operator == ComparisonOperator.IN_LIST and not any(genre.lower() in [str(v).lower() for v in crit.value] for genre in self.book_genres))
                ):
                    return False
        return all(
            [
                self._validate_field(self.book_name, criteria.name),
                self._validate_field(self.book_year, criteria.year),
                self._validate_field(self.book_rating, criteria.rating),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "PurchaseBookEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        genres = _extract_genres(data, "genres")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            book_name=data.get("name", ""),
            book_year=data.get("year"),
            book_genres=genres,
            book_rating=data.get("rating"),
        )


# class ShoppingCartEvent(Event, BaseEventValidator):
#     """Event triggered when a user adds a book to shopping cart"""
#
#     event_name: str = "SHOPPING_CART"
#
#     book_name: str
#     book_year: int | None = None
#     book_genres: list[str] = Field(default_factory=list)
#     book_rating: float | None = None
#
#     class ValidationCriteria(BaseModel):
#         name: str | CriterionValue | None = None
#         genre: str | CriterionValue | None = None
#         year: int | CriterionValue | None = None
#         rating: float | CriterionValue | None = None
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         if not criteria:
#             return True
#         if criteria.genre is not None:
#             genre_values = [genre.lower() for genre in self.book_genres]
#
#             if isinstance(criteria.genre, str):
#                 if not any(criteria.genre.lower() in g for g in genre_values):
#                     return False
#             else:
#                 op = criteria.genre.operator
#                 val = criteria.genre.value
#                 val_lower = val.lower() if isinstance(val, str) else val
#
#                 if op == ComparisonOperator.EQUALS:
#                     if not any(g == val_lower for g in genre_values):
#                         return False
#                 elif op == ComparisonOperator.NOT_EQUALS:
#                     if any(g == val_lower for g in genre_values):
#                         return False
#                 elif op == ComparisonOperator.CONTAINS:
#                     if not any(val_lower in g for g in genre_values):
#                         return False
#                 elif op == ComparisonOperator.NOT_CONTAINS:
#                     if any(val_lower in g for g in genre_values):
#                         return False
#                 elif op == ComparisonOperator.IN_LIST:
#                     val_list = [v.lower() if isinstance(v, str) else v for v in val]
#                     if not any(g in val_list for g in genre_values):
#                         return False
#                 elif op == ComparisonOperator.NOT_IN_LIST:
#                     val_list = [v.lower() if isinstance(v, str) else v for v in val]
#                     if any(g in val_list for g in genre_values):
#                         return False
#         return all(
#             [
#                 self._validate_field(self.book_name, criteria.name),
#                 self._validate_field(self.book_year, criteria.year),
#                 self._validate_field(self.book_rating, criteria.rating),
#             ]
#         )
#
#     @classmethod
#     def parse(cls, backend_event: "BackendEvent") -> "ShoppingCartEvent":
#         base_event = Event.parse(backend_event)
#         data = backend_event.data
#         genres = _extract_genres(data, "genres")
#         return cls(
#             event_name=base_event.event_name,
#             timestamp=base_event.timestamp,
#             web_agent_id=base_event.web_agent_id,
#             user_id=base_event.user_id,
#             book_name=data.get("name", ""),
#             book_year=data.get("year"),
#             book_genres=genres,
#             book_rating=data.get("rating"),
#         )


class ViewCartBookEvent(Event, BaseEventValidator):
    """Event triggered when a user views the shopping cart"""

    event_name: str = "VIEW_CART_BOOK"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewCartBookEvent":
        base_event = Event.parse(backend_event)
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id)


class AddToCartBookEvent(BookDetailEvent):
    """Event triggered when a user adds a book to shopping cart"""

    event_name: str = "ADD_TO_CART_BOOK"


class RemoveFromCartBookEvent(BookDetailEvent):
    """Event triggered when a user removes a book from shopping cart"""

    event_name: str = "REMOVE_FROM_CART_BOOK"


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
    PurchaseBookEvent,
    ShareBookEvent,
    OpenPreviewEvent,
    AddToReadingListEvent,
    RemoveFromReadingListEvent,
    ViewCartBookEvent,
    AddToCartBookEvent,
    RemoveFromCartBookEvent,
]

BACKEND_EVENT_TYPES = {
    "LOGIN_BOOK": LoginEvent,
    "LOGOUT_BOOK": LogoutEvent,
    "REGISTRATION_BOOK": RegistrationEvent,
    "EDIT_USER_BOOK": EditUserEvent,
    "BOOK_DETAIL": BookDetailEvent,
    "SEARCH_BOOK": SearchBookEvent,
    "ADD_BOOK": AddBookEvent,
    "EDIT_BOOK": EditBookEvent,
    "DELETE_BOOK": DeleteBookEvent,
    "ADD_COMMENT_BOOK": AddCommentEvent,
    "CONTACT_BOOK": ContactEvent,
    "FILTER_BOOK": FilterBookEvent,
    "PURCHASE_BOOK": PurchaseBookEvent,
    "SHARE_BOOK": ShareBookEvent,
    "OPEN_PREVIEW": OpenPreviewEvent,
    "ADD_TO_READING_LIST": AddToReadingListEvent,
    "REMOVE_FROM_READING_LIST": RemoveFromReadingListEvent,
    "VIEW_CART_BOOK": ViewCartBookEvent,
    "ADD_TO_CART_BOOK": AddToCartBookEvent,
    "REMOVE_FROM_CART_BOOK": RemoveFromCartBookEvent,
}
