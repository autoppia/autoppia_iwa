from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AppointmentBookedSuccessfullyEvent,
    BookAppointmentEvent,
    CancelBookAppointmentEvent,
    CancelContactDoctorEvent,
    CancelViewReviewsEvent,
    ContactDoctorEvent,
    DoctorContactedSuccessfullyEvent,
    FilterByCategoryEvent,
    FilterBySpecialityEvent,
    FilterReviewsEvent,
    RefillRequestEvent,
    SortReviewsEvent,
    ViewDoctorProfileEvent,
    ViewHealthMetricsEvent,
    ViewPrescriptionEvent,
    ViewReviewClickedEvent,
)
from .generation_functions import (
    generate_appointment_booked_successfully_constraints,
    generate_book_appointment_constraints,
    generate_cancel_appointment_constraints,
    generate_cancel_contact_doctor_constraints,
    generate_cancel_view_review_constraints,
    generate_contact_doctor_constraints,
    generate_doctor_contact_successfully_constraints,
    generate_filter_by_category_constraints,
    generate_filter_by_speciality_constraints,
    generate_filter_reviews_constraints,
    generate_refill_prescription_constraints,
    generate_sort_reviews_constraints,
    generate_view_doctor_profile_constraints,
    generate_view_health_metrics_constraints,
    generate_view_prescription_constraints,
    generate_view_review_clicked_constraints,
)

BOOK_APPOINTMENT_USE_CASE = UseCase(
    name="BOOK_APPOINTMENT",
    description="The user booked an appointment with a doctor for a given date, time, and speciality, including patient details when confirmed. Uses semantic values (doctor names, specialty names, patient names) for natural prompts.",
    event=BookAppointmentEvent,
    event_source_code=BookAppointmentEvent.get_source_code_of_class(),
    constraints_generator=generate_book_appointment_constraints,
    examples=[
        {
            "prompt": "Book an appointment where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "Book an appointment where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "Book an appointment where doctor_name equals 'Dr. Daniel Roberts' and patient_name equals 'John Doe' and patient_email contains '@gmail.com' and reason_for_visit equals 'Chest pain'",
            "prompt_for_task_generation": "Book an appointment where doctor_name equals 'Dr. Daniel Roberts' and patient_name equals 'John Doe' and patient_email contains '@gmail.com' and reason_for_visit equals 'Chest pain'",
        },
        {
            "prompt": "Book an appointment where doctor_name contains 'Nguyen' and speciality equals 'Dermatology' and patient_name equals 'Emma Wilson' and reason_for_visit contains 'skin rash'",
            "prompt_for_task_generation": "Book an appointment where doctor_name contains 'Nguyen' and speciality equals 'Dermatology' and patient_name equals 'Emma Wilson' and reason_for_visit contains 'skin rash'",
        },
        {
            "prompt": "Book an appointment where doctor_name equals 'Dr. Michael Smith' and date equals '2025-09-25' and time equals '2:30 PM' and speciality equals 'Pediatrics' and patient_phone starts with '+1'",
            "prompt_for_task_generation": "Book an appointment where doctor_name equals 'Dr. Michael Smith' and date equals '2025-09-25' and time equals '2:30 PM' and speciality equals 'Pediatrics' and patient_phone starts with '+1'",
        },
    ],
)

APPOINTMENT_BOOKED_SUCCESSFULLY_USE_CASE = UseCase(
    name="APPOINTMENT_BOOKED_SUCCESSFULLY",
    description="The user successfully booked an appointment with a doctor including patient details, insurance, and visit reason.",
    event=AppointmentBookedSuccessfullyEvent,
    event_source_code=AppointmentBookedSuccessfullyEvent.get_source_code_of_class(),
    constraints_generator=generate_appointment_booked_successfully_constraints,
    examples=[
        {
            "prompt": "Appointment booked successfully where patient_name equals 'John Doe' and doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-23' and time equals '10:00 AM' and speciality equals 'Cardiology' and reason_for_visit equals 'Chest pain'",
            "prompt_for_task_generation": "Appointment booked successfully where patient_name equals 'John Doe' and doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-23' and time equals '10:00 AM' and speciality equals 'Cardiology' and reason_for_visit equals 'Chest pain'",
        },
        {
            "prompt": "Appointment booked successfully where patient_name not equals 'Sarah Lee' and insurance_provider equals 'BlueCross' and insurance_number contains 'BCX123' and doctor_name equals 'Dr. Daniel Roberts' and date greater than '2025-09-20'",
            "prompt_for_task_generation": "Appointment booked successfully where patient_name not equals 'Sarah Lee' and insurance_provider equals 'BlueCross' and insurance_number contains 'BCX123' and doctor_name equals 'Dr. Daniel Roberts' and date greater than '2025-09-20'",
        },
        {
            "prompt": "Appointment booked successfully where patient_email contains '@gmail.com' and patient_phone starts with '+1' and emergency_contact equals 'Jane Doe' and emergency_phone equals '555-1234' and notes contains 'Bring previous reports'",
            "prompt_for_task_generation": "Appointment booked successfully where patient_email contains '@gmail.com' and patient_phone starts with '+1' and emergency_contact equals 'Jane Doe' and emergency_phone equals '555-1234' and notes contains 'Bring previous reports'",
        },
        {
            "prompt": "Appointment booked successfully where doctor_name contains 'Nguyen' and speciality equals 'Dermatology' and date less than '2025-10-01' and reason_for_visit equals 'Skin rash' and patient_name equals 'Emma Wilson'",
            "prompt_for_task_generation": "Appointment booked successfully where doctor_name contains 'Nguyen' and speciality equals 'Dermatology' and date less than '2025-10-01' and reason_for_visit equals 'Skin rash' and patient_name equals 'Emma Wilson'",
        },
        {
            "prompt": "Appointment booked successfully where insurance_provider not equals 'Aetna' and insurance_number not contains 'XYZ' and patient_phone equals '444-5678' and patient_email equals 'michael.smith@example.com' and notes contains 'First-time consultation'",
            "prompt_for_task_generation": "Appointment booked successfully where insurance_provider not equals 'Aetna' and insurance_number not contains 'XYZ' and patient_phone equals '444-5678' and patient_email equals 'michael.smith@example.com' and notes contains 'First-time consultation'",
        },
        {
            "prompt": "Appointment booked successfully where emergency_contact equals 'Robert King' and emergency_phone equals '222-9999' and doctor_name equals 'Dr. Clara Nguyen' and date equals '2025-09-29' and time equals '2:30 PM' and speciality equals 'Orthopedics'",
            "prompt_for_task_generation": "Appointment booked successfully where emergency_contact equals 'Robert King' and emergency_phone equals '222-9999' and doctor_name equals 'Dr. Clara Nguyen' and date equals '2025-09-29' and time equals '2:30 PM' and speciality equals 'Orthopedics'",
        },
    ],
)

CANCEL_BOOK_APPOINTMENT_USE_CASE = UseCase(
    name="CANCEL_BOOK_APPOINTMENT",
    description="The user canceled a previously booked appointment with a doctor for a given date, time, and speciality.",
    event=CancelBookAppointmentEvent,
    event_source_code=CancelBookAppointmentEvent.get_source_code_of_class(),
    constraints_generator=generate_cancel_appointment_constraints,
    examples=[
        {
            "prompt": "Cancel an appointment where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "Cancel an appointment where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "Cancel an appointment where doctor_name not equals 'Dr. Clara Nguyen' and date not equals '2025-09-21' and time equals '10:30 AM' and speciality equals 'Dermatology'",
            "prompt_for_task_generation": "Cancel an appointment where doctor_name not equals 'Dr. Clara Nguyen' and date not equals '2025-09-21' and time equals '10:30 AM' and speciality equals 'Dermatology'",
        },
        {
            "prompt": "Cancel an appointment where doctor_name contains 'Daniel' and date less than '2025-09-25' and time greater than '11:00 AM' and speciality equals 'Orthopedics'",
            "prompt_for_task_generation": "Cancel an appointment where doctor_name contains 'Daniel' and date less than '2025-09-25' and time greater than '11:00 AM' and speciality equals 'Orthopedics'",
        },
        {
            "prompt": "Cancel an appointment where speciality equals 'Neurology' and doctor_name equals 'Dr. Robert King' and date greater than '2025-09-28' and time equals '1:00 PM'",
            "prompt_for_task_generation": "Cancel an appointment where speciality equals 'Neurology' and doctor_name equals 'Dr. Robert King' and date greater than '2025-09-28' and time equals '1:00 PM'",
        },
        {
            "prompt": "Cancel an appointment where doctor_name equals 'Dr. Michael Smith' and date equals '2025-09-30' and time not equals '3:00 PM' and speciality equals 'Pediatrics'",
            "prompt_for_task_generation": "Cancel an appointment where doctor_name equals 'Dr. Michael Smith' and date equals '2025-09-30' and time not equals '3:00 PM' and speciality equals 'Pediatrics'",
        },
        {
            "prompt": "Cancel an appointment where doctor_name contains 'Emma' and speciality not equals 'Oncology' and date less than '2025-10-05' and time equals '4:15 PM'",
            "prompt_for_task_generation": "Cancel an appointment where doctor_name contains 'Emma' and speciality not equals 'Oncology' and date less than '2025-10-05' and time equals '4:15 PM'",
        },
    ],
)

FILTER_BY_SPECIALITY_USE_CASE = UseCase(
    name="FILTER_BY_SPECIALTY",
    description="The user filters prescriptions by a given status.",
    event=FilterBySpecialityEvent,
    event_source_code=FilterBySpecialityEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_by_speciality_constraints,
    examples=[
        {
            "prompt": "Filter prescriptions where status equals 'completed'",
            "prompt_for_task_generation": "Filter prescriptions where status equals 'completed'",
        },
        {
            "prompt": "Filter prescriptions where status equals 'active'",
            "prompt_for_task_generation": "Filter prescriptions where status equals 'active'",
        },
        {
            "prompt": "Filter prescriptions where status equals 'discontinued'",
            "prompt_for_task_generation": "Filter prescriptions where status equals 'discontinued'",
        },
        {
            "prompt": "Filter prescriptions where status equals 'all'",
            "prompt_for_task_generation": "Filter prescriptions where status equals 'all'",
        },
        {
            "prompt": "Filter prescriptions where status equals 'refill_needed'",
            "prompt_for_task_generation": "Filter prescriptions where status equals 'refill_needed'",
        },
        {
            "prompt": "Filter prescriptions where status not equals 'completed'",
            "prompt_for_task_generation": "Filter prescriptions where status not equals 'completed'",
        },
    ],
)

REFILL_PRESCRIPTION_USE_CASE = UseCase(
    name="REFILL_PRESCRIPTION",
    description="The user requested a prescription refill for a specific medicine.",
    event=RefillRequestEvent,
    event_source_code=RefillRequestEvent.get_source_code_of_class(),
    constraints_generator=generate_refill_prescription_constraints,
    examples=[
        {
            "prompt": "Refill prescription where medicine_name equals 'Atorvastatin'",
            "prompt_for_task_generation": "Refill prescription where medicine_name equals 'Atorvastatin'",
        },
        {
            "prompt": "Refill prescription where medicine_name equals 'Metformin'",
            "prompt_for_task_generation": "Refill prescription where medicine_name equals 'Metformin'",
        },
        {
            "prompt": "Refill prescription where medicine_name equals 'Ibuprofen'",
            "prompt_for_task_generation": "Refill prescription where medicine_name equals 'Ibuprofen'",
        },
        {
            "prompt": "Refill prescription where medicine_name not equals 'Amoxicillin'",
            "prompt_for_task_generation": "Refill prescription where medicine_name not equals 'Amoxicillin'",
        },
        {
            "prompt": "Refill prescription where medicine_name contains 'Vitamin'",
            "prompt_for_task_generation": "Refill prescription where medicine_name contains 'Vitamin'",
        },
        {
            "prompt": "Refill prescription where medicine_name equals 'Lisinopril'",
            "prompt_for_task_generation": "Refill prescription where medicine_name equals 'Lisinopril'",
        },
    ],
)


VIEW_PRESCRIPTION_USE_CASE = UseCase(
    name="VIEW_PRESCRIPTION",
    description="The user viewed a prescription containing doctor information, medicine details, dosage, and start date.",
    event=ViewPrescriptionEvent,
    event_source_code=ViewPrescriptionEvent.get_source_code_of_class(),
    constraints_generator=generate_view_prescription_constraints,
    examples=[
        {
            "prompt": "View a prescription where doctor_name equals 'Dr. Alice Thompson' and start_date equals '2025-08-01' and dosage equals '10 mg daily' and medicine_name equals 'Atorvastatin' and status equals 'active' and category equals 'cholesterol'",
            "prompt_for_task_generation": "View a prescription where doctor_name equals 'Dr. Alice Thompson' and start_date equals '2025-08-01' and dosage equals '10 mg daily' and medicine_name equals 'Atorvastatin' and status equals 'active' and category equals 'cholesterol'",
        },
        {
            "prompt": "View a prescription where doctor_name equals 'Dr. Brian Patel' and start_date equals '2025-09-05' and dosage contains '500 mg' and medicine_name equals 'Amoxicillin' and status not equals 'active' and category equals 'antibiotic'",
            "prompt_for_task_generation": "View a prescription where doctor_name equals 'Dr. Brian Patel' and start_date equals '2025-09-05' and dosage contains '500 mg' and medicine_name equals 'Amoxicillin' and status not equals 'active' and category equals 'antibiotic'",
        },
        {
            "prompt": "View a prescription where doctor_name contains 'Daniel' and start_date less than '2025-08-01' and dosage equals '200 mg as needed' and medicine_name equals 'Ibuprofen' and status equals 'active' and category equals 'pain_management'",
            "prompt_for_task_generation": "View a prescription where doctor_name contains 'Daniel' and start_date less than '2025-08-01' and dosage equals '200 mg as needed' and medicine_name equals 'Ibuprofen' and status equals 'active' and category equals 'pain_management'",
        },
    ],
)

VIEW_HEALTH_METRICS_USE_CASE = UseCase(
    name="VIEW_HEALTH_METRICS",
    description="The user viewed health metric files with details such as file name, type, and size.",
    event=ViewHealthMetricsEvent,
    event_source_code=ViewHealthMetricsEvent.get_source_code_of_class(),
    constraints_generator=generate_view_health_metrics_constraints,
    examples=[
        {
            "prompt": "View health metrics where record_title equals 'Complete Blood Count (CBC)' and record_type equals 'lab_result' and record_date equals '2024-01-15'",
            "prompt_for_task_generation": "View health metrics where record_title equals 'Complete Blood Count (CBC)' and record_type equals 'lab_result' and record_date equals '2024-01-15'",
        },
        {
            "prompt": "View health metrics where record_title contains 'Ray' and record_type equals 'imaging' and record_date greater than '2024-02-01'",
            "prompt_for_task_generation": "View health metrics where record_title contains 'Ray' and record_type equals 'imaging' and record_date greater than '2024-02-01'",
        },
        {
            "prompt": "View health metrics where record_title not equals 'Annual Flu Shot' and record_type not equals 'vaccination' and record_date equals '2024-02-05'",
            "prompt_for_task_generation": "View health metrics where record_title not equals 'Annual Flu Shot' and record_type not equals 'vaccination' and record_date equals '2024-02-05'",
        },
    ],
)
FILTER_BY_CATEGORY_USE_CASE = UseCase(
    name="FILTER_BY_CATEGORY",
    description="The user filtered medical records based on their category.",
    event=FilterByCategoryEvent,
    event_source_code=FilterByCategoryEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_by_category_constraints,
    examples=[
        {
            "prompt": "Filter medical records where category equals 'diagnostic'",
            "prompt_for_task_generation": "Filter medical records where category equals 'diagnostic'",
        },
        {
            "prompt": "Filter medical records where category equals 'preventive'",
            "prompt_for_task_generation": "Filter medical records where category equals 'preventive'",
        },
        {
            "prompt": "Filter medical records where category equals 'monitoring'",
            "prompt_for_task_generation": "Filter medical records where category equals 'monitoring'",
        },
        {
            "prompt": "Filter medical records where category equals 'treatment'",
            "prompt_for_task_generation": "Filter medical records where category equals 'treatment'",
        },
    ],
)
VIEW_DOCTOR_PROFILE_USE_CASE = UseCase(
    name="VIEW_DOCTOR_PROFILE",
    description="The user viewed a doctor's profile, including name, rating, and speciality.",
    event=ViewDoctorProfileEvent,
    event_source_code=ViewDoctorProfileEvent.get_source_code_of_class(),
    constraints_generator=generate_view_doctor_profile_constraints,
    examples=[
        {
            "prompt": "View a doctor profile where doctor_name equals 'Dr. Alice Thompson' and rating greater than 4.5 and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "View a doctor profile where doctor_name equals 'Dr. Alice Thompson' and rating greater than 4.5 and speciality equals 'Cardiology'",
        },
        {
            "prompt": "View a doctor profile where doctor_name not equals 'Dr. Brian Patel' and rating less than 4.0 and speciality equals 'Dermatology'",
            "prompt_for_task_generation": "View a doctor profile where doctor_name not equals 'Dr. Brian Patel' and rating less than 4.0 and speciality equals 'Dermatology'",
        },
        {
            "prompt": "View a doctor profile where doctor_name contains 'Clara' and rating equals 4.2 and speciality equals 'Pediatrics'",
            "prompt_for_task_generation": "View a doctor profile where doctor_name contains 'Clara' and rating equals 4.2 and speciality equals 'Pediatrics'",
        },
    ],
)
CONTACT_DOCTOR_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "Contact a doctor...".
2. Do not mention a single constraint more than once in the request.

Correct examples:
- Contact a doctor where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology' and rating equals '4.8'.

Incorrect examples:
- Retrieve doctor 'Dr. Alice Thompson'.

3. Pay attention to the constraints:
Example:
constraints:
{
'doctor_name': {'operator': 'equals', 'value': 'Dr. Alice Thompson'},
'rating': {'operator': 'equals', 'value': '4.8'},
'speciality': {'operator': 'equals', 'value': 'Cardiology'}
}
Correct:
"Contact a doctor where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology' and rating equals '4.8'."
Incorrect:
"Retrieve doctor 'Dr. Alice Thompson' and speciality equals 'Cardiology'."
""".strip()
CONTACT_DOCTOR_USE_CASE = UseCase(
    name="CONTACT_DOCTOR",
    description="The user wants to contact a doctor based on their name, speciality, or rating.",
    event=ContactDoctorEvent,
    event_source_code=ContactDoctorEvent.get_source_code_of_class(),
    additional_prompt_info=CONTACT_DOCTOR_ADDITIONAL_INFO,
    constraints_generator=generate_contact_doctor_constraints,
    examples=[
        {
            "prompt": "Contact a doctor where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Contact a doctor where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Contact a doctor where speciality equals 'Dermatology'",
            "prompt_for_task_generation": "Contact a doctor where speciality equals 'Dermatology'",
        },
        {
            "prompt": "Contact a doctor where rating greater than 4.7",
            "prompt_for_task_generation": "Contact a doctor where rating greater than 4.7",
        },
        {
            "prompt": "Contact a doctor where speciality equals 'Pediatrics' and rating greater than 4.5",
            "prompt_for_task_generation": "Contact a doctor where speciality equals 'Pediatrics' and rating greater than 4.5",
        },
        {
            "prompt": "Contact a doctor where doctor_name not equals 'Dr. Daniel Ruiz'",
            "prompt_for_task_generation": "Contact a doctor where doctor_name not equals 'Dr. Daniel Ruiz'",
        },
        {
            "prompt": "Contact a doctor where speciality contains 'Cardio'",
            "prompt_for_task_generation": "Contact a doctor where speciality contains 'Cardio'",
        },
    ],
)

DOCTOR_CONTACTED_SUCCESSFULLY_USE_CASE = UseCase(
    name="DOCTOR_CONTACTED_SUCCESSFULLY",
    description="The user has successfully contacted a doctor, providing personal details, contact preferences, and message context.",
    event=DoctorContactedSuccessfullyEvent,
    event_source_code=DoctorContactedSuccessfullyEvent.get_source_code_of_class(),
    # additional_prompt_info=CONTACT_DOCTOR_SUCCESSFULLY_ADDITIONAL_INFO,
    constraints_generator=generate_doctor_contact_successfully_constraints,
    examples=[
        {
            "prompt": "Doctor contacted successfully where doctor_name equals 'Dr. Alice Thompson' and patient_name equals 'John Smith'",
            "prompt_for_task_generation": "Doctor contacted successfully where doctor_name equals 'Dr. Alice Thompson' and patient_name equals 'John Smith'",
        },
        {
            "prompt": "Doctor contacted successfully where speciality equals 'Dermatology' and urgency equals 'high'",
            "prompt_for_task_generation": "Doctor contacted successfully where speciality equals 'Dermatology' and urgency equals 'high'",
        },
        {
            "prompt": "Doctor contacted successfully where patient_email equals 'maria.gonzalez@example.com' and preferred_contact_method equals 'email'",
            "prompt_for_task_generation": "Doctor contacted successfully where patient_email equals 'maria.gonzalez@example.com' and preferred_contact_method equals 'email'",
        },
        {
            "prompt": "Doctor contacted successfully where subject contains 'knee pain' and message contains 'difficulty walking'",
            "prompt_for_task_generation": "Doctor contacted successfully where subject contains 'knee pain' and message contains 'difficulty walking'",
        },
        {
            "prompt": "Doctor contacted successfully where doctor_name equals 'Dr. Brian Patel' and preferred_contact_method equals 'phone'",
            "prompt_for_task_generation": "Doctor contacted successfully where doctor_name equals 'Dr. Brian Patel' and preferred_contact_method equals 'phone'",
        },
        {
            "prompt": "Doctor contacted successfully where patient_phone equals '+1-555-678-1234' and urgency equals 'low'",
            "prompt_for_task_generation": "Doctor contacted successfully where patient_phone equals '+1-555-678-1234' and urgency equals 'low'",
        },
    ],
)
CANCEL_CONTACT_DOCTOR_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "Cancel contact request...".
2. Do not mention a single constraint more than once in the request.

Correct examples:
- Cancel contact request where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'.

Incorrect examples:
- Retrieve doctor 'Dr. Alice Thompson'.

3. Pay attention to the constraints:
Example:
constraints:
{
'doctor_name': {'operator': 'equals', 'value': 'Dr. Alice Thompson'},
'speciality': {'operator': 'equals', 'value': 'Cardiology'}
}
Correct:
"Cancel contact request where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'."
Incorrect:
"Cancel doctor 'Dr. Alice Thompson' and speciality equals 'Cardiology'."
""".strip()
CANCEL_CONTACT_DOCTOR_USE_CASE = UseCase(
    name="CANCEL_CONTACT_DOCTOR",
    description="The user canceled a request to contact a doctor.",
    event=CancelContactDoctorEvent,
    event_source_code=CancelContactDoctorEvent.get_source_code_of_class(),
    additional_prompt_info=CANCEL_CONTACT_DOCTOR_ADDITIONAL_INFO,
    constraints_generator=generate_cancel_contact_doctor_constraints,
    examples=[
        {
            "prompt": "Cancel contact request where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Cancel contact request where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Cancel contact request where doctor_name equals 'Dr. John Smith'",
            "prompt_for_task_generation": "Cancel contact request where doctor_name equals 'Dr. John Smith'",
        },
        {
            "prompt": "Cancel contact request where speciality equals 'Cardiologist'",
            "prompt_for_task_generation": "Cancel contact request where speciality equals 'Cardiologist'",
        },
        {
            "prompt": "Cancel contact request where speciality equals 'Dermatologist'",
            "prompt_for_task_generation": "Cancel contact request where speciality equals 'Dermatologist'",
        },
        {
            "prompt": "Cancel contact request where doctor_name not equals 'Dr. Emily Davis'",
            "prompt_for_task_generation": "Cancel contact request where doctor_name not equals 'Dr. Emily Davis'",
        },
        {
            "prompt": "Cancel contact request where speciality contains 'Pediatric'",
            "prompt_for_task_generation": "Cancel contact request where speciality contains 'Pediatric'",
        },
    ],
)
VIEW_REVIEW_CLICKED_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "View reviews clicked...".
2. Do not mention a single constraint more than once in the request.

Correct examples:
- View reviews clicked where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology' and rating equals '4.8'.

Incorrect examples:
- View review 'Dr. Alice Thompson'.

3. Pay attention to the constraints:
Example:
constraints:
{
'doctor_name': {'operator': 'equals', 'value': 'Dr. Alice Thompson'},
'speciality': {'operator': 'equals', 'value': 'Cardiology'},
'rating': {'operator': 'equals', 'value': '4.8'},
}
Correct:
"View reviews clicked where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology' and rating equals '4.8'."
Incorrect:
"View reviews 'Dr. Alice Thompson' and speciality equals 'Cardiology'."
""".strip()
VIEW_REVIEWS_CLICKED_USE_CASE = UseCase(
    name="VIEW_REVIEWS_CLICKED",
    description="The user clicked to view reviews for a doctor.",
    event=ViewReviewClickedEvent,
    event_source_code=ViewReviewClickedEvent.get_source_code_of_class(),
    additional_prompt_info=VIEW_REVIEW_CLICKED_ADDITIONAL_INFO,
    constraints_generator=generate_view_review_clicked_constraints,
    examples=[
        {
            "prompt": "View reviews clicked where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "View reviews clicked where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "View reviews clicked where doctor_name equals 'Dr. Michael Johnson'",
            "prompt_for_task_generation": "View reviews clicked where doctor_name equals 'Dr. Michael Johnson'",
        },
        {
            "prompt": "View reviews clicked where speciality equals 'Cardiologist'",
            "prompt_for_task_generation": "View reviews clicked where speciality equals 'Cardiologist'",
        },
        {
            "prompt": "View reviews clicked where speciality contains 'Dermatology'",
            "prompt_for_task_generation": "View reviews clicked where speciality contains 'Dermatology'",
        },
        {
            "prompt": "View reviews clicked where rating greater than 4.5",
            "prompt_for_task_generation": "View reviews clicked where rating greater than 4.5",
        },
        {
            "prompt": "View reviews clicked where rating less than 3.0",
            "prompt_for_task_generation": "View reviews clicked where rating less than 3.0",
        },
    ],
)
FILTER_REVIEWS_USE_CASE = UseCase(
    name="FILTER_REVIEWS",
    description="The user filtered doctor reviews based on rating, doctor name, or speciality.",
    event=FilterReviewsEvent,
    event_source_code=FilterReviewsEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_reviews_constraints,
    examples=[
        {
            "prompt": "Filter reviews where filter_rating equals 5",
            "prompt_for_task_generation": "Filter reviews where filter_rating equals 5",
        },
        {
            "prompt": "Filter reviews where filter_rating equals 3 and speciality equals 'Dermatologist'",
            "prompt_for_task_generation": "Filter reviews where filter_rating equals 3 and speciality equals 'Dermatologist'",
        },
        {
            "prompt": "Filter reviews for doctor 'Dr. Alice Thompson' where filter_rating greater than 4",
            "prompt_for_task_generation": "Filter reviews for doctor 'Dr. Alice Thompson' where filter_rating greater than 4",
        },
        {
            "prompt": "Filter reviews where speciality equals 'Neurologist' and filter_rating less than 3",
            "prompt_for_task_generation": "Filter reviews where speciality equals 'Neurologist' and filter_rating less than 3",
        },
        {
            "prompt": "Filter reviews where doctor_name equals 'Dr. John Smith' and filter_rating not equals 2",
            "prompt_for_task_generation": "Filter reviews where doctor_name equals 'Dr. John Smith' and filter_rating not equals 2",
        },
        {
            "prompt": "Filter reviews where filter_rating equals 1 and speciality equals 'Cardiologist'",
            "prompt_for_task_generation": "Filter reviews where filter_rating equals 1 and speciality equals 'Cardiologist'",
        },
    ],
)
SORT_REVIEWS_USE_CASE = UseCase(
    name="SORT_REVIEWS",
    description="The user sorted doctor reviews by order such as lowest, highest, oldest, or newest, optionally filtered by doctor or speciality.",
    event=SortReviewsEvent,
    event_source_code=SortReviewsEvent.get_source_code_of_class(),
    constraints_generator=generate_sort_reviews_constraints,
    examples=[
        {
            "prompt": "Sort reviews where sort_order equals 'highest'",
            "prompt_for_task_generation": "Sort reviews where sort_order equals 'highest'",
        },
        {
            "prompt": "Sort reviews where sort_order equals 'lowest' for doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Sort reviews where sort_order equals 'lowest' for doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Sort reviews where sort_order equals 'newest' and speciality equals 'Cardiologist'",
            "prompt_for_task_generation": "Sort reviews where sort_order equals 'newest' and speciality equals 'Cardiologist'",
        },
        {
            "prompt": "Sort reviews where sort_order equals 'oldest' for doctor_name equals 'Dr. John Smith'",
            "prompt_for_task_generation": "Sort reviews where sort_order equals 'oldest' for doctor_name equals 'Dr. John Smith'",
        },
        {
            "prompt": "Sort reviews where sort_order equals 'highest' and speciality equals 'Dermatologist'",
            "prompt_for_task_generation": "Sort reviews where sort_order equals 'highest' and speciality equals 'Dermatologist'",
        },
        {
            "prompt": "Sort reviews where sort_order equals 'newest'",
            "prompt_for_task_generation": "Sort reviews where sort_order equals 'newest'",
        },
    ],
)
CANCEL_VIEW_REVIEW_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "Cancel view reviews...".
2. Do not mention a single constraint more than once in the request.

Correct examples:
- Cancel view reviews clicked where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'.

Incorrect examples:
- Cancel view review 'Dr. Alice Thompson'.

3. Pay attention to the constraints:
Example:
constraints:
{
'doctor_name': {'operator': 'equals', 'value': 'Dr. Alice Thompson'},
'speciality': {'operator': 'equals', 'value': 'Cardiology'},
}
Correct:
"Cancel view reviews clicked where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'."
Incorrect:
"View reviews 'Dr. Alice Thompson' and speciality equals 'Cardiology'."
""".strip()
CANCEL_VIEW_REVIEWS_USE_CASE = UseCase(
    name="CANCEL_VIEW_REVIEWS",
    description="The user canceled viewing reviews of a doctor or speciality.",
    event=CancelViewReviewsEvent,
    event_source_code=CancelViewReviewsEvent.get_source_code_of_class(),
    additional_prompt_info=CANCEL_VIEW_REVIEW_ADDITIONAL_INFO,
    constraints_generator=generate_cancel_view_review_constraints,
    examples=[
        {
            "prompt": "Cancel view reviews where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Cancel view reviews where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Cancel view reviews where speciality equals 'Cardiologist'",
            "prompt_for_task_generation": "Cancel view reviews where speciality equals 'Cardiologist'",
        },
        {
            "prompt": "Cancel view reviews where doctor_name equals 'Dr. John Smith' and speciality equals 'Dermatologist'",
            "prompt_for_task_generation": "Cancel view reviews where doctor_name equals 'Dr. John Smith' and speciality equals 'Dermatologist'",
        },
        {
            "prompt": "Cancel view reviews for doctor_name equals 'Dr. Emily Davis'",
            "prompt_for_task_generation": "Cancel view reviews for doctor_name equals 'Dr. Emily Davis'",
        },
        {
            "prompt": "Cancel view reviews where speciality equals 'Neurologist'",
            "prompt_for_task_generation": "Cancel view reviews where speciality equals 'Neurologist'",
        },
        {
            "prompt": "Cancel view reviews without specifying doctor_name or speciality",
            "prompt_for_task_generation": "Cancel view reviews without specifying doctor_name or speciality",
        },
    ],
)
ALL_USE_CASES = [
    BOOK_APPOINTMENT_USE_CASE,
    # APPOINTMENT_BOOKED_SUCCESSFULLY_USE_CASE,
    # CANCEL_BOOK_APPOINTMENT_USE_CASE,
    # VIEW_PRESCRIPTION_USE_CASE,
    # FILTER_BY_SPECIALITY_USE_CASE,
    # REFILL_PRESCRIPTION_USE_CASE,
    # VIEW_HEALTH_METRICS_USE_CASE,
    # FILTER_BY_CATEGORY_USE_CASE,
    # VIEW_DOCTOR_PROFILE_USE_CASE,
    # CONTACT_DOCTOR_USE_CASE,
    # DOCTOR_CONTACTED_SUCCESSFULLY_USE_CASE,
    # CANCEL_CONTACT_DOCTOR_USE_CASE,
    # VIEW_REVIEWS_CLICKED_USE_CASE,
    # FILTER_REVIEWS_USE_CASE,
    # SORT_REVIEWS_USE_CASE,
    # CANCEL_VIEW_REVIEWS_USE_CASE,
]
