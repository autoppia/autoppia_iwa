from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue, validate_criterion

# =============================================================================
#                            USER EVENTS
# =============================================================================


class RegistrationEvent(Event):
    """Event triggered when a user registration is completed"""

    username: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating registration events"""

        expected_username: Optional[Union[str, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this registration event meets the criteria.
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
        Parse a registration event from backend data.
        """
        base_event = super().parse(backend_event)
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
        Validate if this login event meets the criteria.
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
        Parse a login event from backend data.
        """
        base_event = super().parse(backend_event)
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
        Validate if this logout event meets the criteria.
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
        Parse a logout event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get('data', {})
        username = data.get('username', '')
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class EditUserEvent(Event):
    """Event triggered when a user edits their profile"""

    user_id: Optional[int] = None
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    profile_id: Optional[int] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    has_profile_pic: bool = False
    favorite_genres: List[str] = Field(default_factory=list)
    previous_values: Dict[str, Any] = Field(default_factory=dict)

    class ValidationCriteria(BaseModel):
        """Criteria for validating edit user events"""

        username: Optional[Union[str, CriterionValue]] = None
        email: Optional[Union[str, CriterionValue]] = None
        name_contains: Optional[Union[str, CriterionValue]] = None  # For first or last name
        location: Optional[Union[str, CriterionValue]] = None
        bio_contains: Optional[Union[str, CriterionValue]] = None
        has_profile_pic: Optional[Union[bool, CriterionValue]] = None
        has_favorite_genre: Optional[Union[str, CriterionValue]] = None
        has_website: Optional[Union[bool, CriterionValue]] = None
        changed_field: Optional[Union[str, List[str], CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
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
        if criteria.username is not None:
            if not validate_criterion(self.username, criteria.username):
                return False

        # Validate email
        if criteria.email is not None:
            if not validate_criterion(self.email, criteria.email):
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
                elif criteria.name_contains.operator == ComparisonOperator.EQUALS:
                    if criteria.name_contains.value.lower() != full_name.lower():
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
            if isinstance(criteria.bio_contains, str):
                if criteria.bio_contains.lower() not in self.bio.lower():
                    return False
            else:
                # Using operator
                if criteria.bio_contains.operator == ComparisonOperator.CONTAINS:
                    if criteria.bio_contains.value.lower() not in self.bio.lower():
                        return False

        # Validate has_profile_pic
        if criteria.has_profile_pic is not None:
            if not validate_criterion(self.has_profile_pic, criteria.has_profile_pic):
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
                elif criteria.has_favorite_genre.operator == ComparisonOperator.EQUALS:
                    if not any(criteria.has_favorite_genre.value.lower() == genre.lower() for genre in self.favorite_genres):
                        return False

        # Validate has_website
        if criteria.has_website is not None:
            has_website = self.website is not None and self.website != ''
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
                elif criteria.changed_field.operator == ComparisonOperator.EQUALS:
                    if criteria.changed_field.value not in changed_fields:
                        return False

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "EditUserEvent":
        """
        Parse an edit user event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            EditUserEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract data
        data = backend_event.get('data', {})

        # Extract favorite genres as a list of strings
        favorite_genres = []
        if 'favorite_genres' in data and isinstance(data['favorite_genres'], list):
            favorite_genres = [genre.get('name', '') for genre in data['favorite_genres'] if isinstance(genre, dict) and 'name' in genre]

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=data.get('username', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            profile_id=data.get('profile_id'),
            bio=data.get('bio'),
            location=data.get('location'),
            website=data.get('website'),
            has_profile_pic=data.get('has_profile_pic', False),
            favorite_genres=favorite_genres,
            previous_values=data.get('previous_values', {}),
        )


# =============================================================================
#                           FILM EVENTS
# =============================================================================


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
        Validation criteria for FilmDetailEvent.
        Supports both simple values and advanced criteria with operators.
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
        Validate this FilmDetailEvent against the criteria.
        """
        if not criteria:
            return True
        if criteria.name is not None:
            if not validate_criterion(self.movie_name, criteria.name):
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
        if criteria.director is not None:
            if not validate_criterion(self.movie_director, criteria.director):
                return False
        if criteria.year is not None:
            if not validate_criterion(self.movie_year, criteria.year):
                return False
        if criteria.rating is not None:
            if not validate_criterion(self.movie_rating, criteria.rating):
                return False
        if criteria.duration is not None:
            if not validate_criterion(self.movie_duration, criteria.duration):
                return False
        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "FilmDetailEvent":
        """
        Parse a film detail event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get('data', {})
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


class AddFilmEvent(Event):
    """Event triggered when a user adds a new film"""

    movie_id: int
    movie_name: str
    movie_director: Optional[str] = None
    movie_year: Optional[int] = None
    movie_genres: List[str] = Field(default_factory=list)
    movie_rating: Optional[float] = None
    movie_duration: Optional[int] = None
    movie_cast: Optional[str] = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating add film events"""

        name: Optional[Union[str, CriterionValue]] = None
        genre: Optional[Union[str, CriterionValue]] = None
        director: Optional[Union[str, CriterionValue]] = None
        year: Optional[Union[int, CriterionValue]] = None
        rating: Optional[Union[float, CriterionValue]] = None
        duration: Optional[Union[int, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this add film event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.name is not None:
            if not validate_criterion(self.movie_name, criteria.name):
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
        if criteria.director is not None:
            if not validate_criterion(self.movie_director, criteria.director):
                return False
        if criteria.year is not None:
            if not validate_criterion(self.movie_year, criteria.year):
                return False
        if criteria.rating is not None:
            if not validate_criterion(self.movie_rating, criteria.rating):
                return False
        if criteria.duration is not None:
            if not validate_criterion(self.movie_duration, criteria.duration):
                return False
        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "AddFilmEvent":
        """
        Parse an add film event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get('data', {})
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


class EditFilmEvent(Event):
    """Event triggered when a user edits an existing film"""

    movie_id: int
    movie_name: str
    movie_director: Optional[str] = None
    movie_year: Optional[int] = None
    movie_genres: List[str] = Field(default_factory=list)
    movie_rating: Optional[float] = None
    movie_duration: Optional[int] = None
    movie_cast: Optional[str] = None
    previous_values: Dict[str, Any] = Field(default_factory=dict)
    changed_fields: List[str] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        """Criteria for validating edit film events"""

        movie_id: Optional[Union[int, CriterionValue]] = None
        name: Optional[Union[str, CriterionValue]] = None
        genre: Optional[Union[str, CriterionValue]] = None
        director: Optional[Union[str, CriterionValue]] = None
        year: Optional[Union[int, CriterionValue]] = None
        rating: Optional[Union[float, CriterionValue]] = None
        changed_field: Optional[Union[str, CriterionValue]] = None  # Check if a specific field was changed

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this edit film event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.movie_id is not None:
            if not validate_criterion(self.movie_id, criteria.movie_id):
                return False
        if criteria.name is not None:
            if not validate_criterion(self.movie_name, criteria.name):
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
        if criteria.director is not None:
            if not validate_criterion(self.movie_director, criteria.director):
                return False
        if criteria.year is not None:
            if not validate_criterion(self.movie_year, criteria.year):
                return False
        if criteria.rating is not None:
            if not validate_criterion(self.movie_rating, criteria.rating):
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
    def parse(cls, backend_event: Dict[str, Any]) -> "EditFilmEvent":
        """
        Parse an edit film event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get('data', {})
        genres = []
        if 'genres' in data and isinstance(data['genres'], list):
            genres = [genre.get('name', '') for genre in data['genres'] if isinstance(genre, dict) and 'name' in genre]
        previous_values = data.get('previous_values', {})
        changed_fields = data.get('changed_fields', [])
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
            previous_values=previous_values,
            changed_fields=changed_fields,
        )


class DeleteFilmEvent(Event):
    """Event triggered when a user deletes a film"""

    movie_id: int
    movie_name: str
    movie_director: Optional[str] = None
    movie_year: Optional[int] = None
    movie_genres: List[str] = Field(default_factory=list)
    movie_rating: Optional[float] = None
    movie_duration: Optional[int] = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating delete film events"""

        movie_id: Optional[Union[int, CriterionValue]] = None
        name: Optional[Union[str, CriterionValue]] = None
        genre: Optional[Union[str, CriterionValue]] = None
        director: Optional[Union[str, CriterionValue]] = None
        year: Optional[Union[int, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this delete film event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.movie_id is not None:
            if not validate_criterion(self.movie_id, criteria.movie_id):
                return False
        if criteria.name is not None:
            if not validate_criterion(self.movie_name, criteria.name):
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
                    if not any(genre.lower() in [v.lower() if isinstance(v, str) else v for v in criteria.genre.value] for genre in self.movie_genres):
                        return False
        if criteria.director is not None:
            if not validate_criterion(self.movie_director, criteria.director):
                return False
        if criteria.year is not None:
            if not validate_criterion(self.movie_year, criteria.year):
                return False
        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "DeleteFilmEvent":
        """
        Parse a delete film event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get('data', {})
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
        )


class SearchFilmEvent(Event):
    """Event triggered when a user searches for a film"""

    query: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating search film events"""

        query: Optional[Union[str, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this search event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.query is not None:
            if not validate_criterion(self.query, criteria.query):
                return False
        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "SearchFilmEvent":
        """
        Parse a search film event from backend data.
        """
        base_event = super().parse(backend_event)
        query = backend_event.get('search_query', '')
        if not query and 'data' in backend_event:
            query = backend_event.get('data', {}).get('query', '')
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, query=query)


class AddCommentEvent(Event):
    """Event triggered when a user adds a comment to a film"""

    comment_id: int
    commenter_name: str
    content: str
    movie_id: int
    movie_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating add comment events"""

        content_contains: Optional[Union[str, CriterionValue]] = None
        commenter_name: Optional[Union[str, CriterionValue]] = None
        movie_id: Optional[Union[int, CriterionValue]] = None
        movie_name: Optional[Union[str, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this add comment event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.content_contains is not None:
            if not validate_criterion(
                self.content,
                CriterionValue(value=criteria.content_contains.value if isinstance(criteria.content_contains, CriterionValue) else criteria.content_contains, operator=ComparisonOperator.CONTAINS),
            ):
                return False
        if criteria.commenter_name is not None:
            if not validate_criterion(self.commenter_name, criteria.commenter_name):
                return False
        if criteria.movie_id is not None:
            if not validate_criterion(self.movie_id, criteria.movie_id):
                return False
        if criteria.movie_name is not None:
            if not validate_criterion(self.movie_name, criteria.movie_name):
                return False
        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "AddCommentEvent":
        """
        Parse an add comment event from backend data.
        """
        base_event = super().parse(backend_event)
        data = backend_event.get('data', {})
        movie_data = data.get('movie', {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            comment_id=data.get('comment_id', 0),
            commenter_name=data.get('name', ''),
            content=data.get('content', ''),
            movie_id=movie_data.get('id', 0),
            movie_name=movie_data.get('name', ''),
        )


# =============================================================================
#                     CONTACT
# =============================================================================


class ContactEvent(Event):
    """Event triggered when a user submits a contact form"""

    contact_id: int
    name: str
    email: str
    subject: str
    message: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating contact events"""

        name: Optional[Union[str, CriterionValue]] = None
        email: Optional[Union[str, CriterionValue]] = None
        subject: Optional[Union[str, CriterionValue]] = None
        message_contains: Optional[Union[str, CriterionValue]] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """
        Validate if this contact event meets the criteria

        Args:
            criteria: Optional validation criteria to check against

        Returns:
            True if criteria is met or not provided, False otherwise
        """
        if not criteria:
            return True

        # Validate name
        if criteria.name is not None:
            if not validate_criterion(self.name, criteria.name):
                return False

        # Validate email
        if criteria.email is not None:
            if not validate_criterion(self.email, criteria.email):
                return False

        # Validate subject
        if criteria.subject is not None:
            if not validate_criterion(self.subject, criteria.subject):
                return False

        # Validate message_contains
        if criteria.message_contains is not None:
            if isinstance(criteria.message_contains, str):
                if criteria.message_contains.lower() not in self.message.lower():
                    return False
            else:
                # Using the operator with default CONTAINS for message_contains
                operator = criteria.message_contains.operator
                value = criteria.message_contains.value

                if operator == ComparisonOperator.CONTAINS:
                    if value.lower() not in self.message.lower():
                        return False
                elif operator == ComparisonOperator.NOT_CONTAINS:
                    if value.lower() in self.message.lower():
                        return False
                elif operator == ComparisonOperator.EQUALS:
                    if value.lower() != self.message.lower():
                        return False

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "ContactEvent":
        """
        Parse a contact event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            ContactEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract data
        data = backend_event.get('data', {})

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            contact_id=data.get('id', 0),
            name=data.get('name', ''),
            email=data.get('email', ''),
            subject=data.get('subject', ''),
            message=data.get('message', ''),
        )


class FilterFilmEvent(Event):
    """Event triggered when a user filters films by genre and/or year"""

    genre_id: Optional[int] = None
    genre_name: Optional[str] = None
    year: Optional[int] = None
    filters_applied: Dict[str, bool] = Field(default_factory=dict)

    class ValidationCriteria(BaseModel):
        """Criteria for validating filter film events"""

        genre_id: Optional[Union[int, CriterionValue]] = None
        genre_name: Optional[Union[str, CriterionValue]] = None
        year: Optional[Union[int, CriterionValue]] = None
        has_genre_filter: Optional[bool] = None
        has_year_filter: Optional[bool] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
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
            has_genre = self.filters_applied.get('genre', False)
            if has_genre != criteria.has_genre_filter:
                return False

        # Validate has_year_filter
        if criteria.has_year_filter is not None:
            has_year = self.filters_applied.get('year', False)
            if has_year != criteria.has_year_filter:
                return False

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "FilterFilmEvent":
        """
        Parse a filter film event from backend data

        Args:
            backend_event: Event data from the backend API

        Returns:
            FilterFilmEvent object populated with data from the backend event
        """
        base_event = super().parse(backend_event)

        # Extract data
        data = backend_event.get('data', {})
        genre_data = data.get('genre', {})

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            genre_id=genre_data.get('id') if genre_data else None,
            genre_name=genre_data.get('name') if genre_data else None,
            year=data.get('year'),
            filters_applied=data.get('filters_applied', {}),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================


EVENTS = [RegistrationEvent, LoginEvent, LogoutEvent, FilmDetailEvent, SearchFilmEvent, AddFilmEvent, EditFilmEvent, DeleteFilmEvent, AddCommentEvent, ContactEvent, EditUserEvent, FilterFilmEvent]

BACKEND_EVENT_TYPES = {
    'LOGIN': LoginEvent,
    'LOGOUT': LogoutEvent,
    'REGISTRATION': RegistrationEvent,
    'EDIT_USER': EditUserEvent,
    'FILM_DETAIL': FilmDetailEvent,
    'SEARCH_FILM': SearchFilmEvent,
    'ADD_FILM': AddFilmEvent,
    'EDIT_FILM': EditFilmEvent,
    'DELETE_FILM': DeleteFilmEvent,
    'ADD_COMMENT': AddCommentEvent,
    "CONTACT": ContactEvent,
    'FILTER_FILM': FilterFilmEvent,
}

# =============================================================================
#                          EXAMPLE USAGE
# =============================================================================
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
