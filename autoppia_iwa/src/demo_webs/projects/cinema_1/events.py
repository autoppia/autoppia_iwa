from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue, validate_criterion

# ================ Event Classes with Nested Validation Criteria ================


class RegistrationEvent(Event):
    """Event triggered when a user registration is completed"""

    username: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating registration events"""

        expected_username: Optional[Union[str, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this registration event meets the criteria

        Args:
            criteria: Optional validation criteria to check against

        Returns:
            True if criteria is met or not provided, False otherwise
        """
        if not criteria:
            return True

        if criteria.expected_username is not None:
            if not validate_criterion(self.username, criteria.expected_username):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "RegistrationEvent":
        """
        Parse a registration event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            RegistrationEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract username from data field
        data = backend_event.get('data', {})
        username = data.get('username', '')

        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class LoginEvent(Event):
    """Event triggered when a user logs in"""

    username: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating login events"""

        expected_username: Optional[Union[str, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this login event meets the criteria

        Args:
            criteria: Optional validation criteria to check against

        Returns:
            True if criteria is met or not provided, False otherwise
        """
        if not criteria:
            return True

        if criteria.expected_username is not None:
            if not validate_criterion(self.username, criteria.expected_username):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "LoginEvent":
        """
        Parse a login event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            LoginEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract username from data field
        data = backend_event.get('data', {})
        username = data.get('username', '')

        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class LogoutEvent(Event):
    """Event triggered when a user logs out"""

    username: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating logout events"""

        expected_username: Optional[Union[str, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this logout event meets the criteria

        Args:
            criteria: Optional validation criteria to check against

        Returns:
            True if criteria is met or not provided, False otherwise
        """
        if not criteria:
            return True

        if criteria.expected_username is not None:
            if not validate_criterion(self.username, criteria.expected_username):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "LogoutEvent":
        """
        Parse a logout event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            LogoutEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract username from data field
        data = backend_event.get('data', {})
        username = data.get('username', '')

        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class FilmDetailEvent(Event):
    """Event triggered when a film detail page is viewed"""

    movie_id: int
    movie_name: str
    movie_director: Optional[str] = None
    movie_year: Optional[int] = None
    movie_genres: List[str] = Field(default_factory=list)
    movie_rating: Optional[float] = None
    movie_duration: Optional[int] = None
    movie_cast: Optional[str] = None

    class ValidationCriteria(BaseModel):
        """
        Validation criteria for FilmDetailEvent
        Supports both simple values and advanced criteria with operators
        """

        name: Optional[Union[str, CriterionValue]] = None
        genre: Optional[Union[str, CriterionValue]] = None
        director: Optional[Union[str, CriterionValue]] = None
        year: Optional[Union[int, CriterionValue]] = None
        rating: Optional[Union[float, CriterionValue]] = None
        duration: Optional[Union[int, CriterionValue]] = None

        class Config:
            title = "Film Detail Validation"
            description = "Validates that a film detail page was viewed with specific attributes"

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate this FilmDetailEvent against the criteria

        Args:
            criteria: Optional validation criteria to check against

        Returns:
            True if all criteria are met or not provided, False otherwise
        """
        if not criteria:
            return True

        # Validate name
        if criteria.name is not None:
            if not validate_criterion(self.movie_name, criteria.name):
                return False

        # Validate genre
        if criteria.genre is not None:
            # Special logic for genres since it's a list
            if isinstance(criteria.genre, str):
                # Default behavior: check if any genre contains the criterion
                if not any(criteria.genre.lower() in genre.lower() for genre in self.movie_genres):
                    return False
            else:
                # Validation with operator for genres
                if criteria.genre.operator == ComparisonOperator.EQUALS:
                    # Must have a genre exactly matching (case insensitive)
                    if not any(criteria.genre.value.lower() == genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.CONTAINS:
                    # Must have a genre containing the value
                    if not any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.NOT_CONTAINS:
                    # Must not have genres containing the value
                    if any(criteria.genre.value.lower() in genre.lower() for genre in self.movie_genres):
                        return False
                elif criteria.genre.operator == ComparisonOperator.IN_LIST:
                    # Value must be a list and at least one genre must be in it
                    if not isinstance(criteria.genre.value, list):
                        return False
                    if not any(genre.lower() in [v.lower() for v in criteria.genre.value] for genre in self.movie_genres):
                        return False

        # Validate director
        if criteria.director is not None:
            if not validate_criterion(self.movie_director, criteria.director):
                return False

        # Validate year
        if criteria.year is not None:
            if not validate_criterion(self.movie_year, criteria.year):
                return False

        # Validate rating
        if criteria.rating is not None:
            if not validate_criterion(self.movie_rating, criteria.rating):
                return False

        # Validate duration
        if criteria.duration is not None:
            if not validate_criterion(self.movie_duration, criteria.duration):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "FilmDetailEvent":
        """
        Parse a film detail event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            FilmDetailEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract movie details from data field
        data = backend_event.get('data', {})

        # Extract genres as a list of strings
        genres = []
        if 'genres' in data and isinstance(data['genres'], list):
            genres = [genre.get('name', '') for genre in data['genres'] if isinstance(genre, dict) and 'name' in genre]

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            movie_id=data.get('id', 0),
            movie_name=data.get('name', ''),
            movie_director=data.get('director', ''),
            movie_year=data.get('year'),
            movie_genres=genres,
            movie_rating=data.get('rating'),
            movie_duration=data.get('duration'),
            movie_cast=data.get('cast', ''),
        )


# ================ Available Events and Use Cases ================
EVENTS = [
    RegistrationEvent,
    LoginEvent,
    LogoutEvent,
    FilmDetailEvent,
]

BACKEND_EVENT_TYPES = {
    'LOGIN': LoginEvent,
    'LOGOUT': LogoutEvent,
    'REGISTRATION': RegistrationEvent,
    'FILM_DETAIL': FilmDetailEvent,
}


# ================ Example Usage ================
"""
# Example 1: Basic validation for a login event
login_criteria = LoginEvent.ValidationCriteria(
    expected_username="testuser"
)

# Example 2: Advanced login validation with operators
login_criteria_advanced = LoginEvent.ValidationCriteria(
    expected_username=CriterionValue(
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
