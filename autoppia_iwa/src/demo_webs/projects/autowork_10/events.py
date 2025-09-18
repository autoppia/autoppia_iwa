from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

from ..criterion_helper import ComparisonOperator


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
    role: str | None = None

    class ValidationCriteria(BaseModel):
        country: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        role: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.name, criteria.name),
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
            role=data.get("role"),
        )


class SelectHiringTeamEvent(Event, BaseEventValidator):
    event_name: str = "SELECT_HIRING_TEAM"
    name: str | None = None
    team: str | None = None

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        team: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.name, criteria.name),
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
            team=data.get("team"),
        )


class HireConsultantEvent(Event, BaseEventValidator):
    """event triggered when someone click on hire button inside hire page"""

    event_name: str = "HIRE_CONSULTANT"
    country: str | None = None
    name: str | None = None
    increaseHowMuch: str | None = None
    increaseWhen: str | None = None
    paymentType: str | None = None
    role: str | None = None

    class ValidationCriteria(BaseModel):
        country: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        increaseHowMuch: str | CriterionValue | None = None
        increaseWhen: str | CriterionValue | None = None
        paymentType: str | CriterionValue | None = None
        role: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.increaseWhen, criteria.increaseWhen),
                self._validate_field(self.increaseHowMuch, criteria.increaseHowMuch),
                self._validate_field(self.paymentType, criteria.paymentType),
                self._validate_field(self.role, criteria.role),
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
            country=data.get("country"),
            paymentType=data.get("paymentType"),
            increaseHowMuch=data.get("increaseHowMuch"),
            increaseWhen=data.get("increaseWhen"),
            role=data.get("role"),
        )


class CancelHireEvent(Event, BaseEventValidator):
    """event triggered when someone click cancel button instead of hire while hiring consultant"""

    event_name: str = "CANCEL_HIRE"
    country: str | None = None
    name: str | None = None
    rate: str | None = None
    role: str | None = None
    slug: str | None = None

    class ValidationCriteria(BaseModel):
        country: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        rate: str | CriterionValue | None = None
        role: str | CriterionValue | None = None
        slug: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.rate, criteria.rate),
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
            country=expert.get("country"),
            name=expert.get("name"),
            rate=expert.get("rate"),
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
    def parse(cls, backend_event: "BackendEvent") -> "WriteJobTitleEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            query=backend_event.data.get("query"),
        )


class SearchSkillEvent(Event, BaseEventValidator):
    """event triggered when someone start typing to search skills"""

    event_name: str = "SEARCH_SKILL"
    skill: str

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
    def parse(cls, backend_event: "BackendEvent") -> "AddSkillEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            skill=backend_event.data.get("skill"),
        )


class SubmitJobEvent(Event, BaseEventValidator):
    """event triggered when someone click submit job button after successful adding previous steps information"""

    event_name: str = "SUBMIT_JOB"
    budgetType: str
    description: str
    duration: str
    rate_from: int | None
    rate_to: int | None
    scope: str
    skills: list[str]
    step: int
    title: str

    class ValidationCriteria(BaseModel):
        budgetType: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        duration: str | CriterionValue | None = None
        rate_from: int | CriterionValue | None = None
        rate_to: int | CriterionValue | None = None
        scope: str | CriterionValue | None = None
        skills: str | CriterionValue | None = None
        step: int | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _skill_validation(self, criteria: CriterionValue | None = None) -> bool:
        if not criteria:
            return True
        if criteria.skills is not None:
            if isinstance(criteria, str):
                if not any(criteria.skills.lower() in skills.lower() for skills in self.skills):
                    return False
            else:
                if criteria.skills.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.skills.value.lower() in skills.lower() for skills in self.skills):
                        return False
                elif criteria.skills.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.skills.value.lower() in skills.lower() for skills in self.skills):
                        return False
                elif criteria.skills.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.skills.value, list):
                        return False
                    if not any(skills.lower() in [v.lower() for v in criteria.skills.value] for skills in self.skills):
                        return False
                elif criteria.skills.operator == ComparisonOperator.NOT_IN_LIST:
                    if not isinstance(criteria.skills.value, list):
                        return False
                    if any(skills.lower() in [v.lower() for v in criteria.skills.value] for skills in self.skills):
                        return False
        return True

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
                self._skill_validation(criteria),
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
            budgetType=data.get("budgetType"),
            description=data.get("description"),
            duration=data.get("duration"),
            rate_from=int(data.get("rateFrom")) if data.get("rateFrom") else None,
            rate_to=int(data.get("rateTo")) if data.get("rateTo") else None,
            scope=data.get("scope"),
            step=data.get("step"),
            title=data.get("title"),
            skills=data.get("skills", []),
        )


class ClosePostAJobWindowEvent(Event, BaseEventValidator):
    """event triggered when someone close post a job window"""

    event_name: str = "CLOSE_POST_A_JOB_WINDOW"
    budgetType: str
    description: str
    duration: str
    rate_from: int | None
    rate_to: int | None
    scope: str
    skills: list[str]
    step: int
    title: str

    class ValidationCriteria(BaseModel):
        budgetType: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        duration: str | CriterionValue | None = None
        rate_from: int | CriterionValue | None = None
        rate_to: int | CriterionValue | None = None
        scope: str | CriterionValue | None = None
        skills: str | CriterionValue | None = None
        step: int | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _skill_validation(self, criteria: CriterionValue | None = None) -> bool:
        if not criteria:
            return True
        if criteria.skills is not None:
            if isinstance(criteria, str):
                if not any(criteria.skills.lower() in skills.lower() for skills in self.skills):
                    return False
            else:
                if criteria.skills.operator == ComparisonOperator.CONTAINS:
                    if not any(criteria.skills.value.lower() in skills.lower() for skills in self.skills):
                        return False
                elif criteria.skills.operator == ComparisonOperator.NOT_CONTAINS:
                    if any(criteria.skills.value.lower() in skills.lower() for skills in self.skills):
                        return False
                elif criteria.skills.operator == ComparisonOperator.IN_LIST:
                    if not isinstance(criteria.skills.value, list):
                        return False
                    if not any(skills.lower() in [v.lower() for v in criteria.skills.value] for skills in self.skills):
                        return False
                elif criteria.skills.operator == ComparisonOperator.NOT_IN_LIST:
                    if not isinstance(criteria.skills.value, list):
                        return False
                    if any(skills.lower() in [v.lower() for v in criteria.skills.value] for skills in self.skills):
                        return False
        return True

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
                self._skill_validation(criteria),
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
            rate_from=int(data.get("rateFrom")) if data.get("rateFrom") else None,
            rate_to=int(data.get("rateTo")) if data.get("rateTo") else None,
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
    SearchSkillEvent,
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
    "CLOSE_POST_A_JOB_WINDOW": ClosePostAJobWindowEvent,
    "ADD_SKILL": AddSkillEvent,
    "SEARCH_SKILL": SearchSkillEvent,
}
