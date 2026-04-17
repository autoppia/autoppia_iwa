import copy
import random
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from random import choice
from typing import Any

from autoppia_iwa.src.demo_webs.data_provider import get_seed_from_url

from ...criterion_helper import ComparisonOperator
from ...shared_utils import create_constraint_dict, random_str_not_contained_in
from .data import (
    FIELD_MAP_CONTACT_DOCTOR_SUCCESSFULLY,
    FIELD_OPERATORS_MAP_APPOINTMENT_BOOKED_SUCCESSFULLY,
    FIELD_OPERATORS_MAP_CONTACT_DOCTOR,
    FIELD_OPERATORS_MAP_CONTACT_SITE_FORM,
    FIELD_OPERATORS_MAP_FILTER_DOCTOR_REVIEWS,
    FIELD_OPERATORS_MAP_OPEN_APPOINTMENT_FORM,
    FIELD_OPERATORS_MAP_OPEN_CONTACT_DOCTOR_FORM,
    FIELD_OPERATORS_MAP_REFILL_PRESCRIPTION,
    FIELD_OPERATORS_MAP_REQUEST_QUICK_APPOINTMENT,
    FIELD_OPERATORS_MAP_SEARCH_APPOINTMENT,
    FIELD_OPERATORS_MAP_SEARCH_DOCTORS,
    FIELD_OPERATORS_MAP_SEARCH_MEDICAL_ANALYSIS,
    FIELD_OPERATORS_MAP_SEARCH_PRESCRIPTION,
    FIELD_OPERATORS_MAP_VIEW_DOCTOR_AVAILABILITY,
    FIELD_OPERATORS_MAP_VIEW_DOCTOR_EDUCATION,
    FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE,
    FIELD_OPERATORS_MAP_VIEW_MEDICAL_ANALYSIS,
    FIELD_OPERATORS_MAP_VIEW_PRESCRIPTION,
    MODIFIED_EMERGENCY_CONTACT,
    MODIFIED_EMERGENCY_PHONE,
    MODIFIED_INSURANCE_NUMBER,
    MODIFIED_INSURANCE_PROVIDER,
    MODIFIED_NOTES,
    MODIFIED_PATIENT_EMAILS,
    MODIFIED_PATIENT_NAMES,
    MODIFIED_PATIENT_PHONES,
    MODIFIED_REASON_FOR_VISIT,
)
from .data_utils import (
    fetch_data,
    transform_appointments_to_modified,
    transform_doctors_to_modified,
    transform_medical_records_to_modified,
    transform_prescriptions_to_modified,
)

# Contact-doctor successfully: message/subject/dataset options (shared to avoid rebuilding every call)
CONTACT_DOCTOR_MESSAGES = [
    "Hello Doctor, I have been experiencing headaches for the past few days.",
    "Good morning, can we schedule a follow-up appointment?",
    "I noticed side effects from my new medication, please advise.",
    "Can you review my latest blood test results?",
    "I have a persistent cough and would like your guidance.",
    "Could you recommend exercises for back pain?",
    "I need a prescription refill for my current medication.",
    "Please advise if I should continue my current treatment plan.",
    "I have been feeling unusually fatigued lately.",
    "Can you provide advice on managing my allergy symptoms?",
    "I recently injured my knee and need a consultation.",
    "I would like to get a vaccination update at my next visit.",
    "Can I adjust the dosage of my current medication safely?",
    "I need a medical certificate for my workplace.",
    "Please provide guidance on improving my sleep patterns.",
]
CONTACT_DOCTOR_SUBJECTS = [
    "Headache Issues",
    "Follow-up Appointment Request",
    "Medication Side Effects",
    "Blood Test Review",
    "Persistent Cough",
    "Back Pain Advice",
    "Prescription Refill Request",
    "Treatment Plan Guidance",
    "Fatigue Concern",
    "Allergy Symptoms Management",
    "Knee Injury Consultation",
    "Vaccination Update",
    "Medication Dosage Inquiry",
    "Medical Certificate Request",
    "Sleep Improvement Guidance",
]
MODIFIED_CONTACT_MESSAGE = [{"message": m} for m in CONTACT_DOCTOR_MESSAGES]
MODIFIED_CONTACT_SUBJECT = [{"subject": s} for s in CONTACT_DOCTOR_SUBJECTS]
APPOINTMENT_REQUEST_DATASET = [{"appointment_request": True}, {"appointment_request": False}]

# Shared field set and field_map for doctor profile / contact / availability / education / form constraints
DOCTOR_PROFILE_CORE_FIELDS = [
    "doctor_name",
    "speciality",
    "rating",
    "consultation_fee",
    "language",
]
FIELD_MAP_LANGUAGE_TO_PRIMARY = {"language": "primary_language"}


def _build_data_extraction_result(
    selected_item: dict[str, Any],
    visible_fields: list[str],
    *,
    verify_field: str | None = None,
    question_fields_override: list[str] | None = None,
) -> dict[str, Any] | None:
    """Build constraints + question_fields_and_values for data_extraction_only; returns None on validation failure."""
    available_fields = [f for f in visible_fields if selected_item.get(f) is not None]
    if len(available_fields) < 2:
        return None

    if question_fields_override:
        question_fields = [f for f in question_fields_override if f in available_fields and selected_item.get(f) is not None]
        if question_fields:
            remaining = [f for f in available_fields if f not in question_fields]
            if not remaining:
                return None
            chosen_verify_field = verify_field if verify_field is not None and verify_field in remaining else random.choice(remaining)
            remaining_for_extra = [f for f in available_fields if f != chosen_verify_field and f not in question_fields]
            if len(remaining_for_extra) >= 2:
                num_extra = random.randint(1, len(remaining_for_extra))
                question_fields = question_fields + random.sample(remaining_for_extra, num_extra)
        else:
            question_fields = []
            chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
    else:
        chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
        question_fields = []

    if chosen_verify_field not in available_fields:
        return None
    verify_value = selected_item.get(chosen_verify_field)
    if verify_value is None:
        return None

    if question_fields:
        question_candidates = question_fields
    else:
        question_candidates = [f for f in available_fields if f != chosen_verify_field]
        if not question_candidates:
            return None
        num_question_fields = 1 if len(question_candidates) == 1 else 2
        question_candidates = random.sample(question_candidates, num_question_fields)

    question_fields_and_values: dict[str, Any] = {}
    for qf in question_candidates:
        val = selected_item.get(qf)
        if val is not None:
            question_fields_and_values[qf] = val
    if not question_fields_and_values:
        return None

    constraints = [create_constraint_dict(chosen_verify_field, ComparisonOperator.EQUALS, verify_value)]
    return {
        "constraints": constraints,
        "question_fields_and_values": question_fields_and_values,
    }


def _appointment_row_to_selected_item(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if row.get("doctor_name") is not None:
        out["doctor_name"] = row["doctor_name"]
    if row.get("speciality") is not None:
        out["speciality"] = row["speciality"]
    if row.get("date") is not None:
        out["date"] = row["date"]
    if row.get("time") is not None:
        out["time"] = row["time"]
    return out


def _doctor_row_to_selected_item(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if row.get("doctor_name") is not None:
        out["doctor_name"] = row["doctor_name"]
    if row.get("speciality") is not None:
        out["speciality"] = row["speciality"]
    if row.get("rating") is not None:
        out["rating"] = row["rating"]
    if row.get("consultation_fee") is not None:
        raw_fee = row["consultation_fee"]
        fee = f"${raw_fee}"
        out["consultation_fee"] = fee
    if row.get("languages") is not None:
        out["languages"] = row["languages"]
    if row.get("experience") is not None:
        raw_experience = row["experience"]
        experience = f"{raw_experience} years experience"
        out["experience"] = experience
    if row.get("specialties") is not None:
        out["sub_specialities"] = row["specialties"]
    if row.get("officeLocation") is not None:
        out["office_location"] = row["officeLocation"]
    if row.get("email") is not None:
        out["email"] = row["email"]
    if row.get("education") is not None:
        out["education"] = row["education"]
    if row.get("availability") is not None:
        out["availability"] = row["availability"]
    if row.get("patientReviews") is not None:
        out["patient_review"] = row["patientReviews"]
    if row.get("phone") is not None:
        out["doctor_phone"] = row["phone"]
    return out


def _prescription_row_to_selected_item(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in ("medicine_name", "doctor_name", "start_date", "dosage", "status", "refills_remaining"):
        val = row.get(key)
        if val is not None:
            if key == "status" and val == "refill_needed":
                val = "refill needed"
            out[key] = val

    # VIEW_PRESCRIPTION extra visible fields: backend sends them in camelCase,
    # but the UI/constraints use underscore-style snake_case keys.
    end_date = row.get("end_date", row.get("endDate"))
    if end_date is not None:
        out["end_date"] = end_date

    if row.get("pharmacy") is not None:
        out["pharmacy"] = row["pharmacy"]

    prescription_number = row.get("prescription_number", row.get("prescriptionNumber"))
    if prescription_number is not None:
        out["prescription_number"] = prescription_number

    if row.get("cost") is not None:
        cost = row["cost"]
        ui_cost_format = f"${cost}"
        out["cost"] = ui_cost_format

    side_effects = row.get("side_effects", row.get("sideEffects"))
    if side_effects is not None:
        out["side_effects"] = side_effects

    if row.get("instructions") is not None:
        out["instructions"] = row["instructions"]
    return out


def _medical_record_row_to_selected_item(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if "status" in row:
        # rename backend field "status" to constraint field "record_status"
        row["record_status"] = row.pop("status")
    for key in ("record_title", "doctor_name", "record_status", "record_date", "description", "facility"):
        val = row.get(key)
        if val is not None:
            out[key] = val

    # Flatten additional structured attributes under "values" (if present).
    # Example:
    #   "values": {"Vaccine": "...", "Lot Number": "..."}
    # becomes top-level fields in `out`.
    values = row.get("values")
    if isinstance(values, dict):
        for k, v in values.items():
            if v is not None:
                out[k] = v
    return out


async def _ensure_entity_dataset(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Extract entity data from the cache dataset, or fetch from server if not available.

    Dynamically fetches only the requested entity_type using the provided method and filter_key.
    Returns a dictionary with entity_type as the key.
    """
    _ = dataset  # Unused parameter kept for backward compatibility

    # Otherwise, fetch the specific entity type dynamically using the provided parameters
    seed = get_seed_from_url(task_url)

    fetched_dataset = await fetch_data(
        entity_type=entity_type,
        method=method,
        filter_key=filter_key,
        seed_value=seed,
    )

    # Return as dictionary with entity_type as key
    return {entity_type: fetched_dataset}


async def _get_entity_data(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    entity_type: str,
    filter_key: str,
    transform_fn: Callable[[list], list],
    *,
    method: str = "distribute",
) -> list[dict]:
    """Fetch entity data and return transformed list; empty if none available."""
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type=entity_type, method=method, filter_key=filter_key)
    items = dataset_dict.get(entity_type, [])
    return transform_fn(items) if items else []


async def _get_appointments_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract appointments data from the cache dataset, or fetch from server if not available."""
    return await _get_entity_data(task_url, dataset, "appointments", "specialty", transform_appointments_to_modified)


async def _get_doctors_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract doctors data from the cache dataset, or fetch from server if not available."""
    return await _get_entity_data(task_url, dataset, "doctors", "specialty", transform_doctors_to_modified)


async def _get_prescriptions_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract prescriptions data from the cache dataset, or fetch from server if not available."""
    return await _get_entity_data(task_url, dataset, "prescriptions", "category", transform_prescriptions_to_modified)


async def _get_medical_records_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract medical records data from the cache dataset, or fetch from server if not available."""
    return await _get_entity_data(task_url, dataset, "medical-records", "type", transform_medical_records_to_modified)


def _filter_eligible_refill_prescriptions(
    prescriptions_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return prescriptions with refills remaining; if none, return original list as fallback."""
    eligible = [copy.deepcopy(d) for d in prescriptions_data if d.get("refills_remaining", 0) != 0 or d.get("refillsRemaining", 0) != 0]
    return eligible if eligible else prescriptions_data


def _get_nested_value(obj: dict, dotted_key: str, default: Any = None) -> Any:
    """Resolve nested field values using dotted keys (e.g. 'user.name')."""
    for key in dotted_key.split("."):
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return default
    return obj


def _collect_field_values_from_dataset(dataset: list[dict[str, Any]], field: str) -> list[Any]:
    """Return unique non-None values for field across dataset rows."""
    return list({v.get(field) for v in dataset if field in v and v.get(field) is not None})


def _pick_different_value_from_dataset(dataset: list[dict[str, Any]], field: str, exclude_value: Any, fallback: Any = None) -> Any:
    """Return a random value for field from dataset that is not exclude_value, or fallback."""
    valid = [v[field] for v in dataset if v.get(field) is not None and v.get(field) != exclude_value]
    return choice(valid) if valid else fallback


def _generate_constraint_value(
    operator: ComparisonOperator,
    field_value: Any,
    field: str,
    dataset: list[dict[str, Any]],
) -> Any:
    """
    Generate a constraint value for a given operator, field, and dataset.
    Handles various data types and operators robustly.
    """
    if field == "rating" and field_value is not None:
        try:
            rating = float(field_value)
            rating = max(0.0, min(5.0, rating))
            rating = round(rating, 1)
        except (TypeError, ValueError):
            rating = None
        if rating is not None:
            if operator == ComparisonOperator.EQUALS:
                return rating
            if operator == ComparisonOperator.NOT_EQUALS:
                valid = [v.get(field) for v in dataset if v.get(field) is not None]
                if valid:
                    normalized_valid: list[float] = []
                    for value in valid:
                        try:
                            value_f = float(value)
                            value_f = max(0.0, min(5.0, value_f))
                            value_f = round(value_f, 1)
                            if value_f != rating:
                                normalized_valid.append(value_f)
                        except (TypeError, ValueError):
                            continue
                    if normalized_valid:
                        return random.choice(normalized_valid)
                delta = 0.5 if rating <= 4.5 else -0.5
                return round(max(0.0, min(5.0, rating + delta)), 1)
            if operator in {
                ComparisonOperator.GREATER_THAN,
                ComparisonOperator.LESS_THAN,
                ComparisonOperator.GREATER_EQUAL,
                ComparisonOperator.LESS_EQUAL,
            }:
                if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                    return rating
                delta = random.choice([0.1, 0.2, 0.3, 0.4, 0.5])
                if operator == ComparisonOperator.GREATER_THAN:
                    return round(max(0.0, rating - delta), 1)
                if operator == ComparisonOperator.LESS_THAN:
                    return round(min(5.0, rating + delta), 1)

    if isinstance(field_value, datetime | date):
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
            return field_value
        if operator == ComparisonOperator.NOT_EQUALS:
            return field_value + timedelta(days=delta_days + 1)

    if isinstance(field_value, time):
        delta_minutes = random.choice([5, 10, 15, 30, 60])

        def add_minutes(t, mins):
            full_dt = datetime.combine(date.today(), t) + timedelta(minutes=mins)
            return full_dt.time()

        if operator == ComparisonOperator.GREATER_THAN:
            return add_minutes(field_value, -delta_minutes)
        if operator == ComparisonOperator.LESS_THAN:
            return add_minutes(field_value, delta_minutes)
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
            return field_value
        if operator == ComparisonOperator.NOT_EQUALS:
            return _pick_different_value_from_dataset(dataset, field, field_value, add_minutes(field_value, delta_minutes + 5))

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        return _pick_different_value_from_dataset(dataset, field, field_value, None)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return random_str_not_contained_in(field_value)

    if operator == ComparisonOperator.IN_LIST:
        all_values = _collect_field_values_from_dataset(dataset, field)
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST:
        all_values = _collect_field_values_from_dataset(dataset, field)
        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - delta
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + delta
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
            return field_value

    return None


def _generate_constraints(
    dataset: list[dict], field_operators: dict, field_map: dict | None = None, min_constraints: int | None = 1, num_constraints: int | None = None, selected_fields: list | None = None
) -> list[dict[str, Any]]:
    """
    Generates constraints based on the dataset and field operator mapping.
    DB first: dataset must contain valid entities; empty dataset returns no constraints.
    """
    if not dataset:
        return []
    all_constraints = []
    sample_data = choice(dataset)
    possible_fields = list(field_operators.keys())
    if selected_fields:
        possible_fields = [f for f in possible_fields if f not in selected_fields]
    else:
        selected_fields = []

    if num_constraints is None:
        num_constraints = random.randint(min_constraints, len(possible_fields)) if possible_fields else 0

    if possible_fields and num_constraints > 0:
        n = min(num_constraints, len(possible_fields))
        selected_fields.extend(random.sample(possible_fields, n))

    if field_map is None:
        field_map = {}

    for field in selected_fields:
        allowed_ops = field_operators.get(field, [])
        if not allowed_ops:
            continue

        op = ComparisonOperator(choice(allowed_ops))
        new_field = field_map.get(field, field)

        field_value = None
        constraint_value = None
        if isinstance(new_field, list):
            random.shuffle(new_field)
            for f in new_field:
                field_value = sample_data.get(f)
                new_field = f
                break
        elif isinstance(new_field, str):
            field_value = _get_nested_value(sample_data, new_field) if "." in new_field else sample_data.get(new_field)
        elif isinstance(new_field, dict):
            custom_dataset = new_field.get("dataset", [])
            new_field = new_field.get("field", "")
            field_value = choice(custom_dataset).get(new_field)
            if new_field:
                constraint_value = _generate_constraint_value(op, field_value, new_field, dataset=custom_dataset)

        if field_value is None:
            continue

        if constraint_value is None:
            # Generate a constraint value based on the operator and field value
            constraint_value = _generate_constraint_value(op, field_value, new_field, dataset)

        if constraint_value is not None:
            constraint = create_constraint_dict(field, op, constraint_value)
            all_constraints.append(constraint)

    return all_constraints


async def _generate_from_entity(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    get_data_fn: Callable[..., Any],
    field_operators: dict,
    selected_fields: list[str],
    field_map: dict | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Fetch entity data and generate constraints; avoids repeating get_data + _generate_constraints in each generator."""
    data = await get_data_fn(task_url, dataset)
    return _generate_constraints(data, field_operators, selected_fields=selected_fields, field_map=field_map, **kwargs)


async def _generate_doctor_profile_constraints(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    field_operators: dict,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints from doctors data using DOCTOR_PROFILE_CORE_FIELDS and FIELD_MAP_LANGUAGE_TO_PRIMARY."""
    if test_types == "data_extraction_only":
        data = await _get_doctors_data(task_url, dataset)
        if not data:
            return []
        selected = _doctor_row_to_selected_item(choice(data))
        visible = ["doctor_name", "speciality", "rating", "consultation_fee", "language", "experience", "rating", "sub_specialities", "office_location", "email", "phone"]
        return _build_data_extraction_result(selected, visible, question_fields_override=["doctor_name"]) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_doctors_data,
        field_operators,
        DOCTOR_PROFILE_CORE_FIELDS,
        field_map=FIELD_MAP_LANGUAGE_TO_PRIMARY,
    )


async def generate_open_appointment_form_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for OPEN_APPOINTMENT_FORM: doctor_name, speciality, date, time from appointments (DB first). num_constraints=0..1 to keep reviewer consistency while allowing lateral field picks."""
    if test_types == "data_extraction_only":
        data = await _get_appointments_data(task_url, dataset)
        if not data:
            return []
        selected = _appointment_row_to_selected_item(choice(data))
        visible = ["doctor_name", "speciality", "date", "time"]
        return _build_data_extraction_result(selected, visible, question_fields_override=["doctor_name"]) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_appointments_data,
        FIELD_OPERATORS_MAP_OPEN_APPOINTMENT_FORM,
        ["doctor_name", "speciality", "date", "time"],
        num_constraints=random.randint(0, 1),
    )


APPOINTMENT_BOOKED_FIELD_MAP = {
    "emergency_contact": {"field": "name", "dataset": MODIFIED_EMERGENCY_CONTACT},
    "emergency_phone": {"field": "phone", "dataset": MODIFIED_EMERGENCY_PHONE},
    "insurance_number": {"field": "number", "dataset": MODIFIED_INSURANCE_NUMBER},
    "insurance_provider": {"field": "provider", "dataset": MODIFIED_INSURANCE_PROVIDER},
    "notes": {"field": "note", "dataset": MODIFIED_NOTES},
    "patient_name": {"field": "patient_name", "dataset": MODIFIED_PATIENT_NAMES},
    "patient_email": {"field": "email", "dataset": MODIFIED_PATIENT_EMAILS},
    "patient_phone": {"field": "contact", "dataset": MODIFIED_PATIENT_PHONES},
    "reason_for_visit": {"field": "reason", "dataset": MODIFIED_REASON_FOR_VISIT},
}


async def generate_appointment_booked_successfully_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        data = await _get_appointments_data(task_url, dataset)
        if not data:
            return []
        selected = _appointment_row_to_selected_item(choice(data))
        visible = ["doctor_name", "speciality", "date", "time"]
        return _build_data_extraction_result(selected, visible, question_fields_override=["doctor_name"]) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_appointments_data,
        FIELD_OPERATORS_MAP_APPOINTMENT_BOOKED_SUCCESSFULLY,
        ["doctor_name", "time", "speciality", "patient_name", "patient_email", "patient_phone", "reason_for_visit"],
        field_map=APPOINTMENT_BOOKED_FIELD_MAP,
    )


_REQUEST_QUICK_APPOINTMENT_FIELD_MAP = {
    "speciality": "speciality",
    "patient_name": {"field": "patient_name", "dataset": MODIFIED_PATIENT_NAMES},
    "patient_email": {"field": "email", "dataset": MODIFIED_PATIENT_EMAILS},
    "patient_phone": {"field": "contact", "dataset": MODIFIED_PATIENT_PHONES},
}


async def generate_request_quick_appointment_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for REQUEST_QUICK_APPOINTMENT: speciality from doctors, patient fields from MODIFIED_*."""
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_doctors_data,
        FIELD_OPERATORS_MAP_REQUEST_QUICK_APPOINTMENT,
        ["speciality", "patient_name"],
        field_map=_REQUEST_QUICK_APPOINTMENT_FIELD_MAP,
    )


async def generate_search_appointment_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for SEARCH_APPOINTMENT: doctor_name, speciality, date from appointments (DB first)."""
    if test_types == "data_extraction_only":
        data = await _get_appointments_data(task_url, dataset)
        if not data:
            return []
        selected = _appointment_row_to_selected_item(choice(data))
        visible = ["doctor_name", "speciality", "date", "time"]
        return _build_data_extraction_result(selected, visible) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_appointments_data,
        FIELD_OPERATORS_MAP_SEARCH_APPOINTMENT,
        ["doctor_name", "speciality", "date"],
        field_map={"speciality": "speciality"},
    )


async def generate_search_doctors_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for SEARCH_DOCTORS: doctor_name, speciality, language from doctors page (Search button)."""
    if test_types == "data_extraction_only":
        data = await _get_doctors_data(task_url, dataset)
        if not data:
            return []
        selected = _doctor_row_to_selected_item(choice(data))
        visible = ["doctor_name", "speciality", "languages", "consultation_fee"]
        return _build_data_extraction_result(selected, visible, question_fields_override=["doctor_name", "languages"]) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_doctors_data,
        FIELD_OPERATORS_MAP_SEARCH_DOCTORS,
        ["doctor_name", "speciality", "language"],
        field_map={"doctor_name": "name", "speciality": "speciality", "language": "primary_language"},
    )


async def generate_search_prescription_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for SEARCH_PRESCRIPTION: medicine_name, doctor_name from prescriptions (DB first)."""
    if test_types == "data_extraction_only":
        data = await _get_prescriptions_data(task_url, dataset)
        if not data:
            return []
        selected = _prescription_row_to_selected_item(choice(data))
        visible = ["medicine_name", "doctor_name", "dosage", "start_date", "status"]
        return _build_data_extraction_result(selected, visible) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_prescriptions_data,
        FIELD_OPERATORS_MAP_SEARCH_PRESCRIPTION,
        ["medicine_name", "doctor_name"],
    )


async def generate_view_prescription_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_PRESCRIPTION: medicine_name, doctor_name, start_date, dosage, status, category from prescriptions."""
    if test_types == "data_extraction_only":
        data = await _get_prescriptions_data(task_url, dataset)
        if not data:
            return []
        selected = _prescription_row_to_selected_item(choice(data))
        visible = [
            "medicine_name",
            "doctor_name",
            "start_date",
            "dosage",
            "status",
            "end_date",
            "pharmacy",
            "prescription_number",
            "cost",
            "side_effects",
            "instructions",
        ]
        return _build_data_extraction_result(selected, visible, question_fields_override=["medicine_name"]) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_prescriptions_data,
        FIELD_OPERATORS_MAP_VIEW_PRESCRIPTION,
        ["medicine_name", "doctor_name", "start_date"],
    )


async def generate_refill_prescription_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for REFILL_PRESCRIPTION: medicine_name, doctor_name from eligible prescriptions (DB first). num_constraints=0..1 to keep reviewer consistency while allowing lateral field picks."""
    prescriptions_data = await _get_prescriptions_data(task_url, dataset)
    data_source = _filter_eligible_refill_prescriptions(prescriptions_data)
    if test_types == "data_extraction_only":
        if not data_source:
            return []
        selected = _prescription_row_to_selected_item(choice(data_source))
        visible = ["medicine_name", "doctor_name", "dosage", "start_date", "status", "refills_remaining"]
        return _build_data_extraction_result(selected, visible, question_fields_override=["medicine_name"], verify_field="refills_remaining") or []
    return _generate_constraints(
        data_source,
        FIELD_OPERATORS_MAP_REFILL_PRESCRIPTION,
        selected_fields=["medicine_name", "doctor_name"],
        num_constraints=random.randint(0, 1),
    )


async def generate_search_medical_analysis_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for SEARCH_MEDICAL_ANALYSIS: record_title, doctor_name from medical records (DB first)."""
    if test_types == "data_extraction_only":
        data = await _get_medical_records_data(task_url, dataset)
        if not data:
            return []
        selected = _medical_record_row_to_selected_item(choice(data))
        visible = ["record_title", "doctor_name", "record_date", "record_status", "description"]
        return _build_data_extraction_result(selected, visible, question_fields_override=["record_title"]) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_medical_records_data,
        FIELD_OPERATORS_MAP_SEARCH_MEDICAL_ANALYSIS,
        ["record_title", "doctor_name"],
    )


async def generate_view_medical_analysis_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_MEDICAL_ANALYSIS: record_title, doctor_name, record_type from medical records (DB first)."""
    if test_types == "data_extraction_only":
        data = await _get_medical_records_data(task_url, dataset)
        if not data:
            return []
        medical_record = random.choice(data)
        selected = _medical_record_row_to_selected_item(medical_record)
        visible = ["record_title", "doctor_name", "record_status", "record_date", "description", "facility"]

        record_values = medical_record.get("values")
        if isinstance(record_values, dict):
            # Ensure `values` sub-fields are available as top-level visible fields.
            # `_medical_record_row_to_selected_item` already flattens them into `selected`;
            # this just updates the visible schema.
            visible.extend([k for k in record_values if k not in visible and (str(k).lower() != "status")])
        return _build_data_extraction_result(selected, visible, question_fields_override=["record_title"]) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_medical_records_data,
        FIELD_OPERATORS_MAP_VIEW_MEDICAL_ANALYSIS,
        ["record_title", "doctor_name", "record_type"],
    )


async def generate_view_doctor_profile_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_DOCTOR_PROFILE: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    return await _generate_doctor_profile_constraints(task_url, dataset, FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE, test_types=test_types)


async def generate_view_doctor_education_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_DOCTOR_EDUCATION: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    if test_types == "data_extraction_only":
        data = await _get_doctors_data(task_url, dataset)
        if not data:
            return []
        selected = _doctor_row_to_selected_item(choice(data))
        visible = ["doctor_name", "speciality", "consultation_fee", "education"]
        return _build_data_extraction_result(selected, visible, question_fields_override=["doctor_name"], verify_field="education") or []
    return await _generate_doctor_profile_constraints(task_url, dataset, FIELD_OPERATORS_MAP_VIEW_DOCTOR_EDUCATION, test_types="events_only")


async def generate_view_doctor_availability_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_DOCTOR_AVAILABILITY: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    if test_types == "data_extraction_only":
        data = await _get_doctors_data(task_url, dataset)
        if not data:
            return []
        selected = _doctor_row_to_selected_item(choice(data))
        availability = selected.get("availability")
        if isinstance(availability, dict) and availability:
            chosen_day = random.choice(list(availability.keys()))
            chosen_day_field = f"{chosen_day}_availability"
            selected[chosen_day_field] = availability.get(chosen_day)
            visible = ["doctor_name", "speciality", "consultation_fee", chosen_day_field]
            return (
                _build_data_extraction_result(
                    selected,
                    visible,
                    question_fields_override=["doctor_name"],
                    verify_field=chosen_day_field,
                )
                or []
            )
    return await _generate_doctor_profile_constraints(task_url, dataset, FIELD_OPERATORS_MAP_VIEW_DOCTOR_AVAILABILITY)


async def generate_open_contact_doctor_form_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for OPEN_CONTACT_DOCTOR_FORM: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    return await _generate_doctor_profile_constraints(task_url, dataset, FIELD_OPERATORS_MAP_OPEN_CONTACT_DOCTOR_FORM, test_types=test_types)


async def generate_contact_doctor_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for CONTACT_DOCTOR: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    if test_types == "data_extraction_only":
        return await generate_view_doctor_profile_constraints(
            task_url=task_url,
            dataset=dataset,
            test_types="data_extraction_only",
        )
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_doctors_data,
        FIELD_OPERATORS_MAP_CONTACT_DOCTOR,
        ["doctor_name"],
        field_map=FIELD_MAP_LANGUAGE_TO_PRIMARY,
    )


# Field map for contact-doctor successfully (urgency/contact method options reused)
CONTACT_SUCCESSFULLY_FIELD_MAP = {
    "patient_name": {"field": "patient_name", "dataset": MODIFIED_PATIENT_NAMES},
    "patient_email": {"field": "email", "dataset": MODIFIED_PATIENT_EMAILS},
    "patient_phone": {"field": "contact", "dataset": MODIFIED_PATIENT_PHONES},
    "message": {"field": "message", "dataset": MODIFIED_CONTACT_MESSAGE},
    "subject": {"field": "subject", "dataset": MODIFIED_CONTACT_SUBJECT},
    "appointment_request": {"field": "appointment_request", "dataset": APPOINTMENT_REQUEST_DATASET},
    "urgency": {"field": "urgency", "dataset": [{"urgency": a} for a in ["low", "medium", "high"]]},
    "preferred_contact_method": {"field": "option", "dataset": [{"option": i} for i in ["either", "email", "phone"]]},
}


async def generate_doctor_contact_successfully_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    return _generate_constraints(
        doctors_data,
        FIELD_MAP_CONTACT_DOCTOR_SUCCESSFULLY,
        selected_fields=["doctor_name", "patient_name", "subject"],
        field_map=CONTACT_SUCCESSFULLY_FIELD_MAP,
    )


FILTER_DOCTOR_REVIEWS_FIELD_MAP = {
    "filter_rating": {"field": "rating", "dataset": [{"rating": r} for r in [1, 2, 3, 4, 5]]},
    "sort_order": {"field": "sort_order", "dataset": [{"sort_order": o} for o in ["newest", "oldest", "highest", "lowest"]]},
}


async def generate_filter_doctor_reviews_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for FILTER_DOCTOR_REVIEWS: doctor_name, filter_rating, sort_order (DB first). num_constraints=0..1 to keep reviewer consistency while allowing lateral field picks (e.g. speciality)."""
    if test_types == "data_extraction_only":
        data = await _get_doctors_data(task_url, dataset)
        if not data:
            return []
        selected = _doctor_row_to_selected_item(choice(data))
        reviews = selected.get("patient_review", [])
        chosen_review = random.choice(reviews) if reviews else {}
        selected["reviewer_name"] = chosen_review.get("patientName")
        selected["review_content"] = chosen_review.get("comment")
        raw_review_date = chosen_review.get("date")
        if isinstance(raw_review_date, str) and raw_review_date.strip():
            try:
                dt = datetime.strptime(raw_review_date.strip(), "%m/%d/%Y")
                selected["review_date"] = f"{dt.month}/{dt.day}/{dt.year}"  # no leading zeros
            except ValueError:
                # fallback: keep original if format is unexpected
                selected["review_date"] = raw_review_date
        else:
            selected["review_date"] = raw_review_date
        visible = ["doctor_name", "speciality", "reviewer_name", "review_date", "review_content"]
        verify_field_candidates = ["reviewer_name", "review_date", "review_content"]
        chosen_verify_field = random.choice(verify_field_candidates)
        if chosen_verify_field == "reviewer_name":
            question_fields_override = ["doctor_name", "review_date", "review_content"]
        elif chosen_verify_field == "reviewer_date":
            question_fields_override = ["doctor_name", "reviewer_name"]
        else:
            question_fields_override = ["doctor_name", "reviewer_name"]
        return _build_data_extraction_result(selected, visible, question_fields_override=question_fields_override) or []
    return await _generate_from_entity(
        task_url,
        dataset,
        _get_doctors_data,
        FIELD_OPERATORS_MAP_FILTER_DOCTOR_REVIEWS,
        ["doctor_name", "filter_rating", "sort_order"],
        field_map=FILTER_DOCTOR_REVIEWS_FIELD_MAP,
        num_constraints=random.randint(0, 1),
    )


async def generate_contact_site_form_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Site contact page: constrain on subject or email using static operators map."""
    _ = task_url, dataset
    field = random.choice(list(FIELD_OPERATORS_MAP_CONTACT_SITE_FORM.keys()))
    ops = FIELD_OPERATORS_MAP_CONTACT_SITE_FORM[field]
    op = ComparisonOperator(random.choice(ops))
    if field == "email":
        val = "patient@example.com"
    elif field == "subject":
        val = "General inquiry"
    elif field == "name":
        val = "Jane Doe"
    else:
        val = "I need help with billing."
    return [create_constraint_dict(field, op, val)]


async def generate_view_help_page_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    _ = task_url, dataset
    return [create_constraint_dict("page", ComparisonOperator.EQUALS, "help")]
