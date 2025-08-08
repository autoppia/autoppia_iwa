# from autoppia_iwa.src.demo_webs.projects.operators import NOT_EQUALS, CONTAINS, NOT_CONTAINS
from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS

JOBS = [
    {
        "title": "Build front-end of e-commerce website",
        "status": "In progress",
        "start": "Mar 26",
        "activity": "last active yesterday on Time logged this week: 36:00 hrs ($576)",
        "time": "36:00 hrs ($576)",
        "timestr": "Time logged this week:",
        "active": True,
    },
    {
        "title": "Develop mobile app for social networking",
        "status": "Pending",
        "start": "Mar 27",
        "activity": "last active 3 days ago on Initial project setup",
        "time": "0:00 hrs ($0)",
        "timestr": "Time logged this week:",
        "active": False,
    },
    {
        "title": "Create backend API for payment processing",
        "status": "Completed",
        "start": "Mar 20",
        "activity": "last active 1 week ago on Deployed to production",
        "time": "120:00 hrs ($1920)",
        "timestr": "Total time logged:",
        "active": False,
    },
    {
        "title": "Design UI/UX for a fintech application",
        "status": "In review",
        "start": "Mar 22",
        "activity": "last active 2 days ago on Submitted final designs for review",
        "time": "42:00 hrs ($672)",
        "timestr": "Time logged this week:",
        "active": False,
    },
]
HIRES = [
    {
        "name": "Brian K.",
        "country": "Colombia",
        "rate": "$15.00/hr",
        "rating": 4.5,
        "jobs": 120,
        "role": "Full Stack Developer",
        "avatar": "https://ext.same-assets.com/1836270417/1435009301.png",
        "rehire": True,
    },
    {
        "name": "Carol A.",
        "country": "Spain",
        "rate": "$40.00/hr",
        "rating": 4.8,
        "jobs": 95,
        "role": "UI/UX Designer",
        "avatar": "https://ext.same-assets.com/1836270417/1791229698.png",
        "rehire": True,
    },
    {
        "name": "Charles D.",
        "country": "China",
        "rate": "$60.00/hr",
        "rating": 4.7,
        "jobs": 110,
        "role": "Data Scientist",
        "avatar": "https://ext.same-assets.com/1836270417/1118120895.png",
        "rehire": True,
    },
    {
        "name": "Chris O.",
        "country": "Morocco",
        "rate": "$70.00/hr",
        "rating": 4.9,
        "jobs": 80,
        "role": "Blockchain Expert",
        "avatar": "https://ext.same-assets.com/1836270417/3108172840.png",
        "rehire": True,
    },
]
EXPERTS = [
    {
        "name": "Alexa R.",
        "country": "United States",
        "role": "Full Stack Developer",
        "avatar": "https://ext.same-assets.com/1836270417/271536834.png",
        "rate": "$50.00/hr",
        "rating": 4.5,
        "jobs": 120,
        "consultation": "$100 per hour",
        "desc": "Available for web development projects",
    },
    {
        "name": "Angela W.",
        "country": "Spain",
        "role": "UI/UX Designer",
        "avatar": "https://ext.same-assets.com/1836270417/3930451942.png",
        "rate": "$40.00/hr",
        "rating": 4.8,
        "jobs": 95,
        "consultation": "$90 per hour",
        "desc": "Specializing in user experience design",
    },
    {
        "name": "Ashley C.",
        "country": "China",
        "role": "Data Scientist",
        "avatar": "https://ext.same-assets.com/1836270417/2621635319.png",
        "rate": "$60.00/hr",
        "rating": 4.7,
        "jobs": 110,
        "consultation": "$120 per hour",
        "desc": "Data analysis and machine learning projects",
    },
    {
        "name": "Brandon M.",
        "country": "Morocco",
        "role": "Blockchain Expert",
        "avatar": "https://ext.same-assets.com/1836270417/281053763.png",
        "rate": "$70.00/hr",
        "rating": 4.9,
        "jobs": 80,
        "consultation": "$150 per hour",
        "desc": "Blockchain development and consultation",
    },
]

EXPERTS_IN_WORK = [
    {
        "slug": "alexa-r",
        "name": "Alexa R.",
        "country": "Mosquera, Colombia",
        "role": "Full-stack developer",
        "avatar": "https://ext.same-assets.com/1836270417/271536834.png",
        "stats": {"earnings": "$2k+", "jobs": 4, "hours": 100},
        "about": (
            "I'm a full-stack developer with 4 years of experience in web development. "
            "I have a passion for learning and sharing my knowledge with others as publicly as possible. "
            "I write articles, speak at conferences, and host workshops. I'm a big fan of JavaScript and love "
            "building scalable and maintainable web applications."
        ),
        "hoursPerWeek": "More than 30 hrs/week",
        "languages": ["English: Conversational", "Spanish: Native or Bilingual"],
        "lastReview": {
            "title": "Squarespace Designer to create new company website",
            "stars": 5,
            "text": "Great communication! Always takes the initiative on features to add that would improve the website quality.",
            "price": "$500",
            "rate": "$50/hr",
            "time": "10 hours",
            "dates": "Jun 16, 2024 - Jun 17, 2024",
        },
    },
    {
        "slug": "ashley-c",
        "name": "Ashley C.",
        "country": "USA",
        "role": "Backend Developer",
        "avatar": "https://randomuser.me/api/portraits/women/32.jpg",
        "stats": {"earnings": "$1k+", "jobs": 3, "hours": 90},
        "about": "Backend specialist with a focus on scalable systems and great team communication.",
        "hoursPerWeek": "30 hrs/week",
        "languages": ["English: Fluent"],
        "lastReview": {
            "title": "Great collaborator!",
            "stars": 5,
            "text": "Ashley was amazing to work with.",
            "price": "$250",
            "rate": "$35/hr",
            "time": "8 hours",
            "dates": "Jun 1, 2025 - Jun 5, 2025",
        },
    },
    {
        "slug": "angela-w",
        "name": "Angela W.",
        "country": "Spain",
        "role": "UI/UX Designer",
        "avatar": "https://ext.same-assets.com/1836270417/3930451942.png",
        "stats": {"earnings": "$4k+", "jobs": 95, "hours": 300},
        "about": (
            "Experienced UI/UX designer with a focus on crafting user-centered digital experiences. "
            "I help businesses create beautiful and usable interfaces. Passionate about accessibility, "
            "responsive design, and Figma prototyping."
        ),
        "hoursPerWeek": "20-30 hrs/week",
        "languages": ["English: Fluent", "Spanish: Native"],
        "lastReview": {
            "title": "Figma design for mobile app",
            "stars": 5,
            "text": "Angela delivered high-quality designs and quickly understood the product vision.",
            "price": "$720",
            "rate": "$40/hr",
            "time": "18 hours",
            "dates": "May 3, 2025 - May 10, 2025",
        },
    },
    {
        "slug": "brandon-m",
        "name": "Brandon M.",
        "country": "Morocco",
        "role": "Blockchain Expert",
        "avatar": "https://ext.same-assets.com/1836270417/281053763.png",
        "stats": {"earnings": "$6k+", "jobs": 80, "hours": 200},
        "about": ("Blockchain expert specializing in decentralized applications, smart contracts, and Ethereum. I work with startups and enterprises to build secure blockchain-based solutions."),
        "hoursPerWeek": "30+ hrs/week",
        "languages": ["English: Fluent", "Arabic: Native", "French: Conversational"],
        "lastReview": {
            "title": "Smart contract development for NFT project",
            "stars": 5,
            "text": "Very professional, delivered everything ahead of schedule with clean Solidity code.",
            "price": "$1,000",
            "rate": "$70/hr",
            "time": "15 hours",
            "dates": "Apr 20, 2025 - Apr 25, 2025",
        },
    },
]


EXPERTS_IN_WORK_MODIFIED = []
for data in EXPERTS_IN_WORK:
    new_data = data.copy()
    if data.get("lastReview") and isinstance(data["lastReview"], dict):
        for k, v in data["lastReview"].items():
            new_data["lastReview" + k.title()] = v
    EXPERTS_IN_WORK_MODIFIED.append(new_data)


FIELD_OPERATORS_MAP_USER_BOOK_CONSULTANT = {
    "country": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "expertName": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "jobs": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "rate": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "rating": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "role": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}

FIELD_OPERATORS_MAP_HIRE_BUTTON = {
    "country": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "expertName": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "expertSlug": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "role": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}

FIELD_OPERATORS_MAP_HIRING_TEAM = {
    "expertName": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "expertSlug": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
    "team": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}

FIELD_OPERATORS_MAP_HIRING_CONSULTANT = {
    "country": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "expertName": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
    "expertSlug": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
    "increaseHowMuch": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
    "increaseWhen": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
    "paymentType": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
    "role": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
    "rate": [EQUALS, NOT_EQUALS, CONTAINS, CONTAINS],
}
