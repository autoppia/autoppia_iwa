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
    UploadHealthDataEvent,
    ViewDoctorProfileEvent,
    ViewHealthMetricsEvent,
    ViewPrescriptionEvent,
    ViewReviewsEvent,
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
    generate_upload_health_data_constraints,
    generate_view_doctor_profile_constraints,
    generate_view_health_metrics_constraints,
    generate_view_prescription_constraints,
    generate_view_reviews_constraints,
)

BOOK_APPOINTMENT_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.
2. MANDATORY: You MUST include ALL constraint values explicitly in the prompt. Every constraint value specified in the constraints MUST appear in the generated prompt text.
3. Wrap specific constraint values in single quotes when they are strings (e.g., 'Dr. Alice Thompson', 'Cardiology', 'September 20th, 2025').
4. Use natural phrasing for operators:
   - "equals" → "is" or "with" (e.g., "with Dr. Alice Thompson" not "where doctor_name equals")
   - "not_equals" → "other than" or "except" (e.g., "any doctor except 'Dr. Clara Nguyen'")
   - "contains" → "contains" or "includes" or "with ... in" (e.g., "with Gmail in the email")
   - "greater_than" → "after" (for dates) or "above" (for numbers)
   - "less_than" → "before" (for dates) or "below" (for numbers)

Correct examples:
- Book an appointment with Dr. Alice Thompson on September 20th, 2025 at 9:00 AM for Cardiology.
- Book an appointment with Dr. Daniel Roberts for patient John Doe who has a Gmail address for chest pain.
- Book an appointment with a doctor named Nguyen in Dermatology for patient Emma Wilson about skin rash.

Incorrect examples:
- Book an appointment where doctor_name equals 'Dr. Alice Thompson' and date equals 'September 20th, 2025'. (uses "equals" - too technical)
- Book an appointment with Dr. Alice Thompson. (missing date, time, or specialty constraints)
""".strip()

BOOK_APPOINTMENT_USE_CASE = UseCase(
    name="BOOK_APPOINTMENT",
    description="The user booked an appointment with a doctor for a given date, time, and speciality, including patient details when confirmed. Uses semantic values (doctor names, specialty names, patient names) for natural prompts.",
    event=BookAppointmentEvent,
    event_source_code=BookAppointmentEvent.get_source_code_of_class(),
    additional_prompt_info=BOOK_APPOINTMENT_ADDITIONAL_INFO,
    constraints_generator=generate_book_appointment_constraints,
    examples=[
        {
            "prompt": "Book an appointment with Dr. Alice Thompson on September 20th, 2025 at 9:00 AM for Cardiology",
            "prompt_for_task_generation": "Book an appointment with Dr. Alice Thompson on September 20th, 2025 at 9:00 AM for Cardiology",
        },
        {
            "prompt": "Book an appointment with Dr. Daniel Roberts for patient John Doe who has a Gmail address for chest pain",
            "prompt_for_task_generation": "Book an appointment with Dr. Daniel Roberts for patient John Doe who has a Gmail address for chest pain",
        },
        {
            "prompt": "Book an appointment with a doctor named Nguyen in Dermatology for patient Emma Wilson about skin rash",
            "prompt_for_task_generation": "Book an appointment with a doctor named Nguyen in Dermatology for patient Emma Wilson about skin rash",
        },
        {
            "prompt": "Book an appointment with Dr. Michael Smith on September 25th, 2025 at 2:30 PM in Pediatrics with a US phone number",
            "prompt_for_task_generation": "Book an appointment with Dr. Michael Smith on September 25th, 2025 at 2:30 PM in Pediatrics with a US phone number",
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
            "prompt": "Appointment booked successfully for patient John Doe with Dr. Alice Thompson on September 23rd, 2025 at 10:00 AM in Cardiology for chest pain",
            "prompt_for_task_generation": "Appointment booked successfully for patient John Doe with Dr. Alice Thompson on September 23rd, 2025 at 10:00 AM in Cardiology for chest pain",
        },
        {
            "prompt": "Appointment booked successfully for a patient other than Sarah Lee with BlueCross insurance and insurance number that includes BCX123 with Dr. Daniel Roberts scheduled after September 20th, 2025",
            "prompt_for_task_generation": "Appointment booked successfully for a patient other than Sarah Lee with BlueCross insurance and insurance number that includes BCX123 with Dr. Daniel Roberts scheduled after September 20th, 2025",
        },
        {
            "prompt": "Appointment booked successfully with a Gmail email address and US phone number with emergency contact Jane Doe at 555-1234 and notes about bringing previous reports",
            "prompt_for_task_generation": "Appointment booked successfully with a Gmail email address and US phone number with emergency contact Jane Doe at 555-1234 and notes about bringing previous reports",
        },
        {
            "prompt": "Appointment booked successfully with a doctor named Nguyen in Dermatology scheduled before October 1st, 2025 for skin rash for patient Emma Wilson",
            "prompt_for_task_generation": "Appointment booked successfully with a doctor named Nguyen in Dermatology scheduled before October 1st, 2025 for skin rash for patient Emma Wilson",
        },
        {
            "prompt": "Appointment booked successfully with insurance provider other than Aetna and insurance number without XYZ with phone 444-5678 and email michael.smith@example.com with notes about first-time consultation",
            "prompt_for_task_generation": "Appointment booked successfully with insurance provider other than Aetna and insurance number without XYZ with phone 444-5678 and email michael.smith@example.com with notes about first-time consultation",
        },
        {
            "prompt": "Appointment booked successfully with emergency contact Robert King at 222-9999 with Dr. Clara Nguyen on September 29th, 2025 at 2:30 PM in Orthopedics",
            "prompt_for_task_generation": "Appointment booked successfully with emergency contact Robert King at 222-9999 with Dr. Clara Nguyen on September 29th, 2025 at 2:30 PM in Orthopedics",
        },
    ],
)

CANCEL_BOOK_APPOINTMENT_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.
2. MANDATORY: You MUST include ALL constraint values explicitly in the prompt. Every constraint value specified in the constraints MUST appear in the generated prompt text.
3. Wrap specific constraint values in single quotes when they are strings (e.g., 'Dr. Alice Thompson', 'September 20th, 2025').
4. Use natural phrasing for operators:
   - "equals" → "with" (e.g., "Cancel an appointment with Dr. Alice Thompson")
   - "not_equals" → "except" or "other than" (e.g., "any doctor except Dr. Clara Nguyen")
   - "contains" → "named" (e.g., "a doctor named Daniel")
   - "greater_than" → "after" (for dates/times)
   - "less_than" → "before" (for dates/times)

Correct examples:
- Cancel an appointment with Dr. Alice Thompson on September 20th, 2025 at 9:00 AM for Cardiology.
- Cancel an appointment with any doctor except Dr. Clara Nguyen on any date except September 21st, 2025 at 10:30 AM for Dermatology.
- Cancel an appointment with a doctor named Daniel scheduled before September 25th, 2025 after 11:00 AM in Orthopedics.

Incorrect examples:
- Cancel appointment where doctor_name equals 'Dr. Alice Thompson' and date equals 'September 20th, 2025'. (uses "equals" - too technical)
- Cancel an appointment. (missing constraint values)
""".strip()

CANCEL_BOOK_APPOINTMENT_USE_CASE = UseCase(
    name="CANCEL_BOOK_APPOINTMENT",
    description="The user canceled a previously booked appointment with a doctor for a given date, time, and speciality.",
    event=CancelBookAppointmentEvent,
    event_source_code=CancelBookAppointmentEvent.get_source_code_of_class(),
    additional_prompt_info=CANCEL_BOOK_APPOINTMENT_ADDITIONAL_INFO,
    constraints_generator=generate_cancel_appointment_constraints,
    examples=[
        {
            "prompt": "Cancel an appointment with Dr. Alice Thompson on September 20th, 2025 at 9:00 AM for Cardiology",
            "prompt_for_task_generation": "Cancel an appointment with Dr. Alice Thompson on September 20th, 2025 at 9:00 AM for Cardiology",
        },
        {
            "prompt": "Cancel an appointment with any doctor except Dr. Clara Nguyen on any date except September 21st, 2025 at 10:30 AM for Dermatology",
            "prompt_for_task_generation": "Cancel an appointment with any doctor except Dr. Clara Nguyen on any date except September 21st, 2025 at 10:30 AM for Dermatology",
        },
        {
            "prompt": "Cancel an appointment with a doctor named Daniel scheduled before September 25th, 2025 after 11:00 AM in Orthopedics",
            "prompt_for_task_generation": "Cancel an appointment with a doctor named Daniel scheduled before September 25th, 2025 after 11:00 AM in Orthopedics",
        },
        {
            "prompt": "Cancel an appointment in Neurology with Dr. Robert King scheduled after September 28th, 2025 at 1:00 PM",
            "prompt_for_task_generation": "Cancel an appointment in Neurology with Dr. Robert King scheduled after September 28th, 2025 at 1:00 PM",
        },
        {
            "prompt": "Cancel an appointment with Dr. Michael Smith on September 30th, 2025 at any time except 3:00 PM for Pediatrics",
            "prompt_for_task_generation": "Cancel an appointment with Dr. Michael Smith on September 30th, 2025 at any time except 3:00 PM for Pediatrics",
        },
        {
            "prompt": "Cancel an appointment with a doctor named Emma in any speciality except Oncology scheduled before October 5th, 2025 at 4:15 PM",
            "prompt_for_task_generation": "Cancel an appointment with a doctor named Emma in any speciality except Oncology scheduled before October 5th, 2025 at 4:15 PM",
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
            "prompt": "Show me prescriptions with status 'completed'",
            "prompt_for_task_generation": "Show me prescriptions with status 'completed'",
        },
        {
            "prompt": "Filter prescriptions to show only 'active' ones",
            "prompt_for_task_generation": "Filter prescriptions to show only 'active' ones",
        },
        {
            "prompt": "Show prescriptions with status 'discontinued'",
            "prompt_for_task_generation": "Show prescriptions with status 'discontinued'",
        },
        {
            "prompt": "Show all prescriptions",
            "prompt_for_task_generation": "Show all prescriptions",
        },
        {
            "prompt": "Filter to show prescriptions that need a refill",
            "prompt_for_task_generation": "Filter to show prescriptions that need a refill",
        },
        {
            "prompt": "Show prescriptions that are not completed",
            "prompt_for_task_generation": "Show prescriptions that are not completed",
        },
    ],
)

REFILL_PRESCRIPTION_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.
2. MANDATORY: You MUST include ALL constraint values explicitly in the prompt. Every constraint value specified in the constraints MUST appear in the generated prompt text.
3. Wrap specific constraint values in single quotes when they are strings (e.g., 'Atorvastatin', 'Metformin').
4. Use natural phrasing for operators:
   - "equals" → "for" (e.g., "Request a refill for 'Atorvastatin'")
   - "not_equals" → "except" or "other than" (e.g., "Refill any prescription except 'Amoxicillin'")
   - "contains" → "with ... in the name" (e.g., "Refill a prescription with Vitamin in the name")

Correct examples:
- Request a refill for 'Atorvastatin'.
- I need to refill my 'Metformin' prescription.
- Refill any prescription except 'Amoxicillin'.
- Refill a prescription with Vitamin in the name.

Incorrect examples:
- Request a refill where medicine_name equals 'Atorvastatin'. (uses "equals" - too technical)
- Refill prescription. (missing constraint value)
""".strip()

REFILL_PRESCRIPTION_USE_CASE = UseCase(
    name="REFILL_PRESCRIPTION",
    description="The user requested a prescription refill for a specific medicine.",
    event=RefillRequestEvent,
    event_source_code=RefillRequestEvent.get_source_code_of_class(),
    additional_prompt_info=REFILL_PRESCRIPTION_ADDITIONAL_INFO,
    constraints_generator=generate_refill_prescription_constraints,
    examples=[
        {
            "prompt": "Request a refill for 'Atorvastatin'",
            "prompt_for_task_generation": "Request a refill for 'Atorvastatin'",
        },
        {
            "prompt": "I need to refill my 'Metformin' prescription",
            "prompt_for_task_generation": "I need to refill my 'Metformin' prescription",
        },
        {
            "prompt": "Refill the 'Ibuprofen' prescription",
            "prompt_for_task_generation": "Refill the 'Ibuprofen' prescription",
        },
        {
            "prompt": "Refill any prescription except 'Amoxicillin'",
            "prompt_for_task_generation": "Refill any prescription except 'Amoxicillin'",
        },
        {
            "prompt": "Refill a prescription with Vitamin in the name",
            "prompt_for_task_generation": "Refill a prescription with Vitamin in the name",
        },
        {
            "prompt": "Request a refill for 'Lisinopril'",
            "prompt_for_task_generation": "Request a refill for 'Lisinopril'",
        },
    ],
)

VIEW_PRESCRIPTION_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.
2. MANDATORY: You MUST include ALL constraint values explicitly in the prompt. Every constraint value specified in the constraints MUST appear in the generated prompt text.
3. Wrap specific constraint values in single quotes when they are strings (e.g., 'Dr. Alice Thompson', 'Atorvastatin').
4. Use natural phrasing for operators:
   - "equals" → "is" or "from" (e.g., "from Dr. Alice Thompson" not "where doctor_name equals")
   - "not_equals" → "other than" or "not" (e.g., "status not active")
   - "contains" → "includes" or "that includes" (e.g., "dosage that includes 500 mg")
   - "greater_than" → "after" (for dates) or "above" (for numbers)
   - "less_than" → "before" (for dates) or "below" (for numbers)

Correct examples:
- Show me the prescription from Dr. Alice Thompson started on August 1st, 2025 for Atorvastatin with dosage 10 mg daily, status active, in the cholesterol category.
- View the prescription from Dr. Brian Patel started on September 5th, 2025 for Amoxicillin with dosage that includes 500 mg, status not active, in the antibiotic category.

Incorrect examples:
- View prescription where doctor_name equals 'Dr. Alice Thompson' and medicine_name equals 'Atorvastatin'. (uses "equals" - too technical)
- Show me a prescription. (missing constraint values)
""".strip()

VIEW_PRESCRIPTION_USE_CASE = UseCase(
    name="VIEW_PRESCRIPTION",
    description="The user viewed a prescription containing doctor information, medicine details, dosage, and start date.",
    event=ViewPrescriptionEvent,
    event_source_code=ViewPrescriptionEvent.get_source_code_of_class(),
    additional_prompt_info=VIEW_PRESCRIPTION_ADDITIONAL_INFO,
    constraints_generator=generate_view_prescription_constraints,
    examples=[
        {
            "prompt": "Show me the prescription from Dr. Alice Thompson started on August 1st, 2025 for Atorvastatin with dosage 10 mg daily, status active, in the cholesterol category",
            "prompt_for_task_generation": "Show me the prescription from Dr. Alice Thompson started on August 1st, 2025 for Atorvastatin with dosage 10 mg daily, status active, in the cholesterol category",
        },
        {
            "prompt": "View the prescription from Dr. Brian Patel started on September 5th, 2025 for Amoxicillin with dosage that includes 500 mg, status not active, in the antibiotic category",
            "prompt_for_task_generation": "View the prescription from Dr. Brian Patel started on September 5th, 2025 for Amoxicillin with dosage that includes 500 mg, status not active, in the antibiotic category",
        },
        {
            "prompt": "Show me a prescription from a doctor named Daniel started before August 1st, 2025 for Ibuprofen with dosage 200 mg as needed, status active, in the pain management category",
            "prompt_for_task_generation": "Show me a prescription from a doctor named Daniel started before August 1st, 2025 for Ibuprofen with dosage 200 mg as needed, status active, in the pain management category",
        },
    ],
)

UPLOAD_HEALTH_DATA_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "Upload ... health data file(s)..." or equivalent.
2. Specify the exact number of files to upload (file_count constraint).

Correct examples:
- Upload 3 health data files to your medical records.
- Upload 1 health data file.

Incorrect examples:
- Upload some files.
- View medical records.
""".strip()

UPLOAD_HEALTH_DATA_USE_CASE = UseCase(
    name="UPLOAD_HEALTH_DATA",
    description="The user uploaded one or more health data files to medical records.",
    event=UploadHealthDataEvent,
    event_source_code=UploadHealthDataEvent.get_source_code_of_class(),
    additional_prompt_info=UPLOAD_HEALTH_DATA_ADDITIONAL_INFO,
    constraints_generator=generate_upload_health_data_constraints,
    examples=[
        {"prompt": "Upload 2 health data files", "prompt_for_task_generation": "Upload 2 health data files"},
        {"prompt": "Upload 1 health data file to medical records", "prompt_for_task_generation": "Upload 1 health data file to medical records"},
        {"prompt": "Upload 4 health data files", "prompt_for_task_generation": "Upload 4 health data files"},
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
            "prompt": "Show me the health record Complete Blood Count (CBC) which is a lab result from January 15th, 2024",
            "prompt_for_task_generation": "Show me the health record Complete Blood Count (CBC) which is a lab result from January 15th, 2024",
        },
        {
            "prompt": "View health records with Ray in the title that are imaging records after February 1st, 2024",
            "prompt_for_task_generation": "View health records with Ray in the title that are imaging records after February 1st, 2024",
        },
        {
            "prompt": "Show me health records from February 5th, 2024 that are not titled Annual Flu Shot and are not vaccination records",
            "prompt_for_task_generation": "Show me health records from February 5th, 2024 that are not titled Annual Flu Shot and are not vaccination records",
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
            "prompt": "Filter medical records to show only 'diagnostic' category",
            "prompt_for_task_generation": "Filter medical records to show only 'diagnostic' category",
        },
        {
            "prompt": "Show me medical records in the 'preventive' category",
            "prompt_for_task_generation": "Show me medical records in the 'preventive' category",
        },
        {
            "prompt": "Filter to show 'monitoring' category records",
            "prompt_for_task_generation": "Filter to show 'monitoring' category records",
        },
        {
            "prompt": "Show medical records with category 'treatment'",
            "prompt_for_task_generation": "Show medical records with category 'treatment'",
        },
    ],
)

VIEW_DOCTOR_PROFILE_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.
2. MANDATORY: You MUST include ALL constraint values explicitly in the prompt. Every constraint value specified in the constraints MUST appear in the generated prompt text.
3. Wrap specific constraint values in single quotes when they are strings (e.g., 'Dr. Alice Thompson', 'Cardiology').
4. Use natural phrasing for operators:
   - "equals" → "is" or "for" (e.g., "Show me the profile for Dr. Alice Thompson")
   - "not_equals" → "but not" or "other than" (e.g., "but not Dr. Brian Patel")
   - "contains" → "named" (e.g., "a doctor named Clara")
   - "greater_than" → "above" (e.g., "with a rating above 4.5")
   - "less_than" → "below" (e.g., "with rating below 4.0")

Correct examples:
- Show me the profile for Dr. Alice Thompson in Cardiology with a rating above 4.5.
- View a doctor profile in Dermatology with rating below 4.0, but not Dr. Brian Patel.
- Show me the profile of a doctor named Clara in Pediatrics with rating 4.2.

Incorrect examples:
- View doctor profile where doctor_name equals 'Dr. Alice Thompson' and rating equals '4.5'. (uses "equals" - too technical)
- Show me a doctor profile. (missing constraint values)
""".strip()

VIEW_DOCTOR_PROFILE_USE_CASE = UseCase(
    name="VIEW_DOCTOR_PROFILE",
    description="The user viewed a doctor's profile, including name, rating, and speciality.",
    event=ViewDoctorProfileEvent,
    event_source_code=ViewDoctorProfileEvent.get_source_code_of_class(),
    additional_prompt_info=VIEW_DOCTOR_PROFILE_ADDITIONAL_INFO,
    constraints_generator=generate_view_doctor_profile_constraints,
    examples=[
        {
            "prompt": "Show me the profile for Dr. Alice Thompson in Cardiology with a rating above 4.5",
            "prompt_for_task_generation": "Show me the profile for Dr. Alice Thompson in Cardiology with a rating above 4.5",
        },
        {
            "prompt": "View a doctor profile in Dermatology with rating below 4.0, but not Dr. Brian Patel",
            "prompt_for_task_generation": "View a doctor profile in Dermatology with rating below 4.0, but not Dr. Brian Patel",
        },
        {
            "prompt": "Show me the profile of a doctor named Clara in Pediatrics with rating 4.2",
            "prompt_for_task_generation": "Show me the profile of a doctor named Clara in Pediatrics with rating 4.2",
        },
    ],
)
CONTACT_DOCTOR_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "Contact [DOCTOR_NAME] about [SUBJECT]...".
2. MANDATORY: You MUST include ALL constraint values explicitly in the prompt. Every constraint value specified in the constraints MUST appear in the generated prompt text.
3. When a constraint specifies a field (doctor_name, subject, patient_name, patient_email, patient_phone, urgency, preferred_contact_method, speciality, appointment_request), you MUST mention both the field name AND its exact value from the constraints.
4. Include patient information (name, email, phone) when specified in constraints - use the EXACT values from constraints.
5. Include message details (subject, urgency, preferred contact method) when specified - use the EXACT values from constraints.
6. Do not mention a single constraint more than once in the request.
7. Wrap specific constraint values in single quotes when they are strings (e.g., 'Dr. Alice Thompson', 'high', 'email').
8. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc. Use phrases like "with patient_name 'John Doe'" not "where patient_name equals 'John Doe'".

Correct examples (showing ALL constraint values explicitly, using natural language):
- Contact Dr. Alice Thompson about 'Prescription question'. Fill in your name, email, phone, message, urgency level, and preferred contact method.
- Contact Dr. Daniel Roberts about 'Follow-up question' with patient_name 'John Doe', patient_email 'john.doe@example.com', urgency 'high', and preferred_contact_method 'email'.
- Contact Dr. Michael Smith about 'Test results inquiry' with patient_name 'Emily Johnson', patient_email 'emily.johnson@example.com', patient_phone '+1-202-555-0142', urgency 'medium', and preferred_contact_method 'phone'.

Incorrect examples:
- Retrieve doctor 'Dr. Alice Thompson' (missing subject and other constraints).
- Contact doctor without subject (missing required constraint).
- Contact Dr. Daniel Roberts about prescription question (missing explicit constraint values for patient info, urgency, etc.).
""".strip()
CONTACT_DOCTOR_USE_CASE = UseCase(
    name="CONTACT_DOCTOR",
    description="The user contacted a doctor about a subject. Fill in all required patient information including name, email, phone, message, urgency level, and preferred contact method. Uses semantic values (doctor names, specialty names, patient names) for natural prompts.",
    event=ContactDoctorEvent,
    event_source_code=ContactDoctorEvent.get_source_code_of_class(),
    additional_prompt_info=CONTACT_DOCTOR_ADDITIONAL_INFO,
    constraints_generator=generate_contact_doctor_constraints,
    examples=[
        {
            "prompt": "Contact Dr. Alice Thompson about 'General inquiry'. Fill in your name, email, phone, message, urgency level, and preferred contact method.",
            "prompt_for_task_generation": "Contact Dr. Alice Thompson about 'General inquiry'. Fill in your name, email, phone, message, urgency level, and preferred contact method.",
        },
        {
            "prompt": "Contact Dr. Daniel Roberts about 'Follow-up question' with patient_name 'John Doe', patient_email 'john.doe@example.com', patient_phone '+1-202-555-0141', urgency 'high', and preferred_contact_method 'email'.",
            "prompt_for_task_generation": "Contact Dr. Daniel Roberts about 'Follow-up question' with patient_name 'John Doe', patient_email 'john.doe@example.com', patient_phone '+1-202-555-0141', urgency 'high', and preferred_contact_method 'email'.",
        },
        {
            "prompt": "Contact a doctor named Nguyen in Dermatology about 'Appointment request' for patient Emma Wilson with patient_email 'emily.johnson@example.com', urgency 'medium', and preferred_contact_method 'email'.",
            "prompt_for_task_generation": "Contact a doctor named Nguyen in Dermatology about 'Appointment request' for patient Emma Wilson with patient_email 'emily.johnson@example.com', urgency 'medium', and preferred_contact_method 'email'.",
        },
        {
            "prompt": "Contact Dr. Michael Smith about 'Test results inquiry' with patient_name 'Emily Johnson', patient_email 'emily.johnson@example.com', patient_phone '+1-202-555-0142', urgency 'low', and preferred_contact_method 'phone'.",
            "prompt_for_task_generation": "Contact Dr. Michael Smith about 'Test results inquiry' with patient_name 'Emily Johnson', patient_email 'emily.johnson@example.com', patient_phone '+1-202-555-0142', urgency 'low', and preferred_contact_method 'phone'.",
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
            "prompt": "Successfully contacted Dr. Alice Thompson for patient John Smith",
            "prompt_for_task_generation": "Successfully contacted Dr. Alice Thompson for patient John Smith",
        },
        {
            "prompt": "Doctor contacted successfully in Dermatology with high urgency",
            "prompt_for_task_generation": "Doctor contacted successfully in Dermatology with high urgency",
        },
        {
            "prompt": "Successfully contacted a doctor via email for patient with email maria.gonzalez@example.com",
            "prompt_for_task_generation": "Successfully contacted a doctor via email for patient with email maria.gonzalez@example.com",
        },
        {
            "prompt": "Doctor contacted successfully about knee pain with a message about difficulty walking",
            "prompt_for_task_generation": "Doctor contacted successfully about knee pain with a message about difficulty walking",
        },
        {
            "prompt": "Successfully contacted Dr. Brian Patel by phone",
            "prompt_for_task_generation": "Successfully contacted Dr. Brian Patel by phone",
        },
        {
            "prompt": "Doctor contacted successfully for patient with phone +1-555-678-1234 with low urgency",
            "prompt_for_task_generation": "Doctor contacted successfully for patient with phone +1-555-678-1234 with low urgency",
        },
    ],
)
CANCEL_CONTACT_DOCTOR_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "Cancel contact request...".
2. Do not mention a single constraint more than once in the request.
3. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.

Correct examples (using natural language):
- Cancel contact request for 'Dr. Alice Thompson' in 'Cardiology'.
- Cancel the contact request for 'Dr. Alice Thompson'.
- Cancel contact request for a Cardiologist.

Incorrect examples:
- Retrieve doctor 'Dr. Alice Thompson'.

4. Pay attention to the constraints:
Example:
constraints:
{
'doctor_name': {'operator': 'equals', 'value': 'Dr. Alice Thompson'},
'speciality': {'operator': 'equals', 'value': 'Cardiology'}
}
Correct (using natural language):
"Cancel contact request for 'Dr. Alice Thompson' in 'Cardiology'."
"Cancel the contact request for 'Dr. Alice Thompson'."
Incorrect (using technical terms):
"Cancel contact request where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'." (uses "equals" - too technical)
"Cancel doctor 'Dr. Alice Thompson'." (missing speciality constraint)
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
            "prompt": "Cancel the contact request for 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Cancel the contact request for 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Cancel contact request with 'Dr. John Smith'",
            "prompt_for_task_generation": "Cancel contact request with 'Dr. John Smith'",
        },
        {
            "prompt": "Cancel contact request for a Cardiologist",
            "prompt_for_task_generation": "Cancel contact request for a Cardiologist",
        },
        {
            "prompt": "Cancel the contact request for a Dermatologist",
            "prompt_for_task_generation": "Cancel the contact request for a Dermatologist",
        },
        {
            "prompt": "Cancel contact request for any doctor except 'Dr. Emily Davis'",
            "prompt_for_task_generation": "Cancel contact request for any doctor except 'Dr. Emily Davis'",
        },
        {
            "prompt": "Cancel contact request for a speciality containing 'Pediatric'",
            "prompt_for_task_generation": "Cancel contact request for a speciality containing 'Pediatric'",
        },
    ],
)
VIEW_REVIEWS_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "View reviews clicked..." or "Show me reviews for..." or "View reviews for...".
2. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.
3. MANDATORY: You MUST include ALL constraint values explicitly in the prompt. Every constraint value specified in the constraints MUST appear in the generated prompt text.
4. Do not mention a single constraint more than once in the request.
5. Wrap specific constraint values in single quotes when they are strings (e.g., 'Dr. Alice Thompson', '4.8').

OPERATOR TRANSLATION TO NATURAL LANGUAGE:
- "equals" → "is" or "is equal to" (use natural phrasing like "for 'Dr. Alice Thompson'" not "where doctor_name equals")
- "not_equals" → "is not" or "other than" or "except" (e.g., "but not 'Dr. Daniel Ruiz'")
- "contains" → "contains" or "includes" or "with ... in the name" (e.g., "whose name contains 'Thom'")
- "not_contains" → "does not contain" or "without" or "not containing"
- "greater_than" → "above" or "greater than" or "more than" (e.g., "with rating above '4.5'")
- "less_than" → "below" or "less than" or "under" (e.g., "with rating below '3.0'")
- "greater_equal" → "at least" or "or above"
- "less_equal" → "at most" or "or below"

Correct examples (using natural language):
- View reviews clicked for 'Dr. Alice Thompson' in 'Cardiology' with rating '4.8'.
- Show me reviews for a doctor in 'Cardiology' with rating above '4.5'.
- View reviews for doctors with rating below '3.0', but not for 'Dr. Brian Patel'.
- Show me reviews for a doctor whose name contains 'Thom' with rating that is not '3.7'.

Incorrect examples (using technical terms):
- View reviews clicked where doctor_name equals 'Dr. Alice Thompson' and rating equals '4.8'. (uses "equals" - too technical)
- View reviews clicked where doctor_name not_equals 'Dr. Daniel Ruiz' and rating equals '4.8'. (uses "not_equals" and "equals" - too technical)
- View review 'Dr. Alice Thompson'. (missing constraints)
""".strip()
VIEW_REVIEWS_USE_CASE = UseCase(
    name="VIEW_REVIEWS",
    description="The user viewed reviews for a doctor.",
    event=ViewReviewsEvent,
    event_source_code=ViewReviewsEvent.get_source_code_of_class(),
    additional_prompt_info=VIEW_REVIEWS_ADDITIONAL_INFO,
    constraints_generator=generate_view_reviews_constraints,
    examples=[
        {
            "prompt": "Show me reviews for 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Show me reviews for 'Dr. Alice Thompson'",
        },
        {
            "prompt": "View reviews for 'Dr. Michael Johnson'",
            "prompt_for_task_generation": "View reviews for 'Dr. Michael Johnson'",
        },
        {
            "prompt": "Show me reviews for Cardiologists",
            "prompt_for_task_generation": "Show me reviews for Cardiologists",
        },
        {
            "prompt": "View reviews for doctors in specialities with Dermatology in the name",
            "prompt_for_task_generation": "View reviews for doctors in specialities with Dermatology in the name",
        },
        {
            "prompt": "Show me reviews for doctors with rating above 4.5",
            "prompt_for_task_generation": "Show me reviews for doctors with rating above 4.5",
        },
        {
            "prompt": "View reviews for doctors with rating below 3.0",
            "prompt_for_task_generation": "View reviews for doctors with rating below 3.0",
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
            "prompt": "Filter reviews to show only 5-star ratings",
            "prompt_for_task_generation": "Filter reviews to show only 5-star ratings",
        },
        {
            "prompt": "Show me 3-star reviews for Dermatologists",
            "prompt_for_task_generation": "Show me 3-star reviews for Dermatologists",
        },
        {
            "prompt": "Filter reviews for 'Dr. Alice Thompson' to show ratings above 4",
            "prompt_for_task_generation": "Filter reviews for 'Dr. Alice Thompson' to show ratings above 4",
        },
        {
            "prompt": "Show reviews for Neurologists with rating below 3",
            "prompt_for_task_generation": "Show reviews for Neurologists with rating below 3",
        },
        {
            "prompt": "Filter reviews for 'Dr. John Smith' excluding 2-star ratings",
            "prompt_for_task_generation": "Filter reviews for 'Dr. John Smith' excluding 2-star ratings",
        },
        {
            "prompt": "Show me 1-star reviews for Cardiologists",
            "prompt_for_task_generation": "Show me 1-star reviews for Cardiologists",
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
            "prompt": "Sort reviews by highest rating",
            "prompt_for_task_generation": "Sort reviews by highest rating",
        },
        {
            "prompt": "Sort reviews for 'Dr. Alice Thompson' by lowest rating",
            "prompt_for_task_generation": "Sort reviews for 'Dr. Alice Thompson' by lowest rating",
        },
        {
            "prompt": "Sort reviews for Cardiologists by newest first",
            "prompt_for_task_generation": "Sort reviews for Cardiologists by newest first",
        },
        {
            "prompt": "Sort reviews for 'Dr. John Smith' by oldest first",
            "prompt_for_task_generation": "Sort reviews for 'Dr. John Smith' by oldest first",
        },
        {
            "prompt": "Sort reviews for Dermatologists by highest rating",
            "prompt_for_task_generation": "Sort reviews for Dermatologists by highest rating",
        },
        {
            "prompt": "Sort reviews to show newest first",
            "prompt_for_task_generation": "Sort reviews to show newest first",
        },
    ],
)
CANCEL_VIEW_REVIEW_ADDITIONAL_INFO = """
CRITICAL REQUIREMENTS:
1. The request must start with: "Cancel view reviews...".
2. Do not mention a single constraint more than once in the request.
3. MANDATORY: Use NATURAL LANGUAGE only - NEVER use technical terms like "equals", "not_equals", "contains", etc.

Correct examples (using natural language):
- Cancel viewing reviews for 'Dr. Alice Thompson' in 'Cardiology'.
- Cancel view reviews for 'Dr. Alice Thompson'.
- Cancel viewing reviews for Cardiologists.

Incorrect examples:
- Cancel view review 'Dr. Alice Thompson'.

4. Pay attention to the constraints:
Example:
constraints:
{
'doctor_name': {'operator': 'equals', 'value': 'Dr. Alice Thompson'},
'speciality': {'operator': 'equals', 'value': 'Cardiology'},
}
Correct (using natural language):
"Cancel viewing reviews for 'Dr. Alice Thompson' in 'Cardiology'."
"Cancel view reviews for 'Dr. Alice Thompson'."
Incorrect (using technical terms):
"Cancel view reviews clicked where doctor_name equals 'Dr. Alice Thompson' and speciality equals 'Cardiology'." (uses "equals" - too technical)
"View reviews 'Dr. Alice Thompson'." (missing speciality constraint)
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
            "prompt": "Cancel viewing reviews for 'Dr. Alice Thompson'",
            "prompt_for_task_generation": "Cancel viewing reviews for 'Dr. Alice Thompson'",
        },
        {
            "prompt": "Cancel view reviews for Cardiologists",
            "prompt_for_task_generation": "Cancel view reviews for Cardiologists",
        },
        {
            "prompt": "Cancel viewing reviews for 'Dr. John Smith' in Dermatology",
            "prompt_for_task_generation": "Cancel viewing reviews for 'Dr. John Smith' in Dermatology",
        },
        {
            "prompt": "Cancel view reviews for 'Dr. Emily Davis'",
            "prompt_for_task_generation": "Cancel view reviews for 'Dr. Emily Davis'",
        },
        {
            "prompt": "Cancel viewing reviews for Neurologists",
            "prompt_for_task_generation": "Cancel viewing reviews for Neurologists",
        },
        {
            "prompt": "Cancel viewing reviews",
            "prompt_for_task_generation": "Cancel viewing reviews",
        },
    ],
)
ALL_USE_CASES = [
    BOOK_APPOINTMENT_USE_CASE,
    CONTACT_DOCTOR_USE_CASE,
    VIEW_PRESCRIPTION_USE_CASE,
    # APPOINTMENT_BOOKED_SUCCESSFULLY_USE_CASE,
    CANCEL_BOOK_APPOINTMENT_USE_CASE,
    # FILTER_BY_SPECIALITY_USE_CASE,
    REFILL_PRESCRIPTION_USE_CASE,
    VIEW_HEALTH_METRICS_USE_CASE,
    UPLOAD_HEALTH_DATA_USE_CASE,
    # FILTER_BY_CATEGORY_USE_CASE,
    VIEW_DOCTOR_PROFILE_USE_CASE,
    # DOCTOR_CONTACTED_SUCCESSFULLY_USE_CASE,
    # CANCEL_CONTACT_DOCTOR_USE_CASE,
    VIEW_REVIEWS_USE_CASE,
    # FILTER_REVIEWS_USE_CASE,
    # SORT_REVIEWS_USE_CASE,
    # CANCEL_VIEW_REVIEWS_USE_CASE,
]
