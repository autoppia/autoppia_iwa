from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddExperienceEvent,
    ApplyForJobEvent,
    BackToAllJobsEvent,
    CancelApplicationEvent,
    CommentOnPostEvent,
    ConnectWithUserEvent,
    EditExperienceEvent,
    EditProfileEvent,
    FilterJobsEvent,
    FollowPageEvent,
    HidePostEvent,
    HomeNavbarEvent,
    JobsNavbarEvent,
    LikePostEvent,
    PostStatusEvent,
    RemovePostEvent,
    SavePostEvent,
    SearchJobsEvent,
    SearchUsersEvent,
    UnfollowPageEvent,
    UnhidePostEvent,
    ViewAppliedJobsEvent,
    ViewHiddenPostsEvent,
    ViewJobEvent,
    ViewSavedPostsEvent,
    ViewUserProfileEvent,
)
from .generation_functions import (
    generate_add_experience_constraints,
    generate_apply_for_job_constraints,
    generate_back_to_all_jobs_constraints,
    generate_cancel_application_constraints,
    generate_comment_on_post_constraints,
    generate_connect_with_user_constraints,
    generate_edit_experience_constraints,
    generate_edit_profile_constraints,
    generate_filter_jobs_constraints,
    generate_follow_page_constraints,
    generate_like_post_constraints,
    generate_post_status_constraints,
    generate_remove_post_constraints,
    generate_save_post_constraints,
    generate_search_jobs_constraints,
    generate_search_users_constraints,
    generate_unfollow_page_constraints,
    generate_unhide_post_constraints,
    generate_view_job_constraints,
    generate_view_user_profile_constraints,
)

VIEW_USER_PROFILE_INFO = """
Critical requirements:
1. The request must start with "View user profile" or "View the profile of user" (or similar).
2. Include ALL mentioned constraints in the prompt.
3. Do not add additional information that is not in the constraints.
4. All constraint values must be copied exactly as provided (e.g., in single quotes).

EXAMPLES:
✅ CORRECT: View the profile of user where name not equals 'Smith'.
❌ INCORRECT: View the profile of user 'janedoe' where the name is NOT 'sarahlee'. (Do not invent user identifiers not in constraints; use exact constraint field and value.)
""".strip()

VIEW_USER_PROFILE_USE_CASE = UseCase(
    name="VIEW_USER_PROFILE",
    description="The user views another user's profile.",
    event=ViewUserProfileEvent,
    event_source_code=ViewUserProfileEvent.get_source_code_of_class(),
    constraints_generator=generate_view_user_profile_constraints,
    additional_prompt_info=VIEW_USER_PROFILE_INFO,
    examples=[
        {
            "prompt": "View the profile of user where name equals 'janedoe'.",
            "prompt_for_task_generation": "View the profile of user where name equals 'janedoe'.",
        },
        {
            "prompt": "View the profile of user where name is not equal to 'Smith'.",
            "prompt_for_task_generation": "View the profile of user where name is not equal to 'Smith'.",
        },
        {
            "prompt": "Open the profile of user where name contains 'Jane'.",
            "prompt_for_task_generation": "View the profile of user where name contains 'Jane'.",
        },
    ],
)

BACK_TO_ALL_JOBS_INFO = """
Critical requirements:
1. The request must start with "Go back to all jobs" (or equivalent).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes; do not reformat or paraphrase.
""".strip()

BACK_TO_ALL_JOBS_USE_CASE = UseCase(
    name="BACK_TO_ALL_JOBS",
    description="The user navigates back to the main jobs list.",
    event=BackToAllJobsEvent,
    event_source_code=BackToAllJobsEvent.get_source_code_of_class(),
    constraints_generator=generate_back_to_all_jobs_constraints,
    additional_prompt_info=BACK_TO_ALL_JOBS_INFO,
    examples=[
        {
            "prompt": "Go back to all jobs from a job detail page.",
            "prompt_for_task_generation": "Go back to all jobs from a job detail page.",
        },
        {
            "prompt": "Go back to all jobs from a job where location equals 'San Francisco, CA', title equals 'Senior Frontend Developer' and company equals 'Tech Innovations'.",
            "prompt_for_task_generation": "Go back to all jobs from a job where location equals 'San Francisco, CA', title equals 'Senior Frontend Developer' and company equals 'Tech Innovations'.",
        },
        {
            "prompt": "Go back to all jobs from a job where location not equals 'Data Scientist', title contains 'Frontend' and company equals 'Tech Innovations'.",
            "prompt_for_task_generation": "Go back to all jobs from a job where location not equals 'Data Scientist', title contains 'Frontend' and company equals 'Tech Innovations'.",
        },
    ],
)

CONNECT_WITH_USER_INFO = """
Critical requirements:
1. The request must start with "Connect with" or "Send connection request to" (or equivalent).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

CONNECT_WITH_USER_USE_CASE = UseCase(
    name="CONNECT_WITH_USER",
    description="The user sends a connection request to another user.",
    event=ConnectWithUserEvent,
    event_source_code=ConnectWithUserEvent.get_source_code_of_class(),
    constraints_generator=generate_connect_with_user_constraints,
    additional_prompt_info=CONNECT_WITH_USER_INFO,
    examples=[
        {
            "prompt": "Connect with Jane Doe.",
            "prompt_for_task_generation": "Connect with Jane Doe.",
        },
    ],
)


POST_STATUS_INFO = """
Critical requirements:
1. The request must start with "Post a status" or "Post" (or equivalent).
2. Include the content constraint with its value in single quotes; copy exactly.
""".strip()

POST_STATUS_USE_CASE = UseCase(
    name="POST_STATUS",
    description="The user posts a new status update.",
    event=PostStatusEvent,
    event_source_code=PostStatusEvent.get_source_code_of_class(),
    constraints_generator=generate_post_status_constraints,
    additional_prompt_info=POST_STATUS_INFO,
    examples=[
        {
            "prompt": "Post a status where content equals 'hi'.",
            "prompt_for_task_generation": "Post a status where content equals 'hi'.",
        },
        {
            "prompt": "Post a status saying 'Just shipped a new feature!'",
            "prompt_for_task_generation": "Post a status where content contains 'shipped'.",
        },
    ],
)

LIKE_POST_INFO = """
Critical requirements:
1. The request must start with "Like the post" (or equivalent).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

LIKE_POST_USE_CASE = UseCase(
    name="LIKE_POST",
    description="The user likes a post",
    event=LikePostEvent,
    event_source_code=LikePostEvent.get_source_code_of_class(),
    constraints_generator=generate_like_post_constraints,
    additional_prompt_info=LIKE_POST_INFO,
    examples=[
        {
            "prompt": "Like the post where poster_content contains 'I finally got my AWS certification!'",
            "prompt_for_task_generation": "Like the post where poster_content contains 'I finally got my AWS certification!'",
        },
        {
            "prompt": "Like the post where poster_content contains 'Launching my first startup today!'",
            "prompt_for_task_generation": "Like the post where poster_content contains 'Launching my first startup today!'",
        },
        {
            "prompt": "Like the post where poster_content equals 'Grateful for everyone who supported me on this journey.'",
            "prompt_for_task_generation": "Like the post where poster_content equals 'Grateful for everyone who supported me on this journey.'",
        },
        {
            "prompt": "Like the post where poster_content not contains 'Looking for job opportunities.'",
            "prompt_for_task_generation": "Like the post where poster_content not contains 'Looking for job opportunities.'",
        },
        {
            "prompt": "Like the post where poster_content not equals 'Just completed my first year at TechCorp!'",
            "prompt_for_task_generation": "Like the post where poster_content not equals 'Just completed my first year at TechCorp!'",
        },
        {
            "prompt": "Like the post where poster_content contains 'Excited to attend PyCon this year!'",
            "prompt_for_task_generation": "Like the post where poster_content contains 'Excited to attend PyCon this year!'",
        },
    ],
)

COMMENT_ON_POST_INFO = """
Critical requirements:
1. The request must start with "Comment" and include the comment text and post constraint (e.g., poster_content).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

COMMENT_ON_POST_USE_CASE = UseCase(
    name="COMMENT_ON_POST",
    description="The user comments on a post.",
    event=CommentOnPostEvent,
    event_source_code=CommentOnPostEvent.get_source_code_of_class(),
    constraints_generator=generate_comment_on_post_constraints,
    additional_prompt_info=COMMENT_ON_POST_INFO,
    examples=[
        {
            "prompt": "Comment 'Great work!' on the post where poster_content contains 'Just released a new app version!'",
            "prompt_for_task_generation": "Comment 'Great work!' on the post where poster_content contains 'Just released a new app version!'",
        },
        {
            "prompt": "Comment 'Congrats!' on the post where poster_content contains 'I just got promoted to Senior Developer.'",
            "prompt_for_task_generation": "Comment 'Congrats!' on the post where poster_content contains 'I just got promoted to Senior Developer.'",
        },
        {
            "prompt": "Comment 'Very insightful!' on the post where poster_content contains 'Here's what I learned from switching to microservices.'",
            "prompt_for_task_generation": "Comment 'Very insightful!' on the post where poster_content contains 'Here's what I learned from switching to microservices.'",
        },
        {
            "prompt": "Comment 'Thanks for sharing!' on the post where poster_content contains '5 tips for improving frontend performance.'",
            "prompt_for_task_generation": "Comment 'Thanks for sharing!' on the post where poster_content contains '5 tips for improving frontend performance.'",
        },
    ],
)


APPLY_FOR_JOB_INFO = """
Critical requirements:
1. The request must start with "Apply for" or "Submit application" (or equivalent).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

APPLY_FOR_JOB_USE_CASE = UseCase(
    name="APPLY_FOR_JOB",
    description="The user applies for a job.",
    event=ApplyForJobEvent,
    event_source_code=ApplyForJobEvent.get_source_code_of_class(),
    constraints_generator=generate_apply_for_job_constraints,
    additional_prompt_info=APPLY_FOR_JOB_INFO,
    examples=[
        {
            "prompt": "Apply for a job where job_title equals 'Frontend Developer', company equals 'Tech Innovations', and location equals 'Remote'.",
            "prompt_for_task_generation": "Apply for a job where job_title equals 'Frontend Developer', company equals 'Tech Innovations', and location equals 'Remote'.",
        },
        {
            "prompt": "Apply for a job where job_title contains 'Product Designer' and location equals 'New York, NY'.",
            "prompt_for_task_generation": "Apply for a job where job_title contains 'Product Designer' and location equals 'New York, NY'.",
        },
        {
            "prompt": "Apply for a job where company equals 'Creative Studio' and job_title contains 'Product Designer'.",
            "prompt_for_task_generation": "Apply for a job where company equals 'Creative Studio' and job_title contains 'Product Designer'.",
        },
        {
            "prompt": "Apply for a job where job_title not equals 'Backend Engineer', location not equals 'Remote', and company contains 'o'.",
            "prompt_for_task_generation": "Apply for a job where job_title not equals 'Backend Engineer', location not equals 'Remote', and company contains 'o'.",
        },
    ],
)


SEARCH_USERS_INFO = """
Critical requirements:
1. The request must start with "Search for users" or "Find users" (or equivalent).
2. Include the query constraint with its value in single quotes; copy exactly.
""".strip()

SEARCH_USERS_USE_CASE = UseCase(
    name="SEARCH_USERS",
    description="The user searches for other users.",
    event=SearchUsersEvent,
    event_source_code=SearchUsersEvent.get_source_code_of_class(),
    constraints_generator=generate_search_users_constraints,
    additional_prompt_info=SEARCH_USERS_INFO,
    examples=[
        {
            "prompt": "Search for users where query equals 'al'.",
            "prompt_for_task_generation": "Search for users where query equals 'al'.",
        },
        {
            "prompt": "Find users where query contains 'engineer'.",
            "prompt_for_task_generation": "Search for users where query contains 'engineer'.",
        },
    ],
)


FOLLOW_PAGE_INFO = """
Critical requirements:
1. The request must start with "Follow" and reference a company page (or equivalent).
2. Include ALL mentioned constraints in the prompt.

""".strip()

FOLLOW_PAGE_USE_CASE = UseCase(
    name="FOLLOW_PAGE",
    description="The user follows a company page.",
    event=FollowPageEvent,
    event_source_code=FollowPageEvent.get_source_code_of_class(),
    constraints_generator=generate_follow_page_constraints,
    additional_prompt_info=FOLLOW_PAGE_INFO,
    examples=[
        {
            "prompt": "Follow the Adobe company page.",
            "prompt_for_task_generation": "Follow the company page where recommendation equals 'Adobe'.",
        },
    ],
)

UNFOLLOW_PAGE_INFO = """
Critical requirements:
1. The request must start with "Unfollow" and reference a company page (or equivalent).
2. Include the company constraint with its value in single quotes; copy exactly.
""".strip()

UNFOLLOW_PAGE_USE_CASE = UseCase(
    name="UNFOLLOW_PAGE",
    description="The user unfollows a company page.",
    event=UnfollowPageEvent,
    event_source_code=UnfollowPageEvent.get_source_code_of_class(),
    constraints_generator=generate_unfollow_page_constraints,
    additional_prompt_info=UNFOLLOW_PAGE_INFO,
    examples=[
        {
            "prompt": "Unfollow the Adobe company page.",
            "prompt_for_task_generation": "Unfollow the company page where company equals 'Adobe'.",
        },
    ],
)

SEARCH_JOBS_INFO = """
Critical requirements:
1. The request must start with "Search for jobs" or "Find jobs" (or equivalent).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

SEARCH_JOBS_USE_CASE = UseCase(
    name="SEARCH_JOBS",
    description="The user searches for jobs.",
    event=SearchJobsEvent,
    event_source_code=SearchJobsEvent.get_source_code_of_class(),
    constraints_generator=generate_search_jobs_constraints,
    additional_prompt_info=SEARCH_JOBS_INFO,
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

FILTER_JOBS_INFO = """
Critical requirements:
1. The request must start with "Filter jobs" (or equivalent).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

FILTER_JOBS_USE_CASE = UseCase(
    name="FILTER_JOBS",
    description="The user applies filters to job listings.",
    event=FilterJobsEvent,
    event_source_code=FilterJobsEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_jobs_constraints,
    additional_prompt_info=FILTER_JOBS_INFO,
    examples=[
        {
            "prompt": "Filter jobs where remote equals 'true'.",
            "prompt_for_task_generation": "Filter jobs where remote equals 'true'.",
        },
        {
            "prompt": "Filter jobs where salary equals '100000-125000'.",
            "prompt_for_task_generation": "Filter jobs where salary equals '100000-125000'.",
        },
    ],
)

VIEW_JOB_INFO = """
Critical requirements:
1. The request must start with "View the job" or "Open job details" (or equivalent).
2. Include ALL mentioned constraints in the prompt.
3. Copy constraint values exactly in single quotes.
""".strip()

VIEW_JOB_USE_CASE = UseCase(
    name="VIEW_JOB",
    description="The user views a job posting in detail.",
    event=ViewJobEvent,
    event_source_code=ViewJobEvent.get_source_code_of_class(),
    constraints_generator=generate_view_job_constraints,
    additional_prompt_info=VIEW_JOB_INFO,
    examples=[
        {
            "prompt": "View the job where job_title equals 'Senior Frontend Developer' and company equals 'Tech Innovations'.",
            "prompt_for_task_generation": "View the job where job_title equals 'Senior Frontend Developer' and company equals 'Tech Innovations'.",
        },
        {
            "prompt": "Open the job where job_title contains 'Backend Engineer' and location equals 'Remote'.",
            "prompt_for_task_generation": "View the job where job_title contains 'Backend Engineer' and location equals 'Remote'.",
        },
        {
            "prompt": "View the job where job_title contains 'Frontend Developer' and location contains 'San Francisco'.",
            "prompt_for_task_generation": "View the job where job_title contains 'Frontend Developer' and location contains 'San Francisco'.",
        },
    ],
)

HOME_NAVBAR_USE_CASE = UseCase(
    name="HOME_NAVBAR",
    description="The user opens the Home tab from the navbar.",
    event=HomeNavbarEvent,
    event_source_code=HomeNavbarEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Go to the Home tab.", "prompt_for_task_generation": "Go to the Home tab."},
        {"prompt": "Navigate back to Home from the navbar.", "prompt_for_task_generation": "Navigate back to Home from the navbar."},
        {"prompt": "Open Home in navigation.", "prompt_for_task_generation": "Open Home in navigation."},
    ],
)

JOBS_NAVBAR_USE_CASE = UseCase(
    name="JOBS_NAVBAR",
    description="The user opens the Jobs tab via the navbar.",
    event=JobsNavbarEvent,
    event_source_code=JobsNavbarEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Switch to the Jobs tab.", "prompt_for_task_generation": "Switch to the Jobs tab."},
        {"prompt": "Open Jobs from navigation.", "prompt_for_task_generation": "Open Jobs from navigation."},
        {"prompt": "Go to the jobs section in the navbar.", "prompt_for_task_generation": "Go to the jobs section in the navbar."},
    ],
)


SAVE_POST_INFO = """
Critical requirements:
1. The request must start with "Save the post" or "Bookmark" (or equivalent).
2. Include ALL mentioned constraints in the prompt when present; copy values in single quotes.
""".strip()

SAVE_POST_USE_CASE = UseCase(
    name="SAVE_POST",
    description="The user saves a post to view later.",
    event=SavePostEvent,
    event_source_code=SavePostEvent.get_source_code_of_class(),
    constraints_generator=generate_save_post_constraints,
    additional_prompt_info=SAVE_POST_INFO,
    examples=[
        {"prompt": "Save the post where content contains 'AI trends'.", "prompt_for_task_generation": "Save the post where content contains 'AI trends'."},
        {"prompt": "Bookmark the post where content contains 'hiring announcement'.", "prompt_for_task_generation": "Save the post where content contains 'hiring announcement'."},
        {"prompt": "Save the post where author equals 'Alex'.", "prompt_for_task_generation": "Save the post where author equals 'Alex'."},
    ],
)

HIDE_POST_INFO = """
Critical requirements:
1. The request must start with "Hide the post" or "Hide this post" (or equivalent).
2. Include ALL mentioned constraints in the prompt when present; copy values in single quotes.
""".strip()

HIDE_POST_USE_CASE = UseCase(
    name="HIDE_POST",
    description="The user hides a post from their feed.",
    event=HidePostEvent,
    event_source_code=HidePostEvent.get_source_code_of_class(),
    constraints_generator=generate_save_post_constraints,
    additional_prompt_info=HIDE_POST_INFO,
    examples=[
        {"prompt": "Hide the post where content contains 'irrelevant'.", "prompt_for_task_generation": "Hide the post where content contains 'irrelevant'."},
        {"prompt": "Hide the post where content contains 'duplicate'.", "prompt_for_task_generation": "Hide the post where content contains 'duplicate'."},
        {"prompt": "Hide the post where author equals 'Marketing'.", "prompt_for_task_generation": "Hide the post where author equals 'Marketing'."},
    ],
)

VIEW_SAVED_POSTS_USE_CASE = UseCase(
    name="VIEW_SAVED_POSTS",
    description="The user views their saved posts list.",
    event=ViewSavedPostsEvent,
    event_source_code=ViewSavedPostsEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Open my saved posts.", "prompt_for_task_generation": "Open my saved posts."},
        {"prompt": "View the saved items from the sidebar.", "prompt_for_task_generation": "View the saved items from the sidebar."},
    ],
)

VIEW_APPLIED_JOBS_USE_CASE = UseCase(
    name="VIEW_APPLIED_JOBS",
    description="The user views jobs they have applied to.",
    event=ViewAppliedJobsEvent,
    event_source_code=ViewAppliedJobsEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Show my applied jobs list.", "prompt_for_task_generation": "Show my applied jobs list."},
        {"prompt": "View the roles I already applied to.", "prompt_for_task_generation": "View the roles I already applied to."},
    ],
)

CANCEL_APPLICATION_INFO = """
Critical requirements:
1. The request must start with "Cancel application" or "Withdraw application" (or equivalent).
2. Include ALL mentioned constraints in the prompt; copy values in single quotes.
""".strip()

CANCEL_APPLICATION_USE_CASE = UseCase(
    name="CANCEL_APPLICATION",
    description="The user cancels a job application.",
    event=CancelApplicationEvent,
    event_source_code=CancelApplicationEvent.get_source_code_of_class(),
    constraints_generator=generate_cancel_application_constraints,
    additional_prompt_info=CANCEL_APPLICATION_INFO,
    examples=[
        {"prompt": "Cancel application for job where job_title equals 'Product Designer'.", "prompt_for_task_generation": "Cancel application for job where job_title equals 'Product Designer'."},
        {"prompt": "Withdraw application where company equals 'Stripe'.", "prompt_for_task_generation": "Cancel application where company equals 'Stripe'."},
    ],
)

EDIT_PROFILE_INFO = """
Critical requirements:
1. The request must start with "Edit profile" or "Update profile" (or equivalent).
2. Include ALL mentioned constraints in the prompt; copy values in single quotes.
""".strip()

EDIT_PROFILE_USE_CASE = UseCase(
    name="EDIT_PROFILE",
    description="The user edits their profile information.",
    event=EditProfileEvent,
    event_source_code=EditProfileEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_profile_constraints,
    additional_prompt_info=EDIT_PROFILE_INFO,
    examples=[
        {"prompt": "Edit profile where bio contains 'engineer'.", "prompt_for_task_generation": "Edit profile where bio contains 'engineer'."},
        {"prompt": "Update profile where name equals 'Alex Smith'.", "prompt_for_task_generation": "Edit profile where name equals 'Alex Smith'."},
    ],
)

EDIT_EXPERIENCE_INFO = """
Critical requirements:
1. The request must start with "Edit experience" or "Update experience" (or equivalent).
2. Include ALL mentioned constraints in the prompt; copy values in single quotes.
""".strip()

EDIT_EXPERIENCE_USE_CASE = UseCase(
    name="EDIT_EXPERIENCE",
    description="The user edits or adds job experience entries.",
    event=EditExperienceEvent,
    event_source_code=EditExperienceEvent.get_source_code_of_class(),
    constraints_generator=generate_edit_experience_constraints,
    additional_prompt_info=EDIT_EXPERIENCE_INFO,
    examples=[
        {"prompt": "Edit experience where name equals 'Alex'.", "prompt_for_task_generation": "Edit experience where name equals 'Alex'."},
        {
            "prompt": "Edit experience where company contains 'Tech' and title equals 'Developer'.",
            "prompt_for_task_generation": "Edit experience where company contains 'Tech' and title equals 'Developer'.",
        },
    ],
)

ADD_EXPERIENCE_INFO = """
Critical requirements:
1. The request must start with "Add experience" or "Add new experience" (or equivalent).
2. Include ALL mentioned constraints in the prompt when present; copy values in single quotes.
""".strip()

ADD_EXPERIENCE_USE_CASE = UseCase(
    name="ADD_EXPERIENCE",
    description="The user adds a new experience entry to their profile.",
    event=AddExperienceEvent,
    event_source_code=AddExperienceEvent.get_source_code_of_class(),
    constraints_generator=generate_add_experience_constraints,
    additional_prompt_info=ADD_EXPERIENCE_INFO,
    examples=[
        {"prompt": "Add experience where name equals 'TechCorp'.", "prompt_for_task_generation": "Add experience where name equals 'TechCorp'."},
        {"prompt": "Add new experience to my profile.", "prompt_for_task_generation": "Add new experience to my profile."},
    ],
)

REMOVE_POST_INFO = """
Critical requirements:
1. The request must start with "Remove post" or "Delete saved post" (or equivalent).
2. Include ALL mentioned constraints in the prompt; copy values in single quotes.
""".strip()

REMOVE_POST_USE_CASE = UseCase(
    name="REMOVE_POST",
    description="The user removes a post from a list (e.g., saved items).",
    event=RemovePostEvent,
    event_source_code=RemovePostEvent.get_source_code_of_class(),
    constraints_generator=generate_remove_post_constraints,
    additional_prompt_info=REMOVE_POST_INFO,
    examples=[
        {
            "prompt": "Remove saved post where content contains 'Just wrapped up!'.",
            "prompt_for_task_generation": "Remove saved post where content contains 'Just wrapped up!'.",
        },
        {"prompt": "Remove saved post where author equals 'Alex'.", "prompt_for_task_generation": "Remove saved post where author equals 'Alex'."},
    ],
)

VIEW_HIDDEN_POSTS_USE_CASE = UseCase(
    name="VIEW_HIDDEN_POSTS",
    description="The user views hidden posts.",
    event=ViewHiddenPostsEvent,
    event_source_code=ViewHiddenPostsEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Open my hidden posts list.", "prompt_for_task_generation": "Open my hidden posts list."},
        {"prompt": "View the posts I hide earlier.", "prompt_for_task_generation": "View the posts I hide earlier."},
    ],
)

UNHIDE_POST_INFO = """
Critical requirements:
1. The request must start with "Unhide the post" or "Restore post" (or equivalent).
2. Include ALL mentioned constraints in the prompt when present; copy values in single quotes.
""".strip()

UNHIDE_POST_USE_CASE = UseCase(
    name="UNHIDE_POST",
    description="The user restores a previously hidden post.",
    event=UnhidePostEvent,
    event_source_code=UnhidePostEvent.get_source_code_of_class(),
    constraints_generator=generate_unhide_post_constraints,
    additional_prompt_info=UNHIDE_POST_INFO,
    examples=[
        {"prompt": "Unhide the post where content contains 'Just wrapped up'.", "prompt_for_task_generation": "Unhide the post where content contains 'Just wrapped up'."},
        {"prompt": "Restore hidden post to my feed.", "prompt_for_task_generation": "Unhide the post."},
    ],
)

ALL_USE_CASES = [
    VIEW_USER_PROFILE_USE_CASE,
    CONNECT_WITH_USER_USE_CASE,
    POST_STATUS_USE_CASE,
    LIKE_POST_USE_CASE,
    COMMENT_ON_POST_USE_CASE,
    SAVE_POST_USE_CASE,
    HIDE_POST_USE_CASE,
    VIEW_SAVED_POSTS_USE_CASE,
    VIEW_APPLIED_JOBS_USE_CASE,
    CANCEL_APPLICATION_USE_CASE,
    EDIT_PROFILE_USE_CASE,
    EDIT_EXPERIENCE_USE_CASE,
    ADD_EXPERIENCE_USE_CASE,
    REMOVE_POST_USE_CASE,
    VIEW_HIDDEN_POSTS_USE_CASE,
    UNHIDE_POST_USE_CASE,
    SEARCH_USERS_USE_CASE,
    FOLLOW_PAGE_USE_CASE,
    UNFOLLOW_PAGE_USE_CASE,
    VIEW_JOB_USE_CASE,
    FILTER_JOBS_USE_CASE,
    BACK_TO_ALL_JOBS_USE_CASE,
    APPLY_FOR_JOB_USE_CASE,
    SEARCH_JOBS_USE_CASE,
    HOME_NAVBAR_USE_CASE,
    JOBS_NAVBAR_USE_CASE,
]
