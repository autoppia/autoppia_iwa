from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


class ViewUserProfileEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_USER_PROFILE"
    username: str
    name: str

    class ValidationCriteria(BaseModel):
        username: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.username, criteria.username),
                self._validate_field(self.name, criteria.name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewUserProfileEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=data.get("username", ""),
            name=data.get("name", ""),
        )


class ConnectWithUserEvent(Event, BaseEventValidator):
    event_name: str = "CONNECT_WITH_USER"
    target_username: str
    target_name: str

    class ValidationCriteria(BaseModel):
        target_username: str | CriterionValue | None = None
        target_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.target_username, criteria.target_username),
                self._validate_field(self.target_name, criteria.target_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ConnectWithUserEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        target = data.get("targetUser", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            target_username=target.get("username", ""),
            target_name=target.get("name", ""),
        )


class HomeNavbarEvent(Event, BaseEventValidator):
    event_name: str = "HOME_NAVBAR"
    label: str

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.label, criteria.label)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "HomeNavbarEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            label=data.get("label", ""),
        )


class PostStatusEvent(Event, BaseEventValidator):
    event_name: str = "POST_STATUS"
    user_name: str
    content: str
    post_id: str

    class ValidationCriteria(BaseModel):
        user_name: str | CriterionValue | None = None
        content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.user_name, criteria.user_name),
                self._validate_field(self.content, criteria.content),
                self._validate_field(self.post_id, criteria.post_id),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PostStatusEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            user_name=data.get("userName", ""),
            content=data.get("content", ""),
            post_id=data.get("postId", ""),
        )


class LikePostEvent(Event, BaseEventValidator):
    event_name: str = "LIKE_POST"
    user_name: str
    poster_name: str
    poster_content: str

    class ValidationCriteria(BaseModel):
        user_name: str | CriterionValue | None = None
        poster_name: str | CriterionValue | None = None
        poster_content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.poster_name, criteria.poster_name),
                self._validate_field(self.poster_content, criteria.poster_content),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "LikePostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            user_name=data.get("userName", ""),
            poster_name=data.get("posterName", ""),
            poster_content=data.get("posterContent", ""),
        )


class CommentOnPostEvent(Event, BaseEventValidator):
    event_name: str = "COMMENT_ON_POST"
    user_name: str
    comment_text: str
    poster_name: str
    poster_content: str

    class ValidationCriteria(BaseModel):
        user_name: str | CriterionValue | None = None
        comment_text: str | CriterionValue | None = None
        poster_name: str | CriterionValue | None = None
        poster_content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.user_name, criteria.user_name),
                self._validate_field(self.comment_text, criteria.comment_text),
                self._validate_field(self.poster_name, criteria.poster_name),
                self._validate_field(self.poster_content, criteria.poster_content),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CommentOnPostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            user_name=data.get("userName", ""),
            comment_text=data.get("commentText", ""),
            poster_name=data.get("posterName", ""),
            poster_content=data.get("posterContent", ""),
        )


class JobsNavbarEvent(Event, BaseEventValidator):
    event_name: str = "JOBS_NAVBAR"
    label: str

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.label, criteria.label)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "JobsNavbarEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            label=data.get("label", ""),
        )


class ApplyForJobEvent(Event, BaseEventValidator):
    event_name: str = "APPLY_FOR_JOB"
    job_title: str
    company: str
    location: str

    class ValidationCriteria(BaseModel):
        job_title: str | CriterionValue | None = None
        company: str | CriterionValue | None = None
        location: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.job_title, criteria.job_title),
                self._validate_field(self.company, criteria.company),
                self._validate_field(self.location, criteria.location),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ApplyForJobEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            job_title=data.get("jobTitle", ""),
            company=data.get("company", ""),
            location=data.get("location", ""),
        )


class ProfileNavbarEvent(Event, BaseEventValidator):
    event_name: str = "PROFILE_NAVBAR"
    label: str
    username: str

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None
        username: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.label, criteria.label),
                self._validate_field(self.username, criteria.username),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ProfileNavbarEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            label=data.get("label", ""),
            username=data.get("username", ""),
        )


class SearchUsersEvent(Event, BaseEventValidator):
    event_name: str = "SEARCH_USERS"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.query, criteria.query),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchUsersEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=data.get("query", ""),
        )


class ViewAllRecommendationsEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_ALL_RECOMMENDATIONS"
    source: str

    class ValidationCriteria(BaseModel):
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.source, criteria.source)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewAllRecommendationsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            source=data.get("source", ""),
        )


class FollowPageEvent(Event, BaseEventValidator):
    event_name: str = "FOLLOW_PAGE"
    company: str

    # action: str

    class ValidationCriteria(BaseModel):
        company: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.company, criteria.company),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FollowPageEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            company=data.get("company", ""),
        )


class SearchJobsEvent(Event, BaseEventValidator):
    event_name: str = "SEARCH_JOBS"
    query: str
    experience: str
    location: str
    remote: bool
    salary: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None
        experience: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        remote: bool | CriterionValue | None = None
        salary: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.query, criteria.query),
                # self._validate_field(self.result_count, criteria.result_count),
                self._validate_field(self.experience, criteria.experience),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.remote, criteria.remote),
                self._validate_field(self.salary, criteria.salary),
                # self._validate_field(self.search, criteria.search),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchJobsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        filters = data.get("filters", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=data.get("query", ""),
            # result_count=data.get("resultCount", 0),
            experience=filters.get("experience", ""),
            location=filters.get("location", ""),
            remote=filters.get("remote", False),
            salary=filters.get("salary", ""),
            # search=filters.get("search", ''),
        )


class ViewJobEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_JOB"
    job_title: str
    company: str
    location: str

    class ValidationCriteria(BaseModel):
        job_title: str | CriterionValue | None = None
        company: str | CriterionValue | None = None
        location: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.job_title, criteria.job_title),
                self._validate_field(self.company, criteria.company),
                self._validate_field(self.location, criteria.location),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewJobEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            job_title=data.get("jobTitle", ""),
            company=data.get("company", ""),
            location=data.get("location", ""),
        )


EVENTS = [
    ViewUserProfileEvent,
    ConnectWithUserEvent,
    PostStatusEvent,
    LikePostEvent,
    CommentOnPostEvent,
    ApplyForJobEvent,
    SearchUsersEvent,
    ViewAllRecommendationsEvent,
    FollowPageEvent,
    SearchJobsEvent,
    ViewJobEvent,
]

BACKEND_EVENT_TYPES = {
    "VIEW_USER_PROFILE": ViewUserProfileEvent,
    "CONNECT_WITH_USER": ConnectWithUserEvent,
    "POST_STATUS": PostStatusEvent,
    "LIKE_POST": LikePostEvent,
    "COMMENT_ON_POST": CommentOnPostEvent,
    "APPLY_FOR_JOB": ApplyForJobEvent,
    "SEARCH_USERS": SearchUsersEvent,
    "VIEW_ALL_RECOMMENDATIONS": ViewAllRecommendationsEvent,
    "FOLLOW_PAGE": FollowPageEvent,
    "SEARCH_JOBS": SearchJobsEvent,
    "VIEW_JOB": ViewJobEvent,
}
