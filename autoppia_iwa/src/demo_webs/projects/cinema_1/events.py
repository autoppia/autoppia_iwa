import re
from typing import Optional

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.cinema_1.models import Movie
from autoppia_iwa.src.demo_webs.projects.events import Event

# ================ Event Classes with Nested Validation Criteria ================


class RegistrationEvent(Event):
    """Event triggered when a user registration is completed"""


class LoginEvent(Event):
    """Event triggered when a user logs in"""

    username: str


class LogoutEvent(Event):
    """Event triggered when a user logs in"""

    username: str


class FilmDetailEvent(Event):
    """Event triggered when a film detail page is viewed"""

    movie: Movie

    class ValidationCriteria(BaseModel):
        """Validation criteria for FilmDetailEvent"""

        name: Optional[str] = None
        genre: Optional[str] = None
        director: Optional[str] = None
        year: Optional[int] = None

        class Config:
            title = "Film Detail Validation"
            description = "Validates that a film detail page was viewed with specific attributes"

    def validate_criteria(self, criteria: ValidationCriteria) -> bool:
        """Validate this FilmDetailEvent against the criteria"""
        if not super().validate_criteria():
            return False

        # Check movie attributes (exact matches only)
        if criteria.name and self.movie.name.lower() != criteria.name.lower():
            return False

        if criteria.genre:
            # Handle genre being a M2M field
            movie_genres = [g.name.lower() for g in self.movie.genres.all()]
            if criteria.genre.lower() not in movie_genres:
                return False

        if criteria.director and self.movie.director and self.movie.director.lower() != criteria.director.lower():
            return False

        # Check year if specified (exact match only)
        if criteria.year is not None and self.movie.year != criteria.year:
            return False

        return True


class SearchEvent(Event):
    """Event triggered when a search is performed"""

    query: str

    class ValidationCriteria(Event.ValidationCriteria):
        """Validation criteria for SearchEvent"""

        query: Optional[str] = None
        match_type: str = "exact"  # Default to exact matching

        class Config:
            title = "Search Validation"
            description = "Validates that a search was performed with specific query"

    def validate_criteria(self, criteria: ValidationCriteria) -> bool:
        """Validate this SearchEvent against the criteria"""
        if not super().validate_criteria():
            return False

        if not criteria.query:
            return True

        # Match query based on match_type
        if criteria.match_type == "exact":
            return self.query.lower() == criteria.query.lower()
        elif criteria.match_type == "contains":
            return criteria.query.lower() in self.query.lower()
        elif criteria.match_type == "regex":
            return bool(re.search(criteria.query, self.query))

        return False


# ================ Available Events and Use Cases ================
EVENTS = [
    RegistrationEvent,
    LoginEvent,
    LogoutEvent,
    FilmDetailEvent,
    SearchEvent,
]
