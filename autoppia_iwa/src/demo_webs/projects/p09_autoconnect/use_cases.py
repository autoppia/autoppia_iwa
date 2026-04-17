from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddExperienceEvent,
    ApplyForJobEvent,
    BackToAllJobsEvent,
    CancelApplicationEvent,
    CommentOnPostEvent,
    ConnectWithUserEvent,
    DeleteCommentEvent,
    DeletePostEvent,
    EditExperienceEvent,
    EditProfileEvent,
    FilterJobsEvent,
    FilterNotificationsEvent,
    FollowPageEvent,
    HidePostEvent,
    HomeNavbarEvent,
    JobsNavbarEvent,
    LikePostEvent,
    MarkAllNotificationsReadEvent,
    MarkNotificationReadEvent,
    PostStatusEvent,
    RemovePostEvent,
    SavePostEvent,
    SearchJobsEvent,
    SearchUsersEvent,
    UnfollowPageEvent,
    UnhidePostEvent,
    ViewAllRecommendationsEvent,
    ViewAppliedJobsEvent,
    ViewHiddenPostsEvent,
    ViewJobEvent,
    ViewNotificationsEvent,
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
    generate_filter_notifications_constraints,
    generate_follow_page_constraints,
    generate_like_post_constraints,
    generate_mark_notification_read_constraints,
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

GENERIC_DATA_EXTRACTION_PROMPT_INFO = """
Generate a single natural-language question that asks for the value of the verify field in this use case.

Use only natural wording and avoid schema-style field names or names with underscores (_).
Use selected identifying fields and their values to identify the target item, then ask for the verify field value.
Do not include the verify field value in the question text.

The output must be exactly one question.
""".strip()

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

VIEW_USER_PROFILE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a user profile in the view user profile context (e.g., name, title, bio, company, experience title, experience duration).

Use natural language only. Do NOT use schema-style field names such as "name", "title", "bio", "company", "experience_title", "experience_duration" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., user name, title, bio, company, experience title, experience duration).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "View...", "Open...", or "Show...".

Always end the question naturally with "after viewing profile."

For example, if the verify field is 'company', format the question naturally:
- "Can you tell me the company of the user 'Alice Johnson', whose title is 'Software Engineer', bio is 'Passionate about building scalable systems', experience title is 'Backend Developer', and experience duration is '3 years', so I can view the user profile?"

Examples:
- "Can you tell me the bio of the user 'John Smith', whose title is 'Data Scientist', company is 'DataWorks', experience title is 'ML Engineer', and experience duration is '4 years', after viewing profile?"
- "Can you tell me the experience title of the user 'Emily Clark', whose title is 'UX Designer', bio is 'Designing intuitive interfaces', company is 'Creative Studio', and experience duration is '2 years', after viewing profile?"
- "Can you tell me the experience duration of the user 'Michael Lee', whose title is 'DevOps Engineer', bio is 'Automation and cloud enthusiast', company is 'CloudNet', and experience title is 'Infrastructure Engineer', after viewing profile?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

CONNECT_WITH_USER_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a user profile in the connect with user context (e.g., name, title, bio, company, experience title, experience duration).

Use natural language only. Do NOT use schema-style field names such as "name", "title", "bio", "company", "experience_title", "experience_duration" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., user name, title, bio, company, experience title, experience duration).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Connect...", "Add...", or "Follow...".

Always end the question naturally with "so I can connect with the user."

For example, if the verify field is 'company', format the question naturally:
- "Can you tell me the company of the user 'Alice Johnson', whose title is 'Software Engineer', bio is 'Passionate about building scalable systems', experience title is 'Backend Developer', and experience duration is '3 years', so I can connect with the user?"

Examples:
- "Can you tell me the bio of the user 'John Smith', whose title is 'Data Scientist', company is 'DataWorks', experience title is 'ML Engineer', and experience duration is '4 years', so I can connect with the user?"
- "Can you tell me the experience title of the user 'Emily Clark', whose title is 'UX Designer', bio is 'Designing intuitive interfaces', company is 'Creative Studio', and experience duration is '2 years', so I can connect with the user?"
- "Can you tell me the experience duration of the user 'Michael Lee', whose title is 'DevOps Engineer', bio is 'Automation and cloud enthusiast', company is 'CloudNet', and experience title is 'Infrastructure Engineer', so I can connect with the user?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

LIKE_POST_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a post in the like post context (e.g., poster name, poster content, likes).

Use natural language only. Do NOT use schema-style field names such as "poster_name", "poster_content", "likes" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., poster name, post content, number of likes).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Like...", "React...", or "Tap...".

Always end the question naturally with "so I can like the post."

For example, if the verify field is 'likes', format the question naturally:
- "Can you tell me how many likes the post by 'Alice Johnson', which has content 'Excited to share my new project!', has, so I can like the post?"

Examples:
- "Can you tell me the post content shared by 'John Smith', which has 85 likes, so I can like the post?"
- "Can you tell me how many likes the post by 'Emily Clark', which has content 'Just finished a marathon!', has, so I can like the post?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

COMMENT_ON_POST_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a post in the comment on post context (e.g., commenter name, comment text, total number of comments, poster name, post content).

Use natural language only. Do NOT use schema-style field names such as "commenter_name", "comment_text", "total_comments", "poster_name", "poster_content" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., commenter name, comment text, total number of comments, poster name, post content).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Comment...", "Reply...", or "Write...".

Always end the question naturally with "so I can comment on the post."

For example, if the verify field is 'total_comments', format the question naturally:
- "Can you tell me total number of comments on the post by 'David Wilson', which has content 'Loving the sunny weather today!' and includes a comment 'So true!', has, so I can comment on the post?"

Examples:
- "Can you tell me the commenter name who wrote 'Amazing work!' on the post by 'Emily Clark', which has content 'Just finished a marathon!' and has 40 comments, so I can comment on the post?"
- "Can you tell me the post content on which 'Michael Lee' wrote 'Great insights!', which has 30 comments and is posted by 'Sophia Brown', so I can comment on the post?"
- "Can you tell me total number of comments on the post by 'David Wilson', which has content 'Loving the sunny weather today!' and includes a comment 'So true!', has, so I can comment on the post?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

APPLY_FOR_JOB_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a job in the apply for job context (e.g., job title, company, location, experience, salary, job type).

Use natural language only. Do NOT use schema-style field names such as "job_title", "company", "location", "experience", "salary", "job_type" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., job title, company, location, experience required, salary, job type).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Apply...", "Submit...", or "Send...".

Always end the question naturally with "so I can apply for the job."

For example, if the verify field is 'salary', format the question naturally:
- "Can you tell me the salary for the job 'Software Engineer' at 'TechCorp', located in New York, which requires 3 years of experience and is a full-time role, so I can apply for the job?"

Examples:
- "Can you tell me the job title at 'InnovateX', located in London, which requires 5 years of experience, offers a salary of $120k, and is a full-time role, so I can apply for the job?"
- "Can you tell me the company offering the job 'Data Scientist', located in San Francisco, which requires 4 years of experience, offers a salary of $110k, and is a contract role, so I can apply for the job?"
- "Can you tell me the location of the job 'Product Manager' at 'BuildIt', which requires 6 years of experience, offers a salary of $130k, and is a full-time role, so I can apply for the job?"
- "Can you tell me the job type for the job 'UI Designer' at 'Creative Studio', located in Berlin, which requires 2 years of experience and offers a salary of $70k, so I can apply for the job?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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


VIEW_ALL_RECOMMENDATIONS_INFO = """
Critical requirements:
1. The user opens the full recommendations feed (from nav, bottom bar, or the recommendations page).
2. Include the ``source`` constraint exactly as generated (e.g. recommendations_page, navbar, bottom_nav).
""".strip()

VIEW_ALL_RECOMMENDATIONS_USE_CASE = UseCase(
    name="VIEW_ALL_RECOMMENDATIONS",
    description="The user navigates to view all recommendations.",
    event=ViewAllRecommendationsEvent,
    event_source_code=ViewAllRecommendationsEvent.get_source_code_of_class(),
    constraints_generator=None,
    additional_prompt_info=VIEW_ALL_RECOMMENDATIONS_INFO,
    examples=[
        {
            "prompt": "Open the recommendations page from the main feed.",
            "prompt_for_task_generation": "View all recommendations where source equals 'recommendations_page'.",
        },
        {
            "prompt": "Go to Recs from the bottom navigation.",
            "prompt_for_task_generation": "View all recommendations where source equals 'bottom_nav'.",
        },
    ],
)

FOLLOW_PAGE_INFO = """
Critical requirements:
1. The request must start with "Follow" and reference a company page (or equivalent).
2. Include ALL mentioned constraints in the prompt.

""".strip()

FOLLOW_PAGE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a page in the follow page context (e.g., match score, category, title, reason).

Use natural language only. Do NOT use schema-style field names such as "match_score", "category", "title", "reason" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., match score, category, title, reason).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Follow...", "Subscribe...", or "Join...".

Always end the question naturally with "so I can follow it."

For example, if the verify field is 'title', format the question naturally:
- "Can you tell me the title of the page which has a match score of 0.92, belongs to the category 'Technology', and has reason 'Recommended based on your interests', so I can follow it?"

Examples:
- "Can you tell me the category of the page titled 'AI Innovations', which has a match score of 0.88 and reason 'Trending in your network', so I can follow it?"
- "Can you tell me the match score of the page titled 'Healthy Living', which belongs to the category 'Wellness' and has reason 'Based on your activity', so I can follow it?"
- "Can you tell me the reason for recommending the page titled 'Travel Diaries', which has a match score of 0.85 and belongs to the category 'Travel', so I can follow it?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

FILTER_JOBS_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a job in the filter jobs context (e.g., job title, company, location, experience, salary).

Use natural language only. Do NOT use schema-style field names such as "job_title", "company", "location", "experience", "salary" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., job title, company, location, experience required, salary).

Include only the selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Filter...", "Apply...", or "Select...".

Always end the question naturally with "so I can filter the job."

For example, if the verify field is 'salary', format the question naturally:
- "Can you tell me the salary for the job 'Software Engineer' at 'TechCorp', located in New York, which requires 3 years of experience, so I can filter the job?"

Examples:
- "Can you tell me the company offering a job located in San Francisco, which requires 4 years of experience and offers a salary of $110k, so I can filter the job?"
- "Can you tell me the location of a job titled 'Product Manager', which requires 6 years of experience and offers a salary of $130k, so I can filter the job?"
- "Can you tell me the experience required for the job 'UI Designer' at 'Creative Studio', located in Berlin, so I can filter the job?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

VIEW_JOB_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a job in the view job context (e.g., job title, company, location, experience, salary, job type).

Use natural language only. Do NOT use schema-style field names such as "job_title", "company", "location", "experience", "salary", "job_type" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., job title, company, location, experience required, salary, job type).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "View...", "Open...", or "See...".

Always end the question naturally with "after viewing the job."

For example, if the verify field is 'salary', format the question naturally:
- "Can you tell me the salary for the job 'Software Engineer' at 'TechCorp', located in New York, which requires 3 years of experience and is a full-time role, after viewing the job?"

Examples:
- "Can you tell me the company name offering the job 'Data Scientist', located in San Francisco, which requires 4 years of experience, offers a salary of $110k, after viewing the job?"
- "Can you tell me the location of the job 'Product Manager' at 'BuildIt', which requires 6 years of experience, offers a salary of $130k, and is a full-time role, after viewing the job?"
- "Can you tell me the job type for the job 'UI Designer' at 'Creative Studio', located in Berlin, which requires 2 years of experience and offers a salary of $70k, after viewing the job?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

SAVE_POST_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the poster name in the save post context.

Use natural language only. Do NOT use schema-style field names such as "poster_name", "poster_content" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., poster name, post content).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the poster name.

Do NOT start questions with imperative phrasing like "Save...", "Bookmark...", or "Store...".

Always end the question naturally with "so I can save the post."

For example, format the question naturally like:
- "Can you tell me the poster name of the post that content 'Excited to share my new project!', so I can save the post?"

Examples:
- "Can you tell me the poster name of the post that content 'Loving the sunny weather today!', so I can save the post?"
- "Can you tell me the poster name of the post that content 'Just finished a marathon!', so I can save the post?"
- "Can you tell me the poster name of the post that content 'Learning new skills every day!', so I can save the post?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value (poster name) itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the poster name.
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

HIDE_POST_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the poster name in the hide post context.

Use natural language only. Do NOT use schema-style field names such as "poster_name", "poster_content" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., poster name, post content).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the poster name.

Do NOT start questions with imperative phrasing like "Hide...", "Remove...", or "Block...".

Always end the question naturally with "so I can hide the post."

For example, format the question naturally like:
- "Can you tell me the poster name of the post that content 'Excited to share my new project!', so I can hide the post?"

Examples:
- "Can you tell me the poster name of the post that content 'Loving the sunny weather today!', so I can hide the post?"
- "Can you tell me the poster name of the post that content 'Just finished a marathon!', so I can hide the post?"
- "Can you tell me the poster name of the post that content 'Learning new skills every day!', so I can hide the post?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value (poster name) itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the poster name.
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

EDIT_PROFILE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a user profile in the edit profile context (e.g., name, title, bio).

Use natural language only. Do NOT use schema-style field names such as "name", "title", "bio" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., user name, title, bio).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Edit...", "Update...", or "Change...".

Always end the question naturally with "so I can update the profile."

For example, if the verify field is 'title', format the question naturally:
- "Can you tell me the title of the user 'Alice Johnson', whose bio is 'Frontend developer and tech enthusiast', so I can update the profile?"

Examples:
- "Can you tell me the bio of the user 'John Smith', whose title is 'Project Manager', so I can update the profile?"
- "Can you tell me the title of the user 'Emily Clark', whose bio is 'UX designer and coffee lover', so I can update the profile?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

EDIT_EXPERIENCE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a user experience in the edit experience context (e.g., name, company, experience duration, company location, experience description, experience title).

Use natural language only. Do NOT use schema-style field names such as "name", "company", "experience_duration", "experience_location", "experience_description", "experience_title" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., user name, company, experience duration, location, experience description, experience title).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Edit...", "Update...", or "Change...".

Always end the question naturally with "so I can update the experience."

For example, if the verify field is 'experience title', format the question naturally:
- "Can you tell me the experience title of the user 'Alice Johnson', who works at 'TechCorp', has an experience duration of '3 years', is located in 'New York', and has experience description 'Worked on backend systems', so I can update the experience?"

Examples:
- "Can you tell me the company of the user 'John Smith', whose experience title is 'Data Scientist', has an experience duration of '4 years', is located in 'San Francisco', and has experience description 'Built machine learning models', so I can update the experience?"
- "Can you tell me the experience duration of the user 'Emily Clark', who works at 'Creative Studio', has experience title 'UX Designer', is located in 'London', and has experience description 'Designed user interfaces', so I can update the experience?"
- "Can you tell me the experience location of the user 'Michael Lee', who works at 'CloudNet', has experience title 'DevOps Engineer', has an experience duration of '5 years', and has experience description 'Managed cloud infrastructure', so I can update the experience?"
- "Can you tell me the experience description of the user 'Sophia Brown', who works at 'InnovateX', has experience title 'Product Manager', has an experience duration of '6 years', and is located in 'Berlin', so I can update the experience?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

ADD_EXPERIENCE_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which could be any attribute of a user profile in the add experience context (e.g., name, title, bio).

Use natural language only. Do NOT use schema-style field names such as "name", "title", "bio" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., user name, title, bio).

Include all selected question fields with their values (except the verify field) in the question for identification, then ask naturally for the verify field value.

Do NOT start questions with imperative phrasing like "Add...", "Create...", or "Insert...".

Always end the question naturally with "so I can add the experience."

For example, if the verify field is 'title', format the question naturally:
- "Can you tell me the title of the user 'Alice Johnson', whose bio is 'Frontend developer and tech enthusiast', so I can add the experience?"

Examples:
- "Can you tell me the bio of the user 'John Smith', whose title is 'Project Manager', so I can add the experience?"
- "Can you tell me the title of the user 'Emily Clark', whose bio is 'UX designer and coffee lover', so I can add the experience?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the verify field value.
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

REMOVE_POST_DATA_EXTRACTION_PROMPT_INFO = """
Generate a QUESTION that asks for the value of the verify field, which is the poster name in the remove post context.

Use natural language only. Do NOT use schema-style field names such as "poster_name", "poster_content" or any names with underscores (_).

Always refer to fields using simple phrasing (e.g., poster name, post content).

Include all question fields with their values (except the verify field) in the question for identification, then ask naturally for the poster name.

Do NOT start questions with imperative phrasing like "Remove...", "Delete...", or "Erase...".

Always end the question naturally with "so I can remove the post."

For example, format the question naturally like:
- "Can you tell me the poster name of the post that content 'Excited to share my new project!', so I can remove the post?"

Examples:
- "Can you tell me the poster name of the post that content 'Loving the sunny weather today!', so I can remove the post?"
- "Can you tell me the poster name of the post that content 'Just finished a marathon!', so I can remove the post?"
- "Can you tell me the poster name of the post that content 'Learning new skills every day!', so I can remove the post?"

CRITICAL ANTI-LEAK RULES:
- Never include the verify field value (poster name) itself in the question text.
- Use only selected question fields with their values for identification.
- Do NOT include all visible fields—only the selected question fields with values.

The output must be a single question asking only for the poster name.
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

VIEW_NOTIFICATIONS_USE_CASE = UseCase(
    name="VIEW_NOTIFICATIONS",
    description="User opened the notifications page.",
    event=ViewNotificationsEvent,
    event_source_code=ViewNotificationsEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[{"prompt": "Open my notifications.", "prompt_for_task_generation": "View the notifications page."}],
)

FILTER_NOTIFICATIONS_USE_CASE = UseCase(
    name="FILTER_NOTIFICATIONS",
    description="User changed the notification list filter.",
    event=FilterNotificationsEvent,
    event_source_code=FilterNotificationsEvent.get_source_code_of_class(),
    constraints_generator=generate_filter_notifications_constraints,
    examples=[{"prompt": "Show only unread notifications.", "prompt_for_task_generation": "Filter notifications by unread."}],
)

MARK_NOTIFICATION_READ_USE_CASE = UseCase(
    name="MARK_NOTIFICATION_READ",
    description="User toggled read state on a single notification.",
    event=MarkNotificationReadEvent,
    event_source_code=MarkNotificationReadEvent.get_source_code_of_class(),
    constraints_generator=generate_mark_notification_read_constraints,
    examples=[{"prompt": "Mark this notification as read.", "prompt_for_task_generation": "Mark one notification read."}],
)

MARK_ALL_NOTIFICATIONS_READ_USE_CASE = UseCase(
    name="MARK_ALL_NOTIFICATIONS_READ",
    description="User marked all notifications as read.",
    event=MarkAllNotificationsReadEvent,
    event_source_code=MarkAllNotificationsReadEvent.get_source_code_of_class(),
    constraints_generator=None,
    examples=[{"prompt": "Clear all unread notifications.", "prompt_for_task_generation": "Mark all notifications read."}],
)

DELETE_POST_USE_CASE = UseCase(
    name="DELETE_POST",
    description="User permanently deleted their own post.",
    event=DeletePostEvent,
    event_source_code=DeletePostEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[{"prompt": "Delete my latest post.", "prompt_for_task_generation": "Delete a post I authored."}],
)

DELETE_COMMENT_USE_CASE = UseCase(
    name="DELETE_COMMENT",
    description="User deleted their own comment on a post.",
    event=DeleteCommentEvent,
    event_source_code=DeleteCommentEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[{"prompt": "Remove my comment on this post.", "prompt_for_task_generation": "Delete my comment."}],
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
    VIEW_ALL_RECOMMENDATIONS_USE_CASE,
    FOLLOW_PAGE_USE_CASE,
    UNFOLLOW_PAGE_USE_CASE,
    VIEW_JOB_USE_CASE,
    FILTER_JOBS_USE_CASE,
    BACK_TO_ALL_JOBS_USE_CASE,
    APPLY_FOR_JOB_USE_CASE,
    SEARCH_JOBS_USE_CASE,
    HOME_NAVBAR_USE_CASE,
    JOBS_NAVBAR_USE_CASE,
    VIEW_NOTIFICATIONS_USE_CASE,
    FILTER_NOTIFICATIONS_USE_CASE,
    MARK_NOTIFICATION_READ_USE_CASE,
    MARK_ALL_NOTIFICATIONS_READ_USE_CASE,
    DELETE_POST_USE_CASE,
    DELETE_COMMENT_USE_CASE,
]
