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

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "HomeNavbarEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
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
    author: str | None = None
    content: str | None = None

    class ValidationCriteria(BaseModel):
        author: str | CriterionValue | None = None
        content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.author, criteria.author),
                self._validate_field(self.content, criteria.content),
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
            author=data.get("author", ""),
            content=data.get("postContent", ""),
        )


class HidePostEvent(SavePostEvent):
    event_name: str = "HIDE_POST"


class JobsNavbarEvent(HomeNavbarEvent):
    event_name: str = "JOBS_NAVBAR"


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
    company: str | None = None
    location: str | None = None
    title: str | None = None

    class ValidationCriteria(BaseModel):
        company: str | CriterionValue | None = None
        title: str | CriterionValue | None = None
        location: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.company, criteria.company),
                self._validate_field(self.title, criteria.title),
                self._validate_field(self.location, criteria.location),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BackToAllJobsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        job_data = data.get("data", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            company=job_data.get("company"),
            title=job_data.get("title"),
            location=job_data.get("location"),
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
    recommendation: str

    # action: str

    class ValidationCriteria(BaseModel):
        recommendation: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.recommendation, criteria.recommendation),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FollowPageEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        recommendation_data = data.get("data", "")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            recommendation=recommendation_data.get("recommendation", ""),
        )


class UnfollowPageEvent(FollowPageEvent):
    event_name: str = "UNFOLLOW_PAGE"


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
    experience: str
    location: str
    remote: bool
    salary: str

    class ValidationCriteria(BaseModel):
        experience: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        remote: bool | CriterionValue | None = None
        salary: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.experience, criteria.experience),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.remote, criteria.remote),
                self._validate_field(self.salary, criteria.salary),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FilterJobsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        filter_data = data.get("filters", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            experience=filter_data.get("experience", ""),
            location=filter_data.get("location", ""),
            remote=filter_data.get("remote", False),
            salary=filter_data.get("salary", ""),
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

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewSavedPostsEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
        )


class ViewAppliedJobsEvent(ViewSavedPostsEvent):
    event_name: str = "VIEW_APPLIED_JOBS"


class CancelApplicationEvent(Event, BaseEventValidator):
    event_name: str = "CANCEL_APPLICATION"
    job_title: str | None = None
    company: str | None = None
    location: str | None = None

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
    def parse(cls, backend_event: BackendEvent) -> "CancelApplicationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            job_title=data.get("jobTitle"),
            company=data.get("company"),
            location=data.get("location"),
        )


class EditProfileEvent(Event, BaseEventValidator):
    event_name: str = "EDIT_PROFILE"
    name: str | None = None
    bio: str | None = None
    about: str | None = None
    title: str | None = None

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        bio: str | CriterionValue | None = None
        about: str | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.bio, criteria.bio),
                self._validate_field(self.about, criteria.about),
                self._validate_field(self.title, criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditProfileEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        updated_data = data.get("updated", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=updated_data.get("name"),
            bio=updated_data.get("bio"),
            about=updated_data.get("about"),
            title=updated_data.get("title"),
        )


class experiences(BaseModel):
    company: str | None = None
    destination: str | None = None
    duration: str | None = None
    location: str | None = None
    title: str | None = None


class EditExperienceEvent(Event, BaseEventValidator):
    event_name: str = "EDIT_EXPERIENCE"
    experiences: list[experiences]
    name: str | None = None

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        title: str | CriterionValue | None = None
        company: str | CriterionValue | None = None
        duration: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        description: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        if len(self.experiences) == 0:
            return False

        for experience in self.experiences:
            if (
                self._validate_field(experience.title, criteria.title)
                and self._validate_field(experience.location, criteria.location)
                and self._validate_field(experience.duration, criteria.duration)
                and self._validate_field(experience.description, criteria.description)
                and self._validate_field(experience.company, criteria.company)
            ):
                return True
        return False

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditExperienceEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        # experience_data = data.get("experience")
        experience_data = [experiences(**experience) for experience in data.get("experiences", [])]

        return cls(
            event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, name=data.get("name"), experiences=experience_data
        )


class RemovePostEvent(Event, BaseEventValidator):
    event_name: str = "REMOVE_POST"
    author: str | None = None
    content: str | None = None

    class ValidationCriteria(BaseModel):
        author: str | CriterionValue | None = None
        content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.author, criteria.author),
                self._validate_field(self.content, criteria.content),
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
            author=data.get("author"),
            content=data.get("content"),
        )


class ViewHiddenPostsEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_HIDDEN_POSTS"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewHiddenPostsEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
        )


class UnhidePostEvent(Event, BaseEventValidator):
    event_name: str = "UNHIDE_POST"
    author: str | None = None
    post_content: str | None = None

    class ValidationCriteria(BaseModel):
        author: str | CriterionValue | None = None
        post_content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.author, criteria.author),
                self._validate_field(self.post_content, criteria.post_content),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "UnhidePostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            author=data.get("author"),
            post_content=data.get("postContent"),
        )


class AddExperienceEvent(Event, BaseEventValidator):
    event_name: str = "ADD_EXPERIENCE"
    company: str | None = None
    description: str | None = None
    duration: str | None = None
    title: str | None = None
    location: str | None = None

    class ValidationCriteria(BaseModel):
        company: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        duration: str | CriterionValue | None = None
        title: str | CriterionValue | None = None
        location: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.company, criteria.company),
                self._validate_field(self.description, criteria.description),
                self._validate_field(self.duration, criteria.duration),
                self._validate_field(self.title, criteria.title),
                self._validate_field(self.location, criteria.location),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddExperienceEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        experience_data = data.get("experience")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            company=experience_data.get("company"),
            description=experience_data.get("description"),
            duration=experience_data.get("duration"),
            location=experience_data.get("location"),
            title=experience_data.get("title"),
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
    RemovePostEvent,
    ViewHiddenPostsEvent,
    UnhidePostEvent,
    AddExperienceEvent,
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
    "REMOVE_POST": RemovePostEvent,
    "VIEW_HIDDEN_POSTS": ViewHiddenPostsEvent,
    "UNHIDE_POST": UnhidePostEvent,
    "ADD_EXPERIENCE": AddExperienceEvent,
}
