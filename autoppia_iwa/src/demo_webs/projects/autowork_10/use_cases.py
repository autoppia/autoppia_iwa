from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddSkillEvent,
    BookAConsultationEvent,
    BrowseFavoriteExpertEvent,
    CancelHireEvent,
    ChooseBudgetTypeEvent,
    ChooseProjectSizeEvent,
    ChooseTimelineEvent,
    ClosePostAJobWindowEvent,
    ContactExpertMessageSentEvent,
    ContactExpertOpenedEvent,
    EditAboutEvent,
    EditProfileEmailEvent,
    EditProfileLocationEvent,
    EditProfileNameEvent,
    EditProfileTitleEvent,
    FavoriteExpertRemovedEvent,
    FavoriteExpertSelectedEvent,
    HireButtonClickedEvent,
    HireConsultantEvent,
    HireLaterEvent,
    NavbarExpertsClickEvent,
    NavbarFavoritesClickEvent,
    NavbarHireLaterClickEvent,
    NavbarHiresClickEvent,
    NavbarJobsClickEvent,
    NavbarProfileClickEvent,
    PostAJobEvent,
    QuickHireEvent,
    SearchSkillEvent,
    SelectHiringTeamEvent,
    SetRateRangeEvent,
    SubmitJobEvent,
    WriteJobDescriptionEvent,
    WriteJobTitleEvent,
)
from .generation_functions import (
    generate_add_skill_constraint,
    generate_book_consultant_constraint,
    generate_budget_type_constraint,
    generate_cancel_hire_constraint,
    generate_close_posting_job_constraint,
    generate_content_expert_message_sent_constraint,
    generate_edit_about_constraint,
    generate_edit_profile_email_constraint,
    generate_edit_profile_location_constraint,
    generate_edit_profile_name_constraint,
    generate_edit_profile_title_constraint,
    generate_hire_button_clicked_constraint,
    generate_hire_consultation_constraint,
    generate_job_posting_constraint,
    generate_project_size_constraint,
    generate_quick_hire_constraint,
    generate_rate_range_constraint,
    generate_search_skill_constraint,
    generate_select_hiring_team_constraint,
    generate_submit_job_constraint,
    generate_timeline_constraint,
    generate_write_job_description_constraint,
    generate_write_job_title_constraint,
)

BOOK_A_CONSULTATION_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a consultant in the book a consultation context (e.g., name, country, role, rating, consultation fee).

Use natural language only. Do NOT use schema-style field names such as "name", "country", "role", "rating", "consultation_fee" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., consultant name, country, role, rating, consultation fee).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Book...", "Schedule...", or "Reserve...".

Always end the question naturally with "so I can book the consultation."

For example, if the verify field is 'consultation fee', format the question naturally:
- "Can you tell me the consultation fee for the consultant 'Alice Johnson' from USA, who works as a 'Career Coach' and has a rating of 4.8, so I can book the consultation?"

Examples:
- "Can you tell me the country of the consultant 'John Smith', who works as a 'Financial Consultant', has a rating of 4.5, and charges $150 consultation fee per session, so I can book the consultation?"
- "Can you tell me the role of the consultant 'Emily Clark' from UK, who has a rating of 4.7 and charges $120 consultation fee per session, so I can book the consultation?"
- "Can you tell me the rating of the consultant 'Michael Lee' from Australia, who works as a 'Startup Mentor' and charges $200 consultation fee per session, so I can book the consultation?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

BOOK_A_CONSULTATION_USE_CASE = UseCase(
    name="BOOK_A_CONSULTATION",
    description="The user initiate the booking process for a consultation",
    event=BookAConsultationEvent,
    event_source_code=BookAConsultationEvent.get_source_code_of_class(),
    constraints_generator=generate_book_consultant_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=BOOK_A_CONSULTATION_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Book a consultation whose name is 'Alexa R'",
            "prompt_for_task_generation": "Book a consultation whose name is 'Alexa R'",
        },
        {
            "prompt": "Book a consultation whose country is not 'United States'",
            "prompt_for_task_generation": "Book a consultation whose country is not 'United States'",
        },
        {
            "prompt": "Book a consultation whose job is greater than 100",
            "prompt_for_task_generation": "Book a consultation whose job is greater than 100",
        },
        {
            "prompt": "Book a consultation whose rate is $40.00/hr",
            "prompt_for_task_generation": "Book a consultation whose rate is $40.00/hr",
        },
        {
            "prompt": "Book a consultation whose rating is greater than 4.5",
            "prompt_for_task_generation": "Book a consultation whose rating is 4.5",
        },
        {
            "prompt": "Book a consultation whose role is not a 'UI/UX Designer'",
            "prompt_for_task_generation": "Book a consultation whose role is not 'UI/UX Designer'",
        },
    ],
)

HIRE_BTN_CLICKED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a freelancer in the hire button clicked context (e.g., name, country, role, rating, jobs completed, total earning, total jobs, total hours).

Use natural language only. Do NOT use schema-style field names such as "name", "country", "role", "rating", "jobs_completed", "total_earning", "total_jobs", "total_hours" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., freelancer name, country, role, rating, number of jobs completed, total earning, total jobs, total hours).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Hire...", "Select...", or "Choose...".

Always end the question naturally with "so I can start hiring him/her."

For example, if the verify field is 'total earning', format the question naturally:
- "Can you tell me the total earning of the freelancer 'Bob Johnson' from USA, who works as a 'Full Stack Developer', has a rating of 4.9, has completed 120 jobs, has 150 total jobs, and has worked 2000 total hours, so I can start hiring him?"

Examples:
- "Can you tell me the country of the freelancer 'John Smith', who works as a 'Data Analyst', has a rating of 4.6, has completed 90 jobs, has total earnings of $60k+, has 110 total jobs, and has worked 1400 total hours, so I can start hiring him?"
- "Can you tell me the role of the freelancer 'Emily Clark', from UK, who has a rating of 4.8, has completed 150 jobs, has total earnings of $90k+, has 170 total jobs, and has worked 2500 total hours, so I can start hiring her?"
- "Can you tell me the number of jobs completed by the freelancer 'Michael Lee' from Australia, who works as a 'Mobile Developer', has a rating of 4.5, has total earnings of $40k+, has 70 total jobs, and has worked 1000 total hours, so I can start hiring him?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()


HIRE_BUTTON_CLICKED_USE_CASE = UseCase(
    name="HIRE_BTN_CLICKED",
    description="The user clicked hire button to start hiring a consultation workflow",
    event=HireButtonClickedEvent,
    event_source_code=HireButtonClickedEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=HIRE_BTN_CLICKED_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Hire a consultant whose name is 'Brandon M'",
            "prompt_for_task_generation": "Hire a consultant whose name is 'Brandon M'",
        },
        {
            "prompt": "Hire a consultant whose role is 'Blockchain Expert'",
            "prompt_for_task_generation": "Hire a consultant whose role is 'Blockchain Expert'",
        },
        {
            "prompt": "Hire a consultant whose country is 'Morocco'",
            "prompt_for_task_generation": "Hire a consultant whose country is 'Morocco'",
        },
    ],
)
ADDITIONAL_PROMPT_INFO = """
CRITICAL INSTRUCTIONS:
1. Ensure that constraints values are applied correctly in the prompt. Do not modify the constraints values.
"""
SELECT_HIRING_TEAM_USE_CASE = UseCase(
    name="SELECT_HIRING_TEAM",
    description="The user select the hiring team",
    event=SelectHiringTeamEvent,
    event_source_code=SelectHiringTeamEvent.get_source_code_of_class(),
    constraints_generator=generate_select_hiring_team_constraint,
    examples=[
        {
            "prompt": "Select the hiring team 'Apple' where expert name is 'Ashley C.'",
            "prompt_for_task_generation": "Select the hiring team 'Apple' where expert name is 'Ashley C.'",
        },
        {
            "prompt": "Select the hiring team 'Google' where expert slug is 'alex-r'",
            "prompt_for_task_generation": "Select the hiring team 'Google' where expert slug is 'alex-r'",
        },
        {
            "prompt": "Select the hiring team 'Google' where expert name is not 'John D.'",
            "prompt_for_task_generation": "Select the hiring team 'Google' where expert name is not 'John D.'",
        },
    ],
    additional_prompt_info=ADDITIONAL_PROMPT_INFO,
)

HIRE_LATER_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a freelancer in the hire later context (e.g., name, country, role, rating, jobs completed, total earning, total hours).

Use natural language only. Do NOT use schema-style field names such as "name", "country", "role", "rating", "jobs_completed", "total_earning", "total_hours" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., freelancer name, country, role, rating, number of jobs completed, total earning, total hours).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Hire...", "Save...", or "Select...".

Always end the question naturally with "so I can hire him/her later."

For example, if the verify field is 'total earning', format the question naturally:
- "Can you tell me the total earning of the freelancer 'Bob Johnson' from USA, who works as a 'Full Stack Developer', has a rating of 4.9, has completed 120 jobs, and has worked 2000 total hours, so I can hire him later?"

Examples:
- "Can you tell me the country of the freelancer 'John Smith', who works as a 'Data Analyst', has a rating of 4.6, has completed 90 jobs, has total earnings of $60k, and has worked 1400 total hours, so I can hire him later?"
- "Can you tell me the role of the freelancer 'Emily Clark', from UK, who has a rating of 4.8, has completed 150 jobs, has total earnings of $90k, and has worked 2500 total hours, so I can hire her later?"
- "Can you tell me the number of jobs completed by the freelancer 'Michael Lee' from Australia, who works as a 'Mobile Developer', has a rating of 4.5, has total earnings of $40k, and has worked 1000 total hours, so I can hire him later?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

HIRE_LATER_USE_CASE = UseCase(
    name="HIRE_LATER",
    description="The user opts to hire later instead of starting hiring now.",
    event=HireLaterEvent,
    event_source_code=HireLaterEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=HIRE_LATER_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Decide to hire later for expert Jane Doe.",
            "prompt_for_task_generation": "Decide to hire later for expert Jane Doe.",
        },
        {
            "prompt": "Decide to hire later for expert that name is not equals 'Sophia Davis'.",
            "prompt_for_task_generation": "Decide to hire later for expert that name is not equals 'Sophia Davis'.",
        },
        {
            "prompt": "Decide to hire later for expert that role is 'Mobile Developer'.",
            "prompt_for_task_generation": "Decide to hire later for expert that role is 'Mobile Developer'.",
        },
    ],
)

HIRE_LATER_REMOVED_USE_CASE = UseCase(
    name="HIRE_LATER_REMOVED",
    description="The user remove the expert who is in hire later page.",
    event=HireLaterEvent,
    event_source_code=HireLaterEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    examples=[
        {
            "prompt": "Decide to remove expert Jane Doe from hire later page.",
            "prompt_for_task_generation": "Decide to remove expert Jane Doe from hire later page.",
        },
        {
            "prompt": "Decide to remove expert that name is not equals 'Sophia Davis' from hire later page.",
            "prompt_for_task_generation": "Decide to remove expert that name is not equals 'Sophia Davis' from hire later page.",
        },
        {
            "prompt": "Decide to remove expert that role is 'Mobile Developer' from hire later page.",
            "prompt_for_task_generation": "Decide to remove expert that role is 'Mobile Developer' from hire later page.",
        },
    ],
)

HIRE_LATER_START_USE_CASE = UseCase(
    name="HIRE_LATER_START",
    description="The user start hiring the expert who is in hire later page.",
    event=HireLaterEvent,
    event_source_code=HireLaterEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    examples=[
        {
            "prompt": "Decide to start hiring of expert that is in hire later page.",
            "prompt_for_task_generation": "Decide to start hiring of expert that is in hire later page.",
        },
        {
            "prompt": "Decide to start hiring of expert that name is not equals 'Sophia Davis' and is in hire later page.",
            "prompt_for_task_generation": "Decide to start hiring of expert that name is not equals 'Sophia Davis' and is in hire later page.",
        },
        {
            "prompt": "Decide to start hiring of expert that role is 'Mobile Developer' and in the later hire page.",
            "prompt_for_task_generation": "Decide to start hiring of expert that role is 'Mobile Developer' and in the later hire page.",
        },
    ],
)

QUICK_HIRE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a freelancer in the quick hire context (e.g., name, country, role, rating, jobs completed, total earning, total hours).

Use natural language only. Do NOT use schema-style field names such as "name", "country", "role", "rating", "jobs_completed", "total_earning", "total_hours" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., freelancer name, country, role, rating, number of jobs completed, total earning, total hours).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Hire...", "Quick hire...", or "Select...".

Always end the question naturally with "so I can quickly hire him/her."

For example, if the verify field is 'total earning', format the question naturally:
- "Can you tell me the total earning of the freelancer 'Bob Johnson' from USA, who works as a 'Full Stack Developer', has a rating of 4.9, has completed 120 jobs, and has worked 2000 total hours, so I can quickly hire him?"

Examples:
- "Can you tell me the country of the freelancer 'John Smith', who works as a 'Data Analyst', has a rating of 4.6, has completed 90 jobs, has total earnings of $60k, and has worked 1400 total hours, so I can quickly hire him?"
- "Can you tell me the role of the freelancer 'Emily Clark', from UK, who has a rating of 4.8, has completed 150 jobs, has total earnings of $90k, and has worked 2500 total hours, so I can quickly hire her?"
- "Can you tell me the number of jobs completed by the freelancer 'Michael Lee' from Australia, who works as a 'Mobile Developer', has a rating of 4.5, has total earnings of $40k, and has worked 1000 total hours, so I can quickly hire him?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

QUICK_HIRE_USE_CASE = UseCase(
    name="QUICK_HIRE",
    description="The user triggers quick hire directly from expert information.",
    event=QuickHireEvent,
    event_source_code=QuickHireEvent.get_source_code_of_class(),
    constraints_generator=generate_quick_hire_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=QUICK_HIRE_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Quick hire the expert John Smith.",
            "prompt_for_task_generation": "Quick hire the expert John Smith.",
        },
        {
            "prompt": "Quick hire the expert that role is 'DevOps Engineer'.",
            "prompt_for_task_generation": "Quick hire the expert that role is 'DevOps Engineer'.",
        },
        {
            "prompt": "Quick hire the expert that country is 'Germany'.",
            "prompt_for_task_generation": "Quick hire the expert that country is 'Germany'.",
        },
    ],
)

HIRE_CONSULTANT_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a consultant in the hire consultant context (e.g., name, country, role, rating, jobs completed, total earning, total hours).

Use natural language only. Do NOT use schema-style field names such as "name", "country", "role", "rating", "jobs_completed", "total_earning", "total_hours" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., consultant name, country, role, rating, number of jobs completed, total earning, total hours).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Hire...", "Select...", or "Choose...".

Always end the question naturally with "so I can hire him/her."

For example, if the verify field is 'total earning', format the question naturally:
- "Can you tell me the total earning of the consultant 'Bob Johnson' from USA, who works as a 'Career Coach', has a rating of 4.9, has completed 120 jobs, and has worked 2000 total hours, so I can hire him?"

Examples:
- "Can you tell me the country of the consultant 'John Smith', who works as a 'Financial Consultant', has a rating of 4.6, has completed 90 jobs, has total earnings of $60k+, and has worked 1400 total hours, so I can hire him?"
- "Can you tell me the role of the consultant 'Emily Clark' from UK, who has a rating of 4.8, has completed 150 jobs, has total earnings of $90k+, and has worked 2500 total hours, so I can hire her?"
- "Can you tell me the number of jobs completed by the consultant 'Michael Lee' from Australia, who works as a 'Startup Mentor', has a rating of 4.5, has total earnings of $40k+, and has worked 1000 total hours, so I can hire him?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

HIRE_CONSULTATION_USE_CASE = UseCase(
    name="HIRE_CONSULTANT",
    description="The user confirm hiring of a chosen consultation",
    event=HireConsultantEvent,
    event_source_code=HireConsultantEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_consultation_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=HIRE_CONSULTANT_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "The user click 'Hire' button to confirm hiring of a chosen consultation",
            "prompt_for_task_generation": "The user click 'Hire' button to confirm hiring of a chosen consultation",
        },
        {
            "prompt": "Confirm hiring of a consultation whose country is 'Spain'",
            "prompt_for_task_generation": "Confirm hiring of a consultation whose country is 'Spain'",
        },
        {
            "prompt": "Confirm hiring of a consultation whose payment type is 'fixed'",
            "prompt_for_task_generation": "Confirm hiring of a consultation whose payment type is 'fixed'",
        },
        {
            "prompt": "Confirm hiring of a consultation whose name is not 'Alexa R'",
            "prompt_for_task_generation": "Confirm hiring of a consultation whose name is not 'Alexa R'",
        },
        {"prompt": "Confirm hiring of a consultation whose role is 'Full Stack Developer'", "prompt_for_task_generation": "Confirm hiring of a consultation whose role is 'Full Stack Developer'"},
    ],
)

CANCEL_HIRE_USE_CASE = UseCase(
    name="CANCEL_HIRE",
    description="The user cancel hiring of a chosen consultation",
    event=CancelHireEvent,
    event_source_code=CancelHireEvent.get_source_code_of_class(),
    constraints_generator=generate_cancel_hire_constraint,
    examples=[
        {
            "prompt": "The user click 'Cancel' button to cancel the hiring of chosen consultation",
            "prompt_for_task_generation": "The user click 'Cancel' button to cancel the hiring of chosen consultation",
        },
        {
            "prompt": "Cancel hiring of a consultation whose country is 'Spain'",
            "prompt_for_task_generation": "Cancel hiring of a consultation whose country is 'Spain'",
        },
        {
            "prompt": "Cancel hiring of a consultation whose slug is 'ashley-c'",
            "prompt_for_task_generation": "Cancel hiring of a consultation whose slug is 'ashley-c'",
        },
        {
            "prompt": "Cancel hiring of a consultation whose name is not 'Alexa R'",
            "prompt_for_task_generation": "Cancel hiring of a consultation whose name is not 'Alexa R'",
        },
        {"prompt": "Cancel hiring of a consultation whose role is 'Full Stack Developer'", "prompt_for_task_generation": "Cancel hiring of a consultation whose role is 'Full Stack Developer'"},
    ],
)

"""job related use cases"""


POST_A_JOB_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a job post in the post a job context (e.g., title, status, start date, logged time, logged time price).

Use natural language only. Do NOT use schema-style field names such as "title", "status", "start", "logged_time", "logged_time_price" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., job title, status, start date, logged time, logged time price).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Post...", "Create...", or "Add...".

Do NOT add any purpose-based suffix like "so I can...". The question should be direct and complete on its own.

For example, if the verify field is 'status', format the question naturally:
- "Can you tell me the status of the job titled 'Build a Website', which starts on March 10, has logged time of 20 hours, and a logged time price of $500?"
For example, if the verify field is 'jobs_completed', format the question naturally:
- "How many total jobs are completed for now?"
For example, if the verify field is 'jobs_in_progress', format the question naturally:
- "How many jobs are in progress for now?"

Examples:
- "Can you tell me the start date of the job titled 'Design a Logo', which has a status of 'Completed', has logged time of 10 hours, and a logged time price of $200?"
- "Can you tell me the logged time of the job titled 'Develop Mobile App', which has a status of 'Pending', starts on May 1, and has a logged time price of $800?"
- "Can you tell me the logged time price of the job titled 'SEO Optimization', which has a status of 'In Progress', starts on June 12, and has logged time of 25 hours?"
- "How many total jobs are completed for now?"
- "How many jobs are in progress for now?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only non-verify fields for identification.
- Always include all question fields with values in the question for precise identification.

The output must be a single question asking only for the verify field value.
""".strip()

POST_A_JOB_USE_CASE = UseCase(
    name="POST_A_JOB",
    description="The user post a job",
    event=PostAJobEvent,
    event_source_code=PostAJobEvent.get_source_code_of_class(),
    constraints_generator=generate_job_posting_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=POST_A_JOB_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "User clicks 'Post a job' button to initiate the posting process for a job",
            "prompt_for_task_generation": "User clicks 'Post a job' button to initiate the posting process for a job",
        },
        {
            "prompt": "Initiates the posting process for a job when the page is 'home'",
            "prompt_for_task_generation": "Initiates the posting process for a job when the page is 'home'",
        },
    ],
)

WRITING_JOB_TITLE_USE_CASE = UseCase(
    name="WRITE_JOB_TITLE",
    description="The user writes a title of job",
    event=WriteJobTitleEvent,
    event_source_code=WriteJobTitleEvent.get_source_code_of_class(),
    constraints_generator=generate_write_job_title_constraint,
    examples=[
        {
            "prompt": "User initiates a process of job posting by writing a strong title of the job",
            "prompt_for_task_generation": "User initiates a process of job posting by writing a strong title of the job",
        },
        {
            "prompt": "Writes a title of job like web developers job",
            "prompt_for_task_generation": "Writes a title of job like web developers job",
        },
    ],
)

SEARCH_SKILL_USE_CASE = UseCase(
    name="SEARCH_SKILL",
    description="The user search skill",
    event=SearchSkillEvent,
    event_source_code=SearchSkillEvent.get_source_code_of_class(),
    constraints_generator=generate_search_skill_constraint,
    examples=[
        {
            "prompt": "User searches skill that is required for a job",
            "prompt_for_task_generation": "User searches skill that is required for a job",
        },
        {
            "prompt": "Search a skill 'Go'",
            "prompt_for_task_generation": "Search a skill 'Go'",
        },
        {
            "prompt": "Search a skill 'Python'",
            "prompt_for_task_generation": "Search a skill 'Python'",
        },
        {
            "prompt": "Search a skill 'C#'",
            "prompt_for_task_generation": "Search a skill 'C#'",
        },
    ],
)

ADD_SKILL_USE_CASE = UseCase(
    name="ADD_SKILL",
    description="The user adds a skill",
    event=AddSkillEvent,
    event_source_code=AddSkillEvent.get_source_code_of_class(),
    constraints_generator=generate_add_skill_constraint,
    examples=[
        {
            "prompt": "Adds a skill where skill contains 'C'",
            "prompt_for_task_generation": "Adds a skill where skill contains 'C'",
        },
        {
            "prompt": "Adds a skill where skill is 'C++'",
            "prompt_for_task_generation": "Adds a skill where skill is 'C++'",
        },
        {
            "prompt": "Adds a skill where skill not contains '++'",
            "prompt_for_task_generation": "Adds a skill where skill not contains '++'",
        },
    ],
)


SUBMIT_JOB_USE_CASE = UseCase(
    name="SUBMIT_JOB",
    description="The user submits a job",
    event=SubmitJobEvent,
    event_source_code=SubmitJobEvent.get_source_code_of_class(),
    constraints_generator=generate_submit_job_constraint,
    examples=[
        {
            "prompt": "The user submits a job by clicking 'Submit Job Post' button",
            "prompt_for_task_generation": "The user submits a job by clicking 'Submit Job Post' button",
        },
        {
            "prompt": "Submits a job whose budget type is 'hourly'",
            "prompt_for_task_generation": "Submits a job whose budget type is 'hourly'",
        },
        {
            "prompt": "Submit a job whose budget type is 'fixed'",
            "prompt_for_task_generation": "Submit a job whose budget type is 'fixed'",
        },
        {
            "prompt": "Submit a job whose job duration is '3 to 6 months'",
            "prompt_for_task_generation": "Submit a job whose job duration is '3 to 6 months'",
        },
        {
            "prompt": "Submit a job whose scope is 'Large'",
            "prompt_for_task_generation": "Submit a job whose scope is 'Large'",
        },
        {
            "prompt": "Submit a job whose title is 'Web Developers Job'",
            "prompt_for_task_generation": "Submit a job whose title is 'Web Developers Job'",
        },
    ],
)

CHOOSE_BUDGET_TYPE_USE_CASE = UseCase(
    name="CHOOSE_BUDGET_TYPE",
    description="The user selects a budget type for the job.",
    event=ChooseBudgetTypeEvent,
    event_source_code=ChooseBudgetTypeEvent.get_source_code_of_class(),
    constraints_generator=generate_budget_type_constraint,
    examples=[
        {
            "prompt": "Choose hourly as the budget type.",
            "prompt_for_task_generation": "Choose hourly as the budget type.",
        },
        {
            "prompt": "Choose fixed as the budget type.",
            "prompt_for_task_generation": "Choose fixed as the budget type.",
        },
        {
            "prompt": "Choose a budget type that is not equals to 'fixed'",
            "prompt_for_task_generation": "Choose a budget type that is not equals to 'fixed'",
        },
        {
            "prompt": "Choose a budget type that is not equals to 'hourly'",
            "prompt_for_task_generation": "Choose a budget type that is not equals to 'hourly'",
        },
    ],
)

CHOOSE_PROJECT_SIZE_USE_CASE = UseCase(
    name="CHOOSE_PROJECT_SIZE",
    description="The user chooses the project size.",
    event=ChooseProjectSizeEvent,
    event_source_code=ChooseProjectSizeEvent.get_source_code_of_class(),
    constraints_generator=generate_project_size_constraint,
    examples=[
        {
            "prompt": "Select Large project size.",
            "prompt_for_task_generation": "Select Large project size.",
        },
        {
            "prompt": "Select Small project size.",
            "prompt_for_task_generation": "Select Small project size.",
        },
        {
            "prompt": "Select Medium project size.",
            "prompt_for_task_generation": "Select Medium project size.",
        },
    ],
)

CHOOSE_TIMELINE_USE_CASE = UseCase(
    name="CHOOSE_PROJECT_TIMELINE",
    description="The user chooses expected project timeline.",
    event=ChooseTimelineEvent,
    event_source_code=ChooseTimelineEvent.get_source_code_of_class(),
    constraints_generator=generate_timeline_constraint,
    examples=[
        {
            "prompt": "Choose '3 to 6 months' timeline.",
            "prompt_for_task_generation": "Choose '3 to 6 months' timeline.",
        },
        {
            "prompt": "Choose 'More than 6 months' timeline.",
            "prompt_for_task_generation": "Choose 'More than 6 months' timeline.",
        },
        {
            "prompt": "Choose timeline that is not equals 'More than 6 months'.",
            "prompt_for_task_generation": "Choose timeline that is not equals 'More than 6 months'.",
        },
    ],
)

SET_RATE_RANGE_USE_CASE = UseCase(
    name="SET_RATE_RANGE",
    description="The user sets the hourly rate range.",
    event=SetRateRangeEvent,
    event_source_code=SetRateRangeEvent.get_source_code_of_class(),
    constraints_generator=generate_rate_range_constraint,
    examples=[
        {
            "prompt": "Set hourly rate from 20 to 40.",
            "prompt_for_task_generation": "Set hourly rate from 20 to 40.",
        },
        {
            "prompt": "Set hourly rate where from is less than 15, and to is equals to 30.",
            "prompt_for_task_generation": "Set hourly rate where from is less than 15, and to is equals to 30.",
        },
        {
            "prompt": "Set hourly rate where from is greater than 20, and to is equals to 40.",
            "prompt_for_task_generation": "Set hourly rate where from is greater than 20, and to is equals to 40.",
        },
    ],
)

WRITE_JOB_DESCRIPTION_USE_CASE = UseCase(
    name="WRITE_JOB_DESCRIPTION",
    description="The user writes the job description.",
    event=WriteJobDescriptionEvent,
    event_source_code=WriteJobDescriptionEvent.get_source_code_of_class(),
    constraints_generator=generate_write_job_description_constraint,
    examples=[
        {
            "prompt": "Write a job description that contains 'Create intuitive user'.",
            "prompt_for_task_generation": "Write a job description that contains 'Create intuitive user'.",
        },
        {
            "prompt": "Write a job description that is not equals 'Develop mobile applications for iOS and Android with optimized performance.'.",
            "prompt_for_task_generation": "Write a job description that is not equals 'Develop mobile applications for iOS and Android with optimized performance.'.",
        },
        {
            "prompt": "Write a job description that is equals 'Automate CI/CD pipelines, monitor infrastructure, and ensure system scalability.'.",
            "prompt_for_task_generation": "Write a job description that is equals 'Automate CI/CD pipelines, monitor infrastructure, and ensure system scalability.'.",
        },
    ],
)

CLOSE_JOB_POSTING_USE_CASE = UseCase(
    name="CLOSE_POST_A_JOB_WINDOW",
    description="The user closes the posting of job window",
    event=ClosePostAJobWindowEvent,
    event_source_code=ClosePostAJobWindowEvent.get_source_code_of_class(),
    constraints_generator=generate_close_posting_job_constraint,
    examples=[
        {
            "prompt": "The user clicks 'x' button to close the job posting window",
            "prompt_for_task_generation": "The user clicks 'x' button to close the job posting window",
        },
        {
            "prompt": "Close the window of job whose budget type is 'hourly'",
            "prompt_for_task_generation": "Close the window of job whose budget type is 'hourly'",
        },
        {
            "prompt": "Close the window of job whose title is 'Flutter Developers Job'",
            "prompt_for_task_generation": "Close the window of job whose title is 'Flutter Developers Job'",
        },
        {
            "prompt": "Close the window of job whose scope is 'Medium'",
            "prompt_for_task_generation": "Close the window of job whose scope is 'Medium'",
        },
        {
            "prompt": "Close the window of job whose duration is 'more than 6 months'",
            "prompt_for_task_generation": "Close the window of job whose duration is 'more than 6 months'",
        },
    ],
)
NAVBAR_JOB_CLICK_USE_USE = UseCase(
    name="NAVBAR_JOBS_CLICK",
    description="The user click a jobs from navbar option.",
    event=NavbarJobsClickEvent,
    event_source_code=NavbarJobsClickEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "User clicks jobs to view all jobs.",
            "prompt_for_task_generation": "User clicks jobs to view all jobs.",
        },
        {
            "prompt": "Open the job section.",
            "prompt_for_task_generation": "Open the job section.",
        },
    ],
)
NAVBAR_HIRES_CLICK_USE_USE = UseCase(
    name="NAVBAR_HIRES_CLICK",
    description="The user click a hires from navbar option.",
    event=NavbarHiresClickEvent,
    event_source_code=NavbarHiresClickEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "User clicks hires to view all hires.",
            "prompt_for_task_generation": "User clicks hires to view all hires.",
        },
        {
            "prompt": "Open the hire section.",
            "prompt_for_task_generation": "Open the hire section.",
        },
    ],
)
NAVBAR_EXPERTS_CLICK_USE_USE = UseCase(
    name="NAVBAR_EXPERTS_CLICK",
    description="The user click an experts from navbar option.",
    event=NavbarExpertsClickEvent,
    event_source_code=NavbarExpertsClickEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "User clicks experts to view all experts.",
            "prompt_for_task_generation": "User clicks experts to view all experts.",
        },
        {
            "prompt": "Open the experts section.",
            "prompt_for_task_generation": "Open the expertsd section.",
        },
    ],
)
NAVBAR_FAVORITE_CLICK_USE_USE = UseCase(
    name="NAVBAR_FAVORITES_CLICK",
    description="The user click favorite from navbar option.",
    event=NavbarFavoritesClickEvent,
    event_source_code=NavbarFavoritesClickEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "User clicks favorites to view all favorite experts.",
            "prompt_for_task_generation": "User clicks favorites to view all favorite experts.",
        },
        {
            "prompt": "Open the favorite section.",
            "prompt_for_task_generation": "Open the favorite section.",
        },
    ],
)
NAVBAR_HIRE_LATER_CLICK_USE_USE = UseCase(
    name="NAVBAR_HIRE_LATER_CLICK",
    description="The user click a hire later from navbar option.",
    event=NavbarHireLaterClickEvent,
    event_source_code=NavbarHireLaterClickEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "User clicks hire later to view hire later experts.",
            "prompt_for_task_generation": "User clicks hire later to view hire later experts.",
        },
        {
            "prompt": "Open the hire later section.",
            "prompt_for_task_generation": "Open the hire later section.",
        },
    ],
)

NAVBAR_PROFILE_CLICK_USE_USE = UseCase(
    name="NAVBAR_PROFILE_CLICK",
    description="The user click a profile from navbar option.",
    event=NavbarProfileClickEvent,
    event_source_code=NavbarProfileClickEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "User clicks profile to view user profile.",
            "prompt_for_task_generation": "User clicks profile to view user profile.",
        },
        {
            "prompt": "Open the profile section.",
            "prompt_for_task_generation": "Open the profile section.",
        },
    ],
)

CONTACT_EXPERT_OPENED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of an expert in the contact expert context (e.g., name, country, role, rating, jobs completed, total earning, total hours).

Use natural language only. Do NOT use schema-style field names such as "name", "country", "role", "rating", "jobs_completed", "total_earning", "total_hours" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., expert name, country, role, rating, number of jobs completed, total earning, total hours).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Contact...", "Message...", or "Reach out...".

Always end the question naturally with "so I can contact him/her."

For example, if the verify field is 'total earning', format the question naturally:
- "Can you tell me the total earning of the expert 'Bob Johnson' from USA, who works as a 'Career Coach', has a rating of 4.9, has completed 120 jobs, and has worked 2000 total hours, so I can contact him?"

Examples:
- "Can you tell me the country of the expert 'John Smith', who works as a 'Financial Consultant', has a rating of 4.6, has completed 90 jobs, has total earnings of $60k, and has worked 1400 total hours, so I can contact him?"
- "Can you tell me the role of the expert 'Emily Clark' from UK, who has a rating of 4.8, has completed 150 jobs, has total earnings of $90k, and has worked 2500 total hours, so I can contact her?"
- "Can you tell me the number of jobs completed by the expert 'Michael Lee' from Australia, who works as a 'Startup Mentor', has a rating of 4.5, has total earnings of $40k, and has worked 1000 total hours, so I can contact him?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

CONTACT_EXPERT_OPENED_USE_CASE = UseCase(
    name="CONTACT_EXPERT_OPENED",
    description="The user click a contact for contacting with expert.",
    event=ContactExpertOpenedEvent,
    event_source_code=ContactExpertOpenedEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=CONTACT_EXPERT_OPENED_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Contact an expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
            "prompt_for_task_generation": "Contact an expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
        },
        {
            "prompt": "Contact an expert where name not equals 'Chris Martinez' and role contains 'Austra'.",
            "prompt_for_task_generation": "Contact an expert where name not equals 'Chris Martinez' and role contains 'Austra'.",
        },
    ],
)

CONTACT_EXPERT_MESSAGE_SENT_USE_CASE = UseCase(
    name="CONTACT_EXPERT_MESSAGE_SENT",
    description="The user sends a message to an expert after opening the contact expert flow.",
    event=ContactExpertMessageSentEvent,
    event_source_code=ContactExpertMessageSentEvent.get_source_code_of_class(),
    constraints_generator=generate_content_expert_message_sent_constraint,
    examples=[
        {
            "prompt": "Send a message to an expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
            "prompt_for_task_generation": "Send a message to an expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
        },
        {
            "prompt": "Send a message to an expert where name not equals 'Chris Martinez' and role contains 'Australia'.",
            "prompt_for_task_generation": "Send a message to an expert where name not equals 'Chris Martinez' and role contains 'Australia'.",
        },
        {
            "prompt": "Send a message to an expert where name equals 'Daniel Kim' and role equals 'Product Designer'.",
            "prompt_for_task_generation": "Send a message to an expert where name equals 'Daniel Kim' and role equals 'Product Designer'.",
        },
    ],
)

EDIT_PROFILE_NAME_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the profile name in the edit profile name context.

Use natural language only. Do NOT include any other fields, since no question fields are provided.

Do NOT start the question with imperative phrasing like "Edit..." or "Change...".

Always end the question naturally with "so I can edit it."

Format the question naturally to ask for the profile name.
- "Can you tell me my profile name, so I can edit it?"

Examples:
- "Can you tell me my profile name, so I can edit it?"
- "Can you tell me my name, so I can edit it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Do not add any other fields or values, since there are none.

The output must be a single question asking only for the verify field value.
""".strip()

EDIT_PROFILE_NAME_USE_CASE = UseCase(
    name="EDIT_PROFILE_NAME",
    description="The user edits and updates their profile name.",
    event=EditProfileNameEvent,
    event_source_code=EditProfileNameEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_profile_name_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=EDIT_PROFILE_NAME_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Edit profile name where name equals 'Emily Patel'.",
            "prompt_for_task_generation": "Edit profile name where name equals 'Emily Patel'.",
        },
        {
            "prompt": "Edit profile name where name not equals 'John Doe'.",
            "prompt_for_task_generation": "Edit profile name where name not equals 'John Doe'.",
        },
        {
            "prompt": "Edit profile name where name contains 'Alex'.",
            "prompt_for_task_generation": "Edit profile name where name contains 'Alex'.",
        },
    ],
)

EDIT_PROFILE_TITLE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the profile title in the edit profile title context.

Use natural language only. Do NOT include any other fields, since no question fields are provided.

Do NOT start the question with imperative phrasing like "Edit..." or "Change...".

Always end the question naturally with "so I can edit it."

Format the question naturally to ask for the profile title.
- "Can you tell me my profile title, so I can edit it?"

Examples:
- "Can you tell me my profile title, so I can edit it?"
- "Can you tell me my title, so I can edit it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Do not add any other fields or values, since there are none.

The output must be a single question asking only for the verify field value.
""".strip()

EDIT_PROFILE_TITLE_USE_CASE = UseCase(
    name="EDIT_PROFILE_TITLE",
    description="The user edits and updates their profile title.",
    event=EditProfileTitleEvent,
    event_source_code=EditProfileTitleEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_profile_title_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=EDIT_PROFILE_TITLE_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Edit profile title where title equals 'Senior Software Engineer'.",
            "prompt_for_task_generation": "Edit profile title where title equals 'Senior Software Engineer'.",
        },
        {
            "prompt": "Edit profile title where title not equals 'Junior Developer'.",
            "prompt_for_task_generation": "Edit profile title where title not equals 'Junior Developer'.",
        },
        {
            "prompt": "Edit profile title where title contains 'Engineer'.",
            "prompt_for_task_generation": "Edit profile title where title contains 'Engineer'.",
        },
    ],
)

EDIT_PROFILE_LOCATION_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the profile location in the edit profile location context.

Use natural language only. Do NOT include any other fields, since no question fields are provided.

Do NOT start the question with imperative phrasing like "Edit..." or "Change...".

Always end the question naturally with "so I can edit it."

Format the question naturally to ask for the profile location.
- "Can you tell me my profile location, so I can edit it?"

Examples:
- "Can you tell me my profile location, so I can edit it?"
- "Can you tell me my location, so I can edit it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Do not add any other fields or values, since there are none.

The output must be a single question asking only for the verify field value.
""".strip()


EDIT_PROFILE_LOCATION_USE_CASE = UseCase(
    name="EDIT_PROFILE_LOCATION",
    description="The user edits and updates their profile location.",
    event=EditProfileLocationEvent,
    event_source_code=EditProfileLocationEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_profile_location_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=EDIT_PROFILE_LOCATION_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Edit profile location where location equals 'New York, USA'.",
            "prompt_for_task_generation": "Edit profile location where location equals 'New York, USA'.",
        },
        {
            "prompt": "Edit profile location where location not equals 'London, UK'.",
            "prompt_for_task_generation": "Edit profile location where location not equals 'London, UK'.",
        },
        {
            "prompt": "Edit profile location where location contains 'California'.",
            "prompt_for_task_generation": "Edit profile location where location contains 'California'.",
        },
    ],
)

EDIT_PROFILE_ABOUT_USE_CASE = UseCase(
    name="EDIT_ABOUT",
    description="The user edits and updates their profile 'About' or description section.",
    event=EditAboutEvent,
    event_source_code=EditAboutEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_about_constraint,
    examples=[
        {
            "prompt": "Edit profile about where description equals 'Passionate AI developer with 5 years experience'.",
            "prompt_for_task_generation": "Edit profile about where description equals 'Passionate AI developer with 5 years experience'.",
        },
        {
            "prompt": "Edit profile about where description not equals 'Junior UX designer'.",
            "prompt_for_task_generation": "Edit profile about where description not equals 'Junior UX designer'.",
        },
        {
            "prompt": "Edit profile about where description contains 'machine learning'.",
            "prompt_for_task_generation": "Edit profile about where description contains 'machine learning'.",
        },
    ],
)

EDIT_PROFILE_EMAIL_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the profile email in the edit profile email context.

Use natural language only. Do NOT include any other fields, since no question fields are provided.

Do NOT start the question with imperative phrasing like "Edit..." or "Change...".

Always end the question naturally with "so I can edit it."

Format the question naturally to ask for the profile email.
- "Can you tell me my profile email, so I can edit it?"

Examples:
- "Can you tell me my profile email, so I can edit it?"
- "Can you tell me my email, so I can edit it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Do not add any other fields or values, since there are none.

The output must be a single question asking only for the verify field value.
""".strip()

EDIT_PROFILE_EMAIL_USE_CASE = UseCase(
    name="EDIT_PROFILE_EMAIL",
    description="The user edits and updates their profile email address.",
    event=EditProfileEmailEvent,
    event_source_code=EditProfileEmailEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_profile_email_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=EDIT_PROFILE_EMAIL_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Edit profile email where email equals 'emily.patel@example.com'.",
            "prompt_for_task_generation": "Edit profile email where email equals 'emily.patel@example.com'.",
        },
        {
            "prompt": "Edit profile email where email not equals 'john.doe@example.com'.",
            "prompt_for_task_generation": "Edit profile email where email not equals 'john.doe@example.com'.",
        },
        {
            "prompt": "Edit profile email where email contains 'gmail.com'.",
            "prompt_for_task_generation": "Edit profile email where email contains 'gmail.com'.",
        },
    ],
)

BROWSE_FAVORITE_USE_CASE = UseCase(
    name="BROWSE_FAVORITE_EXPERT",
    description="The user edits and updates their profile email address.",
    event=BrowseFavoriteExpertEvent,
    event_source_code=BrowseFavoriteExpertEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {
            "prompt": "Browse to select the favorite expert.",
            "prompt_for_task_generation": "Browse to select the favorite expert.",
        },
        {
            "prompt": "Go to select the favorite expert.",
            "prompt_for_task_generation": "Go to select the favorite expert.",
        },
    ],
)

FAVORITE_EXPERT_SELECTED_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of an expert in the favorite expert context (e.g., name, country, role, rating, jobs completed, total earning, total hours).

Use natural language only. Do NOT use schema-style field names such as "name", "country", "role", "rating", "jobs_completed", "total_earning", "total_hours" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., expert name, country, role, rating, number of jobs completed, total earning, total hours).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Favorite...", "Select...", or "Choose...".

Always end the question naturally with "so I can mark him/her as favorite."

For example, if the verify field is 'total earning', format the question naturally:
- "Can you tell me the total earning of the expert 'Bob Johnson' from USA, who works as a 'Career Coach', has a rating of 4.9, has completed 120 jobs, and has worked 2000 total hours, so I can mark him as favorite?"

Examples:
- "Can you tell me the country of the expert 'John Smith', who works as a 'Financial Consultant', has a rating of 4.6, has completed 90 jobs, has total earnings of $60k, and has worked 1400 total hours, so I can mark him as favorite?"
- "Can you tell me the role of the expert 'Emily Clark' from UK, who has a rating of 4.8, has completed 150 jobs, has total earnings of $90k, and has worked 2500 total hours, so I can mark her as favorite?"
- "Can you tell me the number of jobs completed by the expert 'Michael Lee' from Australia, who works as a 'Startup Mentor', has a rating of 4.5, has total earnings of $40k, and has worked 1000 total hours, so I can mark him as favorite?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
""".strip()

FAVORITE_EXPERT_SELECTED_USE_CASE = UseCase(
    name="FAVORITE_EXPERT_SELECTED",
    description="The user selects an expert to mark them as favorite.",
    event=FavoriteExpertSelectedEvent,
    event_source_code=FavoriteExpertSelectedEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    supports_data_extraction=True,
    additional_prompt_info_for_data_extraction_task=FAVORITE_EXPERT_SELECTED_DATA_EXTRACTION_PROMPT_INFO,
    examples=[
        {
            "prompt": "Select favorite expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
            "prompt_for_task_generation": "Select favorite expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
        },
        {
            "prompt": "Select favorite expert where name not equals 'Chris Martinez' and role contains 'Australia'.",
            "prompt_for_task_generation": "Select favorite expert where name not equals 'Chris Martinez' and role contains 'Australia'.",
        },
        {
            "prompt": "Select favorite expert where name equals 'Daniel Kim' and role equals 'Product Designer'.",
            "prompt_for_task_generation": "Select favorite expert where name equals 'Daniel Kim' and role equals 'Product Designer'.",
        },
    ],
)

FAVORITE_EXPERT_REMOVED_USE_CASE = UseCase(
    name="FAVORITE_EXPERT_REMOVED",
    description="The user removes an expert from their favorites.",
    event=FavoriteExpertRemovedEvent,
    event_source_code=FavoriteExpertRemovedEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    examples=[
        {
            "prompt": "Remove favorite expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
            "prompt_for_task_generation": "Remove favorite expert where name equals 'Nicole Thompson' and role equals 'UX Researcher'.",
        },
        {
            "prompt": "Remove favorite expert where name not equals 'Chris Martinez' and role contains 'Australia'.",
            "prompt_for_task_generation": "Remove favorite expert where name not equals 'Chris Martinez' and role contains 'Australia'.",
        },
        {
            "prompt": "Remove favorite expert where name equals 'Daniel Kim' and role equals 'Product Designer'.",
            "prompt_for_task_generation": "Remove favorite expert where name equals 'Daniel Kim' and role equals 'Product Designer'.",
        },
    ],
)


#
# NAVBAR_PROFILE_CLICK_USE_USE = UseCase(
#     name="NAVBAR_EXPERTS_CLICK",
#     description="The user click a  from navbar option.",
#     event=NavbarProfileClickEvent,
#     event_source_code=PostAJobEvent.get_source_code_of_class(),
#     constraints_generator=False,
#     examples=[
#         {
#             "prompt": "User clicks profile to view user profile.",
#             "prompt_for_task_generation": "User clicks profile to view user profile.",
#         },
#         {
#             "prompt": "Open the profile section.",
#             "prompt_for_task_generation": "Open the profile section.",
#         },
#     ],
# )

ALL_USE_CASES = [
    BOOK_A_CONSULTATION_USE_CASE,
    HIRE_BUTTON_CLICKED_USE_CASE,
    HIRE_LATER_USE_CASE,
    HIRE_LATER_REMOVED_USE_CASE,
    HIRE_LATER_START_USE_CASE,
    QUICK_HIRE_USE_CASE,
    SELECT_HIRING_TEAM_USE_CASE,
    HIRE_CONSULTATION_USE_CASE,
    CANCEL_HIRE_USE_CASE,
    POST_A_JOB_USE_CASE,
    WRITING_JOB_TITLE_USE_CASE,
    SEARCH_SKILL_USE_CASE,
    ADD_SKILL_USE_CASE,
    CHOOSE_BUDGET_TYPE_USE_CASE,
    CHOOSE_PROJECT_SIZE_USE_CASE,
    CHOOSE_TIMELINE_USE_CASE,
    SET_RATE_RANGE_USE_CASE,
    WRITE_JOB_DESCRIPTION_USE_CASE,
    SUBMIT_JOB_USE_CASE,
    CLOSE_JOB_POSTING_USE_CASE,
    NAVBAR_PROFILE_CLICK_USE_USE,
    NAVBAR_JOB_CLICK_USE_USE,
    NAVBAR_EXPERTS_CLICK_USE_USE,
    NAVBAR_FAVORITE_CLICK_USE_USE,
    NAVBAR_HIRE_LATER_CLICK_USE_USE,
    NAVBAR_PROFILE_CLICK_USE_USE,
    NAVBAR_HIRES_CLICK_USE_USE,
    CONTACT_EXPERT_OPENED_USE_CASE,
    CONTACT_EXPERT_MESSAGE_SENT_USE_CASE,
    EDIT_PROFILE_NAME_USE_CASE,
    EDIT_PROFILE_ABOUT_USE_CASE,
    EDIT_PROFILE_EMAIL_USE_CASE,
    EDIT_PROFILE_TITLE_USE_CASE,
    EDIT_PROFILE_LOCATION_USE_CASE,
    BROWSE_FAVORITE_USE_CASE,
    FAVORITE_EXPERT_SELECTED_USE_CASE,
    FAVORITE_EXPERT_REMOVED_USE_CASE,
]
