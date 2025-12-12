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
    # post_id: str

    class ValidationCriteria(BaseModel):
        user_name: str | CriterionValue | None = None
        content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.user_name, criteria.user_name),
                self._validate_field(self.content, criteria.content),
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
            # post_id=data.get("postId", ""),
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


class SavePostEvent(Event, BaseEventValidator):
    event_name: str = "SAVE_POST"
    post_id: str | None = None
    post_content: str | None = None

    class ValidationCriteria(BaseModel):
        post_id: str | CriterionValue | None = None
        post_content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.post_id, criteria.post_id),
                self._validate_field(self.post_content, criteria.post_content),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SavePostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            post_id=str(data.get("postId", "")),
            post_content=data.get("postContent", ""),
        )


class HidePostEvent(Event, BaseEventValidator):
    event_name: str = "HIDE_POST"
    post_id: str | None = None
    reason: str | None = None

    class ValidationCriteria(BaseModel):
        post_id: str | CriterionValue | None = None
        reason: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.post_id, criteria.post_id),
                self._validate_field(self.reason, criteria.reason),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "HidePostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            post_id=str(data.get("postId", "")),
            reason=data.get("reason", ""),
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


class BackToAllJobsEvent(Event, BaseEventValidator):
    event_name: str = "BACK_TO_ALL_JOBS"
    job_id: str | None = None
    title: str | None = None

    class ValidationCriteria(BaseModel):
        job_id: str | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.job_id, criteria.job_id),
                self._validate_field(self.title, criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BackToAllJobsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            job_id=data.get("jobId"),
            title=data.get("title"),
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


class UnfollowPageEvent(Event, BaseEventValidator):
    event_name: str = "UNFOLLOW_PAGE"
    company: str

    class ValidationCriteria(BaseModel):
        company: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.company, criteria.company)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "UnfollowPageEvent":
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


class FilterJobsEvent(Event, BaseEventValidator):
    event_name: str = "FILTER_JOBS"
    filters: dict
    result_count: int | None = None

    class ValidationCriteria(BaseModel):
        filters: dict | CriterionValue | None = None
        result_count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.filters, criteria.filters),
                self._validate_field(self.result_count, criteria.result_count),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FilterJobsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            filters=data.get("filters", {}),
            result_count=data.get("resultCount") or data.get("result_count"),
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


class ViewSavedPostsEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_SAVED_POSTS"
    count: int | None = None
    source: str | None = None

    class ValidationCriteria(BaseModel):
        count: int | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.count, criteria.count),
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewSavedPostsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            count=data.get("count"),
            source=data.get("source"),
        )


class ViewAppliedJobsEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_APPLIED_JOBS"
    count: int | None = None

    class ValidationCriteria(BaseModel):
        count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.count, criteria.count)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewAppliedJobsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            count=data.get("count"),
        )


class CancelApplicationEvent(Event, BaseEventValidator):
    event_name: str = "CANCEL_APPLICATION"
    job_id: str | None = None
    job_title: str | None = None
    company: str | None = None
    location: str | None = None

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
    def parse(cls, backend_event: BackendEvent) -> "CancelApplicationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            job_id=str(data.get("jobId", "")) if data.get("jobId") is not None else None,
            job_title=data.get("jobTitle"),
            company=data.get("company"),
            location=data.get("location"),
        )


class EditProfileEvent(Event, BaseEventValidator):
    event_name: str = "EDIT_PROFILE"
    username: str | None = None
    previous: dict | None = None
    updated: dict | None = None

    class ValidationCriteria(BaseModel):
        username: str | CriterionValue | None = None
        previous: dict | CriterionValue | None = None
        updated: dict | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.username, criteria.username),
                self._validate_field(self.previous, criteria.previous),
                self._validate_field(self.updated, criteria.updated),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditProfileEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=data.get("username"),
            previous=data.get("previous"),
            updated=data.get("updated"),
        )


class EditExperienceEvent(Event, BaseEventValidator):
    event_name: str = "EDIT_EXPERIENCE"
    username: str | None = None
    experience_count: int | None = None
    roles: list[str] | None = None
    name: str | None = None
    experiences: list[dict] | None = None

    class ValidationCriteria(BaseModel):
        username: str | CriterionValue | None = None
        experience_count: int | CriterionValue | None = None
        roles: list[str] | CriterionValue | None = None
        name: str | CriterionValue | None = None
        experiences: list[dict] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.username, criteria.username),
                self._validate_field(self.experience_count, criteria.experience_count),
                self._validate_field(self.roles, criteria.roles),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.experiences, criteria.experiences),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditExperienceEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=data.get("username"),
            experience_count=data.get("experienceCount"),
            roles=data.get("roles"),
            name=data.get("name"),
            experiences=data.get("experiences"),
        )


class DeletePostEvent(Event, BaseEventValidator):
    event_name: str = "DELETE_POST"
    post_id: str | None = None
    author: str | None = None
    content: str | None = None

    class ValidationCriteria(BaseModel):
        post_id: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.post_id, criteria.post_id),
                self._validate_field(self.author, criteria.author),
                self._validate_field(self.content, criteria.content),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeletePostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            post_id=str(data.get("postId", "")) if data.get("postId") is not None else None,
            author=data.get("author"),
            content=data.get("content"),
        )


class RemovePostEvent(Event, BaseEventValidator):
    event_name: str = "REMOVE_POST"
    post_id: str | None = None
    author: str | None = None
    content: str | None = None
    source: str | None = None

    class ValidationCriteria(BaseModel):
        post_id: str | CriterionValue | None = None
        author: str | CriterionValue | None = None
        content: str | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.post_id, criteria.post_id),
                self._validate_field(self.author, criteria.author),
                self._validate_field(self.content, criteria.content),
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "RemovePostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            post_id=str(data.get("postId", "")) if data.get("postId") is not None else None,
            author=data.get("author"),
            content=data.get("content"),
            source=data.get("source"),
        )


EVENTS = [
    ViewUserProfileEvent,
    ConnectWithUserEvent,
    HomeNavbarEvent,
    JobsNavbarEvent,
    PostStatusEvent,
    LikePostEvent,
    CommentOnPostEvent,
    SavePostEvent,
    HidePostEvent,
    ApplyForJobEvent,
    SearchUsersEvent,
    ViewAllRecommendationsEvent,
    FollowPageEvent,
    UnfollowPageEvent,
    SearchJobsEvent,
    FilterJobsEvent,
    ViewJobEvent,
    BackToAllJobsEvent,
    ViewSavedPostsEvent,
    ViewAppliedJobsEvent,
    CancelApplicationEvent,
    EditProfileEvent,
    EditExperienceEvent,
    DeletePostEvent,
    RemovePostEvent,
]

BACKEND_EVENT_TYPES = {
    "VIEW_USER_PROFILE": ViewUserProfileEvent,
    "CONNECT_WITH_USER": ConnectWithUserEvent,
    "HOME_NAVBAR": HomeNavbarEvent,
    "JOBS_NAVBAR": JobsNavbarEvent,
    "POST_STATUS": PostStatusEvent,
    "LIKE_POST": LikePostEvent,
    "COMMENT_ON_POST": CommentOnPostEvent,
    "SAVE_POST": SavePostEvent,
    "HIDE_POST": HidePostEvent,
    "APPLY_FOR_JOB": ApplyForJobEvent,
    "SEARCH_USERS": SearchUsersEvent,
    "VIEW_ALL_RECOMMENDATIONS": ViewAllRecommendationsEvent,
    "FOLLOW_PAGE": FollowPageEvent,
    "UNFOLLOW_PAGE": UnfollowPageEvent,
    "SEARCH_JOBS": SearchJobsEvent,
    "FILTER_JOBS": FilterJobsEvent,
    "VIEW_JOB": ViewJobEvent,
    "BACK_TO_ALL_JOBS": BackToAllJobsEvent,
    "VIEW_SAVED_POSTS": ViewSavedPostsEvent,
    "VIEW_APPLIED_JOBS": ViewAppliedJobsEvent,
    "CANCEL_APPLICATION": CancelApplicationEvent,
    "EDIT_PROFILE": EditProfileEvent,
    "EDIT_EXPERIENCE": EditExperienceEvent,
    "DELETE_POST": DeletePostEvent,
    "REMOVE_POST": RemovePostEvent,
}
