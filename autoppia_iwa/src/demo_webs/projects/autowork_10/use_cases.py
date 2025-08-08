from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddSkillEvent,
    AttachFileClickedEvent,
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
    generate_book_consultant_constraint,
    generate_hire_button_clicked_constraint,
    generate_hire_consultation_constraint,
    generate_select_hiring_team_constraint,
)

BOOK_A_CONSULTATION_USE_CASE = UseCase(
    name="BOOK_A_CONSULTATION",
    description="The user initiate the booking process for a consultation",
    event=BookAConsultationEvent,
    event_source_code=BookAConsultationEvent.get_source_code_of_class(),
    constraints_generator=generate_book_consultant_constraint,
    examples=[
        {
            "prompt": "Go to the jobs page and navigate to end of the page and click on 'Book a consultation' button to book a that particular consultation",
            "prompt_for_task_generation": "Go to the jobs page and navigate to end of the page and click on 'Book a consultation' button to book a that particular consultation",
        },
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
    name="HIRE_BUTTON_CLICKED",
    description="The user clicked hire button to start hiring a consultation workflow",
    event=HireButtonClickedEvent,
    event_source_code=HireButtonClickedEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_button_clicked_constraint,
    examples=[
        {
            "prompt": "The user clicks 'Hire' button to start hiring a consultation workflow",
            "prompt_for_task_generation": "The user clicks 'Hire' button to start hiring a consultation workflow",
        },
        {
            "prompt": "Start a hiring consultation workflow if consultation name is 'Brandon M'",
            "prompt_for_task_generation": "Start a hiring consultation workflow if consultation name is 'Brandon M'",
        },
        {
            "prompt": "Start a hiring consultation workflow if consultation role is 'Blockchain Expert'",
            "prompt_for_task_generation": "Start a hiring consultation workflow if consultation role is 'Blockchain Expert'",
        },
        {
            "prompt": "Start a hiring consultation workflow if consultation country is 'Morocco'",
            "prompt_for_task_generation": "Start a hiring consultation workflow if consultation country is 'Morocco'",
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
    name="HIRE_CONSULTATION",
    description="The user confirm hiring of a chosen consultation",
    event=HireConsultantEvent,
    event_source_code=HireConsultantEvent.get_source_code_of_class(),
    constraints_generator=generate_hire_consultation_constraint,
    examples=[{}],
)

CANCEL_HIRE_CONSULTATION_USE_CASE = UseCase(
    name="CANCEL_HIRE_CONSULTATION",
    description="The user cancel hiring of a chosen consultation",
    event=CancelHireEvent,
    event_source_code=CancelHireEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[{}],
)

"""job related use cases"""

POST_A_JOB_USE_CASE = UseCase(
    name="POST_A_JOB", description="The user post a job", event=PostAJobEvent, event_source_code=PostAJobEvent.get_source_code_of_class(), constraints_generator=None, examples=[]
)

WRITING_JOB_TITLE_USE_CASE = UseCase(
    name="WRITE_JOB_TITLE",
    description="The user write a title of job",
    event=WriteJobTitleEvent,
    event_source_code=WriteJobTitleEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[],
)

SEARCH_SKILL_USE_CASE = UseCase(
    name="SEARCH_SKILL", description="The user search skill", event=SearchSkillEvent, event_source_code=SearchSkillEvent.get_source_code_of_class(), constraints_generator=None, examples=[]
)

ADD_SKILL_USE_CASE = UseCase(
    name="ADD_SKILL", description="The user add skill", event=AddSkillEvent, event_source_code=AddSkillEvent.get_source_code_of_class(), constraints_generator=None, examples=[]
)

REMOVE_SKILL_USE_CASE = UseCase(
    name="REMOVE_SKILL", description="The user remove the added skill", event=RemoveSkillEvent, event_source_code=RemoveSkillEvent.get_source_code_of_class(), constraints_generator=None, examples=[]
)

ATTACH_FILE_USE_CASE = UseCase(
    name="ATTACH_FILE", description="The user attach file", event=AttachFileClickedEvent, event_source_code=AttachFileClickedEvent.get_source_code_of_class(), constraints_generator=None, examples=[]
)

SUBMIT_JOB_USE_CASE = UseCase(
    name="SUBMIT_JOB", description="The user submits a job", event=SubmitJobEvent, event_source_code=SubmitJobEvent.get_source_code_of_class(), constraints_generator=None, examples=[]
)

CLOSE_JOB_POSTING_USE_CASE = UseCase(
    name="CLOSE_JOB_POST",
    description="The user clos the posting of job",
    event=ClosePostAJobWindowEvent,
    event_source_code=ClosePostAJobWindowEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[],
)
