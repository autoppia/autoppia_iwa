from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import ApplyForJobEvent, CommentOnPostEvent, ConnectWithUserEvent, FollowPageEvent, LikePostEvent, PostStatusEvent, SearchJobsEvent, SearchUsersEvent, ViewJobEvent, ViewUserProfileEvent
from .generation_functions import (
    generate_apply_for_job_constraints,
    generate_comment_on_post_constraints,
    generate_connect_with_user_constraints,
    generate_follow_page_constraints,
    generate_like_post_constraints,
    generate_post_status_constraints,
    generate_search_jobs_constraints,
    generate_search_users_constraints,
    generate_view_job_constraints,
    generate_view_user_profile_constraints,
)

ADDITIONAL_PROMPT_INFO = """
IMPORTANT REQUIREMENTS:
1. Start prompt with View user profile or view the profile of user"""

VIEW_USER_PROFILE_USE_CASE = UseCase(
    name="VIEW_USER_PROFILE",
    description="The user views another user's profile.",
    event=ViewUserProfileEvent,
    event_source_code=ViewUserProfileEvent.get_source_code_of_class(),
    constraints_generator=generate_view_user_profile_constraints,
    examples=[
        {
            "prompt": "View the profile of user 'janedoe'.",
            "prompt_for_task_generation": "View the profile of user 'janedoe'.",
        },
        {
            "prompt": "Open Jane Doe's profile from a post header.",
            "prompt_for_task_generation": "Open Jane Doe's profile from a post header.",
        },
    ],
)

CONNECT_WITH_USER_USE_CASE = UseCase(
    name="CONNECT_WITH_USER",
    description="The user sends a connection request to another user.",
    event=ConnectWithUserEvent,
    event_source_code=ConnectWithUserEvent.get_source_code_of_class(),
    constraints_generator=generate_connect_with_user_constraints,
    examples=[
        {
            "prompt": "Connect with Jane Doe.",
            "prompt_for_task_generation": "Connect with Jane Doe.",
        },
    ],
)


POST_STATUS_USE_CASE = UseCase(
    name="POST_STATUS",
    description="The user posts a new status update.",
    event=PostStatusEvent,
    event_source_code=PostStatusEvent.get_source_code_of_class(),
    constraints_generator=generate_post_status_constraints,
    examples=[
        {
            "prompt": "Post a status saying 'hi' ",
            "prompt_for_task_generation": "Post a status saying 'hi'",
        },
    ],
)

LIKE_POST_USE_CASE = UseCase(
    name="LIKE_POST",
    description="The user likes a post",
    event=LikePostEvent,
    event_source_code=LikePostEvent.get_source_code_of_class(),
    constraints_generator=generate_like_post_constraints,
    examples=[
        {
            "prompt": "Like the post where the poster wrote 'I finally got my AWS certification!'",
            "prompt_for_task_generation": "Like the post where the poster wrote 'I finally got my AWS certification!'",
        },
        {
            "prompt": "Like the post that includes the phrase 'Launching my first startup today!'",
            "prompt_for_task_generation": "Like the post that includes the phrase 'Launching my first startup today!'",
        },
        {
            "prompt": "Like the post where the content is exactly 'Grateful for everyone who supported me on this journey.'",
            "prompt_for_task_generation": "Like the post where the content is exactly 'Grateful for everyone who supported me on this journey.'",
        },
        {
            "prompt": "Like the post which does not include the sentence 'Looking for job opportunities.'",
            "prompt_for_task_generation": "Like the post which does not include the sentence 'Looking for job opportunities.'",
        },
        {
            "prompt": "Like the post with content not equal to 'Just completed my first year at TechCorp!'",
            "prompt_for_task_generation": "Like the post with content not equal to 'Just completed my first year at TechCorp!'",
        },
        {"prompt": "Like the post that contains 'Excited to attend PyCon this year!'", "prompt_for_task_generation": "Like the post that contains 'Excited to attend PyCon this year!'"},
        {
            "prompt": "Like the post where the user said 'Pushed a major UI update to the product today.'",
            "prompt_for_task_generation": "Like the post where the user said 'Pushed a major UI update to the product today.'",
        },
        {
            "prompt": "Like the post which includes the line 'Remote work has been a game changer for me.'",
            "prompt_for_task_generation": "Like the post which includes the line 'Remote work has been a game changer for me.'",
        },
    ],
)

COMMENT_ON_POST_USE_CASE = UseCase(
    name="COMMENT_ON_POST",
    description="The user comments on a post.",
    event=CommentOnPostEvent,
    event_source_code=CommentOnPostEvent.get_source_code_of_class(),
    constraints_generator=generate_comment_on_post_constraints,
    examples=[
        {
            "prompt": "Comment 'Great work!' on the post with poster content 'Just released a new app version!'",
            "prompt_for_task_generation": "Comment 'Great work!' on the post with poster content 'Just released a new app version!'",
        },
        {
            "prompt": "Comment 'Congrats!' on the post where the poster said 'I just got promoted to Senior Developer.'",
            "prompt_for_task_generation": "Comment 'Congrats!' on the post where the poster said 'I just got promoted to Senior Developer.'",
        },
        {
            "prompt": "Comment 'Very insightful!' on the post with poster content 'Here's what I learned from switching to microservices.'",
            "prompt_for_task_generation": "Comment 'Very insightful!' on the post with poster content 'Here's what I learned from switching to microservices.'",
        },
        {
            "prompt": "Comment 'Thanks for sharing!' on the post that says '5 tips for improving frontend performance.'",
            "prompt_for_task_generation": "Comment 'Thanks for sharing!' on the post that says '5 tips for improving frontend performance.'",
        },
        {
            "prompt": "Comment 'Wishing you luck!' on the post with content 'Starting my new role at DevX this Monday!'",
            "prompt_for_task_generation": "Comment 'Wishing you luck!' on the post with content 'Starting my new role at DevX this Monday!'",
        },
        {
            "prompt": "Comment 'Love this!' on the post that includes the sentence 'Diversity makes us stronger.'",
            "prompt_for_task_generation": "Comment 'Love this!' on the post that includes the sentence 'Diversity makes us stronger.'",
        },
        {
            "prompt": "Comment 'Well done' on the post where the poster shared 'Finally completed my AWS certification!'",
            "prompt_for_task_generation": "Comment 'Well done' on the post where the poster shared 'Finally completed my AWS certification!'",
        },
        {
            "prompt": "Comment 'Following this for updates.' on the post with poster content 'Experimenting with fine-tuning LLMs on medical datasets.'",
            "prompt_for_task_generation": "Comment 'Following this for updates.' on the post with poster content 'Experimenting with fine-tuning LLMs on medical datasets.'",
        },
    ],
)


APPLY_FOR_JOB_USE_CASE = UseCase(
    name="APPLY_FOR_JOB",
    description="The user applies for a job.",
    event=ApplyForJobEvent,
    event_source_code=ApplyForJobEvent.get_source_code_of_class(),
    constraints_generator=generate_apply_for_job_constraints,
    examples=[
        {
            "prompt": "Apply for the Frontend Developer job at Tech Innovations (Remote).",
            "prompt_for_task_generation": "Apply for the Frontend Developer job at Tech Innovations (Remote).",
        },
        {
            "prompt": "Submit an application for the Product Designer position in New York, NY.",
            "prompt_for_task_generation": "Submit an application for the Product Designer position in New York, NY.",
        },
        {
            "prompt": "Apply to Creative Studio for the Product Designer role.",
            "prompt_for_task_generation": "Apply to Creative Studio for the Product Designer role.",
        },
        {
            "prompt": "Send my resume for the Marketing Specialist job at Startup Hub.",
            "prompt_for_task_generation": "Send my resume for the Marketing Specialist job at Startup Hub.",
        },
        {
            "prompt": "Apply for a job in San Francisco, CA.",
            "prompt_for_task_generation": "Apply for a job in San Francisco, CA.",
        },
        {
            "prompt": "Apply for the Backend Engineer position at DataStream Inc. in Boston, MA.",
            "prompt_for_task_generation": "Apply for the Backend Engineer position at DataStream Inc. in Boston, MA.",
        },
        {
            "prompt": "Apply for a job where the title is not 'Backend Engineer', the location is not remote, and the company name contains the letter 'o'.",
            "prompt_for_task_generation": "Apply for a job where the title is not 'Backend Engineer', the location is not remote, and the company name contains the letter 'o'.",
        },
        {
            "prompt": "Apply to QualityFirst for the QA Tester opening.",
            "prompt_for_task_generation": "Apply to QualityFirst for the QA Tester opening.",
        },
        {
            "prompt": "Apply for the UI/UX Designer job.",
            "prompt_for_task_generation": "Apply for the UI/UX Designer job.",
        },
        {
            "prompt": "Apply to MediaWorks in Seattle, WA.",
            "prompt_for_task_generation": "Apply to MediaWorks in Seattle, WA.",
        },
    ],
)


SEARCH_USERS_USE_CASE = UseCase(
    name="SEARCH_USERS",
    description="The user searches for other users.",
    event=SearchUsersEvent,
    event_source_code=SearchUsersEvent.get_source_code_of_class(),
    constraints_generator=generate_search_users_constraints,
    examples=[
        {
            "prompt": "Search for users with the query 'al'.",
            "prompt_for_task_generation": "Search for users with the query '<query>'.",
        },
    ],
)


FOLLOW_PAGE_USE_CASE = UseCase(
    name="FOLLOW_PAGE",
    description="The user follows a company page.",
    event=FollowPageEvent,
    event_source_code=FollowPageEvent.get_source_code_of_class(),
    constraints_generator=generate_follow_page_constraints,
    examples=[
        {
            "prompt": "Follow the Adobe company page.",
            "prompt_for_task_generation": "Follow the <company> company page.",
        },
    ],
)
SEARCH_JOBS_USE_CASE = UseCase(
    name="SEARCH_JOBS",
    description="The user searches for jobs.",
    event=SearchJobsEvent,
    event_source_code=SearchJobsEvent.get_source_code_of_class(),
    constraints_generator=generate_search_jobs_constraints,
    examples=[
        # Query (STRING_OPERATORS)
        {
            "prompt": "Search for jobs with the query 'fro'.",
            "prompt_for_task_generation": "Search for jobs with the query 'fro'.",
        },
        {
            "prompt": "Find jobs where the query contains 'engineer'.",
            "prompt_for_task_generation": "Find jobs where the query contains 'engineer'.",
        },
        {
            "prompt": "Look for jobs with the query starting with 'full'.",
            "prompt_for_task_generation": "Look for jobs with the query starting with 'full'.",
        },
        {
            "prompt": "Search for jobs with the query exactly equal to 'data scientist'.",
            "prompt_for_task_generation": "Search for jobs with the query exactly equal to 'data scientist'.",
        },
        # Experience (EQUALS, NOT_EQUALS)
        {
            "prompt": "Find jobs that require experience equal to 'mid'.",
            "prompt_for_task_generation": "Find jobs that require experience equal to 'mid'.",
        },
        {
            "prompt": "Search for jobs where the experience level is not 'entry'.",
            "prompt_for_task_generation": "Search for jobs where the experience level is not 'entry'.",
        },
        # Location (STRING_OPERATORS)
        {
            "prompt": "Search for jobs located in 'New York'.",
            "prompt_for_task_generation": "Search for jobs located in 'New York'.",
        },
        {
            "prompt": "Find jobs where the location contains 'valley'.",
            "prompt_for_task_generation": "Find jobs where the location contains 'valley'.",
        },
        {
            "prompt": "Look for jobs with location starting with 'San'.",
            "prompt_for_task_generation": "Look for jobs with location starting with 'San'.",
        },
        {
            "prompt": "Search jobs with location equal to 'Remote'.",
            "prompt_for_task_generation": "Search jobs with location equal to 'Remote'.",
        },
        # Remote (EQUALS)
        {
            "prompt": "Find remote jobs only.",
            "prompt_for_task_generation": "Find remote jobs only.",
        },
        {
            "prompt": "Search for jobs that are not remote.",
            "prompt_for_task_generation": "Search for jobs that are not remote.",
        },
        # Salary (EQUALS, NOT_EQUALS)
        {
            "prompt": "Search for jobs with a salary equal to 80000.",
            "prompt_for_task_generation": "Search for jobs with a salary equal to 80000.",
        },
        {
            "prompt": "Find jobs where salary is not 50000.",
            "prompt_for_task_generation": "Find jobs where salary is not 50000.",
        },
    ],
)

VIEW_JOB_USE_CASE = UseCase(
    name="VIEW_JOB",
    description="The user views a job posting in detail.",
    event=ViewJobEvent,
    event_source_code=ViewJobEvent.get_source_code_of_class(),
    constraints_generator=generate_view_job_constraints,
    examples=[
        {
            "prompt": "View the job posting for 'Senior Frontend Developer' at Tech Innovations.",
            "prompt_for_task_generation": "View the job posting for 'Senior Frontend Developer' at Tech Innovations.",
        },
        {
            "prompt": "Open the detailed job description for a remote Backend Engineer role.",
            "prompt_for_task_generation": "Open the detailed job description for a remote Backend Engineer role.",
        },
        {
            "prompt": "Check the job details for a Frontend Developer position located in San Francisco.",
            "prompt_for_task_generation": "Check the job details for a Frontend Developer position located in San Francisco.",
        },
    ],
)

ALL_USE_CASES = [
    VIEW_USER_PROFILE_USE_CASE,
    CONNECT_WITH_USER_USE_CASE,
    POST_STATUS_USE_CASE,
    LIKE_POST_USE_CASE,
    COMMENT_ON_POST_USE_CASE,
    SEARCH_USERS_USE_CASE,
    FOLLOW_PAGE_USE_CASE,
    VIEW_JOB_USE_CASE,
    APPLY_FOR_JOB_USE_CASE,
    SEARCH_JOBS_USE_CASE,
]
