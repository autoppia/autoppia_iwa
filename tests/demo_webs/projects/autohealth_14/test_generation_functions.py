from __future__ import annotations

from datetime import date, time

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p14_autohealth import generation_functions as gf

DOCTORS = [
    {
        "doctor_name": "Dr. Alice",
        "name": "Dr. Alice",
        "speciality": "Cardiology",
        "rating": 4.5,
        "consultation_fee": 120.0,
        "language": "English",
        "primary_language": "English",
    },
    {
        "doctor_name": "Dr. Bob",
        "name": "Dr. Bob",
        "speciality": "Dermatology",
        "rating": 4.8,
        "consultation_fee": 95.0,
        "language": "Spanish",
        "primary_language": "Spanish",
    },
]

APPOINTMENTS = [
    {
        "doctor_name": "Dr. Alice",
        "speciality": "Cardiology",
        "date": date(2026, 4, 10),
        "time": time(9, 0),
        "patient_name": "Jane Roe",
        "patient_email": "jane@example.com",
        "patient_phone": "600123123",
        "reason_for_visit": "Checkup",
    }
]

PRESCRIPTIONS = [
    {
        "medicine_name": "Atorvastatin",
        "doctor_name": "Dr. Alice",
        "start_date": date(2026, 3, 1),
        "refills_remaining": 2,
        "status": "active",
        "category": "Cardiology",
    },
    {
        "medicine_name": "Ibuprofen",
        "doctor_name": "Dr. Bob",
        "start_date": date(2026, 3, 5),
        "refills_remaining": 0,
        "status": "expired",
        "category": "General",
    },
]

MEDICAL_RECORDS = [
    {
        "record_title": "Blood Panel",
        "doctor_name": "Dr. Alice",
        "record_type": "analysis",
    },
    {
        "record_title": "MRI Scan",
        "doctor_name": "Dr. Bob",
        "record_type": "imaging",
    },
]


@pytest.fixture
def deterministic_random(monkeypatch: pytest.MonkeyPatch) -> None:
    def _choice(seq):
        if isinstance(seq, str):
            return seq[-1]
        return next(iter(seq))

    monkeypatch.setattr(gf, "choice", _choice)
    monkeypatch.setattr(gf.random, "choice", _choice)
    monkeypatch.setattr(gf.random, "sample", lambda population, k: list(population)[:k])
    monkeypatch.setattr(gf.random, "shuffle", lambda population: None)
    monkeypatch.setattr(gf.random, "randint", lambda a, b: b)
    monkeypatch.setattr(gf.random, "uniform", lambda a, b: b)


@pytest.fixture
def patched_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _appointments(task_url=None, dataset=None):
        return APPOINTMENTS

    async def _doctors(task_url=None, dataset=None):
        return DOCTORS

    async def _prescriptions(task_url=None, dataset=None):
        return PRESCRIPTIONS

    async def _medical_records(task_url=None, dataset=None):
        return MEDICAL_RECORDS

    monkeypatch.setattr(gf, "_get_appointments_data", _appointments)
    monkeypatch.setattr(gf, "_get_doctors_data", _doctors)
    monkeypatch.setattr(gf, "_get_prescriptions_data", _prescriptions)
    monkeypatch.setattr(gf, "_get_medical_records_data", _medical_records)


def test_helper_filters_and_nested_access():
    eligible = gf._filter_eligible_refill_prescriptions(PRESCRIPTIONS)
    assert len(eligible) == 1
    assert eligible[0]["medicine_name"] == "Atorvastatin"
    assert gf._get_nested_value({"a": {"b": 2}}, "a.b") == 2
    assert gf._get_nested_value({"a": {}}, "a.b", "fallback") == "fallback"
    assert set(gf._collect_field_values_from_dataset(DOCTORS, "doctor_name")) == {"Dr. Alice", "Dr. Bob"}
    assert gf._pick_different_value_from_dataset(DOCTORS, "doctor_name", "Dr. Alice") == "Dr. Bob"


def test_generate_constraint_value_for_ratings_strings_dates_times_and_numbers(deterministic_random):
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, 4.5, "rating", DOCTORS) == 4.5
    assert gf._generate_constraint_value(ComparisonOperator.NOT_EQUALS, 4.5, "rating", DOCTORS) == 4.8
    assert gf._generate_constraint_value(ComparisonOperator.GREATER_THAN, 4.5, "rating", DOCTORS) < 4.5
    assert gf._generate_constraint_value(ComparisonOperator.LESS_THAN, 4.5, "rating", DOCTORS) > 4.5
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, "Dr. Alice", "doctor_name", DOCTORS) == "Dr. Alice"
    contains_value = gf._generate_constraint_value(ComparisonOperator.CONTAINS, "Dr. Alice", "doctor_name", DOCTORS)
    assert isinstance(contains_value, str)
    assert contains_value
    assert contains_value in "Dr. Alice"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, "Dr. Alice", "doctor_name", DOCTORS) == "zzz"
    assert set(gf._generate_constraint_value(ComparisonOperator.IN_LIST, "Dr. Alice", "doctor_name", DOCTORS)) == {"Dr. Alice", "Dr. Bob"}
    assert gf._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, "Dr. Alice", "doctor_name", DOCTORS) == ["Dr. Bob"]
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, date(2026, 4, 10), "date", [{"date": date(2026, 4, 10)}]) == date(2026, 4, 10)
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, time(9, 0), "time", [{"time": time(9, 0)}]) == time(9, 0)
    assert gf._generate_constraint_value(ComparisonOperator.GREATER_THAN, 120.0, "consultation_fee", DOCTORS) < 120.0


def test_generate_constraints_and_empty_dataset_behavior(deterministic_random):
    assert gf._generate_constraints([], {"doctor_name": ["equals"]}) == []
    constraints = gf._generate_constraints(
        DOCTORS,
        {"doctor_name": ["equals"], "language": ["equals"]},
        field_map={"language": "primary_language"},
        selected_fields=["doctor_name", "language"],
    )
    assert {c["field"] for c in constraints} == {"doctor_name", "language"}


@pytest.mark.asyncio
async def test_generate_from_entity_and_doctor_profile_helpers(deterministic_random, patched_entities):
    generated = await gf._generate_from_entity(None, None, gf._get_doctors_data, {"doctor_name": ["equals"]}, ["doctor_name"])
    profile = await gf._generate_doctor_profile_constraints(None, None, gf.FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE)
    assert generated[0]["field"] == "doctor_name"
    assert {c["field"] for c in profile}


@pytest.mark.asyncio
async def test_appointment_related_generators(deterministic_random, patched_entities):
    open_form = await gf.generate_open_appointment_form_constraints()
    booked = await gf.generate_appointment_booked_successfully_constraints()
    quick = await gf.generate_request_quick_appointment_constraints()
    search = await gf.generate_search_appointment_constraints()
    assert {c["field"] for c in open_form}
    assert {c["field"] for c in booked}
    assert {c["field"] for c in quick}
    assert {c["field"] for c in search}


@pytest.mark.asyncio
async def test_doctor_and_prescription_generators(deterministic_random, patched_entities):
    doctors = await gf.generate_search_doctors_constraints()
    search_prescription = await gf.generate_search_prescription_constraints()
    view_prescription = await gf.generate_view_prescription_constraints()
    refill = await gf.generate_refill_prescription_constraints()
    assert {c["field"] for c in doctors}
    assert {c["field"] for c in search_prescription}
    assert {c["field"] for c in view_prescription}
    assert {c["field"] for c in refill}


@pytest.mark.asyncio
async def test_medical_record_and_doctor_profile_generators(deterministic_random, patched_entities):
    search_analysis = await gf.generate_search_medical_analysis_constraints()
    view_analysis = await gf.generate_view_medical_analysis_constraints()
    view_profile = await gf.generate_view_doctor_profile_constraints()
    view_education = await gf.generate_view_doctor_education_constraints()
    view_availability = await gf.generate_view_doctor_availability_constraints()
    open_contact = await gf.generate_open_contact_doctor_form_constraints()
    contact = await gf.generate_contact_doctor_constraints()
    contact_success = await gf.generate_doctor_contact_successfully_constraints()
    review_filter = await gf.generate_filter_doctor_reviews_constraints()
    assert {c["field"] for c in search_analysis}
    assert {c["field"] for c in view_analysis}
    assert {c["field"] for c in view_profile}
    assert {c["field"] for c in view_education}
    assert {c["field"] for c in view_availability}
    assert {c["field"] for c in open_contact}
    assert {c["field"] for c in contact}
    assert {c["field"] for c in contact_success}
    assert {c["field"] for c in review_filter}
