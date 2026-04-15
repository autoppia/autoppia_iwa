from autoppia_iwa.src.demo_webs.classes import UseCase

STRICT_COPY_INSTRUCTION = "CRITICAL: Copy values EXACTLY as provided in the constraints. Do NOT correct typos, do NOT remove numbers, do NOT truncate or summarize strings, and do NOT 'clean up' names or titles (e.g., if constraint is 'Sofia 4', write 'Sofia 4', NOT 'Sofia'; if it is 'al signs R', write 'al signs R')."

from .events import (
    AppointmentBookedSuccessfullyEvent,
    ContactDoctorEvent,
    DoctorContactedSuccessfullyEvent,
    FilterDoctorReviewsEvent,
    OpenAppointmentFormEvent,
    OpenContactDoctorFormEvent,
    RefillRequestEvent,
    RequestQuickAppointmentEvent,
    SearchAppointmentEvent,
    SearchDoctorsEvent,
    SearchMedicalAnalysisEvent,
    SearchPrescriptionEvent,
    ViewDoctorAvailabilityEvent,
    ViewDoctorEducationEvent,
    ViewDoctorProfileEvent,
    ViewMedicalAnalysisEvent,
    ViewPrescriptionEvent,
)
from .generation_functions import (
    generate_appointment_booked_successfully_constraints,
    generate_contact_doctor_constraints,
    generate_doctor_contact_successfully_constraints,
    generate_filter_doctor_reviews_constraints,
    generate_open_appointment_form_constraints,
    generate_open_contact_doctor_form_constraints,
    generate_refill_prescription_constraints,
    generate_request_quick_appointment_constraints,
    generate_search_appointment_constraints,
    generate_search_doctors_constraints,
    generate_search_medical_analysis_constraints,
    generate_search_prescription_constraints,
    generate_view_doctor_availability_constraints,
    generate_view_doctor_education_constraints,
    generate_view_doctor_profile_constraints,
    generate_view_medical_analysis_constraints,
    generate_view_prescription_constraints,
)

###############################################################################
# DATA EXTRACTION PROMPTS (used when test_types=data_extraction_only)
###############################################################################

OPEN_APPOINTMENT_FORM_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of an appointment row in the open appointment form context (e.g., doctor name, medical specialty, appointment date, appointment time).

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "date", "time" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., doctor name, specialty, appointment date, appointment time).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Open...", "Book...", or "Click...".

Always end the question naturally with "so I can open the booking form for that appointment."

Examples:
- "Can you tell me the time of appointment with doctor name 'Dr. Lisa Green', specialty is 'Cardiology', and where the appointment date is '2025-09-01', so I can open the booking form for that appointment?"
- "Can you tell me the specialty for the appointment where the doctor name 'Dr. Linda Lewis', appointment date is '2025-09-02', and the appointment time is '11:15 AM', so I can open the booking form for that appointment?"
- "Can you tell me the date of the appointment with doctor 'Dr. Smith', speciality is 'Cardiology' and where appointment time is '10:00 AM', so I can open the booking form for that appointment?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

APPOINTMENT_BOOKED_SUCCESSFULLY_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field for an appointment slot in the successfully booked appointment context (e.g., doctor name, medical specialty, appointment date, appointment time).

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "date", "time" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., doctor name, specialty, appointment date, appointment time).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Book...", "Schedule...", or "Submit...".

Always end the question naturally with "so I can book it."

Examples:
- "Can you tell me the appointment date for the slot where the doctor name is 'Dr. Lisa Green', specialty is 'Cardiology', and the appointment time is '11:00 AM', so I can book it?"
- "Can you tell me the specialty for the appointment where the doctor name is 'Dr. Linda Lewis', appointment date is '2025-09-02', and the appointment time is '11:15 AM', so I can book it?"
- "Can you tell me the appointment time for the slot where the doctor name is 'Dr. Smith', speciality is 'Cardiology' and appointment time is '10:00 AM', so I can book it?"



CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

SEARCH_APPOINTMENT_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of an appointment in the search appointments context (e.g., doctor name, medical specialty, appointment date, appointment time).

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "date", "time" or any names with underscores (_).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Search...", "Filter...", or "Find...".

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.

The output must be a single question asking only for the verify field value.
""".strip()

SEARCH_DOCTORS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a doctor in the search doctors context (e.g., doctor name, specialty, languages, consultation fee).

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "language", "consultation fee" or any names with underscores (_).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Search...", "Look up...", or "Find...".

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.

The output must be a single question asking only for the verify field value.
""".strip()

SEARCH_PRESCRIPTION_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a prescription in the search prescriptions context (e.g., medicine name, prescribing doctor name, prescription start date, status, dosage).

Use natural language only. Do NOT use schema-style field names such as "medicine_name", "doctor_name", "start_date" or any names with underscores (_).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Search...", "Find...", or "Look up...".

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.

The output must be a single question asking only for the verify field value.
""".strip()

REFILL_PRESCRIPTION_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be the remaining refills for the prescription, the medicine name, the prescribing doctor name, prescription start date, status or dosage in the refill prescription context.

Use natural language only. Do NOT use schema-style field names such as "medicine_name", "doctor_name", "start_date", "refills_remaining" or any names with underscores (_).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Refill...", "Order...", or "Request...".

Always end the question naturally with "so I can request a refill."

For example, format the question naturally:
- "Can you tell me how many refills remaining for the prescribed medicine 'Paracetamol', prescribed by doctor 'Dr. Smith', whose dosage is '500mg', start date is '10 Jan 2025', and status is 'active', so I can refill the prescription?"

Examples:
- "Can you tell me how many refills remaining for the prescribed medicine 'Ibuprofen', prescribed by doctor 'Dr. John Doe', whose dosage is '200mg', start date is '15 Feb 2025', and status is 'active', so I can refill the prescription?"
- "Can you tell me how many refills remaining for the prescribed medicine 'Amoxicillin', prescribed by doctor 'Dr. Emily Clark', whose dosage is '250mg', start date is '20 Mar 2025', and status is 'completed', so I can refill the prescription?"
- "Can you tell me how many refills remaining for the prescribed medicine 'Metformin', prescribed by doctor 'Dr. Michael Lee', whose dosage is '850mg', start date is '5 Apr 2025', and status is 'refill needed', so I can refill the prescription?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.

The output must be a single question asking only for the verify field value.
""".strip()

VIEW_PRESCRIPTION_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a prescription in the view prescription context (e.g., medicine name, doctor name, start date, dosage, status, end date, pharmacy, prescription number, cost, side effects, instructions).

Use natural language only. Do NOT use schema-style field names such as "medicine_name", "doctor_name", "start_date", "dosage", "status", "end_date", "pharmacy", "prescription_number", "cost", "side_effects", "instructions" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., medicine name, doctor name, start date, dosage, status, end date, pharmacy, prescription number, cost, side effects, instructions).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "View...", "Check...", or "See...".

Always end the question naturally with "after viewing the prescription."

For example, if the verify field is 'cost', format the question naturally:
- "Can you tell me the cost of the prescribed medicine 'Paracetamol', prescribed by doctor 'Dr. Smith', whose start date is '2024-12-15', dosage is '500mg', status is 'active', end date is '20 Jan 2025', pharmacy is 'City Pharmacy', prescription number is 'RX12345', side effects are 'Nausea', and instructions are 'Take after meals', after viewing the prescription?"

Examples:
- "Can you tell me the medicine name prescribed by doctor 'Dr. John Doe', whose start date is '2025-11-19', dosage is '200mg', status is 'active', end date is '2025-12-15', pharmacy is 'HealthPlus', prescription number is 'RX67890', cost is '$20.1', side effects are 'Dizziness, Nausea', and instructions are 'Take twice daily', after viewing the prescription?"
- "Can you tell me the doctor name for the prescribed medicine 'Ibuprofen', whose start date is '2025-07-15', dosage is '400mg', status is 'completed', end date is '2025-08-15', pharmacy is 'MediCare', prescription number is 'RX11223', cost is '$15.01', side effects are 'Stomach upset, Fatigue', and instructions are 'Take with food', after viewing the prescription?"
- "Can you tell me the dosage of the prescribed medicine 'Amoxicillin', prescribed by doctor 'Dr. Emily Clark', whose start date is '2025-04-20', status is 'active', end date is '2025-04-30', pharmacy is 'Wellness Pharmacy', prescription number is 'RX33445', cost is '$30.45', side effects are 'Rash', and instructions are 'Complete full course', after viewing the prescription?"
- "Can you tell me the instructions for the prescribed medicine 'Metformin', prescribed by doctor 'Dr. Michael Lee', whose start date is '2026-02-05', dosage is '850mg', status is 'refill needed', end date is '2026-02-23', pharmacy is 'Care Pharmacy', prescription number is 'RX55667', cost is '$25', and side effects are 'Fatigue', after viewing the prescription?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.

The output must be a single question asking only for the verify field value.
""".strip()

SEARCH_MEDICAL_ANALYSIS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a medical record in the search medical records context (e.g., record title, doctor name, record status, record date).

Use natural language only. Do NOT use schema-style field names such as "record_title", "doctor_name", "record_status", "record_date" or any names with underscores (_).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Search...", "Find...", or "Filter...".

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.

The output must be a single question asking only for the verify field value.
""".strip()

VIEW_MEDICAL_ANALYSIS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a medical analysis record in the view medical analysis context (e.g., record title, doctor name, record status, record date, description, facility).

Use natural language only. Do NOT use schema-style field names such as "record_title", "doctor_name", "record_status", "record_date", "description", "facility" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., record title, doctor name, record status, record date, description, facility).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "View...", "Check...", or "See...".

Always end the question naturally with "after viewing the medical analysis."

For example, if the verify field is 'facility', format the question naturally:
- "Can you tell me the facility of the record whose title is 'Blood Test Report', doctor name is 'Dr. Smith', record status is 'completed', record date is '2025-08-23', and description is 'Routine blood checkup', after viewing the medical analysis?"

Examples:
- "Can you tell me the doctor name for the record whose title is 'X-Ray Report', record status is 'completed', record date is '2025-11-19', description is 'Chest X-ray', and facility is 'HealthPlus Center', after viewing the medical analysis?"
- "Can you tell me the record status of the record whose title is 'CT Scan', doctor name is 'Dr. Emily Clark', record date is '2026-03-01', description is 'Brain scan', and facility is 'MediCare Lab', after viewing the medical analysis?"
- "Can you tell me the description of the record whose title is 'Ultrasound Report', doctor name is 'Dr. Michael Lee', record status is 'Completed', record date is '2025-10-27', and facility is 'Wellness Clinic', after viewing the medical analysis?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the verify field value.
""".strip()

VIEW_DOCTOR_PROFILE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a doctor profile in the view doctor profile context (e.g., doctor name, speciality, rating, consultation fee, language, experience, sub specialities, office location, email).

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "rating", "consultation_fee", "language", "experience", "sub_specialities", "office_location", "email" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., doctor name, speciality, rating, consultation fee, language, experience, sub specialities, office location, email).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "View...", "Check...", or "See...".

Always end the question naturally with "after viewing the doctor profile."

For example, if the verify field is 'consultation fee', format the question naturally:
- "Can you tell me the consultation fee of doctor 'Dr. Smith', whose speciality is 'Cardiology', rating is 4.8, language is 'English', experience is '10 years experience', sub specialities are 'Heart Surgery', office location is 'City Hospital', and email is 'dr.smith@example.com', after viewing the doctor profile?"

Examples:
- "Can you tell me the speciality of doctor 'Dr. John Doe', whose rating is 4.6, consultation fee is '$70', language is 'English', experience is '12 years experience', sub specialities are 'Neurology', office location is 'MediCare Center', and email is 'john.doe@example.com', after viewing the doctor profile?"
- "Can you tell me the rating of doctor 'Dr. Emily Clark', speciality is 'Orthopedics', consultation fee is '$60', language is 'English', experience is '9 years experience', sub specialities are 'Joint Replacement', whose office location is 'Wellness Hospital', and whose email is 'emily.clark@example.com', after viewing the doctor profile?"
- "Can you tell me the office location of doctor 'Dr. Michael Lee', speciality is 'Pediatrics', rating is 4.7, consultation fee is '$40', language is 'English', experience is '7 years experience', sub specialities are 'Child Care', and email is 'michael.lee@example.com', after viewing the doctor profile?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the verify field value.
""".strip()

VIEW_DOCTOR_EDUCATION_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the education of a doctor in the view doctor education context.

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "consultation_fee", "education" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., doctor name, speciality, consultation fee, education).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the education.

Do NOT start questions with imperative phrasing like "View...", "Check...", or "See...".

Always end the question naturally with "after viewing the doctor profile."

For example, format the question naturally:
- "Can you tell me the education of doctor 'Dr. Smith', whose speciality is 'Cardiology' and consultation fee is '$100', after viewing the doctor profile?"

Examples:
- "Can you tell me the education of doctor 'Dr. John Doe', whose speciality is 'Dermatology' and consultation fee is '$80', after viewing the doctor profile?"
- "Can you tell me the education of doctor 'Dr. Emily Clark', whose speciality is 'Neurology' and consultation fee is '$120', after viewing the doctor profile?"
- "Can you tell me the education of doctor 'Dr. Michael Lee', whose speciality is 'Orthopedics' and consultation fee is '$90', after viewing the doctor profile?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value (education) itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the education.
""".strip()

VIEW_DOCTOR_AVAILABILITY_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the availability of a doctor for a specific chosen day in the view doctor availability context (e.g., Monday availability, Tuesday availability, Friday availability).

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "consultation_fee", "monday_availability", "tuesday_availability", "friday_availability" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., doctor name, speciality, consultation fee, Monday availability, Tuesday availability, Friday availability).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the availability of the chosen day.

Do NOT start questions with imperative phrasing like "View...", "Check...", or "See...".

Always end the question naturally with "after viewing the doctor profile."

For example, if the verify field is 'Friday availability', format the question naturally:
- "Can you tell me the Friday availability time duration of doctor 'Dr. Smith', whose speciality is 'Cardiology' and consultation fee is '$100', after viewing the doctor availability?"

Examples:
- "Can you tell me the Monday availability time duration of doctor 'Dr. John Doe', whose speciality is 'Dermatology' and consultation fee is '$80', after viewing the doctor availability?"
- "Can you tell me the Tuesday availability time duration of doctor 'Dr. Emily Clark', whose speciality is 'Neurology' and consultation fee is '$120', after viewing the doctor availability?"
- "Can you tell me the Friday availability time duration of doctor 'Dr. Michael Lee', whose speciality is 'Orthopedics' and consultation fee is '$90', after viewing the doctor availability?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value (availability for the chosen day) itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the availability of the chosen day.
""".strip()

FILTER_DOCTOR_REVIEWS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be one of the following attributes of a doctor review in the filter doctor reviews context: reviewer name, review date, or review content.

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "reviewer_name", "review_date", "review_content" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., doctor name, speciality, reviewer name, review date, review content).

Include all question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Filter...", "Sort...", or "Find...".

Always end the question naturally with "after viewing doctor profile."

For example, if the verify field is 'review content', format the question naturally:
- "Can you tell me the review content for doctor 'Dr. Smith', whose speciality is 'Cardiology', where reviewer name is 'John Doe' and review date is '3/21/2026', after viewing doctor profile?"

Examples:
- "Can you tell me the reviewer name for doctor 'Dr. John Doe', whose speciality is 'Dermatology', where review date is '6/27/2025' and review content is 'Excellent service', after viewing doctor profile?"
- "Can you tell me the review date for doctor 'Dr. Emily Clark', whose speciality is 'Neurology', where reviewer name is 'Alice Brown' and review content is 'Very professional', after viewing doctor profile?"
- "Can you tell me the review content for doctor 'Dr. Michael Lee', whose speciality is 'Orthopedics', where reviewer name is 'David Wilson' and review date is '11/11/2025', after viewing doctor profile?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the verify field value.
""".strip()

CONTACT_DOCTOR_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a doctor in the contact doctor context (e.g., doctor name, speciality, rating, consultation fee, language, experience, sub specialities, office location, email, phone).

Use natural language only. Do NOT use schema-style field names such as "doctor_name", "speciality", "rating", "consultation_fee", "language", "experience", "sub_specialities", "office_location", "email", "phone" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., doctor name, speciality, rating, consultation fee, language, experience, sub specialities, office location, email, phone).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Contact...", "Call...", or "Email...".

Always end the question naturally with "so I can contact the doctor."

For example, if the verify field is 'phone', format the question naturally:
- "Can you tell me the phone of doctor 'Dr. Smith', whose speciality is 'Cardiology', rating is 4.8, consultation fee is '$100', language is 'English', experience is '10 years experience', sub specialities are 'Heart Surgery', office location is 'City Hospital', email is 'dr.smith@example.com' and phone is '(555) 123-4567', so I can contact the doctor?"

Examples:
- "Can you tell me the speciality of doctor 'Dr. John Doe', whose rating is 4.6, consultation fee is '$70', language is 'English', experience is '12 years experience', sub specialities are 'Neurology', office location is 'MediCare Center', email is 'john.doe@example.com', and phone is '(555) 123-4567', so I can contact the doctor?"
- "Can you tell me the email of doctor 'Dr. Emily Clark', whose speciality is 'Orthopedics', rating is 4.7, consultation fee is '$60', language is 'English', experience is '9 years experience', sub specialities are 'Joint Replacement', office location is 'Wellness Hospital', and phone is '(555) 123-4567', so I can contact the doctor?"
- "Can you tell me the phone number of doctor 'Dr. Michael Lee', whose speciality is 'Pediatrics', rating is 4.4, consultation fee is '$40', language is 'English', experience is '7 years', sub specialities are 'Child Care', office location is 'Care Clinic', and email is 'michael.lee@example.com', so I can contact the doctor?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the verify field value.
""".strip()

OPEN_APPOINTMENT_FORM_USE_CASE = UseCase(
    name="OPEN_APPOINTMENT_FORM",
    description="The user opened the appointment booking form (clicked Book Appointment on an appointment row).",
    event=OpenAppointmentFormEvent,
    event_source_code=OpenAppointmentFormEvent.get_source_code_of_class(),
    constraints_generator=generate_open_appointment_form_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (doctor_name, speciality, date, time). Format: 'Open appointment form where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
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
    additional_prompt_info=f"CRITICAL: Use explicit field names (patient_name, doctor_name, date, time, speciality, insurance_provider, insurance_number, patient_email, patient_phone, emergency_contact, emergency_phone, notes, reason_for_visit). Format: 'Book an appointment where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "Book an appointment where patient_name equals 'John Doe 4' and doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-23' and speciality equals 'Cardiology' and reason_for_visit contains 'chest pain s'",
            "prompt_for_task_generation": "Book an appointment where patient_name equals 'John Doe 4' and doctor_name equals 'Dr. Alice Thompson' and date equals '2025-09-23' and speciality equals 'Cardiology' and reason_for_visit contains 'chest pain s'",
        },
        {
            "prompt": "Book an appointment where patient_email equals 'jane.d@example.com 2' and patient_phone equals '+1-555-0199' and insurance_provider equals 'HealthCare plus' and notes contains 'Bring history'",
            "prompt_for_task_generation": "Book an appointment where patient_email equals 'jane.d@example.com 2' and patient_phone equals '+1-555-0199' and insurance_provider equals 'HealthCare plus' and notes contains 'Bring history'",
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
            "prompt": "Request quick appointment where patient_name equals 'John Smith' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "Request quick appointment where patient_name equals 'John Smith' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "Submit quick appointment form where speciality equals 'Dermatology'",
            "prompt_for_task_generation": "Request quick appointment where speciality equals 'Dermatology'",
        },
    ],
)

SEARCH_APPOINTMENT_USE_CASE = UseCase(
    name="SEARCH_APPOINTMENT",
    description="The user clicked Search on the Appointments page to apply doctor, speciality, or date filters.",
    event=SearchAppointmentEvent,
    event_source_code=SearchAppointmentEvent.get_source_code_of_class(),
    constraints_generator=generate_search_appointment_constraints,
    additional_prompt_info="CRITICAL: Use explicit field names (doctor_name, speciality, date). Format: 'Search appointments where <field> <operator> '<value>''. Copy values EXACTLY.",
    examples=[
        {
            "prompt": "Search appointments where doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Search appointments where doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Search appointments where speciality equals 'Cardiology' and date equals '2025-09-20'",
            "prompt_for_task_generation": "Search appointments where speciality equals 'Cardiology' and date equals '2025-09-20'",
        },
        {
            "prompt": "Search appointments where date equals '2025-09-25'",
            "prompt_for_task_generation": "Search appointments where date equals '2025-09-25'",
        },
    ],
)

SEARCH_DOCTORS_USE_CASE = UseCase(
    name="SEARCH_DOCTORS",
    description="The user clicked Search on the Doctors page to apply name, speciality, and/or language filters.",
    event=SearchDoctorsEvent,
    event_source_code=SearchDoctorsEvent.get_source_code_of_class(),
    constraints_generator=generate_search_doctors_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (doctor_name, speciality, language). Format: 'Search doctors where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "Search doctors where doctor_name contains 'Alice 7' and speciality equals 'General Practice g'",
            "prompt_for_task_generation": "Search doctors where doctor_name contains 'Alice 7' and speciality equals 'General Practice g'",
        },
    ],
)

SEARCH_PRESCRIPTION_USE_CASE = UseCase(
    name="SEARCH_PRESCRIPTION",
    description="The user clicked Search on the Prescriptions page to apply medicine and/or doctor filters.",
    event=SearchPrescriptionEvent,
    event_source_code=SearchPrescriptionEvent.get_source_code_of_class(),
    constraints_generator=generate_search_prescription_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (medicine_name, doctor_name). Format: 'Search prescriptions where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "Search prescriptions where medicine_name contains 'Vitamin 4' and doctor_name contains 'Smith a'",
            "prompt_for_task_generation": "Search prescriptions where medicine_name contains 'Vitamin 4' and doctor_name contains 'Smith a'",
        },
    ],
)

REFILL_PRESCRIPTION_USE_CASE = UseCase(
    name="REFILL_PRESCRIPTION",
    description="The user requested a prescription refill for a specific medicine.",
    event=RefillRequestEvent,
    event_source_code=RefillRequestEvent.get_source_code_of_class(),
    constraints_generator=generate_refill_prescription_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (medicine_name). Format: 'Refill prescription where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
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
    additional_prompt_info="CRITICAL: Use explicit field names (doctor_name, start_date, dosage, medicine_name, category). Format: 'View a prescription where <field> <operator> '<value>''. Copy values EXACTLY.",
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
    additional_prompt_info=f"CRITICAL: Use explicit field names (record_title, doctor_name). Format: 'Search medical analysis where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "Search medical analysis where record_title equals 'Complete Blood Count (CBC) 99' and doctor_name equals 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Search medical analysis where record_title equals 'Complete Blood Count (CBC) 99' and doctor_name equals 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Search medical analysis where record_title contains 'al signs R' and doctor_name contains 'Smith 12'",
            "prompt_for_task_generation": "Search medical analysis where record_title contains 'al signs R' and doctor_name contains 'Smith 12'",
        },
    ],
)

VIEW_MEDICAL_ANALYSIS_USE_CASE = UseCase(
    name="VIEW_MEDICAL_ANALYSIS",
    description="The user viewed a medical analysis (clicked View Analysis on a card).",
    event=ViewMedicalAnalysisEvent,
    event_source_code=ViewMedicalAnalysisEvent.get_source_code_of_class(),
    constraints_generator=generate_view_medical_analysis_constraints,
    additional_prompt_info="Use format: 'View medical analysis where field operator value'. Always mention each constraint field explicitly (record_title, doctor_name, record_type).",
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
    description="The user viewed a doctor's profile, including name, rating, speciality, consultation fee, and languages.",
    event=ViewDoctorProfileEvent,
    event_source_code=ViewDoctorProfileEvent.get_source_code_of_class(),
    constraints_generator=generate_view_doctor_profile_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (doctor_name, speciality, rating, consultation_fee, language). Format: 'View a doctor profile where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "View a doctor profile where doctor_name equals 'Dr. Alice Thompson' and rating greater than 4.5 and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "View a doctor profile where doctor_name equals 'Dr. Alice Thompson' and rating greater than 4.5 and speciality equals 'Cardiology'",
        },
        {
            "prompt": "View a doctor profile where doctor_name contains 'Clara' and consultation_fee less than 200 and language equals 'Spanish'",
            "prompt_for_task_generation": "View a doctor profile where doctor_name contains 'Clara' and consultation_fee less than 200 and language equals 'Spanish'",
        },
        {
            "prompt": "View a doctor profile where speciality equals 'Dermatology' and language equals 'English'",
            "prompt_for_task_generation": "View a doctor profile where speciality equals 'Dermatology' and language equals 'English'",
        },
    ],
)
VIEW_DOCTOR_EDUCATION_USE_CASE = UseCase(
    name="VIEW_DOCTOR_EDUCATION",
    description="The user viewed a doctor's Education & Certifications tab on the doctor profile page.",
    event=ViewDoctorEducationEvent,
    event_source_code=ViewDoctorEducationEvent.get_source_code_of_class(),
    constraints_generator=generate_view_doctor_education_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (doctor_name, speciality). Format: 'View doctor education where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "View doctor education where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "View doctor education where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "View doctor education where doctor_name contains 'Patel' and rating greater than 4.5 and language equals 'English'",
            "prompt_for_task_generation": "View doctor education where doctor_name contains 'Patel' and rating greater than 4.5 and language equals 'English'",
        },
        {
            "prompt": "View doctor education where speciality equals 'Dermatology' and consultation_fee less than 200",
            "prompt_for_task_generation": "View doctor education where speciality equals 'Dermatology' and consultation_fee less than 200",
        },
    ],
)

VIEW_DOCTOR_AVAILABILITY_USE_CASE = UseCase(
    name="VIEW_DOCTOR_AVAILABILITY",
    description="The user viewed a doctor's Availability tab on the doctor profile page.",
    event=ViewDoctorAvailabilityEvent,
    event_source_code=ViewDoctorAvailabilityEvent.get_source_code_of_class(),
    constraints_generator=generate_view_doctor_availability_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (doctor_name, speciality). Format: 'View doctor availability where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
    examples=[
        {
            "prompt": "View doctor availability where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
            "prompt_for_task_generation": "View doctor availability where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'",
        },
        {
            "prompt": "View doctor availability where doctor_name contains 'Patel' and rating greater than 4.5 and language equals 'English'",
            "prompt_for_task_generation": "View doctor availability where doctor_name contains 'Patel' and rating greater than 4.5 and language equals 'English'",
        },
        {
            "prompt": "View doctor availability where speciality equals 'Dermatology' and consultation_fee less than 200",
            "prompt_for_task_generation": "View doctor availability where speciality equals 'Dermatology' and consultation_fee less than 200",
        },
    ],
)
OPEN_CONTACT_DOCTOR_FORM_USE_CASE = UseCase(
    name="OPEN_CONTACT_DOCTOR_FORM",
    description="The user opened the contact doctor form (clicked Contact Doctor button on a doctor profile).",
    event=OpenContactDoctorFormEvent,
    event_source_code=OpenContactDoctorFormEvent.get_source_code_of_class(),
    constraints_generator=generate_open_contact_doctor_form_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (doctor_name, speciality, language). Format: 'Open contact doctor form where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
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

4. CRITICAL: Copy the constraint values EXACTLY as provided. Do NOT correct typos or remove numbers. (e.g., if constraint is 'Rodriguez 78', write 'Rodriguez 78', NOT 'Rodriguez').
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

DOCTOR_CONTACTED_SUCCESSFULLY_ADDITIONAL_INFO = f"""
CRITICAL: Use explicit field names (doctor_name, patient_name, speciality, patient_email, patient_phone, preferred_contact_method, subject, urgency, message).
Format: "Contact a doctor where <field> <operator> '<value>'"
Example: "Contact a doctor where doctor_name equals 'Dr. Alice Thompson' and patient_name contains 'John Smith' and subject equals 'General consultation'"
{STRICT_COPY_INSTRUCTION}
""".strip()
DOCTOR_CONTACTED_SUCCESSFULLY_USE_CASE = UseCase(
    name="DOCTOR_CONTACTED_SUCCESSFULLY",
    description="The user has successfully contacted a doctor, providing personal details, contact preferences, and message context.",
    event=DoctorContactedSuccessfullyEvent,
    event_source_code=DoctorContactedSuccessfullyEvent.get_source_code_of_class(),
    additional_prompt_info=DOCTOR_CONTACTED_SUCCESSFULLY_ADDITIONAL_INFO,
    constraints_generator=generate_doctor_contact_successfully_constraints,
    examples=[
        {
            "prompt": "Contact a doctor where doctor_name equals 'Dr. Alice Thompson' and patient_name equals 'John Smith' and subject equals 'General consultation'",
            "prompt_for_task_generation": "Contact a doctor where doctor_name equals 'Dr. Alice Thompson' and patient_name equals 'John Smith' and subject equals 'General consultation'",
        },
        {
            "prompt": "Send a message to a doctor where speciality equals 'Dermatology' and urgency equals 'high' and message contains 'urgent rash'",
            "prompt_for_task_generation": "Send a message to a doctor where speciality equals 'Dermatology' and urgency equals 'high' and message contains 'urgent rash'",
        },
        {
            "prompt": "Reach out to a doctor where patient_email equals 'maria.gonzalez@example.com' and preferred_contact_method equals 'email' and doctor_name contains 'Patel'",
            "prompt_for_task_generation": "Reach out to a doctor where patient_email equals 'maria.gonzalez@example.com' and preferred_contact_method equals 'email' and doctor_name contains 'Patel'",
        },
    ],
)
FILTER_DOCTOR_REVIEWS_USE_CASE = UseCase(
    name="FILTER_DOCTOR_REVIEWS",
    description="The user filtered or sorted a doctor's reviews (by star rating and/or sort order: newest, oldest, highest, lowest).",
    event=FilterDoctorReviewsEvent,
    event_source_code=FilterDoctorReviewsEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_doctor_reviews_constraints,
    additional_prompt_info=f"CRITICAL: Use explicit field names (doctor_name, speciality, filter_rating, sort_order). Format: 'Filter doctor reviews where <field> <operator> '<value>''. {STRICT_COPY_INSTRUCTION}",
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
    OPEN_APPOINTMENT_FORM_USE_CASE,
    APPOINTMENT_BOOKED_SUCCESSFULLY_USE_CASE,
    REQUEST_QUICK_APPOINTMENT_USE_CASE,
    SEARCH_APPOINTMENT_USE_CASE,
    SEARCH_DOCTORS_USE_CASE,
    SEARCH_PRESCRIPTION_USE_CASE,
    REFILL_PRESCRIPTION_USE_CASE,
    VIEW_PRESCRIPTION_USE_CASE,
    SEARCH_MEDICAL_ANALYSIS_USE_CASE,
    VIEW_MEDICAL_ANALYSIS_USE_CASE,
    VIEW_DOCTOR_PROFILE_USE_CASE,
    VIEW_DOCTOR_EDUCATION_USE_CASE,
    VIEW_DOCTOR_AVAILABILITY_USE_CASE,
    FILTER_DOCTOR_REVIEWS_USE_CASE,
    OPEN_CONTACT_DOCTOR_FORM_USE_CASE,
    CONTACT_DOCTOR_USE_CASE,
    DOCTOR_CONTACTED_SUCCESSFULLY_USE_CASE,
]
