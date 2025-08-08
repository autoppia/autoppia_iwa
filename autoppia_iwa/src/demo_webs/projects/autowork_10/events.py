from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

# CONSULTANT RELATED EVENTS


class Consultant(BaseModel):
    country: str
    expertName: str
    jobs: int
    rate: str
    rating: float
    role: str
    # timestamp: int


class BookAConsultationEvent(Event, BaseEventValidator):
    """event triggered when someone click on book a consultation button"""

    event_name = "BOOK_A_CONSULTATION"
    consultant: Consultant

    class ValidationCriteria(CriterionValue):
        country: str | CriterionValue | None = None
        expertName: str | CriterionValue | None = None
        jobs: int | CriterionValue | None = None
        rate: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        role: str | CriterionValue | None = None
        # timestamp: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.country, self.criteria.country),
                self._validate_field(self.expertName, self.criteria.expertName),
                self._validate_field(self.jobs, self.criteria.jobs),
                self._validate_field(self.rate, self.criteria.rate),
                self._validate_field(self.rating, self.criteria.rating),
                self._validate_field(self.role, self.criteria.role),
                # self._validate_field(self.timestamp, self.criteria.timestamp)
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookAConsultation":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            consultant=Consultant(**backend_event.data),
        )


class HireButtonData(BaseModel):
    country: str
    expertName: str
    expertSlug: str
    role: str


class HireButtonClickedEvent(Event, BaseEventValidator):
    """event triggered when someone click on hire button"""

    event_name = "HIRE_BTN_CLICKED"
    hireButton: HireButtonData

    class ValidationCriteria(CriterionValue):
        country: str | CriterionValue | None = None
        expertName: str | CriterionValue | None = None
        expertSlug: str | CriterionValue | None = None
        role: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.hireButton.country, self.criteria.country),
                self._validate_field(self.hireButton.expertName, self.criteria.expertName),
                self._validate_field(self.hireButton.expertSlug, self.criteria.expertSlug),
                self._validate_field(self.hireButton.role, self.criteria.role),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "HireButtonClicked":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hireButton=HireButtonData(**base_event.data),
        )


class SelectHiringTeamEventData(BaseModel):
    expertName: str
    expertSlug: str
    team: str


class SelectHiringTeamEvent(Event, BaseEventValidator):
    event_name = "SELECT_HIRING_TEAM"
    select_hiring_team: SelectHiringTeamEventData

    class ValidationCriteria(CriterionValue):
        expertName: str | CriterionValue | None = None
        expertSlug: str | CriterionValue | None = None
        team: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.select_hiring_team.expertName, self.criteria.expertName),
                self._validate_field(self.select_hiring_team.expertSlug, self.criteria.expertSlug),
                self._validate_field(self.select_hiring_team.team, self.criteria.team),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectHiringTeamEventData":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            select_hiring_team=SelectHiringTeamEventData(**base_event.data),
        )


class HireConsultant(BaseModel):
    country: str
    expertName: str
    expertSlug: str
    increaseHowMuch: str
    increaseWhen: str
    paymentType: str
    role: str
    rate: str


class HireConsultantEvent(Event, BaseEventValidator):
    """event triggered when someone click on hire button inside hire page"""

    event_name = "HIRE_CONSULTANT"

    hireConsultant: HireConsultant

    class ValidationCriteria(CriterionValue):
        country: str | CriterionValue | None = None
        expertName: str | CriterionValue | None = None
        expertSlug: str | CriterionValue | None = None
        increaseHowMuch: str | CriterionValue | None = None
        increaseWhen: str | CriterionValue | None = None
        paymentType: str | CriterionValue | None = None
        role: str | CriterionValue | None = None
        rate: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(hireConsultant.country, self.criteria.country),
                self._validate_field(hireConsultant.expertName, self.criteria.expertName),
                self._validate_field(hireConsultant.expertSlug, self.criteria.expertSlug),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "HireConsultantEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hireConsultant=HireConsultant(**backend_event.data),
        )


class CancelHireEvent(Event, BaseEventValidator):
    """event triggered when someone click cancel button instead of hire while hiring consultant"""

    event_name = "CANCEL_HIRE"
    Button: str

    class ValidationCriteria(CriterionValue):
        Button: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.Button, self.criteria.Button),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CancelHireEvent":
        base_event = Event.parse(backend_event)
        data = base_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            Button=data.get("Button"),
        )


# JOB RELATED EVENTS

# class PostAJobData(BaseModel):
#     page: str
#     source: str


class PostAJobEvent(Event, BaseEventValidator):
    """event triggered when someone click on post a job button"""

    event_name = "POST_A_JOB"
    page: str  # direct validate web demo data without pydantic class
    source: str  # direct validate web demo data without pydantic class

    # post_a_job: PostAJobData

    class ValidationCriteria(CriterionValue):
        page: str | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.page, self.criteria.page),
                self._validate_field(self.source, self.criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "PostAJob":
        base_event = Event.parse(backend_event)
        data = base_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            page=data.get("page"),
            source=data.get("source"),
            # post_a_job = PostAJob(**base_event.data),
        )


class WriteJobTitleEvent(Event, BaseEventValidator):
    """event triggered when someone start writing job title"""

    event_name = "WRITE_JOB_TITLE"
    query: str
    step: int

    class ValidationCriteria(CriterionValue):
        query: str | CriterionValue | None = None
        step: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.query, self.criteria.query),
                self._validate_field(self.step, self.criteria.step),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "WriteJobTitle":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user,
            web_agent_id=base_event.web_agent_id,
            query=base_event.data.get("query"),
            step=base_event.data.get("step"),
        )


# class NextSkillsEvent(Event, BaseEventValidator):
#     """event triggered when someone click on Next: Skills button"""
#     event_name: str = "NEXT_SKILLS"
#     buttonText: str
#     step: int
#     title: str
#
#
#     class ValidationCriteria(CriterionValue):
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
#             self._validate_field(self.buttonText, self.criteria.buttonText),
#             self._validate_field(self.step, self.criteria.step),
#             self._validate_field(self.title, self.criteria.title),
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

    event_name = "SEARCH_SKILLS"
    query: str

    # timestamp : int

    class ValidationCriteria(CriterionValue):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.query, self.criteria.query),
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
            query=base_event.data.get("query"),
        )


class AddSkillEvent(Event, BaseEventValidator):
    """event triggered when someone click on Add button after successful search"""

    event_name = "ADD_SKILL"
    skill: str
    method: str
    timestamp: int

    class ValidationCriteria(CriterionValue):
        method: str | CriterionValue | None = None
        skill: str | CriterionValue | None = None
        # timestamp: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.method, self.criteria.method),
                self._validate_field(self.skill, self.criteria.skill),
                # self._validate_field(self.timestamp, self.criteria.timestamp),
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
            method=base_event.data.get("method"),
            skill=base_event.data.get("skill"),
        )


class RemoveSkillEvent(Event, BaseEventValidator):
    """event triggered when someone remove the added skill"""

    event_name = "REMOVE_SKILL"
    skill: str
    timestamp: int

    class ValidationCriteria(CriterionValue):
        skill: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.skill, self.criteria.skill),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "RemoveSkillEvent":
        base_event = Event.parse(backend_event)
        data = base_event.data

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            skill=data.get("skill"),
        )


class AttachFileClickedEvent(Event, BaseEventValidator):
    """event triggered when someone click on AttachFile button and then attached a file"""

    event_name = "ATTACH_FILE"
    filename: str
    size: int
    step: int
    type: str

    class ValidationCriteria(CriterionValue):
        filename: str | CriterionValue | None = None
        size: int | CriterionValue | None = None
        step: int | CriterionValue | None = None
        type: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.filename, self.criteria.filename),
                self._validate_field(self.size, self.criteria.size),
                self._validate_field(self.step, self.criteria.step),
                self._validate_field(self.type, self.criteria.type),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "Event":
        base_event = Event.parse(backend_event)
        data = base_event.data
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

    event_name = "SUBMIT_JOB"
    # submit_job_button_data: SubmitJobButtonData
    budgetType: str
    description: str
    duration: str
    duration: str
    rate_from: str
    rate_to: str
    scope: str
    skills: list[str]
    step: int
    title: str

    class ValidationCriteria(CriterionValue):
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
                self._validate_field(self.budgetType, self.criteria.budgetType),
                self._validate_field(self.description, self.criteria.description),
                self._validate_field(self.duration, self.criteria.duration),
                self._validate_field(self.rate_from, self.criteria.rate_from),
                self._validate_field(self.rate_to, self.criteria.rate_to),
                self._validate_field(self.scope, self.criteria.scope),
                self._validate_field(self.skills, self.criteria.skills),
                self._validate_field(self.step, self.criteria.step),
                self._validate_field(self.title, self.criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SubmitJobEvent":
        base_event = Event.parse(backend_event)
        data = base_event.data

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # submit_job_button_data=SubmitJobButtonData(**backend_event.data),
            budgetType=data.get("budgetType"),
            description=data.get("description"),
            duration=data.get("duration"),
            rate_from=data.get("rate_from"),
            rate_to=data.get("rate_to"),
            scope=data.get("scope"),
            step=data.get("step"),
            title=data.get("title"),
            skills=data.get("skills", []),
        )


class ClosePostAJobWindowEvent(Event, BaseEventValidator):
    """event triggered when someone close post a job window"""

    event_name = "CLOSE_POST_A_JOB"
    budgetType: str
    description: str
    duration: str
    rate_from: str
    rate_to: str
    scope: str
    skills: list[str]
    step: int
    title: str

    class ValidationCriteria(CriterionValue):
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
                self._validate_field(self.budgetType, self.criteria.budgetType),
                self._validate_field(self.description, self.criteria.description),
                self._validate_field(self.duration, self.criteria.duration),
                self._validate_field(self.rate_from, self.criteria.rate_from),
                self._validate_field(self.rate_to, self.criteria.rate_to),
                self._validate_field(self.scope, self.criteria.scope),
                self._validate_field(self.skills, self.criteria.skills),
                self._validate_field(self.step, self.criteria.step),
                self._validate_field(self.title, self.criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ClosePostAJobWindowEvent":
        base_event = Event.parse(backend_event)
        data = base_event.data

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
