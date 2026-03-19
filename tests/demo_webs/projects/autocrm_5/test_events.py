"""Unit tests for autocrm_5 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.p05_autocrm.events import (
    BACKEND_EVENT_TYPES,
    AddClientEvent,
    AddNewMatter,
    ArchiveMatter,
    BillingSearchEvent,
    ChangeUserName,
    DeleteClientEvent,
    DeleteMatter,
    DocumentDeleted,
    DocumentRenamedEvent,
    FilterClientsEvent,
    FilterMatterStatus,
    HelpViewedEvent,
    LogDelete,
    LogEdited,
    NewCalendarEventAdded,
    NewLogAdded,
    SearchClient,
    SearchMatter,
    SortMatterByCreatedAt,
    UpdateMatter,
    ViewClientDetails,
    ViewMatterDetails,
    ViewPendingEvents,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model

# Matter: name, client, status, updated
MATTER_DATA = {"name": "M1", "client": "C1", "status": "active", "updated": "2025-01-01"}
# Client: name, email, matters, avatar, status, last
CLIENT_DATA = {"name": "Client", "email": "c@c.com", "matters": 1, "avatar": "", "status": "active", "last": "2025-01-01"}
# ClientPayload: id?, name, email, matters, status, last
CLIENT_PAYLOAD_DATA = {"name": "CP", "email": "cp@cp.com", "matters": 0, "status": "active", "last": "2025-01-01"}
# Document: name, size, version, updated, status
DOCUMENT_DATA = {"name": "D1", "size": "10 KB", "version": "1", "updated": "2025-01-01", "status": "ok"}


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


TIME_LOG_DATA = {"matter": "M", "client": "C", "date": "2025-01-01", "hours": 1.0, "description": "d", "status": "done"}

AUTOCRM_PARSE_PAYLOADS = [
    ("ADD_NEW_MATTER", MATTER_DATA),
    ("ARCHIVE_MATTER", {"archived": [MATTER_DATA]}),
    ("VIEW_MATTER_DETAILS", MATTER_DATA),
    ("DELETE_MATTER", {"deleted": [MATTER_DATA]}),
    ("VIEW_CLIENT_DETAILS", CLIENT_DATA),
    ("SEARCH_CLIENT", {"query": "q"}),
    ("DOCUMENT_DELETED", DOCUMENT_DATA),
    ("DOCUMENT_RENAMED", {"previousName": "old", "newName": "new"}),
    ("NEW_CALENDAR_EVENT_ADDED", {"date": "2025-01-01", "label": "L", "time": "10:00", "event_type": "meeting"}),
    ("NEW_LOG_ADDED", TIME_LOG_DATA),
    ("LOG_EDITED", {"after": TIME_LOG_DATA}),
    ("BILLING_SEARCH", {"query": "q"}),
    ("LOG_DELETE", TIME_LOG_DATA),
    ("CHANGE_USER_NAME", {"name": "N"}),
    ("SEARCH_MATTER", {"query": "q"}),
    ("FILTER_MATTER_STATUS", {"status": "active"}),
    ("SORT_MATTER_BY_CREATED_AT", {}),
    ("UPDATE_MATTER", {"after": MATTER_DATA}),
    ("VIEW_PENDING_EVENTS", {}),
    ("ADD_CLIENT", CLIENT_PAYLOAD_DATA),
    ("DELETE_CLIENT", CLIENT_PAYLOAD_DATA),
    ("FILTER_CLIENTS", {"status": "active"}),
    ("HELP_VIEWED", {}),
]


class TestParseAutocrmEvents:
    def test_add_new_matter_parse(self):
        e = AddNewMatter.parse(_be("ADD_NEW_MATTER", MATTER_DATA))
        assert e.matter.name == "M1"
        assert e.matter.client == "C1"

    def test_view_matter_details_parse(self):
        e = ViewMatterDetails.parse(_be("VIEW_MATTER_DETAILS", MATTER_DATA))
        assert e.matter.name == "M1"

    def test_search_client_parse(self):
        e = SearchClient.parse(_be("SEARCH_CLIENT", {"query": "acme"}))
        assert e.query == "acme"

    def test_add_client_parse(self):
        e = AddClientEvent.parse(_be("ADD_CLIENT", CLIENT_PAYLOAD_DATA))
        assert e.client.name == "CP"
        assert e.client.email == "cp@cp.com"

    def test_filter_clients_parse(self):
        e = FilterClientsEvent.parse(_be("FILTER_CLIENTS", {"status": "active", "matters": "2"}))
        assert e.status == "active"

    def test_help_viewed_parse(self):
        e = HelpViewedEvent.parse(_be("HELP_VIEWED", {}))
        assert e.event_name == "HELP_VIEWED"


class TestValidateAutocrmEvents:
    def test_add_new_matter_validate_none(self):
        e = AddNewMatter.parse(_be("ADD_NEW_MATTER", MATTER_DATA))
        assert e.validate_criteria(None) is True

    def test_view_matter_details_validate(self):
        e = ViewMatterDetails.parse(_be("VIEW_MATTER_DETAILS", MATTER_DATA))
        criteria = ViewMatterDetails.ValidationCriteria(name="M1", client="C1")
        assert e.validate_criteria(criteria) is True

    def test_search_client_validate(self):
        e = SearchClient.parse(_be("SEARCH_CLIENT", {"query": "q"}))
        criteria = SearchClient.ValidationCriteria(query="q")
        assert e.validate_criteria(criteria) is True

    def test_help_viewed_validate_none(self):
        e = HelpViewedEvent.parse(_be("HELP_VIEWED", {}))
        assert e.validate_criteria(None) is True


class TestValidateAutocrmEventsCriteria:
    """Validate_criteria tests for all autocrm_5 events that have ValidationCriteria."""

    def test_delete_matter_validate_criteria(self):
        e = DeleteMatter.parse(_be("DELETE_MATTER", {"deleted": [MATTER_DATA]}))
        criteria = DeleteMatter.ValidationCriteria(name="M1", client="C1")
        assert e.validate_criteria(criteria) is True

    def test_archive_matter_validate_criteria(self):
        e = ArchiveMatter.parse(_be("ARCHIVE_MATTER", {"archived": [MATTER_DATA]}))
        criteria = ArchiveMatter.ValidationCriteria(name="M1", status="active")
        assert e.validate_criteria(criteria) is True

    def test_view_client_details_validate_criteria(self):
        e = ViewClientDetails.parse(_be("VIEW_CLIENT_DETAILS", CLIENT_DATA))
        criteria = ViewClientDetails.ValidationCriteria(name="Client", email="c@c.com")
        assert e.validate_criteria(criteria) is True

    def test_document_deleted_validate_criteria(self):
        e = DocumentDeleted.parse(_be("DOCUMENT_DELETED", DOCUMENT_DATA))
        criteria = DocumentDeleted.ValidationCriteria(name="D1", status="ok")
        assert e.validate_criteria(criteria) is True

    def test_document_renamed_validate_none(self):
        e = DocumentRenamedEvent.parse(_be("DOCUMENT_RENAMED", {"previousName": "old", "newName": "new"}))
        assert e.validate_criteria(None) is True

    def test_add_client_event_validate_criteria(self):
        e = AddClientEvent.parse(_be("ADD_CLIENT", CLIENT_PAYLOAD_DATA))
        criteria = AddClientEvent.ValidationCriteria(name="CP", email="cp@cp.com")
        assert e.validate_criteria(criteria) is True

    def test_delete_client_event_validate_criteria(self):
        e = DeleteClientEvent.parse(_be("DELETE_CLIENT", CLIENT_PAYLOAD_DATA))
        criteria = DeleteClientEvent.ValidationCriteria(name="CP")
        assert e.validate_criteria(criteria) is True

    def test_filter_clients_event_validate_criteria(self):
        e = FilterClientsEvent.parse(_be("FILTER_CLIENTS", {"status": "active", "matters": "2"}))
        criteria = FilterClientsEvent.ValidationCriteria(status="active", matters="2")
        assert e.validate_criteria(criteria) is True

    def test_new_calendar_event_added_validate_criteria(self):
        e = NewCalendarEventAdded.parse(_be("NEW_CALENDAR_EVENT_ADDED", {"date": "2025-01-01", "label": "L", "time": "10:00", "color": "meeting"}))
        criteria = NewCalendarEventAdded.ValidationCriteria(label="L", date="2025-01-01", time="10:00", event_type="meeting")
        assert e.validate_criteria(criteria) is True

    def test_new_log_added_validate_criteria(self):
        e = NewLogAdded.parse(_be("NEW_LOG_ADDED", TIME_LOG_DATA))
        criteria = NewLogAdded.ValidationCriteria(matter="M", description="d", hours=1.0)
        assert e.validate_criteria(criteria) is True

    def test_log_edited_validate_criteria(self):
        e = LogEdited.parse(_be("LOG_EDITED", {"after": TIME_LOG_DATA}))
        criteria = LogEdited.ValidationCriteria(matter="M", client="C", description="d", hours=1.0, status="done")
        assert e.validate_criteria(criteria) is True

    def test_billing_search_event_validate_criteria(self):
        e = BillingSearchEvent.parse(_be("BILLING_SEARCH", {"query": "q"}))
        criteria = BillingSearchEvent.ValidationCriteria(query="q")
        assert e.validate_criteria(criteria) is True

    def test_log_delete_validate_criteria(self):
        e = LogDelete.parse(_be("LOG_DELETE", TIME_LOG_DATA))
        criteria = LogDelete.ValidationCriteria(matter="M", client="C", hours=1.0, status="done")
        assert e.validate_criteria(criteria) is True

    def test_change_user_name_validate_criteria(self):
        e = ChangeUserName.parse(_be("CHANGE_USER_NAME", {"name": "N"}))
        criteria = ChangeUserName.ValidationCriteria(name="N")
        assert e.validate_criteria(criteria) is True

    def test_search_matter_validate_criteria(self):
        e = SearchMatter.parse(_be("SEARCH_MATTER", {"query": "q"}))
        criteria = SearchMatter.ValidationCriteria(query="q")
        assert e.validate_criteria(criteria) is True

    def test_filter_matter_status_validate_criteria(self):
        e = FilterMatterStatus.parse(_be("FILTER_MATTER_STATUS", {"status": "active"}))
        criteria = FilterMatterStatus.ValidationCriteria(status="active")
        assert e.validate_criteria(criteria) is True

    def test_sort_matter_by_created_at_validate_criteria(self):
        e = SortMatterByCreatedAt.parse(_be("SORT_MATTER_BY_CREATED_AT", {"direction": "asc"}))
        criteria = SortMatterByCreatedAt.ValidationCriteria(direction="asc")
        assert e.validate_criteria(criteria) is True

    def test_update_matter_validate_criteria(self):
        e = UpdateMatter.parse(_be("UPDATE_MATTER", {"after": MATTER_DATA}))
        criteria = UpdateMatter.ValidationCriteria(name="M1", client="C1", status="active")
        assert e.validate_criteria(criteria) is True

    def test_view_pending_events_validate_criteria(self):
        e = ViewPendingEvents.parse(_be("VIEW_PENDING_EVENTS", {"earliest": "2025-01-01"}))
        criteria = ViewPendingEvents.ValidationCriteria(earliest="2025-01-01")
        assert e.validate_criteria(criteria) is True


@pytest.mark.parametrize("event_name,data", AUTOCRM_PARSE_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
