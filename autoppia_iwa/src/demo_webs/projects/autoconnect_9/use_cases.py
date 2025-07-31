from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    ApplyForJobEvent,
    CommentOnPostEvent,
    ConnectWithUserEvent,
    FollowPageEvent,
    HomeNavbarEvent,
    JobsNavbarEvent,
    LikePostEvent,
    PostStatusEvent,
    ProfileNavbarEvent,
    SearchJobsEvent,
    SearchUsersEvent,
    ViewAllRecommendationsEvent,
    ViewUserProfileEvent,
)
from .generation_functions import generate_connect_with_user_constraints, generate_post_status_constraints, generate_view_user_profile_constraints

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
            "prompt_for_task_generation": "Connect with Jane Doe",
        },
    ],
)

HOME_NAVBAR_USE_CASE = UseCase(
    name="HOME_NAVBAR",
    description="The user navigates to the Home page using the navbar.",
    event=HomeNavbarEvent,
    event_source_code=HomeNavbarEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Click on the Home button in the navbar.",
            "prompt_for_task_generation": "Click on the Home button in the navbar.",
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
    description="The user likes a post.",
    event=LikePostEvent,
    event_source_code=LikePostEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Like the post with ID 'e8hsx779aco' as Alex Smith.",
            "prompt_for_task_generation": "Like the post with ID '<post_id>' as <user_name>.",
        },
    ],
)

COMMENT_ON_POST_USE_CASE = UseCase(
    name="COMMENT_ON_POST",
    description="The user comments on a post.",
    event=CommentOnPostEvent,
    event_source_code=CommentOnPostEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Comment 'liked!' on the post with ID 'e8hsx779aco' as Alex Smith.",
            "prompt_for_task_generation": "Comment '<comment_text>' on the post with ID '<post_id>' as <user_name>.",
        },
    ],
)

JOBS_NAVBAR_USE_CASE = UseCase(
    name="JOBS_NAVBAR",
    description="The user navigates to the Jobs page using the navbar.",
    event=JobsNavbarEvent,
    event_source_code=JobsNavbarEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Click on the Jobs button in the navbar.",
            "prompt_for_task_generation": "Click on the Jobs button in the navbar.",
        },
    ],
)

APPLY_FOR_JOB_USE_CASE = UseCase(
    name="APPLY_FOR_JOB",
    description="The user applies for a job.",
    event=ApplyForJobEvent,
    event_source_code=ApplyForJobEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Apply for the Frontend Developer job at Tech Innovations (Remote).",
            "prompt_for_task_generation": "Apply for the <job_title> job at <company> (<location>).",
        },
    ],
)

PROFILE_NAVBAR_USE_CASE = UseCase(
    name="PROFILE_NAVBAR",
    description="The user navigates to their profile page using the navbar.",
    event=ProfileNavbarEvent,
    event_source_code=ProfileNavbarEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Click on the Profile button in the navbar as Alex Smith.",
            "prompt_for_task_generation": "Click on the Profile button in the navbar as <username>.",
        },
    ],
)

SEARCH_USERS_USE_CASE = UseCase(
    name="SEARCH_USERS",
    description="The user searches for other users.",
    event=SearchUsersEvent,
    event_source_code=SearchUsersEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "Search for users with the query 'al'.",
            "prompt_for_task_generation": "Search for users with the query '<query>'.",
        },
    ],
)

VIEW_ALL_RECOMMENDATIONS_USE_CASE = UseCase(
    name="VIEW_ALL_RECOMMENDATIONS",
    description="The user views all recommendations.",
    event=ViewAllRecommendationsEvent,
    event_source_code=ViewAllRecommendationsEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[
        {
            "prompt": "View all recommendations from the recommendations page.",
            "prompt_for_task_generation": "View all recommendations from the <source>.",
        },
    ],
)

FOLLOW_PAGE_USE_CASE = UseCase(
    name="FOLLOW_PAGE",
    description="The user follows a company page.",
    event=FollowPageEvent,
    event_source_code=FollowPageEvent.get_source_code_of_class(),
    constraints_generator=None,
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
    constraints_generator=None,
    examples=[
        {
            "prompt": "Search for jobs with the query 'fro'.",
            "prompt_for_task_generation": "Search for jobs with the query '<query>'.",
        },
    ],
)

ALL_USE_CASES = [
    # VIEW_USER_PROFILE_USE_CASE,
    # CONNECT_WITH_USER_USE_CASE,
    # HOME_NAVBAR_USE_CASE,
    POST_STATUS_USE_CASE,
    # LIKE_POST_USE_CASE,
    # COMMENT_ON_POST_USE_CASE,
    # JOBS_NAVBAR_USE_CASE,
    # APPLY_FOR_JOB_USE_CASE,
    # PROFILE_NAVBAR_USE_CASE,
    # SEARCH_USERS_USE_CASE,
    # VIEW_ALL_RECOMMENDATIONS_USE_CASE,
    # FOLLOW_PAGE_USE_CASE,
    # SEARCH_JOBS_USE_CASE,
]
