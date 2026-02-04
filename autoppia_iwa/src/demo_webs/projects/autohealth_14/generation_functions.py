import copy
import random
from datetime import date, datetime, time, timedelta
from random import choice
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    FIELD_MAP_CONTACT_DOCTOR_SUCCESSFULLY,
    FIELD_OPERATORS_MAP_APPOINTMENT_BOOKED_SUCCESSFULLY,
    FIELD_OPERATORS_MAP_BOOK_APPOINTMENT,
    FIELD_OPERATORS_MAP_CANCEL_APPOINTMENT,
    FIELD_OPERATORS_MAP_CANCEL_CONTACT_DOCTOR,
    FIELD_OPERATORS_MAP_CANCEL_VIEW_REVIEWS,
    FIELD_OPERATORS_MAP_CONTACT_DOCTOR,
    FIELD_OPERATORS_MAP_FILTER_BY_CATEGORY,
    FIELD_OPERATORS_MAP_FILTER_BY_SPECIALITY,
    FIELD_OPERATORS_MAP_FILTER_REVIEWS,
    FIELD_OPERATORS_MAP_REFILL_PRESCRIPTION,
    FIELD_OPERATORS_MAP_SORT_REVIEWS,
    FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE,
    FIELD_OPERATORS_MAP_VIEW_HEALTH_METRICS,
    FIELD_OPERATORS_MAP_VIEW_PRESCRIPTION,
    FIELD_OPERATORS_MAP_VIEW_REVIEW_CLICKED,
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


async def _ensure_entity_dataset(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Extract entity data from the pre-loaded dataset, or fetch from server if not available.

    Dynamically fetches only the requested entity_type using the provided method and filter_key.
    Returns a dictionary with entity_type as the key.
    """
    # If dataset is provided and contains the requested entity, return it in the expected format
    if dataset and entity_type in dataset:
        return {entity_type: dataset[entity_type]}

    # Otherwise, fetch the specific entity type dynamically using the provided parameters
    seed = get_seed_from_url(task_url) if task_url else None
    # Normalize empty strings to None for method and filter_key
    normalized_method = method if method and method.strip() else None
    normalized_filter_key = filter_key if filter_key and filter_key.strip() else None

    fetched_dataset = await fetch_data(
        entity_type=entity_type,
        method=normalized_method if normalized_method else "select",
        filter_key=normalized_filter_key,
        seed_value=seed,
    )

    # Return as dictionary with entity_type as key
    return {entity_type: fetched_dataset}


async def _get_appointments_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract appointments data from the pre-loaded dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="appointments")
    appointments = dataset_dict.get("appointments", [])
    if appointments:
        return transform_appointments_to_modified(appointments)
    return []


async def _get_doctors_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract doctors data from the pre-loaded dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="doctors")
    doctors = dataset_dict.get("doctors", [])
    if doctors:
        return transform_doctors_to_modified(doctors)
    return []


async def _get_prescriptions_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract prescriptions data from the pre-loaded dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="prescriptions")
    prescriptions = dataset_dict.get("prescriptions", [])
    if prescriptions:
        return transform_prescriptions_to_modified(prescriptions)
    return []


async def _get_medical_records_data(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict]:
    """Extract medical records data from the pre-loaded dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, dataset, entity_type="medical-records")
    medical_records = dataset_dict.get("medical-records", [])
    if medical_records:
        return transform_medical_records_to_modified(medical_records)
    return []


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
            valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
            return random.choice(valid) if valid else add_minutes(field_value, delta_minutes + 5)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
        return random.choice(valid) if valid else None

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for _ in range(100):
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str
        return "xyz"  # fallback

    if operator == ComparisonOperator.IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
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
    """
    all_constraints = []
    sample_data = choice(dataset)
    possible_fields = list(field_operators.keys())
    if selected_fields:
        possible_fields = [f for f in possible_fields if f not in selected_fields]
    else:
        selected_fields = []

    if num_constraints is None:
        num_constraints = random.randint(min_constraints, len(possible_fields))

    selected_fields.extend(random.sample(possible_fields, num_constraints))

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
            field_value = sample_data.get(new_field)
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


async def generate_book_appointment_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    appointments_data = await _get_appointments_data(task_url, dataset)
    selected_fields = ["doctor_name", "time"]
    field_operators = FIELD_OPERATORS_MAP_BOOK_APPOINTMENT
    constraints_list = _generate_constraints(appointments_data, field_operators, selected_fields=selected_fields)

    return constraints_list


async def generate_appointment_booked_successfully_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    appointments_data = await _get_appointments_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_APPOINTMENT_BOOKED_SUCCESSFULLY
    field_map = {
        # "doctor_name": "doctorName",  # will remove field map and change field operator in both iwa and agent and also change dataset into modified appointment
        # "speciality": "specialty",
        "emergency_contact": {"field": "name", "dataset": MODIFIED_EMERGENCY_CONTACT},
        "emergency_phone": {"field": "phone", "dataset": MODIFIED_EMERGENCY_PHONE},
        "insurance_number": {"field": "number", "dataset": MODIFIED_INSURANCE_NUMBER},
        "insurance_provider": {"field": "provider", "dataset": MODIFIED_INSURANCE_PROVIDER},
        "notes": {"field": "notes", "dataset": MODIFIED_NOTES},
        "patient_name": {"field": "patient_name", "dataset": MODIFIED_PATIENT_NAMES},
        "patient_email": {"field": "email", "dataset": MODIFIED_PATIENT_EMAILS},
        "patient_phone": {"field": "contact", "dataset": MODIFIED_PATIENT_PHONES},
        "reason_for_visit": {"field": "reason", "dataset": MODIFIED_REASON_FOR_VISIT},
    }
    selected_fields = ["doctor_name", "time", "speciality", "patient_name", "patient_email", "patient_phone", "reason_for_visit"]
    constraints_list = _generate_constraints(appointments_data, field_operators, selected_fields=selected_fields, field_map=field_map)
    return constraints_list


async def generate_cancel_appointment_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    appointments_data = await _get_appointments_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_CANCEL_APPOINTMENT
    selected_fields = ["doctor_name", "time"]
    constraints_list = _generate_constraints(appointments_data, field_operators, selected_fields=selected_fields)
    return constraints_list


async def generate_view_prescription_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    prescriptions_data = await _get_prescriptions_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_VIEW_PRESCRIPTION
    selected_fields = ["medicine_name"]
    constraints_list = _generate_constraints(prescriptions_data, field_operators, selected_fields=selected_fields)
    return constraints_list


async def generate_filter_by_speciality_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    prescriptions_data = await _get_prescriptions_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_FILTER_BY_SPECIALITY
    selected_field = []
    constraints_list = _generate_constraints(prescriptions_data, field_operators, selected_fields=selected_field)
    return constraints_list


async def generate_refill_prescription_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    prescriptions_data = await _get_prescriptions_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_REFILL_PRESCRIPTION
    ELIGIBLE_PRESCRIPTIONS_FOR_REFILL = []
    for data in prescriptions_data:
        if data.get("refills_remaining") != 0 or data.get("refillsRemaining") != 0:
            new_data = copy.deepcopy(data)
            ELIGIBLE_PRESCRIPTIONS_FOR_REFILL.append(new_data)
    selected_field = []
    constraints_list = _generate_constraints(ELIGIBLE_PRESCRIPTIONS_FOR_REFILL, field_operators, selected_fields=selected_field)
    return constraints_list


async def generate_view_health_metrics_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    medical_records_data = await _get_medical_records_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_VIEW_HEALTH_METRICS
    selected_field = ["record_title"]
    constraint_list = _generate_constraints(medical_records_data, field_operators, selected_fields=selected_field)
    return constraint_list


async def generate_filter_by_category_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    medical_records_data = await _get_medical_records_data(task_url, dataset)
    field_operator = FIELD_OPERATORS_MAP_FILTER_BY_CATEGORY
    selected_field = []
    constraints_list = _generate_constraints(medical_records_data, field_operator, selected_fields=selected_field)
    return constraints_list


async def generate_view_doctor_profile_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operator = FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE
    selected_field = ["doctor_name"]
    constraints_list = _generate_constraints(doctors_data, field_operator, selected_fields=selected_field)
    return constraints_list


async def generate_contact_doctor_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operator = FIELD_OPERATORS_MAP_CONTACT_DOCTOR
    selected_field = ["doctor_name"]
    constraints_list = _generate_constraints(doctors_data, field_operator, selected_fields=selected_field)
    return constraints_list


async def generate_doctor_contact_successfully_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operator = FIELD_MAP_CONTACT_DOCTOR_SUCCESSFULLY
    MESSAGE = [
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
    MODIFIED_MESSAGE = [{"message": m} for m in MESSAGE]
    SUBJECT = [
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
    MODIFIED_SUBJECT = [{"subject": s} for s in SUBJECT]
    APPOINTMENT_REQUEST_DATASET = [
        {
            "appointment_request": True,
        },
        {
            "appointment_request": False,
        },
    ]
    field_map = {
        # "doctor_name": "name",
        # "speciality": "specialty",
        "patient_name": {"field": "patient_name", "dataset": MODIFIED_PATIENT_NAMES},
        "patient_email": {"field": "email", "dataset": MODIFIED_PATIENT_EMAILS},
        "patient_phone": {"field": "contact", "dataset": MODIFIED_PATIENT_PHONES},
        "message": {"field": "message", "dataset": MODIFIED_MESSAGE},
        "subject": {"field": "subject", "dataset": MODIFIED_SUBJECT},
        "appointment_request": {"field": "appointment_request", "dataset": APPOINTMENT_REQUEST_DATASET},
        "urgency": {"field": "urgency", "dataset": [{"urgency": a} for a in ["low", "medium", "high"]]},
        "preferred_contact_method": {"field": "option", "dataset": [{"option": i} for i in ["either", "email", "phone"]]},
    }
    selected_fields = ["doctor_name", "patient_name", "patient_email", "subject", "message", "appointment_request"]
    constraints_list = _generate_constraints(doctors_data, field_operator, selected_fields=selected_fields, field_map=field_map)
    return constraints_list


async def generate_cancel_contact_doctor_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, str]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_CANCEL_CONTACT_DOCTOR
    selected_field = ["doctor_name"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=selected_field)
    return constraints_list


async def generate_view_review_clicked_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, str]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_VIEW_REVIEW_CLICKED
    selected_field = ["doctor_name"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=selected_field)
    return constraints_list


async def generate_sort_reviews_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, str]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_SORT_REVIEWS
    field_map = {
        "sort_order": {"field": "order", "dataset": [{"order": e} for e in ["oldest", "highest", "lowest"]]},
    }
    selected_field = ["doctor_name", "sort_order"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=selected_field, field_map=field_map)
    return constraints_list


async def generate_filter_reviews_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, str]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operators = FIELD_OPERATORS_MAP_FILTER_REVIEWS
    field_map = {
        "filter_rating": {"field": "rating", "dataset": [{"rating": r} for r in [1, 2, 3, 4, 5]]},
    }
    selected_field = ["doctor_name", "filter_rating"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=selected_field, field_map=field_map)
    return constraints_list


async def generate_cancel_view_review_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, str]]:
    doctors_data = await _get_doctors_data(task_url, dataset)
    field_operator = FIELD_OPERATORS_MAP_CANCEL_VIEW_REVIEWS
    selected_field = ["doctor_name"]
    constraints_list = _generate_constraints(doctors_data, field_operator, selected_fields=selected_field)
    return constraints_list
