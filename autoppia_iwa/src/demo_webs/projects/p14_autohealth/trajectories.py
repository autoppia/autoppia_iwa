from __future__ import annotations

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions import (
    ClickAction,
    NavigateAction,
    SelectDropDownOptionAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

PROJECT_NUMBER = 14
WEB_PROJECT_ID = "autohealth"

BASE = "http://localhost:8013"


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


def _test(testid: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="data-testid", value=testid)


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _booking_modal_scope() -> str:
    # AutoHealth DialogContent is a plain div (no role=dialog); scope from the modal title.
    return "//h2[contains(.,'Book Appointment')]/ancestor::div[contains(@class,'shadow-lg')][contains(@class,'rounded-lg')][1]"


def _contact_modal_scope() -> str:
    return "//h2[starts-with(normalize-space(.),'Contact')]/ancestor::div[contains(@class,'shadow-lg')][contains(@class,'rounded-lg')][1]"


def _reviews_modal_scope() -> str:
    return "//h2[contains(.,'Patient Reviews')]/ancestor::div[contains(@class,'shadow-lg')][contains(@class,'rounded-lg')][1]"


def _booking_label_input(label_fragment: str) -> Selector:
    return _xp(f"{_booking_modal_scope()}//label[contains(.,'{label_fragment}')]/following::input[1]")


def _booking_label_textarea(label_fragment: str) -> Selector:
    return _xp(f"{_booking_modal_scope()}//label[contains(.,'{label_fragment}')]/following::textarea[1]")


def _doctor_list_view_profile_button(doctor_name: str, *, exact: bool = True) -> Selector:
    """Card on /doctors: CardTitle is h3; decoy wrappers can break older div[.//*[name]] xpaths."""
    name_pred = f"normalize-space()='{doctor_name}'" if exact else f"contains(normalize-space(),'{doctor_name}')"
    return _xp(
        f"(//div[contains(@class,'grid')][contains(@class,'gap-4')]"
        f"//h3[{name_pred}]/ancestor::div[contains(@class,'rounded-lg')][contains(@class,'border')][1]"
        f"//a[contains(@href,'/doctors/')]//button)[1]"
    )


def _first_doctor_list_view_profile_matching_name_constraint(forbidden_substr: str) -> Selector:
    """First grid card whose visible text does not contain forbidden_substr (case-insensitive)."""
    f = forbidden_substr
    return _xp(
        f"(//div[contains(@class,'grid')][contains(@class,'gap-4')]"
        f"//div[contains(@class,'rounded-lg')][contains(@class,'border')]"
        f"[not(contains(translate(.,'{f.upper()}','{f.lower()}'),'{f.lower()}'))]"
        f"//a[contains(@href,'/doctors/')]//button)[1]"
    )


def _first_doctor_list_view_profile_in_grid() -> Selector:
    """First doctor card in the main grid after filters (use when name search is omitted)."""
    return _xp("(//div[contains(@class,'grid')][contains(@class,'gap-4')]//div[contains(@class,'rounded-lg')][contains(@class,'border')]//a[contains(@href,'/doctors/')]//button)[1]")


def _task_home_then(path: str, seed: int) -> list[BaseAction]:
    """Match IWA task entry URL (/?seed=) then open the same seed on a sub-route."""
    path = path.strip()
    if path.startswith("/"):
        path = path[1:]
    sub_url = f"{BASE}/{path}?seed={seed}" if path else f"{BASE}/?seed={seed}"
    return [
        NavigateAction(url=f"{BASE}/?seed={seed}"),
        WaitAction(time_seconds=0.45),
        NavigateAction(url=sub_url),
        WaitAction(time_seconds=0.55),
    ]


def _doctors_search_then_open_profile(
    seed: int,
    *,
    doctor_name: str | None = None,
    specialty: str | None = None,
    language: str | None = None,
    doctor_card_name_exact: bool = True,
    forbidden_card_substr: str | None = None,
) -> list[BaseAction]:
    actions: list[BaseAction] = _task_home_then("doctors", seed)
    if doctor_name:
        actions.append(TypeAction(selector=_test("doctor-name-search"), text=doctor_name))
    if specialty:
        actions.append(SelectDropDownOptionAction(selector=_test("doctor-specialty-filter"), text=specialty))
    if language:
        actions.append(SelectDropDownOptionAction(selector=_test("doctor-language-filter"), text=language))
    if doctor_name:
        profile_selector = _doctor_list_view_profile_button(doctor_name, exact=doctor_card_name_exact)
    elif forbidden_card_substr:
        profile_selector = _first_doctor_list_view_profile_matching_name_constraint(forbidden_card_substr)
    else:
        profile_selector = _first_doctor_list_view_profile_in_grid()
    actions.extend(
        [
            ClickAction(selector=_test("doctors-search-button")),
            WaitAction(time_seconds=0.9),
            ClickAction(selector=profile_selector),
            WaitAction(time_seconds=0.5),
        ]
    )
    return actions


# --- CheckEventTest payloads (import-time init from literals below; no JSON I/O). ---
_RAW_TESTS: dict[str, list[dict]] = {
    "OPEN_APPOINTMENT_FORM": [
        {
            "type": "CheckEventTest",
            "event_name": "OPEN_APPOINTMENT_FORM",
            "event_criteria": {"doctor_name": {"operator": "not_contains", "value": "mbb"}, "speciality": {"operator": "not_contains", "value": "izo"}, "date": "2025-12-14", "time": "09:30 AM"},
            "description": "Check if specific event was triggered",
        }
    ],
    "APPOINTMENT_BOOKED_SUCCESSFULLY": [
        {
            "type": "CheckEventTest",
            "event_name": "APPOINTMENT_BOOKED_SUCCESSFULLY",
            "event_criteria": {
                "doctor_name": {"operator": "not_contains", "value": "jdi"},
                "time": "01:15 PM",
                "speciality": {"operator": "not_contains", "value": "utt"},
                "patient_name": {"operator": "contains", "value": "a"},
                "patient_email": {"operator": "not_contains", "value": "frd"},
                "patient_phone": "+1-202-555-0153",
                "reason_for_visit": "Chronic migraine management",
                "insurance_provider": {"operator": "not_contains", "value": "qul"},
                "emergency_contact": {"operator": "contains", "value": "Jo"},
                "notes": {"operator": "contains", "value": "ipt"},
                "date": "2025-10-15",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "REQUEST_QUICK_APPOINTMENT": [
        {
            "type": "CheckEventTest",
            "event_name": "REQUEST_QUICK_APPOINTMENT",
            "event_criteria": {
                "speciality": "Pediatrics",
                "patient_name": {"operator": "not_equals", "value": "William Taylor"},
                "patient_email": {"operator": "not_contains", "value": "tas"},
                "patient_phone": {"operator": "not_equals", "value": "+1-202-555-0151"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_APPOINTMENT": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_APPOINTMENT",
            "event_criteria": {"doctor_name": {"operator": "not_contains", "value": "yyw"}, "speciality": "Cardiology", "date": "2025-10-12"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_DOCTORS": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_DOCTORS",
            "event_criteria": {"speciality": {"operator": "contains", "value": "ily Med"}, "language": {"operator": "not_contains", "value": "nhh"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_PRESCRIPTION": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_PRESCRIPTION",
            "event_criteria": {"medicine_name": {"operator": "not_contains", "value": "gby"}, "doctor_name": {"operator": "not_equals", "value": "Dr. James Patel"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "REFILL_PRESCRIPTION": [
        {
            "type": "CheckEventTest",
            "event_name": "REFILL_PRESCRIPTION",
            "event_criteria": {"medicine_name": {"operator": "not_contains", "value": "kaa"}, "doctor_name": {"operator": "contains", "value": "cha"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_PRESCRIPTION": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_PRESCRIPTION",
            "event_criteria": {
                "medicine_name": {"operator": "not_contains", "value": "iid"},
                "doctor_name": "Dr. Daniel Martin",
                "start_date": "2024-07-05",
                "status": {"operator": "not_contains", "value": "two"},
                "dosage": {"operator": "contains", "value": "l"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_MEDICAL_ANALYSIS": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_MEDICAL_ANALYSIS",
            "event_criteria": {"record_title": {"operator": "not_contains", "value": "shw"}, "doctor_name": "Dr. Barbara Ruiz"},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_MEDICAL_ANALYSIS": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_MEDICAL_ANALYSIS",
            "event_criteria": {
                "record_title": {"operator": "contains", "value": "-up"},
                "doctor_name": {"operator": "not_contains", "value": "xjl"},
                "record_type": {"operator": "not_contains", "value": "xhl"},
                "record_date": {"operator": "not_equals", "value": "2024-09-29"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_DOCTOR_PROFILE": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_DOCTOR_PROFILE",
            "event_criteria": {
                "doctor_name": {"operator": "contains", "value": "m"},
                "speciality": {"operator": "contains", "value": "ha"},
                "rating": {"operator": "greater_equal", "value": 4.8},
                "consultation_fee": {"operator": "less_than", "value": 351},
                "language": {"operator": "contains", "value": "is"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_DOCTOR_EDUCATION": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_DOCTOR_EDUCATION",
            "event_criteria": {
                "doctor_name": "Dr. Thomas Thomas",
                "speciality": {"operator": "not_equals", "value": "Internal Medicine"},
                "rating": {"operator": "greater_than", "value": 3.6},
                "consultation_fee": {"operator": "greater_than", "value": 163},
                "language": "English",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_DOCTOR_AVAILABILITY": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_DOCTOR_AVAILABILITY",
            "event_criteria": {
                "doctor_name": {"operator": "not_equals", "value": "Dr. Linda Rodriguez"},
                "speciality": "Rheumatology",
                "rating": {"operator": "less_equal", "value": 4.7},
                "consultation_fee": {"operator": "not_equals", "value": 298},
                "language": "English",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "FILTER_DOCTOR_REVIEWS": [
        {
            "type": "CheckEventTest",
            "event_name": "FILTER_DOCTOR_REVIEWS",
            "event_criteria": {
                "doctor_name": {"operator": "not_contains", "value": "cmg"},
                "filter_rating": {"operator": "greater_equal", "value": 5.0},
                "sort_order": {"operator": "contains", "value": "newe"},
                "speciality": {"operator": "not_equals", "value": "Pediatrics"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "OPEN_CONTACT_DOCTOR_FORM": [
        {
            "type": "CheckEventTest",
            "event_name": "OPEN_CONTACT_DOCTOR_FORM",
            "event_criteria": {
                "doctor_name": {"operator": "not_contains", "value": "huy"},
                "speciality": {"operator": "not_contains", "value": "zei"},
                "rating": {"operator": "not_equals", "value": 3.9},
                "consultation_fee": {"operator": "less_than", "value": 257},
                "language": {"operator": "contains", "value": "l"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CONTACT_DOCTOR": [
        {
            "type": "CheckEventTest",
            "event_name": "CONTACT_DOCTOR",
            "event_criteria": {
                "doctor_name": {"operator": "not_equals", "value": "Dr. Linda Hernandez"},
                "patient_name": {"operator": "contains", "value": "is"},
                "subject": {"operator": "contains", "value": " M"},
                "urgency": {"operator": "not_contains", "value": "lsn"},
                "appointment_request": {"operator": "not_equals", "value": False},
                "message": {"operator": "not_contains", "value": "cxs"},
                "speciality": {"operator": "not_equals", "value": "Neurology"},
                "patient_phone": "+1-202-555-0143",
                "preferred_contact_method": "phone",
                "patient_email": {"operator": "contains", "value": "davi"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


OPEN_APPOINTMENT_FORM = _uc(
    "OPEN_APPOINTMENT_FORM",
    prompt="Open appointment form where doctor_name does NOT contain 'mbb' and speciality does NOT contain 'izo' and date equals '2025-12-14' and time equals '09:30 AM'",
    actions=[
        *_task_home_then("appointments", 335),
        TypeAction(selector=_id("date-filter"), text="2025-12-14"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_test("appointments-search-button")),
        WaitAction(time_seconds=0.9),
        ClickAction(
            selector=_xp(
                "//tbody/tr[contains(.,'09:30 AM') and "
                "(contains(.,'2025-12-14') or contains(.,'12/14/2025')) and "
                "not(contains(translate(.,'MBB','mbb'),'mbb')) and "
                "not(contains(translate(.,'IZO','izo'),'izo'))]//button[1]"
            )
        ),
        WaitAction(time_seconds=0.35),
    ],
)

APPOINTMENT_BOOKED_SUCCESSFULLY = _uc(
    "APPOINTMENT_BOOKED_SUCCESSFULLY",
    prompt="Book an appointment where doctor_name does NOT contain 'jdi' and time equals '01:15 PM' and speciality does NOT contain 'utt' and patient_name contains 'a' and patient_email does NOT contain 'frd' and patient_phone equals '+1-202-555-0153' and reason_for_visit equals 'Chronic migraine management' and insurance_provider does NOT contain 'qul' and emergency_contact contains 'Jo' and notes contains 'ipt' and date equals '2025-10-15'",
    actions=[
        *_task_home_then("appointments", 22),
        TypeAction(selector=_id("date-filter"), text="2025-10-15"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_test("appointments-search-button")),
        WaitAction(time_seconds=0.85),
        ClickAction(
            selector=_xp(
                "//tbody/tr[contains(.,'01:15 PM') and "
                "(contains(.,'2025-10-15') or contains(.,'10/15/2025')) and "
                "not(contains(translate(.,'JDI','jdi'),'jdi')) and "
                "not(contains(translate(.,'UTT','utt'),'utt'))]//button[1]"
            )
        ),
        WaitAction(time_seconds=0.45),
        TypeAction(selector=_booking_label_input("Full Name"), text="Maria Anderson"),
        TypeAction(selector=_booking_label_input("Email Address"), text="maria.anderson@example.com"),
        TypeAction(selector=_booking_label_input("Phone Number"), text="+1-202-555-0153"),
        TypeAction(selector=_booking_label_input("Reason for Visit"), text="Chronic migraine management"),
        TypeAction(selector=_booking_label_input("Insurance Provider"), text="Aetna"),
        TypeAction(selector=_booking_label_input("Policy Number"), text="INS-8844-2025"),
        TypeAction(selector=_booking_label_input("Emergency Contact Name"), text="Jordan Cole"),
        TypeAction(selector=_booking_label_input("Emergency Contact Phone"), text="+1-202-555-0100"),
        TypeAction(
            selector=_booking_label_textarea("Notes"),
            text="Please review my prescription script.",
        ),
        ClickAction(selector=_test("confirm-appointment-btn")),
        WaitAction(time_seconds=0.55),
    ],
)

REQUEST_QUICK_APPOINTMENT = _uc(
    "REQUEST_QUICK_APPOINTMENT",
    prompt="Request quick appointment where speciality equals 'Pediatrics' and patient_name not equals 'William Taylor' and patient_email not contains 'tas' and patient_phone not equals '+1-202-555-0151'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed=203"),
        WaitAction(time_seconds=0.55),
        TypeAction(selector=_xp("//label[contains(.,'Full Name')]/following::input[1]"), text="Jordan Smith"),
        TypeAction(selector=_xp("//label[contains(.,'Email')]/following::input[1]"), text="jordan.smith@example.org"),
        TypeAction(selector=_xp("//label[contains(.,'Phone Number')]/following::input[1]"), text="+1-202-555-0199"),
        TypeAction(selector=_xp("//label[contains(.,'Speciality')]/following::input[1]"), text="Pediatrics"),
        WaitAction(time_seconds=0.3),
        ClickAction(selector=_xp("//div[contains(@class,'z-50')]//button[normalize-space(.)='Pediatrics']")),
        ClickAction(selector=_test("request-appointment-submit")),
        WaitAction(time_seconds=0.45),
    ],
)

SEARCH_APPOINTMENT = _uc(
    "SEARCH_APPOINTMENT",
    prompt="Retrieve details of appointments where doctor_name does NOT contain 'yyw', speciality equals 'Cardiology', and date equals '2025-10-12'",
    actions=[
        *_task_home_then("appointments", 812),
        TypeAction(selector=_id("doctor-filter"), text="Dr."),
        WaitAction(time_seconds=0.3),
        TypeAction(selector=_id("specialty-filter"), text="Cardiology"),
        WaitAction(time_seconds=0.3),
        ClickAction(selector=_xp("//div[contains(@class,'z-50')]//button[contains(.,'Cardiology')]")),
        TypeAction(selector=_id("date-filter"), text="2025-10-12"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_test("appointments-search-button")),
        WaitAction(time_seconds=0.55),
    ],
)

SEARCH_DOCTORS = _uc(
    "SEARCH_DOCTORS",
    prompt="Retrieve details of doctors where speciality contains 'ily Med' and language not contains 'nhh'",
    actions=[
        *_task_home_then("doctors", 837),
        SelectDropDownOptionAction(selector=_test("doctor-specialty-filter"), text="Family Medicine"),
        SelectDropDownOptionAction(selector=_test("doctor-language-filter"), text="English"),
        ClickAction(selector=_test("doctors-search-button")),
        WaitAction(time_seconds=0.45),
    ],
)

SEARCH_PRESCRIPTION = _uc(
    "SEARCH_PRESCRIPTION",
    prompt="Show me prescriptions where medicine_name does NOT contain 'gby' and doctor_name does NOT equal 'Dr. James Patel'",
    actions=[
        *_task_home_then("prescriptions", 546),
        TypeAction(selector=_test("search-prescription-medicine"), text="Vitamin"),
        TypeAction(selector=_test("search-prescription-doctor"), text="Alice"),
        ClickAction(selector=_test("prescriptions-search-button")),
        WaitAction(time_seconds=0.45),
    ],
)

REFILL_PRESCRIPTION = _uc(
    "REFILL_PRESCRIPTION",
    prompt="Refill prescription where medicine_name NOT contains 'kaa' and doctor_name contains 'cha'",
    actions=[
        *_task_home_then("prescriptions", 110),
        TypeAction(selector=_test("search-prescription-doctor"), text="cha"),
        ClickAction(selector=_test("prescriptions-search-button")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//tr[contains(translate(.,'CHA','cha'),'cha')]//button[@data-testid='view-prescription-btn'][1]")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_test("request-refill-btn")),
        WaitAction(time_seconds=0.4),
    ],
)

VIEW_PRESCRIPTION = _uc(
    "VIEW_PRESCRIPTION",
    prompt="Show details for a prescription where medicine_name does NOT contain 'iid', doctor_name equals 'Dr. Daniel Martin', start_date equals '2024-07-05', status does NOT contain 'two', and dosage contains 'l'",
    actions=[
        *_task_home_then("prescriptions", 861),
        TypeAction(selector=_test("search-prescription-doctor"), text="Daniel Martin"),
        ClickAction(selector=_test("prescriptions-search-button")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//tr[contains(.,'Dr. Daniel Martin') and contains(.,'2024-07-05')]//button[@data-testid='view-prescription-btn'][1]")),
        WaitAction(time_seconds=0.4),
    ],
)

SEARCH_MEDICAL_ANALYSIS = _uc(
    "SEARCH_MEDICAL_ANALYSIS",
    prompt="Show details for medical records where record_title does NOT contain 'shw' and doctor_name equals 'Dr. Barbara Ruiz'",
    actions=[
        *_task_home_then("medical-records", 965),
        TypeAction(selector=_test("search-record-title"), text="Allergy"),
        TypeAction(selector=_test("search-record-doctor"), text="Dr. Barbara Ruiz"),
        ClickAction(selector=_test("medical-records-search-button")),
        WaitAction(time_seconds=0.45),
    ],
)

VIEW_MEDICAL_ANALYSIS = _uc(
    "VIEW_MEDICAL_ANALYSIS",
    prompt="View medical analysis where record_title contains '-up' AND doctor_name does NOT contain 'xjl' AND record_type does NOT contain 'xhl' AND record_date does NOT equal '2024-09-29'",
    actions=[
        *_task_home_then("medical-records", 62),
        TypeAction(selector=_test("search-record-title"), text="-up"),
        ClickAction(selector=_test("medical-records-search-button")),
        WaitAction(time_seconds=0.5),
        ClickAction(
            selector=_xp(
                "//div[contains(@class,'rounded-lg')][contains(@class,'border')]"
                "[contains(.,'-up')][not(contains(.,'2024-09-29'))]"
                "[not(contains(translate(.,'XJL','xjl'),'xjl'))]"
                "//button[@data-testid='view-record-btn'][1]"
            )
        ),
        WaitAction(time_seconds=0.35),
    ],
)

VIEW_DOCTOR_PROFILE = _uc(
    "VIEW_DOCTOR_PROFILE",
    prompt="Show details for a doctor where doctor_name contains 'm', speciality contains 'ha', rating is greater equal '4.8', consultation_fee is less than '351', and language contains 'is'",
    actions=[
        *_task_home_then("doctors", 10),
        SelectDropDownOptionAction(selector=_test("doctor-specialty-filter"), text="Ophthalmology"),
        SelectDropDownOptionAction(selector=_test("doctor-language-filter"), text="English"),
        SelectDropDownOptionAction(selector=_test("doctors-sort-by"), text="Rating"),
        WaitAction(time_seconds=0.35),
        SelectDropDownOptionAction(selector=_test("doctors-sort-order"), text="Highest first"),
        ClickAction(selector=_test("doctors-search-button")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_first_doctor_list_view_profile_in_grid()),
        WaitAction(time_seconds=0.45),
    ],
)

VIEW_DOCTOR_EDUCATION = _uc(
    "VIEW_DOCTOR_EDUCATION",
    prompt="Retrieve details of a doctor education where doctor_name equals 'Dr. Thomas Thomas' AND speciality not equals 'Internal Medicine' AND rating greater than 3.6 AND consultation_fee greater than 163 AND language equals 'English'",
    actions=[
        *_doctors_search_then_open_profile(229, doctor_name="Dr. Thomas Thomas"),
        ClickAction(selector=_xp("//button[contains(.,'Education')]")),
        WaitAction(time_seconds=0.4),
    ],
)

VIEW_DOCTOR_AVAILABILITY = _uc(
    "VIEW_DOCTOR_AVAILABILITY",
    prompt="Show details for doctor availability where doctor_name is NOT 'Dr. Linda Rodriguez' AND speciality equals 'Rheumatology' AND rating less equal 4.7 AND consultation_fee is NOT '298' AND language equals 'English'",
    actions=[
        *_doctors_search_then_open_profile(410, specialty="Rheumatology", language="English"),
        ClickAction(
            selector=_xp(
                "(//div[contains(@class,'grid')][contains(@class,'gap-4')]"
                "//h3[normalize-space()!='Dr. Linda Rodriguez']"
                "/ancestor::div[contains(@class,'rounded-lg')][contains(@class,'border')][1]"
                "//a[contains(@href,'/doctors/')]//button)[1]"
            )
        ),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//button[contains(.,'Availability')]")),
        WaitAction(time_seconds=0.4),
    ],
)

FILTER_DOCTOR_REVIEWS = _uc(
    "FILTER_DOCTOR_REVIEWS",
    prompt="Show details for doctor reviews where doctor_name does NOT contain 'cmg', filter_rating is greater than or equal to '5.0', sort_order contains 'newe', and speciality is NOT equal to 'Pediatrics'",
    actions=[
        *_task_home_then("doctors", 546),
        SelectDropDownOptionAction(selector=_test("doctor-specialty-filter"), text="Cardiology"),
        ClickAction(selector=_test("doctors-search-button")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_first_doctor_list_view_profile_matching_name_constraint("cmg")),
        WaitAction(time_seconds=1.2),
        ClickAction(selector=_xp("//button[contains(.,'Review')]")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(f"{_reviews_modal_scope()}//button[normalize-space(.)='5★']")),
        WaitAction(time_seconds=0.25),
        SelectDropDownOptionAction(
            selector=_xp(f"{_reviews_modal_scope()}//select[.//option[text()='Newest First']]"),
            text="Newest First",
        ),
        WaitAction(time_seconds=0.35),
    ],
)

OPEN_CONTACT_DOCTOR_FORM = _uc(
    "OPEN_CONTACT_DOCTOR_FORM",
    prompt="Open contact doctor form where doctor_name NOT CONTAINS 'huy' AND speciality NOT CONTAINS 'zei' AND rating NOT EQUALS '3.9' AND consultation_fee LESS THAN '257' AND language CONTAINS 'l'",
    actions=[
        *_doctors_search_then_open_profile(372, specialty="Cardiology", language="Hindi"),
        ClickAction(selector=_first_doctor_list_view_profile_in_grid()),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_test("open-contact-doctor-form-btn")),
        WaitAction(time_seconds=0.4),
    ],
)

CONTACT_DOCTOR = _uc(
    "CONTACT_DOCTOR",
    prompt="Contact a doctor where doctor_name not equals 'Dr. Linda Hernandez' and patient_name contains 'is' and subject contains 'M' and urgency not contains 'lsn' and appointment_request not equals 'False' and message not contains 'cxs' and speciality not equals 'Neurology' and patient_phone equals '+1-202-555-0143' and preferred_contact_method equals 'phone' and patient_email contains 'davi'",
    actions=[
        # One profile open only: after _doctors_search_then_open_profile we are on /doctors/[id], not the grid.
        *_doctors_search_then_open_profile(
            604,
            specialty="Cardiology",
            language="English",
            forbidden_card_substr="linda",
        ),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_test("open-contact-doctor-form-btn")),
        WaitAction(time_seconds=0.45),
        TypeAction(
            selector=_xp(f"{_contact_modal_scope()}//label[contains(.,'Full Name')]/following::input[1]"),
            text="Chris Patient",
        ),
        TypeAction(
            selector=_xp(f"{_contact_modal_scope()}//label[contains(.,'Email Address')]/following::input[1]"),
            text="chris.davi@example.com",
        ),
        TypeAction(
            selector=_xp(f"{_contact_modal_scope()}//label[contains(.,'Phone Number')]/following::input[1]"),
            text="+1-202-555-0143",
        ),
        SelectDropDownOptionAction(
            selector=_xp(f"{_contact_modal_scope()}//label[contains(.,'Urgency')]/following::select[1]"),
            text="Low - General inquiry",
        ),
        TypeAction(
            selector=_xp(f"{_contact_modal_scope()}//label[contains(.,'Subject')]/following::input[1]"),
            text="Follow M up question",
        ),
        TypeAction(
            selector=_xp(f"{_contact_modal_scope()}//label[contains(.,'Message')]/following::textarea[1]"),
            text="I would like to schedule a visit.",
        ),
        SelectDropDownOptionAction(
            selector=_xp(f"{_contact_modal_scope()}//label[contains(.,'Preferred Contact Method')]/following::select[1]"),
            text="Phone only",
        ),
        ClickAction(selector=_xp(f"{_contact_modal_scope()}//input[@type='checkbox'][following-sibling::label[contains(.,'appointment')]]")),
        ClickAction(selector=_test("contact-doctor-submit-btn")),
        WaitAction(time_seconds=0.55),
    ],
)


def load_autohealth_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "OPEN_APPOINTMENT_FORM": OPEN_APPOINTMENT_FORM,
        "APPOINTMENT_BOOKED_SUCCESSFULLY": APPOINTMENT_BOOKED_SUCCESSFULLY,
        "REQUEST_QUICK_APPOINTMENT": REQUEST_QUICK_APPOINTMENT,
        "SEARCH_APPOINTMENT": SEARCH_APPOINTMENT,
        "SEARCH_DOCTORS": SEARCH_DOCTORS,
        "SEARCH_PRESCRIPTION": SEARCH_PRESCRIPTION,
        "REFILL_PRESCRIPTION": REFILL_PRESCRIPTION,
        "VIEW_PRESCRIPTION": VIEW_PRESCRIPTION,
        "SEARCH_MEDICAL_ANALYSIS": SEARCH_MEDICAL_ANALYSIS,
        "VIEW_MEDICAL_ANALYSIS": VIEW_MEDICAL_ANALYSIS,
        "VIEW_DOCTOR_PROFILE": VIEW_DOCTOR_PROFILE,
        "VIEW_DOCTOR_EDUCATION": VIEW_DOCTOR_EDUCATION,
        "VIEW_DOCTOR_AVAILABILITY": VIEW_DOCTOR_AVAILABILITY,
        "FILTER_DOCTOR_REVIEWS": FILTER_DOCTOR_REVIEWS,
        "OPEN_CONTACT_DOCTOR_FORM": OPEN_CONTACT_DOCTOR_FORM,
        "CONTACT_DOCTOR": CONTACT_DOCTOR,
    }


if __name__ == "__main__":
    all_use_cases = load_autohealth_use_case_completion_flows()
    print(all_use_cases)
