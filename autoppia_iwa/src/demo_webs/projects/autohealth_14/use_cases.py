from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AppointmentBookedSuccessfullyEvent,
    BookAppointmentEvent,
    ContactDoctorEvent,
    DoctorContactedSuccessfullyEvent,
    OpenAppointmentFormEvent,
    OpenContactDoctorFormEvent,
    SearchAppointmentEvent,
    SearchPrescriptionEvent,
    SearchMedicalAnalysisEvent,
    FilterDoctorReviewsEvent,
    RefillRequestEvent,
    RequestAppointmentEvent,
    RequestQuickAppointmentEvent,
    SearchDoctorsEvent,
    ViewDoctorProfileEvent,
    ViewDoctorEducationEvent,
    ViewMedicalAnalysisEvent,
    ViewPrescriptionEvent,
    ViewReviewClickedEvent,
)
from .generation_functions import (
    generate_appointment_booked_successfully_constraints,
    generate_book_appointment_constraints,
    generate_contact_doctor_constraints,
    generate_doctor_contact_successfully_constraints,
    generate_search_appointment_constraints,
    generate_search_prescription_constraints,
    generate_search_medical_analysis_constraints,
    generate_filter_doctor_reviews_constraints,
    generate_refill_prescription_constraints,
    generate_request_appointment_constraints,
    generate_request_quick_appointment_constraints,
    generate_search_doctors_constraints,
    generate_view_doctor_profile_constraints,
    generate_view_doctor_education_constraints,
    generate_open_appointment_form_constraints,
    generate_open_contact_doctor_form_constraints,
    generate_view_medical_analysis_constraints,
    generate_view_prescription_constraints,
    generate_view_review_clicked_constraints,
)

BOOK_APPOINTMENT_USE_CASE = UseCase(
    name="BOOK_APPOINTMENT",
    description="The user booked an appointment with a doctor for a given date, time, and speciality",
    event=BookAppointmentEvent,
    event_source_code=BookAppointmentEvent.get_source_code_of_class(),
    constraints_generator=generate_book_appointment_constraints,
    examples=[
        {
            "prompt": "Book an appointment where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "Book an appointment where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "Book an appointment where doctor_name not equals 'Dr. Clara Nguyen' and date not equals '2025-09-21' and time equals '9:00 AM' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "Book an appointment where doctor_name not equals 'Dr. Clara Nguyen' and date not equals '2025-09-21' and time equals '9:00 AM' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "Book an appointment where doctor_name contains 'Daniel' and date less than '2025-09-25' and time greater than '10:00 AM' and speciality equals 'Orthopedics'",
            "prompt_for_task_generation": "Book an appointment where doctor_name contains 'Daniel' and date less than '2025-09-25' and time greater than '10:00 AM' and speciality equals 'Orthopedics'",
        },
    ],
)

OPEN_APPOINTMENT_FORM_USE_CASE = UseCase(
    name="OPEN_APPOINTMENT_FORM",
    description="The user opened the appointment booking form (clicked Book Appointment on an appointment row).",
    event=OpenAppointmentFormEvent,
    event_source_code=OpenAppointmentFormEvent.get_source_code_of_class(),
    constraints_generator=generate_open_appointment_form_constraints,
    examples=[
        {
            "prompt": "Open appointment form where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "Open appointment form where doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-20' and time equals '9:00 AM' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "Open booking form for appointment with Dr. Daniel Roberts at 10:00 AM",
            "prompt_for_task_generation": "Open appointment form where doctor_name contains 'Daniel' and time equals '10:00 AM'",
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

REQUEST_APPOINTMENT_USE_CASE = UseCase(
    name="REQUEST_APPOINTMENT",
    description="The user submitted the homepage Request Appointment form with patient details and optional specialty.",
    event=RequestAppointmentEvent,
    event_source_code=RequestAppointmentEvent.get_source_code_of_class(),
    constraints_generator=generate_request_appointment_constraints,
    examples=[
        {
            "prompt": "Request an appointment where patient_name equals 'John Smith' and specialty equals 'Cardiology'",
            "prompt_for_task_generation": "Request an appointment where patient_name equals 'John Smith' and specialty equals 'Cardiology'",
        },
        {
            "prompt": "Request an appointment where patient_email equals 'emily.johnson@example.com' and specialty equals 'Dermatology'",
            "prompt_for_task_generation": "Request an appointment where patient_email equals 'emily.johnson@example.com' and specialty equals 'Dermatology'",
        },
        {
            "prompt": "Request an appointment where specialty equals 'Neurology' and patient_name contains 'Michael'",
            "prompt_for_task_generation": "Request an appointment where specialty equals 'Neurology' and patient_name contains 'Michael'",
        },
    ],
)

REQUEST_QUICK_APPOINTMENT_USE_CASE = UseCase(
    name="REQUEST_QUICK_APPOINTMENT",
    description="The user submitted the homepage quick appointment form (hero); a popup confirms 'We will contact you as soon as possible'.",
    event=RequestQuickAppointmentEvent,
    event_source_code=RequestQuickAppointmentEvent.get_source_code_of_class(),
    constraints_generator=generate_request_quick_appointment_constraints,
    examples=[
        {
            "prompt": "Request quick appointment where patient_name equals 'John Smith' and specialty equals 'Cardiology'",
            "prompt_for_task_generation": "Request quick appointment where patient_name equals 'John Smith' and specialty equals 'Cardiology'",
        },
        {
            "prompt": "Submit quick appointment form where specialty equals 'Dermatology'",
            "prompt_for_task_generation": "Request quick appointment where specialty equals 'Dermatology'",
        },
    ],
)

SEARCH_APPOINTMENT_USE_CASE = UseCase(
    name="SEARCH_APPOINTMENT",
    description="The user clicked Search on the Appointments page to apply doctor, specialty, or date filters.",
    event=SearchAppointmentEvent,
    event_source_code=SearchAppointmentEvent.get_source_code_of_class(),
    constraints_generator=generate_search_appointment_constraints,
    examples=[
        {
            "prompt": "Search appointments where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Search appointments where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Search appointments where specialty equals 'Cardiology' and date equals '2025-09-20'",
            "prompt_for_task_generation": "Search appointments where specialty equals 'Cardiology' and date equals '2025-09-20'",
        },
        {
            "prompt": "Search appointments where date equals '2025-09-25'",
            "prompt_for_task_generation": "Search appointments where date equals '2025-09-25'",
        },
    ],
)

SEARCH_DOCTORS_USE_CASE = UseCase(
    name="SEARCH_DOCTORS",
    description="The user clicked Search on the Doctors page to apply name and/or specialty filters.",
    event=SearchDoctorsEvent,
    event_source_code=SearchDoctorsEvent.get_source_code_of_class(),
    constraints_generator=generate_search_doctors_constraints,
    examples=[
        {
            "prompt": "Search doctors where action equals 'search' and search_term contains 'Alice'",
            "prompt_for_task_generation": "Search doctors where action equals 'search' and search_term contains 'Alice'",
        },
        {
            "prompt": "Search doctors where specialty equals 'Cardiology'",
            "prompt_for_task_generation": "Search doctors where specialty equals 'Cardiology'",
        },
        {
            "prompt": "Search doctors where specialty equals 'Dermatology'",
            "prompt_for_task_generation": "Search doctors where specialty equals 'Dermatology'",
        },
    ],
)

SEARCH_PRESCRIPTION_USE_CASE = UseCase(
    name="SEARCH_PRESCRIPTION",
    description="The user clicked Search on the Prescriptions page to apply medicine and/or doctor filters.",
    event=SearchPrescriptionEvent,
    event_source_code=SearchPrescriptionEvent.get_source_code_of_class(),
    constraints_generator=generate_search_prescription_constraints,
    examples=[
        {
            "prompt": "Search prescriptions where medicine_name equals 'Atorvastatin'",
            "prompt_for_task_generation": "Search prescriptions where medicine_name equals 'Atorvastatin'",
        },
        {
            "prompt": "Search prescriptions where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Search prescriptions where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Search prescriptions where medicine_name contains 'Vitamin' and doctor_name contains 'Smith'",
            "prompt_for_task_generation": "Search prescriptions where medicine_name contains 'Vitamin' and doctor_name contains 'Smith'",
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

SEARCH_MEDICAL_ANALYSIS_USE_CASE = UseCase(
    name="SEARCH_MEDICAL_ANALYSIS",
    description="The user clicked Search on the Medical Records page to apply title and/or doctor filters.",
    event=SearchMedicalAnalysisEvent,
    event_source_code=SearchMedicalAnalysisEvent.get_source_code_of_class(),
    constraints_generator=generate_search_medical_analysis_constraints,
    examples=[
        {
            "prompt": "Search medical analysis where record_title equals 'Complete Blood Count (CBC)'",
            "prompt_for_task_generation": "Search medical analysis where record_title equals 'Complete Blood Count (CBC)'",
        },
        {
            "prompt": "Search medical analysis where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Search medical analysis where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Search medical analysis where record_title contains 'X-Ray' and doctor_name contains 'Smith'",
            "prompt_for_task_generation": "Search medical analysis where record_title contains 'X-Ray' and doctor_name contains 'Smith'",
        },
    ],
)

VIEW_MEDICAL_ANALYSIS_USE_CASE = UseCase(
    name="VIEW_MEDICAL_ANALYSIS",
    description="The user viewed a medical analysis (clicked View Analysis on a card).",
    event=ViewMedicalAnalysisEvent,
    event_source_code=ViewMedicalAnalysisEvent.get_source_code_of_class(),
    constraints_generator=generate_view_medical_analysis_constraints,
    examples=[
        {
            "prompt": "View medical analysis where record_title equals 'Complete Blood Count (CBC)' and record_type equals 'lab_result' and record_date equals '2024-01-15'",
            "prompt_for_task_generation": "View medical analysis where record_title equals 'Complete Blood Count (CBC)' and record_type equals 'lab_result' and record_date equals '2024-01-15'",
        },
        {
            "prompt": "View medical analysis where record_title contains 'X-Ray' and doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "View medical analysis where record_title contains 'X-Ray' and doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "View medical analysis where record_type equals 'vaccination' and record_date greater than '2024-02-01'",
            "prompt_for_task_generation": "View medical analysis where record_type equals 'vaccination' and record_date greater than '2024-02-01'",
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
VIEW_DOCTOR_EDUCATION_USE_CASE = UseCase(
    name="VIEW_DOCTOR_EDUCATION",
    description="The user viewed a doctor's Education & Certifications tab on the doctor profile page.",
    event=ViewDoctorEducationEvent,
    event_source_code=ViewDoctorEducationEvent.get_source_code_of_class(),
    constraints_generator=generate_view_doctor_education_constraints,
    examples=[
        {
            "prompt": "View doctor education where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "View doctor education where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "View doctor education where doctor_name contains 'Patel' and speciality equals 'Dermatology'",
            "prompt_for_task_generation": "View doctor education where doctor_name contains 'Patel' and speciality equals 'Dermatology'",
        },
    ],
)
OPEN_CONTACT_DOCTOR_FORM_USE_CASE = UseCase(
    name="OPEN_CONTACT_DOCTOR_FORM",
    description="The user opened the contact doctor form (clicked Contact Doctor button on a doctor profile).",
    event=OpenContactDoctorFormEvent,
    event_source_code=OpenContactDoctorFormEvent.get_source_code_of_class(),
    constraints_generator=generate_open_contact_doctor_form_constraints,
    examples=[
        {
            "prompt": "Open contact doctor form where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "Open contact doctor form where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "Open contact form for Dr. Brian Patel",
            "prompt_for_task_generation": "Open contact doctor form where doctor_name contains 'Patel' and speciality equals 'Dermatology'",
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
FILTER_DOCTOR_REVIEWS_USE_CASE = UseCase(
    name="FILTER_DOCTOR_REVIEWS",
    description="The user filtered or sorted a doctor's reviews (by star rating and/or sort order: newest, oldest, highest, lowest).",
    event=FilterDoctorReviewsEvent,
    event_source_code=FilterDoctorReviewsEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_doctor_reviews_constraints,
    examples=[
        {
            "prompt": "Filter doctor reviews where doctor_name equals 'Dr. Alice Thompson' and filter_rating equals 5",
            "prompt_for_task_generation": "Filter doctor reviews where doctor_name equals 'Dr. Alice Thompson' and filter_rating equals 5",
        },
        {
            "prompt": "View 1-star reviews of Dr. Pepe where filter_rating equals 1 and doctor_name contains 'Pepe'",
            "prompt_for_task_generation": "Filter doctor reviews where filter_rating equals 1 and doctor_name contains 'Pepe'",
        },
        {
            "prompt": "Filter doctor reviews where speciality equals 'Dermatology' and sort_order equals 'newest'",
            "prompt_for_task_generation": "Filter doctor reviews where speciality equals 'Dermatology' and sort_order equals 'newest'",
        },
        {
            "prompt": "Sort doctor reviews by highest rating for Dr. Brian Patel",
            "prompt_for_task_generation": "Filter doctor reviews where doctor_name equals 'Dr. Brian Patel' and sort_order equals 'highest'",
        },
    ],
)
ALL_USE_CASES = [
    BOOK_APPOINTMENT_USE_CASE,
    OPEN_APPOINTMENT_FORM_USE_CASE,
    APPOINTMENT_BOOKED_SUCCESSFULLY_USE_CASE,
    REQUEST_APPOINTMENT_USE_CASE,
    REQUEST_QUICK_APPOINTMENT_USE_CASE,
    SEARCH_APPOINTMENT_USE_CASE,
    SEARCH_DOCTORS_USE_CASE,
    SEARCH_PRESCRIPTION_USE_CASE,
    SEARCH_MEDICAL_ANALYSIS_USE_CASE,
    VIEW_MEDICAL_ANALYSIS_USE_CASE,
    VIEW_PRESCRIPTION_USE_CASE,
    VIEW_DOCTOR_PROFILE_USE_CASE,
    VIEW_DOCTOR_EDUCATION_USE_CASE,
    FILTER_DOCTOR_REVIEWS_USE_CASE,
    OPEN_CONTACT_DOCTOR_FORM_USE_CASE,
    CONTACT_DOCTOR_USE_CASE,
    REFILL_PRESCRIPTION_USE_CASE,
    # DOCTOR_CONTACTED_SUCCESSFULLY_USE_CASE,
    # VIEW_REVIEWS_CLICKED_USE_CASE,
]
