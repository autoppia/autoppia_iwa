from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddSkillEvent,
    BookAConsultationEvent,
    CancelHireEvent,
    ClosePostAJobWindowEvent,
    HireButtonClickedEvent,
    HireConsultantEvent,
    PostAJobEvent,
    RemoveSkillEvent,
    SearchSkillEvent,
    SelectHiringTeamEvent,
    SubmitJobEvent,
    WriteJobTitleEvent,
)
from .generation_functions import (
    generate_add_skill_constraint,
    generate_book_consultant_constraint,
    generate_cancel_hire_constraint,
    generate_close_posting_job_constraint,
    generate_hire_button_clicked_constraint,
    generate_hire_consultation_constraint,
    generate_job_posting_constraint,
    generate_remove_skill_constraint,
    generate_search_skill_constraint,
    generate_select_hiring_team_constraint,
    generate_submit_job_constraint,
    generate_write_job_title_constraint,
)

BOOK_A_CONSULTATION_USE_CASE = UseCase(
    name="BOOK_A_CONSULTATION",
    description="The user initiate the booking process for a consultation",
    event=BookAConsultationEvent,
    event_source_code=BookAConsultationEvent.get_source_code_of_class(),
    constraints_generator=generate_book_consultant_constraint,
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

HIRE_BUTTON_CLICKED_USE_CASE = UseCase(
    name="HIRE_BTN_CLICKED",
    description="The user clicked hire button to start hiring a consultation workflow",
    event=HireButtonClickedEvent,
    event_source_code=HireButtonClickedEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
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

SELECT_HIRING_TEAM_USE_CASE = UseCase(
    name="SELECT_HIRING_TEAM",
    description="The user select the hiring team",
    event=SelectHiringTeamEvent,
    event_source_code=SelectHiringTeamEvent.get_source_code_of_class(),
    constraints_generator=generate_select_hiring_team_constraint,
    examples=[
        {
            "prompt": "Select the hiring team where expert name is 'Ashley C'",
            "prompt_for_task_generation": "Select the hiring team where expert name is 'Ashley C'",
        },
        {
            "prompt": "Select the hiring team where expert slug is 'ashley-c'",
            "prompt_for_task_generation": "Select the hiring team where expert slug is 'ashley-c'",
        },
    ],
)

HIRE_CONSULTATION_USE_CASE = UseCase(
    name="HIRE_CONSULTANT",
    description="The user confirm hiring of a chosen consultation",
    event=HireConsultantEvent,
    event_source_code=HireConsultantEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_consultation_constraint,
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

POST_A_JOB_USE_CASE = UseCase(
    name="POST_A_JOB",
    description="The user post a job",
    event=PostAJobEvent,
    event_source_code=PostAJobEvent.get_source_code_of_class(),
    constraints_generator=generate_job_posting_constraint,
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

REMOVE_SKILL_USE_CASE = UseCase(
    name="REMOVE_SKILL",
    description="The user removes the added skill",
    event=RemoveSkillEvent,
    event_source_code=RemoveSkillEvent.get_source_code_of_class(),
    constraints_generator=generate_remove_skill_constraint,
    examples=[
        {
            "prompt": "The user remove the skill that is successfully added for job requirement",
            "prompt_for_task_generation": "The user remove the skill that is successfully added for job requirement",
        },
        {
            "prompt": "Remove skill when the skill is 'C++'",
            "prompt_for_task_generation": "Remove skill when the skill is 'C++'",
        },
        {
            "prompt": "Remove skill that contains 'Python'",
            "prompt_for_task_generation": "Remove skill that contains 'Python'",
        },
    ],
)

# ATTACH_FILE_USE_CASE = UseCase(
#     name="ATTACH_FILE",
#     description="The user attaches a file",
#     event=AttachFileClickedEvent,
#     event_source_code=AttachFileClickedEvent.get_source_code_of_class(),
#     constraints_generator=None,
#     examples=[
#         {
#             "prompt": "The user clicks 'Attach file' button to attach file",
#             "prompt_for_task_generation": "The user clicks 'Attach file' button to attach file",
#         },
#         {
#             "prompt": "Attach a file whose name is 'generation_functions.py'",
#             "prompt_for_task_generation": "Attach a file whose name is 'generation_functions.py'",
#         },
#         {
#             "prompt": "Attach a file whose name is 'document.pdf'",
#             "prompt_for_task_generation": "Attach a file whose name is 'document.pdf'",
#         },
#         {
#             "prompt": "Attach a file when step is equal to 5",
#             "prompt_for_task_generation": "Attach a file when step is equal to 5",
#         },
#         {
#             "prompt": "Attach a file whose type is 'image/png'",
#             "prompt_for_task_generation": "Attach a file whose type is 'image/png'",
#         },
#         {
#             "prompt": "Attach a file whose type is 'application/pdf'",
#             "prompt_for_task_generation": "Attach a file whose type is 'application/pdf'",
#         },
#     ],
# )

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

CLOSE_JOB_POSTING_USE_CASE = UseCase(
    name="CLOSE_JOB_POST",
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

ALL_USE_CASES = [
    # BOOK_A_CONSULTATION_USE_CASE,
    # HIRE_BUTTON_CLICKED_USE_CASE,
    # SELECT_HIRING_TEAM_USE_CASE,
    # HIRE_CONSULTATION_USE_CASE,
    # CANCEL_HIRE_USE_CASE,
    # POST_A_JOB_USE_CASE,
    # WRITING_JOB_TITLE_USE_CASE,
    # SEARCH_SKILL_USE_CASE,
    ADD_SKILL_USE_CASE,
    REMOVE_SKILL_USE_CASE,
    SUBMIT_JOB_USE_CASE,
    CLOSE_JOB_POSTING_USE_CASE,
]
