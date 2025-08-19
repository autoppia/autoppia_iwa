# CONSULTANT RELATED EVENTS

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


class BookAConsultationEvent(Event, BaseEventValidator):
    """Event triggered when someone clicks on the book a consultation button"""

    event_name: str = "BOOK_A_CONSULTATION"
    country: str | None = None
    name: str | None = None
    jobs: int | None = None
    rate: str | None = None
    rating: float | None = None
    role: str | None = None
    slug: str | None = None

    class ValidationCriteria(BaseModel):
        country: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        jobs: int | CriterionValue | None = None
        rate: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        role: str | CriterionValue | None = None
        slug: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.jobs, criteria.jobs),
                self._validate_field(self.rate, criteria.rate),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.role, criteria.role),
                self._validate_field(self.slug, criteria.slug),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookAConsultationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            country=data.get("country"),
            name=data.get("expertName"),
            jobs=data.get("jobs"),
            rate=data.get("rate"),
            rating=data.get("rating"),
            role=data.get("role"),
            slug=data.get("expertSlug"),
        )


class HireButtonClickedEvent(Event, BaseEventValidator):
    """event triggered when someone click on hire button"""

    event_name: str = "HIRE_BTN_CLICKED"
    country: str | None = None
    name: str | None = None
    slug: str | None = None
    role: str | None = None

    class ValidationCriteria(BaseModel):
        country: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        slug: str | CriterionValue | None = None
        role: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.slug, criteria.slug),
                self._validate_field(self.role, criteria.role),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "HireButtonClickedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            country=data.get("country"),
            name=data.get("expertName"),
            slug=data.get("expertSlug"),
            role=data.get("role"),
        )


class SelectHiringTeamEvent(Event, BaseEventValidator):
    event_name: str = "SELECT_HIRING_TEAM"
    name: str | None = None
    slug: str | None = None
    team: str | None = None

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        slug: str | CriterionValue | None = None
        team: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.slug, criteria.slug),
                self._validate_field(self.team, criteria.team),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectHiringTeamEventData":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("expertName"),
            slug=data.get("expertSlug"),
            team=data.get("team"),
        )


class HireConsultantEvent(Event, BaseEventValidator):
    """event triggered when someone click on hire button inside hire page"""

    event_name: str = "HIRE_CONSULTANT"
    country: str | None = None
    name: str | None = None
    slug: str | None = None
    increaseHowMuch: str | None = None
    increaseWhen: str | None = None
    paymentType: str | None = None
    role: str | None = None
    # rate: str | None = None

    class ValidationCriteria(BaseModel):
        country: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        slug: str | CriterionValue | None = None
        increaseHowMuch: str | CriterionValue | None = None
        increaseWhen: str | CriterionValue | None = None
        paymentType: str | CriterionValue | None = None
        role: str | CriterionValue | None = None
        # rate: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.slug, criteria.slug),
                self._validate_field(self.increaseWhen, criteria.increaseWhen),
                self._validate_field(self.increaseHowMuch, criteria.increaseHowMuch),
                self._validate_field(self.paymentType, criteria.paymentType),
                self._validate_field(self.role, criteria.role),
                # self._validate_field(self.rate, criteria.rate)
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "HireConsultantEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("expertName"),
            slug=data.get("expertSlug"),
            country=data.get("country"),
            paymentType=data.get("paymentType"),
            increaseHowMuch=data.get("increaseHowMuch"),
            increaseWhen=data.get("increaseWhen"),
            role=data.get("role"),
            # rate=data.get("rate"),
        )


class CancelHireEvent(Event, BaseEventValidator):
    """event triggered when someone click cancel button instead of hire while hiring consultant"""

    event_name: str = "CANCEL_HIRE"
    # about : str
    # consultation: str
    country: str | None = None
    # desc: str
    # hoursPerWeek: str
    # languages: list[str]
    name: str | None = None
    rate: str | None = None
    # rating: int
    role: str | None = None
    slug: str | None = None

    class ValidationCriteria(BaseModel):
        # about: str | CriterionValue | None = None
        # consultation: str | CriterionValue | None = None
        country: str | CriterionValue | None = None
        # desc: str | CriterionValue | None = None
        # hoursPerWeek: str | CriterionValue | None = None
        # languages: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        rate: str | CriterionValue | None = None
        # rating: int | CriterionValue | None = None
        role: str | CriterionValue | None = None
        slug: str | CriterionValue | None = None
        # Button: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.about, criteria.about),
                # self._validate_field(self.consultation, criteria.consultation),
                self._validate_field(self.country, criteria.country),
                # self._validate_field(self.desc, criteria.desc),
                # self._validate_field(self.hoursPerWeek, criteria.hoursPerWeek),
                # self._validate_field(self.languages, criteria.language),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.rate, criteria.rate),
                # self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.role, criteria.role),
                self._validate_field(self.slug, criteria.slug),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CancelHireEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        expert = data.get("expert")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # Button=expert.get("Button"),
            # about=expert.get("about"),
            # avatar=expert.get("avatar"),
            # consultation=expert.get("consultation"),
            country=expert.get("country"),
            # desc=expert.get("desc"),
            # hoursPerWeek=expert.get("hoursPerWeek"),
            # languages=expert.get("languages"),
            name=expert.get("name"),
            rate=expert.get("rate"),
            # rating=expert.get("rating"),
            role=expert.get("role"),
            slug=expert.get("slug"),
        )


class PostAJobEvent(Event, BaseEventValidator):
    """event triggered when someone click on post a job button"""

    event_name: str = "POST_A_JOB"
    page: str  # direct validate web demo data without pydantic class
    source: str  # direct validate web demo data without pydantic class

    class ValidationCriteria(BaseModel):
        page: str | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.page, criteria.page),
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "PostAJobEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            page=data.get("page"),
            source=data.get("source"),
        )


class WriteJobTitleEvent(Event, BaseEventValidator):
    """event triggered when someone start writing job title"""

    event_name: str = "WRITE_JOB_TITLE"
    query: str

    # step: int

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None
        # step: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.query, criteria.query),
                # self._validate_field(self.step, criteria.step),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "WriteJobTitleEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            query=backend_event.data.get("query"),
            # step=backend_event.data.get("step"),
        )


# class NextSkillsEvent(Event, BaseEventValidator):
#     """event triggered when someone click on Next: Skills button"""
#     event_name: str = "NEXT_SKILLS"
#     buttonText: str
#     step: int
#     title: str
#
#
#     class ValidationCriteria(BaseModel):
#         buttonText: str | CriterionValue | None = None
#         step: int | CriterionValue | None = None
#         title: str | CriterionValue | None = None
#
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         if not criteria:
#             return True
#
#         return all([
#             self._validate_field(self.buttonText, criteria.buttonText),
#             self._validate_field(self.step, criteria.step),
#             self._validate_field(self.title, criteria.title),
#         ])
#
#     @classmethod
#     def parse(cls, backend_event: "BackendEvent") -> "NextSkillsEvent":
#         base_event = Event.parse(backend_event)
#         return cls(
#             event_name=base_event.event_name,
#             timestamp=base_event.timestamp,
#             web_agent_id=base_event.web_agent_id,
#             user_id=base_event.user_id,
#             buttonText=base_event.buttonText,
#             step=base_event.step,
#             title=base_event.title,
#
#         )


class SearchSkillEvent(Event, BaseEventValidator):
    """event triggered when someone start typing to search skills"""

    event_name: str = "SEARCH_SKILL"
    skill: str

    # timestamp : int

    class ValidationCriteria(BaseModel):
        skill: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.skill, criteria.skill),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchSkillEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            skill=backend_event.data.get("query"),
        )


class AddSkillEvent(Event, BaseEventValidator):
    """event triggered when someone click on Add button after successful search"""

    event_name: str = "ADD_SKILL"
    skill: str

    # method: str
    # timestamp: int

    class ValidationCriteria(BaseModel):
        # method: str | CriterionValue | None = None
        skill: str | CriterionValue | None = None
        # timestamp: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.skill, criteria.skill),
                # self._validate_field(self.method, criteria.method),
                # self._validate_field(self.timestamp, criteria.timestamp),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AddSkillEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            skill=backend_event.data.get("skill"),
            # method=backend_event.data.get("method"),
        )


class RemoveSkillEvent(Event, BaseEventValidator):
    """event triggered when someone remove the added skill"""

    event_name: str = "REMOVE_SKILL"
    skill: str
    timestamp: int

    class ValidationCriteria(BaseModel):
        skill: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.skill, criteria.skill),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "RemoveSkillEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            skill=data.get("skill"),
        )


class AttachFileClickedEvent(Event, BaseEventValidator):
    """event triggered when someone click on AttachFile button and then attached a file"""

    event_name: str = "ATTACH_FILE"
    filename: str
    size: int
    step: int
    type: str

    class ValidationCriteria(BaseModel):
        filename: str | CriterionValue | None = None
        size: int | CriterionValue | None = None
        step: int | CriterionValue | None = None
        type: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.filename, criteria.filename),
                self._validate_field(self.size, criteria.size),
                self._validate_field(self.step, criteria.step),
                self._validate_field(self.type, criteria.type),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "Event":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            filename=data.get("filename"),
            size=data.get("size"),
            step=data.get("step"),
            type=data.get("type"),
        )


# pydantic class of submit job button data comes from web demo when we click submit job button
# class SubmitJobButtonData(BaseModel):  # need to do inside the event class
#     budgetType: str
#     description: str
#     duration: str
#     rate_from: str
#     rate_to: str
#     scope: str
#     skills: list[str]
#     step: int
#     title: str


class SubmitJobEvent(Event, BaseEventValidator):
    """event triggered when someone click submit job button after successful adding previous steps information"""

    event_name: str = "SUBMIT_JOB"
    # submit_job_button_data: SubmitJobButtonData
    budgetType: str
    description: str
    duration: str
    rate_from: str | None
    rate_to: str | None
    # rate_from: int | None
    # rate_to: int | None
    scope: str
    skills: list[str]
    step: int
    title: str

    class ValidationCriteria(BaseModel):
        budgetType: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        duration: str | CriterionValue | None = None
        rate_from: str | CriterionValue | None = None
        rate_to: str | CriterionValue | None = None
        scope: str | CriterionValue | None = None
        skills: str | CriterionValue | None = None
        step: int | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.budgetType, criteria.budgetType),
                self._validate_field(self.description, criteria.description),
                self._validate_field(self.duration, criteria.duration),
                self._validate_field(self.rate_from, criteria.rate_from),
                self._validate_field(self.rate_to, criteria.rate_to),
                self._validate_field(self.scope, criteria.scope),
                self._validate_field(self.skills, criteria.skills),
                self._validate_field(self.step, criteria.step),
                self._validate_field(self.title, criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SubmitJobEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # submit_job_button_data=SubmitJobButtonData(**backend_event.data),
            budgetType=data.get("budgetType"),
            description=data.get("description"),
            duration=data.get("duration"),
            # rate_from=int(data.get("rate_from")) if data.get("rate_from") else None,
            # rate_to=int(data.get("rate_to")) if data.get("rate_to") else None,
            rate_from=data.get("rate_from"),
            rate_to=data.get("rate_to"),
            scope=data.get("scope"),
            step=data.get("step"),
            title=data.get("title"),
            skills=data.get("skills", []),
        )


class ClosePostAJobWindowEvent(Event, BaseEventValidator):
    """event triggered when someone close post a job window"""

    event_name: str = "CLOSE_POST_A_JOB"
    budgetType: str
    description: str
    duration: str
    rate_from: str
    rate_to: str
    scope: str
    skills: list[str]
    step: int
    title: str

    class ValidationCriteria(BaseModel):
        budgetType: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        duration: str | CriterionValue | None = None
        rate_from: str | CriterionValue | None = None
        rate_to: str | CriterionValue | None = None
        scope: str | CriterionValue | None = None
        skills: str | CriterionValue | None = None
        step: int | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.budgetType, criteria.budgetType),
                self._validate_field(self.description, criteria.description),
                self._validate_field(self.duration, criteria.duration),
                self._validate_field(self.rate_from, criteria.rate_from),
                self._validate_field(self.rate_to, criteria.rate_to),
                self._validate_field(self.scope, criteria.scope),
                self._validate_field(self.skills, criteria.skills),
                self._validate_field(self.step, criteria.step),
                self._validate_field(self.title, criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ClosePostAJobWindowEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            budgetType=data.get("budgetType"),
            description=data.get("description"),
            duration=data.get("duration"),
            rate_from=data.get("rate_from"),
            rate_to=data.get("rate_to"),
            scope=data.get("scope"),
            skills=data.get("skills", []),
            step=data.get("step"),
            title=data.get("title"),
        )


EVENTS = [
    BookAConsultationEvent,
    HireButtonClickedEvent,
    SelectHiringTeamEvent,
    PostAJobEvent,
    WriteJobTitleEvent,
    SubmitJobEvent,
    ClosePostAJobWindowEvent,
    CancelHireEvent,
    HireConsultantEvent,
    AddSkillEvent,
    RemoveSkillEvent,
    SearchSkillEvent,
    AttachFileClickedEvent,
]

BACKEND_EVENT_TYPES = {
    "BOOK_A_CONSULTATION": BookAConsultationEvent,
    "HIRE_BTN_CLICKED": HireButtonClickedEvent,
    "SELECT_HIRING_TEAM": SelectHiringTeamEvent,
    "HIRE_CONSULTANT": HireConsultantEvent,
    "CANCEL_HIRE": CancelHireEvent,
    "POST_A_JOB": PostAJobEvent,
    "WRITE_JOB_TITLE": WriteJobTitleEvent,
    "SUBMIT_JOB": SubmitJobEvent,
    "CLOSE_POST_A_JOB": ClosePostAJobWindowEvent,
    "ADD_SKILL": AddSkillEvent,
    "REMOVE_SKILL": RemoveSkillEvent,
    "SEARCH_SKILL": SearchSkillEvent,
    "ATTACH_FILE": AttachFileClickedEvent,
}
