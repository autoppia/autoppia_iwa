from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventEmittedTest, CheckPageViewEventTest, FindInHtmlTest
from autoppia_iwa.src.web_agents.classes import Task

TASK_EXAMPLES = [
    Task(
        id='5bd668de-8c2e-4c53-9a72-6037cbdfb9a0',
        prompt="Fill in the email and password fields in the login form and click the 'Log in' button to attempt logging into the website.",
        url='http://localhost:8000/',
        specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
        tests=[
            CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='login'),
            CheckPageViewEventTest(description='Check if the backend logged a page view event for the specified URL', test_type='backend', page_view_url='/login'),
        ],
        relevant_data={'Authorization': {'email': 'admin@jobsapp.com', 'password': 'admin123'}},
        milestones=None,
        web_analysis=None,
        html='',
        screenshot=None,
        is_web_real=False,
    ),
    Task(
        id='002c8e40-226b-412f-a987-26599b74ae41',
        prompt="Click on the 'About Us' link in the navigation menu to view the company's mission, vision, and team information.",
        url='http://localhost:8000/',
        specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
        tests=[
            FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['about us', 'mission', 'vision', 'team']),
            CheckPageViewEventTest(description='Check if the backend logged a page view event for the specified URL', test_type='backend', page_view_url='/about/'),
        ],
        relevant_data={'Authorization': {'email': 'admin@jobsapp.com', 'password': 'admin123'}},
        milestones=None,
        web_analysis=None,
        html='',
        screenshot=None,
        is_web_real=False,
    ),
    # Task(
    #     id='a64ad524-5f79-4dbf-ae1c-9bfbb9d25a25',
    #     prompt='Fill out the job search form by entering a desired position and location, then click the search button to find relevant job listings.',
    #     url='http://localhost:8000/',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='search'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['job search', 'position', 'location', 'featured jobs', 'trending jobs']),
    #         CheckPageViewEventTest(description='Check if the backend logged a page view event for the specified URL', test_type='backend', page_view_url='/search')
    #     ],
    #     relevant_data={
    #         'Authorization': {
    #             'email': 'admin@jobsapp.com',
    #             'password': 'admin123'
    #         }
    #     },
    #     milestones=None,
    #     web_analysis=None,
    #     html='',
    #     screenshot=None,
    #     is_web_real=False
    # ),
    # Task(
    #     id='3852baf6-8f48-46e7-ac97-621a4b8080fa',
    #     prompt="Fill out the contact form by entering your name, email, and message, then click the 'Submit' button to send your message.",
    #     url='http://localhost:8000/',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='message_sent'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['contact us', 'send us a message', 'your name', 'your email', 'your message', 'submit']),
    #         CheckPageViewEventTest(description='Check if the backend logged a page view event for the specified URL', test_type='backend', page_view_url='/contact/')
    #     ],
    #     relevant_data={
    #         'Authorization': {
    #             'email': 'admin@jobsapp.com',
    #             'password': 'admin123'
    #         }
    #     },
    #     milestones=None,
    #     web_analysis=None,
    #     html='',
    #     screenshot=None,
    #     is_web_real=False
    # ),
    # Task(
    #     id='0c9ed488-a266-453d-b4ad-4eb69c3aae8d',
    #     prompt="Fill out the registration form by entering your company name, address, email, and password, then click the 'Register' button to create a new account.",
    #     url='http://localhost:8000/',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['thank you', 'registration successful', 'welcome aboard']),
    #         CheckPageViewEventTest(description='Check if the backend logged a page view event for the specified URL', test_type='backend', page_view_url='/employer/register')
    #     ],
    #     relevant_data={
    #         'Authorization': {
    #             'email': 'admin@jobsapp.com',
    #             'password': 'admin123'
    #         }
    #     },
    #     milestones=None,
    #     web_analysis=None,
    #     html='',
    #     screenshot=None,
    #     is_web_real=False
    # ),
    # Task(
    #     id='899bb79c-51c4-4ed9-b54a-a1aadbc7f0c3',
    #     prompt="Fill out the registration form by entering your first name, last name, email, password, confirming the password, selecting your gender, and then click the 'Register' button to create a new account.",
    #     url='http://localhost:8000/',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='registration'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['account', 'new user', 'customer service']),
    #         CheckPageViewEventTest(description='Check if the backend logged a page view event for the specified URL', test_type='backend', page_view_url='/employee/register')
    #     ],
    #     relevant_data={
    #         'Authorization': {
    #             'email': 'admin@jobsapp.com',
    #             'password': 'admin123'
    #         }
    #     },
    #     milestones=None,
    #     web_analysis=None,
    #     html='',
    #     screenshot=None,
    #     is_web_real=False
    # ),
    # Task(
    #     id='6af822df-ea37-42ba-963d-784916791d67',
    #     prompt='Fill out the job search form by entering a profession and location, then click the search button to find relevant job listings.',
    #     url='http://localhost:8000/',
    #     specifications=BrowserSpecification(viewport_width=1920, viewport_height=1080, screen_width=1920, screen_height=1080, device_pixel_ratio=1.0, scroll_x=0, scroll_y=0, browser_x=0, browser_y=0),
    #     tests=[
    #         CheckEventEmittedTest(description='Verify if the backend emitted the specified event', test_type='backend', event_name='search'),
    #         FindInHtmlTest(description='Find keywords in the current HTML content', test_type='frontend', keywords=['job search', 'profession', 'location', 'find jobs'])
    #     ],
    #     relevant_data={
    #         'Authorization': {
    #             'email': 'admin@jobsapp.com',
    #             'password': 'admin123'
    #         }
    #     },
    #     milestones=None,
    #     web_analysis=None,
    #     html='',
    #     screenshot=None,
    #     is_web_real=False
    # )
]
