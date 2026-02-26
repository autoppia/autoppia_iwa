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
    FIELD_OPERATORS_MAP_CONTACT_DOCTOR,
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

# ============================================================================
# DATA FETCHING HELPERS
# ============================================================================
async def _ensure_entity_dataset(
    task_url: str | None,
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


# ============================================================================
# ENTITY DATA GETTERS
# ============================================================================
async def _get_appointments_data(task_url: str | None = None) -> list[dict]:
    """Extract appointments data from the cache dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="appointments", method="distribute", filter_key="specialty")
    appointments = dataset_dict.get("appointments", [])
    if appointments:
        return transform_appointments_to_modified(appointments)
    return []


async def _get_doctors_data(task_url: str | None = None) -> list[dict]:
    """Extract doctors data from the cache dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="doctors", method="distribute", filter_key="specialty")
    doctors = dataset_dict.get("doctors", [])
    if doctors:
        return transform_doctors_to_modified(doctors)
    return []


async def _get_prescriptions_data(task_url: str | None = None) -> list[dict]:
    """Extract prescriptions data from the cache dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="prescriptions", method="distribute", filter_key="category")
    prescriptions = dataset_dict.get("prescriptions", [])
    if prescriptions:
        return transform_prescriptions_to_modified(prescriptions)
    return []


async def _get_medical_records_data(task_url: str | None = None) -> list[dict]:
    """Extract medical records data from the cache dataset, or fetch from server if not available."""
    dataset_dict = await _ensure_entity_dataset(task_url, entity_type="medical-records", method="distribute", filter_key="type")
    medical_records = dataset_dict.get("medical-records", [])
    if medical_records:
        return transform_medical_records_to_modified(medical_records)
    return []


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def _get_nested_value(obj: dict, dotted_key: str, default: Any = None) -> Any:
    """Resolve nested field values using dotted keys (e.g. 'user.name')."""
    for key in dotted_key.split("."):
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return default
    return obj


# ============================================================================
# CONSTRAINT VALUE GENERATION HELPERS
# ============================================================================
def _normalize_rating_value(field_value: Any) -> float | None:
    """Normalize rating value to be between 0.0 and 5.0, rounded to 1 decimal."""
    try:
        rating = float(field_value)
        rating = max(0.0, min(5.0, rating))
        return round(rating, 1)
    except (TypeError, ValueError):
        return None


def _get_valid_ratings_from_dataset(field: str, dataset: list[dict[str, Any]], exclude_rating: float) -> list[float]:
    """Get valid normalized ratings from dataset excluding the specified rating."""
    valid = [v.get(field) for v in dataset if v.get(field) is not None]
    if not valid:
        return []
    normalized_valid: list[float] = []
    for value in valid:
        normalized = _normalize_rating_value(value)
        if normalized is not None and normalized != exclude_rating:
            normalized_valid.append(normalized)
    return normalized_valid


def _handle_rating_equals(rating: float) -> float:
    """Handle EQUALS operator for rating."""
    return rating


def _handle_rating_not_equals(rating: float, field: str, dataset: list[dict[str, Any]]) -> float:
    """Handle NOT_EQUALS operator for rating."""
    normalized_valid = _get_valid_ratings_from_dataset(field, dataset, rating)
    if normalized_valid:
        return random.choice(normalized_valid)
    delta = 0.5 if rating <= 4.5 else -0.5
    return round(max(0.0, min(5.0, rating + delta)), 1)


def _handle_rating_comparison(operator: ComparisonOperator, rating: float) -> float:
    """Handle comparison operators (GREATER_THAN, LESS_THAN, etc.) for rating."""
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
        return rating
    delta = random.choice([0.1, 0.2, 0.3, 0.4, 0.5])
    if operator == ComparisonOperator.GREATER_THAN:
        return round(max(0.0, rating - delta), 1)
    if operator == ComparisonOperator.LESS_THAN:
        return round(min(5.0, rating + delta), 1)
    return rating


def _handle_rating_constraint(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle constraint value generation for rating field."""
    rating = _normalize_rating_value(field_value)
    if rating is None:
        return None
    if operator == ComparisonOperator.EQUALS:
        return _handle_rating_equals(rating)
    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_rating_not_equals(rating, field, dataset)
    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        return _handle_rating_comparison(operator, rating)
    return rating


def _add_minutes_to_time(t: time, mins: int) -> time:
    """Add minutes to a time object."""
    full_dt = datetime.combine(date.today(), t) + timedelta(minutes=mins)
    return full_dt.time()


def _handle_datetime_constraint(operator: ComparisonOperator, field_value: datetime | date) -> datetime | date:
    """Handle constraint value generation for datetime/date types."""
    delta_days = random.randint(1, 5)
    if operator == ComparisonOperator.GREATER_THAN:
        return field_value - timedelta(days=delta_days)
    if operator == ComparisonOperator.LESS_THAN:
        return field_value + timedelta(days=delta_days)
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
        return field_value
    if operator == ComparisonOperator.NOT_EQUALS:
        return field_value + timedelta(days=delta_days + 1)
    return field_value


def _handle_time_constraint(operator: ComparisonOperator, field_value: time, field: str, dataset: list[dict[str, Any]]) -> time:
    """Handle constraint value generation for time type."""
    delta_minutes = random.choice([5, 10, 15, 30, 60])
    if operator == ComparisonOperator.GREATER_THAN:
        return _add_minutes_to_time(field_value, -delta_minutes)
    if operator == ComparisonOperator.LESS_THAN:
        return _add_minutes_to_time(field_value, delta_minutes)
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
        return field_value
    if operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
        return random.choice(valid) if valid else _add_minutes_to_time(field_value, delta_minutes + 5)
    return field_value


def _handle_equals_operator(field_value: Any) -> Any:
    """Handle EQUALS operator."""
    return field_value


def _handle_not_equals_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator."""
    valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
    return random.choice(valid) if valid else None


def _handle_contains_operator(field_value: str) -> str:
    """Handle CONTAINS operator for strings."""
    if len(field_value) > 2:
        start = random.randint(0, max(0, len(field_value) - 2))
        end = random.randint(start + 1, len(field_value))
        return field_value[start:end]
    return field_value


def _handle_not_contains_operator(field_value: str) -> str:
    """Handle NOT_CONTAINS operator for strings."""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for _ in range(100):
        test_str = "".join(random.choice(alphabet) for _ in range(3))
        if test_str.lower() not in field_value.lower():
            return test_str
    return "xyz"  # fallback


def _handle_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle IN_LIST operator."""
    all_values = list({v.get(field) for v in dataset if field in v})
    if not all_values:
        return [field_value]
    random.shuffle(all_values)
    subset = random.sample(all_values, min(2, len(all_values)))
    if field_value not in subset:
        subset.append(field_value)
    return list(set(subset))


def _handle_not_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle NOT_IN_LIST operator."""
    all_values = list({v.get(field) for v in dataset if field in v})
    if field_value in all_values:
        all_values.remove(field_value)
    return random.sample(all_values, min(2, len(all_values))) if all_values else []


def _handle_numeric_comparison(operator: ComparisonOperator, field_value: int | float) -> int | float | None:
    """Handle numeric comparison operators."""
    delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
    if operator == ComparisonOperator.GREATER_THAN:
        return field_value - delta
    if operator == ComparisonOperator.LESS_THAN:
        return field_value + delta
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
        return field_value
    return None


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
        return _handle_rating_constraint(operator, field_value, field, dataset)

    if isinstance(field_value, datetime | date):
        return _handle_datetime_constraint(operator, field_value)

    if isinstance(field_value, time):
        return _handle_time_constraint(operator, field_value, field, dataset)

    if operator == ComparisonOperator.EQUALS:
        return _handle_equals_operator(field_value)

    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_not_equals_operator(field_value, field, dataset)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        return _handle_contains_operator(field_value)

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return _handle_not_contains_operator(field_value)

    if operator == ComparisonOperator.IN_LIST:
        return _handle_in_list_operator(field_value, field, dataset)

    if operator == ComparisonOperator.NOT_IN_LIST:
        return _handle_not_in_list_operator(field_value, field, dataset)

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        return _handle_numeric_comparison(operator, field_value)

    return None


# ============================================================================
# CONSTRAINT GENERATION HELPERS
# ============================================================================
def _process_list_field(new_field: list[str], sample_data: dict[str, Any]) -> tuple[Any, str | None]:
    """Process field mapping when new_field is a list."""
    random.shuffle(new_field)
    for f in new_field:
        field_value = sample_data.get(f)
        if field_value is not None:
            return field_value, f
    return None, None


def _process_string_field(new_field: str, sample_data: dict[str, Any]) -> Any:
    """Process field mapping when new_field is a string."""
    if "." in new_field:
        return _get_nested_value(sample_data, new_field)
    return sample_data.get(new_field)


def _process_dict_field(new_field: dict[str, Any], op: ComparisonOperator) -> tuple[Any, Any, str]:
    """Process field mapping when new_field is a dict."""
    custom_dataset = new_field.get("dataset", [])
    new_field_name = new_field.get("field", "")
    field_value = choice(custom_dataset).get(new_field_name) if custom_dataset else None
    constraint_value = None
    if new_field_name and field_value is not None:
        constraint_value = _generate_constraint_value(op, field_value, new_field_name, dataset=custom_dataset)
    return field_value, constraint_value, new_field_name


def _process_field_mapping(new_field: Any, sample_data: dict[str, Any], op: ComparisonOperator) -> tuple[Any, Any, str]:
    """Process field mapping and return field_value, constraint_value, and new_field_name."""
    if isinstance(new_field, list):
        field_value, resolved_field = _process_list_field(new_field, sample_data)
        return field_value, None, resolved_field

    if isinstance(new_field, str):
        field_value = _process_string_field(new_field, sample_data)
        return field_value, None, new_field

    if isinstance(new_field, dict):
        return _process_dict_field(new_field, op)

    return None, None, new_field


def _select_fields_for_constraints(
    field_operators: dict, selected_fields: list | None, min_constraints: int, num_constraints: int | None
) -> list[str]:
    """Select fields for constraint generation."""
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

    return selected_fields


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
    field_map = field_map or {}

    selected_fields = _select_fields_for_constraints(field_operators, selected_fields, min_constraints or 1, num_constraints)

    for field in selected_fields:
        allowed_ops = field_operators.get(field, [])
        if not allowed_ops:
            continue

        op = ComparisonOperator(choice(allowed_ops))
        new_field = field_map.get(field, field)

        field_value, constraint_value, new_field_name = _process_field_mapping(new_field, sample_data, op)

        if field_value is None:
            continue

        if constraint_value is None:
            constraint_value = _generate_constraint_value(op, field_value, new_field_name, dataset)

        if constraint_value is not None:
            constraint = create_constraint_dict(field, op, constraint_value)
            all_constraints.append(constraint)

    return all_constraints


# ============================================================================
# CONSTRAINT GENERATION FUNCTIONS
# ============================================================================
# APPOINTMENT CONSTRAINTS
async def generate_open_appointment_form_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for OPEN_APPOINTMENT_FORM: doctor_name, speciality, date, time from appointments (DB first). num_constraints=0..1 to keep reviewer consistency while allowing lateral field picks."""
    appointments_data = await _get_appointments_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_OPEN_APPOINTMENT_FORM
    core_fields = ["doctor_name", "speciality", "date", "time"]
    constraints_list = _generate_constraints(appointments_data, field_operators, selected_fields=core_fields, num_constraints=random.randint(0, 1))
    return constraints_list


async def generate_appointment_booked_successfully_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    appointments_data = await _get_appointments_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_APPOINTMENT_BOOKED_SUCCESSFULLY
    field_map = {
        # "doctor_name": "doctorName",  # will remove field map and change field operator in both iwa and agent and also change dataset into modified appointment
        # "speciality": "speciality",
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
    selected_fields = ["doctor_name", "time", "speciality", "patient_name", "patient_email", "patient_phone", "reason_for_visit"]
    constraints_list = _generate_constraints(appointments_data, field_operators, selected_fields=selected_fields, field_map=field_map)
    return constraints_list


async def generate_request_quick_appointment_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for REQUEST_QUICK_APPOINTMENT: speciality from doctors, patient fields from MODIFIED_*."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_REQUEST_QUICK_APPOINTMENT
    field_map = {
        "speciality": "speciality",
        "patient_name": {"field": "patient_name", "dataset": MODIFIED_PATIENT_NAMES},
        "patient_email": {"field": "email", "dataset": MODIFIED_PATIENT_EMAILS},
        "patient_phone": {"field": "contact", "dataset": MODIFIED_PATIENT_PHONES},
    }
    core_fields = ["speciality", "patient_name"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=core_fields, field_map=field_map)
    return constraints_list


async def generate_search_appointment_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for SEARCH_APPOINTMENT: doctor_name, speciality, date from appointments (DB first)."""
    appointments_data = await _get_appointments_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_SEARCH_APPOINTMENT
    core_fields = ["doctor_name", "speciality", "date"]
    field_map = {"speciality": "speciality"}
    constraints_list = _generate_constraints(appointments_data, field_operators, selected_fields=core_fields, field_map=field_map)
    return constraints_list


# DOCTOR CONSTRAINTS
async def generate_search_doctors_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for SEARCH_DOCTORS: doctor_name, speciality, language from doctors page (Search button)."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_SEARCH_DOCTORS
    field_map = {
        "doctor_name": "name",
        "speciality": "speciality",
        "language": "primary_language",
    }
    core_fields = ["doctor_name", "speciality", "language"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=core_fields, field_map=field_map)
    return constraints_list


# PRESCRIPTION CONSTRAINTS
async def generate_search_prescription_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for SEARCH_PRESCRIPTION: medicine_name, doctor_name from prescriptions (DB first)."""
    prescriptions_data = await _get_prescriptions_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_SEARCH_PRESCRIPTION
    core_fields = ["medicine_name", "doctor_name"]
    constraints_list = _generate_constraints(prescriptions_data, field_operators, selected_fields=core_fields)
    return constraints_list


async def generate_view_prescription_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_PRESCRIPTION: medicine_name, doctor_name, start_date, dosage, status, category from prescriptions."""
    prescriptions_data = await _get_prescriptions_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_VIEW_PRESCRIPTION
    core_fields = ["medicine_name", "doctor_name", "start_date"]
    constraints_list = _generate_constraints(prescriptions_data, field_operators, selected_fields=core_fields)
    return constraints_list


async def generate_refill_prescription_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for REFILL_PRESCRIPTION: medicine_name, doctor_name from eligible prescriptions (DB first). num_constraints=0..1 to keep reviewer consistency while allowing lateral field picks."""
    prescriptions_data = await _get_prescriptions_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_REFILL_PRESCRIPTION
    ELIGIBLE_PRESCRIPTIONS_FOR_REFILL = []
    for data in prescriptions_data:
        if data.get("refills_remaining") != 0 or data.get("refillsRemaining") != 0:
            new_data = copy.deepcopy(data)
            ELIGIBLE_PRESCRIPTIONS_FOR_REFILL.append(new_data)
    # Fallback: use full prescriptions if no eligible ones (avoids 0 tasks when subset has no refills)
    data_source = ELIGIBLE_PRESCRIPTIONS_FOR_REFILL if ELIGIBLE_PRESCRIPTIONS_FOR_REFILL else prescriptions_data
    core_fields = ["medicine_name", "doctor_name"]
    constraints_list = _generate_constraints(data_source, field_operators, selected_fields=core_fields, num_constraints=random.randint(0, 1))
    return constraints_list


# MEDICAL ANALYSIS CONSTRAINTS
async def generate_search_medical_analysis_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for SEARCH_MEDICAL_ANALYSIS: record_title, doctor_name from medical records (DB first)."""
    medical_records_data = await _get_medical_records_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_SEARCH_MEDICAL_ANALYSIS
    core_fields = ["record_title", "doctor_name"]
    constraints_list = _generate_constraints(medical_records_data, field_operators, selected_fields=core_fields)
    return constraints_list


async def generate_view_medical_analysis_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_MEDICAL_ANALYSIS: record_title, doctor_name, record_type from medical records (DB first)."""
    medical_records_data = await _get_medical_records_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_VIEW_MEDICAL_ANALYSIS
    core_fields = ["record_title", "doctor_name", "record_type"]
    constraints_list = _generate_constraints(medical_records_data, field_operators, selected_fields=core_fields)
    return constraints_list


async def generate_view_doctor_profile_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_DOCTOR_PROFILE: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE
    field_map = {"language": "primary_language"}
    core_fields = ["doctor_name", "speciality", "rating", "consultation_fee", "language"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=core_fields, field_map=field_map)
    return constraints_list


async def generate_view_doctor_education_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_DOCTOR_EDUCATION: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_VIEW_DOCTOR_EDUCATION
    field_map = {"language": "primary_language"}
    core_fields = ["doctor_name", "speciality", "rating", "consultation_fee", "language"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=core_fields, field_map=field_map)
    return constraints_list


async def generate_view_doctor_availability_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_DOCTOR_AVAILABILITY: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_VIEW_DOCTOR_AVAILABILITY
    field_map = {"language": "primary_language"}
    core_fields = ["doctor_name", "speciality", "rating", "consultation_fee", "language"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=core_fields, field_map=field_map)
    return constraints_list


async def generate_open_contact_doctor_form_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for OPEN_CONTACT_DOCTOR_FORM: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_OPEN_CONTACT_DOCTOR_FORM
    field_map = {"language": "primary_language"}
    core_fields = ["doctor_name", "speciality", "rating", "consultation_fee", "language"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=core_fields, field_map=field_map)
    return constraints_list


async def generate_contact_doctor_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for CONTACT_DOCTOR: doctor_name, speciality, rating, consultation_fee, language from doctors (DB first)."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_CONTACT_DOCTOR
    field_map = {"language": "primary_language"}
    core_fields = ["doctor_name"]
    constraints_list = _generate_constraints(doctors_data, field_operators, field_map=field_map, selected_fields=core_fields)
    return constraints_list


async def generate_doctor_contact_successfully_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    doctors_data = await _get_doctors_data(task_url)
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
        # "speciality": "speciality",
        "patient_name": {"field": "patient_name", "dataset": MODIFIED_PATIENT_NAMES},
        "patient_email": {"field": "email", "dataset": MODIFIED_PATIENT_EMAILS},
        "patient_phone": {"field": "contact", "dataset": MODIFIED_PATIENT_PHONES},
        "message": {"field": "message", "dataset": MODIFIED_MESSAGE},
        "subject": {"field": "subject", "dataset": MODIFIED_SUBJECT},
        "appointment_request": {"field": "appointment_request", "dataset": APPOINTMENT_REQUEST_DATASET},
        "urgency": {"field": "urgency", "dataset": [{"urgency": a} for a in ["low", "medium", "high"]]},
        "preferred_contact_method": {"field": "option", "dataset": [{"option": i} for i in ["either", "email", "phone"]]},
    }
    selected_fields = ["doctor_name", "patient_name", "subject"]
    constraints_list = _generate_constraints(doctors_data, field_operator, selected_fields=selected_fields, field_map=field_map)
    return constraints_list


async def generate_filter_doctor_reviews_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate constraints for FILTER_DOCTOR_REVIEWS: doctor_name, filter_rating, sort_order (DB first). num_constraints=0..1 to keep reviewer consistency while allowing lateral field picks (e.g. speciality)."""
    doctors_data = await _get_doctors_data(task_url)
    field_operators = FIELD_OPERATORS_MAP_FILTER_DOCTOR_REVIEWS
    field_map = {
        "filter_rating": {"field": "rating", "dataset": [{"rating": r} for r in [1, 2, 3, 4, 5]]},
        "sort_order": {"field": "sort_order", "dataset": [{"sort_order": o} for o in ["newest", "oldest", "highest", "lowest"]]},
    }
    core_fields = ["doctor_name", "filter_rating", "sort_order"]
    constraints_list = _generate_constraints(doctors_data, field_operators, selected_fields=core_fields, field_map=field_map, num_constraints=random.randint(0, 1))
    return constraints_list
