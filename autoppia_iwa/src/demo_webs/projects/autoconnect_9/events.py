from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


class ViewUserProfileEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_USER_PROFILE"
    username: str
    name: str
    source: str

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
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewUserProfileEvent":
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            username=data.get("username", ""),
            name=data.get("name", ""),
            source=data.get("source", ""),
        )


class ConnectWithUserEvent(Event, BaseEventValidator):
    event_name: str = "CONNECT_WITH_USER"
    # current_username: str
    # current_name: str
    target_username: str
    target_name: str

    class ValidationCriteria(BaseModel):
        # current_username: str | CriterionValue | None = None
        # current_name: str | CriterionValue | None = None
        target_username: str | CriterionValue | None = None
        target_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.current_username, criteria.current_username),
                # self._validate_field(self.current_name, criteria.current_name),
                self._validate_field(self.target_username, criteria.target_username),
                self._validate_field(self.target_name, criteria.target_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ConnectWithUserEvent":
        data = backend_event.data or {}
        # current = data.get("currentUser", {})
        target = data.get("targetUser", {})
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            # current_username=current.get("username", ""),
            # current_name=current.get("name", ""),
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
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
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
        post_id: str | CriterionValue | None = None

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
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            user_name=data.get("userName", ""),
            content=data.get("content", ""),
            post_id=data.get("postId", ""),
        )


class LikePostEvent(Event, BaseEventValidator):
    event_name: str = "LIKE_POST"
    post_id: str
    user_name: str
    action: str

    class ValidationCriteria(BaseModel):
        post_id: str | CriterionValue | None = None
        user_name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.post_id, criteria.post_id),
                self._validate_field(self.user_name, criteria.user_name),
                self._validate_field(self.action, criteria.action),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "LikePostEvent":
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            post_id=data.get("postId", ""),
            user_name=data.get("userName", ""),
            action=data.get("action", ""),
        )


class CommentOnPostEvent(Event, BaseEventValidator):
    event_name: str = "COMMENT_ON_POST"
    post_id: str
    comment_id: str
    user_name: str
    comment_text: str

    class ValidationCriteria(BaseModel):
        post_id: str | CriterionValue | None = None
        comment_id: str | CriterionValue | None = None
        user_name: str | CriterionValue | None = None
        comment_text: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.post_id, criteria.post_id),
                self._validate_field(self.comment_id, criteria.comment_id),
                self._validate_field(self.user_name, criteria.user_name),
                self._validate_field(self.comment_text, criteria.comment_text),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CommentOnPostEvent":
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            post_id=data.get("postId", ""),
            comment_id=data.get("commentId", ""),
            user_name=data.get("userName", ""),
            comment_text=data.get("commentText", ""),
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
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            label=data.get("label", ""),
        )


class ApplyForJobEvent(Event, BaseEventValidator):
    event_name: str = "APPLY_FOR_JOB"
    job_id: str
    job_title: str
    company: str
    location: str

    class ValidationCriteria(BaseModel):
        job_id: str | CriterionValue | None = None
        job_title: str | CriterionValue | None = None
        company: str | CriterionValue | None = None
        location: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.job_id, criteria.job_id),
                self._validate_field(self.job_title, criteria.job_title),
                self._validate_field(self.company, criteria.company),
                self._validate_field(self.location, criteria.location),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ApplyForJobEvent":
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            job_id=data.get("jobId", ""),
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
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            label=data.get("label", ""),
            username=data.get("username", ""),
        )


class SearchUsersEvent(Event, BaseEventValidator):
    event_name: str = "SEARCH_USERS"
    query: str
    result_count: int

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None
        result_count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.query, criteria.query),
                self._validate_field(self.result_count, criteria.result_count),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchUsersEvent":
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            query=data.get("query", ""),
            result_count=data.get("resultCount", 0),
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
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            source=data.get("source", ""),
        )


class FollowPageEvent(Event, BaseEventValidator):
    event_name: str = "FOLLOW_PAGE"
    company: str
    action: str

    class ValidationCriteria(BaseModel):
        company: str | CriterionValue | None = None
        action: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.company, criteria.company),
                self._validate_field(self.action, criteria.action),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FollowPageEvent":
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            company=data.get("company", ""),
            action=data.get("action", ""),
        )


class SearchJobsEvent(Event, BaseEventValidator):
    event_name: str = "SEARCH_JOBS"
    query: str
    result_count: int

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None
        result_count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.query, criteria.query),
                self._validate_field(self.result_count, criteria.result_count),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchJobsEvent":
        data = backend_event.data or {}
        return cls(
            event_name=backend_event.event_name,
            timestamp=backend_event.timestamp,
            web_agent_id=backend_event.web_agent_id,
            user_id=backend_event.user_id,
            query=data.get("query", ""),
            result_count=data.get("resultCount", 0),
        )


EVENTS = [
    ViewUserProfileEvent,
    ConnectWithUserEvent,
    HomeNavbarEvent,
    PostStatusEvent,
    LikePostEvent,
    CommentOnPostEvent,
    JobsNavbarEvent,
    ApplyForJobEvent,
    ProfileNavbarEvent,
    SearchUsersEvent,
    ViewAllRecommendationsEvent,
    FollowPageEvent,
    SearchJobsEvent,
]

BACKEND_EVENT_TYPES = {
    "VIEW_USER_PROFILE": ViewUserProfileEvent,
    "CONNECT_WITH_USER": ConnectWithUserEvent,
    "HOME_NAVBAR": HomeNavbarEvent,
    "POST_STATUS": PostStatusEvent,
    "LIKE_POST": LikePostEvent,
    "COMMENT_ON_POST": CommentOnPostEvent,
    "JOBS_NAVBAR": JobsNavbarEvent,
    "APPLY_FOR_JOB": ApplyForJobEvent,
    "PROFILE_NAVBAR": ProfileNavbarEvent,
    "SEARCH_USERS": SearchUsersEvent,
    "VIEW_ALL_RECOMMENDATIONS": ViewAllRecommendationsEvent,
    "FOLLOW_PAGE": FollowPageEvent,
    "SEARCH_JOBS": SearchJobsEvent,
}
