from __future__ import annotations

PROJECT_NUMBER = 1
WEB_PROJECT_ID = "autocinema"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    NavigateAction,
    SendKeysIWAAction,
    TypeAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

ACTIONS = [
    {
        "url": "http://localhost:8000/?seed=58",
        "prompt": "Add a comment to the movie_name that is NOT 'The Godfather' with a content that is NOT 'couldn't look away'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=58",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=58",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "featured-movie-view-details-btn-2",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "featured-movie-view-details-btn-2",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "comment-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "comment-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Agent",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "comment-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Agent",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "comment-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "comment-message-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "comment-message-textarea",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "good movie",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "comment-message-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "good movie",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "comment-message-textarea",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "share-feedback-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "share-feedback-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "ADD_COMMENT",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=287",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Insert a new film with genres equals 'Thriller'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=287",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=287",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "user<web_agent_id>",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "user<web_agent_id>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Passw0rd!",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Passw0rd!",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[normalize-space()='Add Movies']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//button[normalize-space()='Add Movies']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[normalize-space()='Adventure']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//button[normalize-space()='Adventure']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "save-changes-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "save-changes-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "ADD_FILM",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=375",
        "prompt": "Login with the username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then add to watchlist a film with rating less equal 5.0 and duration less than 124 minutes long",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=375",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=375",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-username-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-username-input"]',
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "user<web_agent_id>",
                "type": "TypeAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-username-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "user<web_agent_id>",
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-username-input"]',
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-password-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-password-input"]',
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Passw0rd!",
                "type": "TypeAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-password-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Passw0rd!",
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-password-input"]',
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "featured-movie-view-details-btn",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "featured-movie-view-details-btn",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "watchlist-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "watchlist-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "ADD_TO_WATCHLIST",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/contact?seed=507",
        "prompt": "Fill out the contact form with a name NOT 'Lisa', an email that contains 'in@d', and a subject that does NOT contain 'mwg'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=507",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=507",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[4]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[4]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Javier Test",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Javier Test",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-email-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-email-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "javier.test@example.com",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-email-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "javier.test@example.com",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-email-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-subject-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-subject-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Hello from trajectory",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-subject-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Hello from trajectory",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-subject-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-message-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-message-textarea",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Please help with movie recommendations.",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-message-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Please help with movie recommendations.",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "contact-message-textarea",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "send-message-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "send-message-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "CONTACT",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=488",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Then, delete your movie.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=488",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=488",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "user<web_agent_id>",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "user<web_agent_id>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Passw0rd!",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Passw0rd!",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[normalize-space()='Edit Movies']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//button[normalize-space()='Edit Movies']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "delete-movie-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "delete-movie-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "DELETE_FILM",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=566",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your movie by setting year to '1966'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=566",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=566",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "user<web_agent_id>",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "user<web_agent_id>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Passw0rd!",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Passw0rd!",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[normalize-space()='Edit Movies']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//button[normalize-space()='Edit Movies']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(), 'Year')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(), 'Year')]/input)[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "1966",
                "type": "TypeAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(), 'Year')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "1966",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(), 'Year')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "save-changes-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "save-changes-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "EDIT_FILM",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=889",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your profile: ensure your first_name contains 'mes', your website does NOT contain 'nhl', and your location does NOT contain 'evc'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=889",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=889",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "user<web_agent_id>",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "user<web_agent_id>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Passw0rd!",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Passw0rd!",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-last-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-last-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Alexander",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-last-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Alexander",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-last-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-bio-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-bio-textarea",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "cinema lover",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-bio-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "cinema lover",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-bio-textarea",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-website-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-website-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "https://example.org",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-website-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "https://example.org",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-website-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "save-profile-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "save-profile-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "EDIT_USER",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=518",
        "prompt": "Take me directly to the interstellar film details page",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=518",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=518",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "spotlight-view-details-btn-2",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "FILM_DETAIL",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=732",
        "prompt": "Filter for Action movies",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=732",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=732",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[2]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[2]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[normalize-space()='Action']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//button[normalize-space()='Action']",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "FILTER_FILM",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=321",
        "prompt": "Please login using username equals 'user<web_agent_id>' and password equals 'Passw0rd!'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=321",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=321",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "javier",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "javier",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "123456",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "123456",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "LOGIN",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=364",
        "prompt": "Please login using username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then logout.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=364",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=364",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "AGENTE",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "AGENTE",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Passw0rd!",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Passw0rd!",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/button",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/button",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "LOGOUT",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=807",
        "prompt": "Please register using username equals 'newuser<web_agent_id>', email equals 'newuser<web_agent_id>@gmail.com' and password equals 'Passw0rd!'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=807",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=807",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[5]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[5]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "javier",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "javier",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-email-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-email-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "javi@gmail.com",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-email-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "javi@gmail.com",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-email-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "123456",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "123456",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-confirm-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-confirm-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "123456",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "register-confirm-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "123456",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "register-confirm-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "create-account-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "create-account-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "REGISTRATION",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=396",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and remove a movie from watchlist",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=396",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=396",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[6]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[6]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-username-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-username-input"]',
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "user<web_agent_id>",
                "type": "TypeAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-username-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "user<web_agent_id>",
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-username-input"]',
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-password-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-password-input"]',
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "Passw0rd!",
                "type": "TypeAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="login-password-input"]',
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Passw0rd!",
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="login-password-input"]',
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-sign-in-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-sign-in-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//html/body/header/div/nav/a[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//html/body/header/div/nav/a[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "featured-movie-view-details-btn",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "featured-movie-view-details-btn",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "watchlist-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "watchlist-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "watchlist-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "watchlist-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "REMOVE_FROM_WATCHLIST",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=757",
        "prompt": "Search for the movie 'La La Land'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=757",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=757",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "La La Land",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "La La Land",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "SendKeysAction",
                "keys": ["Enter"],
                "attributes": {"keys": ["Enter"]},
            },
        ],
        "use_case": "SEARCH_FILM",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=767",
        "prompt": "Share a movie directed by one of 'Ethan Coen', 'Lana Wachowski', 'Fernando Meirelles' that is NOT named 'Schindler's List'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=767",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=767",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "text": "ethan Coen",
                "type": "TypeAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "ethan Coen",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "search-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "view-details-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "view-details-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "share-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "share-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "SHARE_MOVIE",
        "has_success": True,
    },
    {
        "url": "http://localhost:8000/?seed=523",
        "prompt": "Watch the trailer for a movie with a duration NOT EQUALS '118' minutes that has a rating GREATER EQUAL '5.0'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=523",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=523",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "featured-movie-view-details-btn",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "featured-movie-view-details-btn",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "watch-trailer-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "watch-trailer-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": '//*[@id="movie_player"]/div[1]/video',
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": '//*[@id="movie_player"]/div[1]/video',
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "WATCH_TRAILER",
        "has_success": True,
    },
]

# CheckEventTest payloads aligned with former autocinema_tasks.json (per use_case.name).
_RAW_TESTS: dict[str, list[dict]] = {
    "FILM_DETAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "FILM_DETAIL",
            "event_criteria": {
                "year": {"operator": "less_than", "value": 2025},
                "name": {"operator": "contains", "value": "ok"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "LOGIN": [
        {
            "type": "CheckEventTest",
            "event_name": "LOGIN",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "DELETE_FILM": [
        {
            "type": "CheckEventTest",
            "event_name": "DELETE_FILM",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "LOGOUT": [
        {
            "type": "CheckEventTest",
            "event_name": "LOGOUT",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "FILTER_FILM": [
        {
            "type": "CheckEventTest",
            "event_name": "FILTER_FILM",
            "event_criteria": {"genre_name": "Crime"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_FILM": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_FILM",
            "event_criteria": {"query": {"operator": "not_equals", "value": "1917"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "CONTACT": [
        {
            "type": "CheckEventTest",
            "event_name": "CONTACT",
            "event_criteria": {
                "name": {"operator": "contains", "value": "Pete"},
                "message": {"operator": "not_contains", "value": "enu"},
                "subject": "Support",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "REGISTRATION": [
        {
            "type": "CheckEventTest",
            "event_name": "REGISTRATION",
            "event_criteria": {
                "username": "newuser<web_agent_id>",
                "email": "newuser<web_agent_id>@gmail.com",
                "password": "Passw0rd!",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_COMMENT": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_COMMENT",
            "event_criteria": {
                "movie_name": "Her",
                "content": {"operator": "not_equals", "value": "brilliant"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_FILM": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_FILM",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
                "movie_rating": 5.8,
                "name": "The Lost Daughter",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_FILM": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_FILM",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
                "director": "Anthony Russo",
                "genres": "Action",
                "cast": {"operator": "not_contains", "value": "lzl"},
                "rating": {"operator": "greater_equal", "value": 5.0},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_USER": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_USER",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
                "first_name": "Benjamin",
                "bio": {"operator": "contains", "value": "films"},
                "website": {"operator": "not_equals", "value": "https://moviereviews.example.net"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_TO_WATCHLIST": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_WATCHLIST",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
                "year": {"operator": "greater_than", "value": 1955},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "REMOVE_FROM_WATCHLIST": [
        {
            "type": "CheckEventTest",
            "event_name": "REMOVE_FROM_WATCHLIST",
            "event_criteria": {
                "username": "user<web_agent_id>",
                "password": "Passw0rd!",
                "genres": {"operator": "not_contains", "value": "Comedy"},
                "rating": {"operator": "greater_equal", "value": 5.0},
                "name": {"operator": "not_contains", "value": "cwz"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "SHARE_MOVIE": [
        {
            "type": "CheckEventTest",
            "event_name": "SHARE_MOVIE",
            "event_criteria": {"name": "Spider-Man: No Way Home"},
            "description": "Check if specific event was triggered",
        }
    ],
    "WATCH_TRAILER": [
        {
            "type": "CheckEventTest",
            "event_name": "WATCH_TRAILER",
            "event_criteria": {"name": {"operator": "not_contains", "value": "odm"}},
            "description": "Check if specific event was triggered",
        }
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


BASE = "http://localhost:8000"
# From autocinema_tasks.json (?seed= in each task URL)
SEED_FILM_DETAIL = 518
SEED_LOGIN = 321
SEED_DELETE_FILM = 488
SEED_LOGOUT = 364
SEED_FILTER_FILM = 732
SEED_SEARCH_FILM = 757
SEED_CONTACT = 507
SEED_REGISTRATION = 807
SEED_ADD_COMMENT = 58
SEED_EDIT_FILM = 566
SEED_ADD_FILM = 287
SEED_EDIT_USER = 889
SEED_ADD_TO_WATCHLIST = 375
SEED_REMOVE_FROM_WATCHLIST = 396
SEED_SHARE_MOVIE = 767
SEED_WATCH_TRAILER = 523


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


ADD_COMMENT = _uc(
    "ADD_COMMENT",
    prompt="Add a comment to the movie_name 'Her' with content that does NOT equal 'brilliant'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_COMMENT}"),
        ClickAction(selector=_id("featured-movie-view-details-btn-2")),
        ClickAction(selector=_id("comment-name-input")),
        TypeAction(selector=_id("comment-name-input"), text="Agent"),
        ClickAction(selector=_id("comment-message-textarea")),
        TypeAction(selector=_id("comment-message-textarea"), text="good movie"),
        ClickAction(selector=_id("share-feedback-button")),
    ],
)

ADD_FILM = _uc(
    "ADD_FILM",
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Register a movie directed by 'Anthony Russo' with genre equals 'Action', ensuring the cast does NOT contain 'lzl' and the rating is greater equal 5.0.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_FILM}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_id("login-username-input")),
        TypeAction(selector=_id("login-username-input"), text="user<web_agent_id>"),
        ClickAction(selector=_id("login-password-input")),
        TypeAction(selector=_id("login-password-input"), text="Passw0rd!"),
        ClickAction(selector=_id("login-sign-in-button")),
        ClickAction(selector=_xp("//button[normalize-space()='Add Movies']")),
        ClickAction(selector=_xp("//button[normalize-space()='Adventure']")),
        ClickAction(selector=_id("save-changes-button")),
    ],
)

ADD_TO_WATCHLIST = _uc(
    "ADD_TO_WATCHLIST",
    prompt="Login with the username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then add to watchlist a movie from year greater than '1955'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_TO_WATCHLIST}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_xp('//*[@id="login-username-input"]')),
        TypeAction(selector=_xp('//*[@id="login-username-input"]'), text="user<web_agent_id>"),
        ClickAction(selector=_xp('//*[@id="login-password-input"]')),
        TypeAction(selector=_xp('//*[@id="login-password-input"]'), text="Passw0rd!"),
        ClickAction(selector=_id("login-sign-in-button")),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[1]")),
        ClickAction(selector=_id("featured-movie-view-details-btn")),
        ClickAction(selector=_id("watchlist-button")),
    ],
)

CONTACT = _uc(
    "CONTACT",
    prompt="Fill out the contact form with a name that contains 'Pete', a message that does NOT contain 'enu', and a subject that equals 'Support'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CONTACT}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[4]")),
        ClickAction(selector=_id("contact-name-input")),
        TypeAction(selector=_id("contact-name-input"), text="Javier Test"),
        ClickAction(selector=_id("contact-email-input")),
        TypeAction(selector=_id("contact-email-input"), text="javier.test@example.com"),
        ClickAction(selector=_id("contact-subject-input")),
        TypeAction(selector=_id("contact-subject-input"), text="Hello from trajectory"),
        ClickAction(selector=_id("contact-message-textarea")),
        TypeAction(selector=_id("contact-message-textarea"), text="Please help with movie recommendations."),
        ClickAction(selector=_id("send-message-button")),
    ],
)

DELETE_FILM = _uc(
    "DELETE_FILM",
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Then, delete your movie.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DELETE_FILM}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_id("login-username-input")),
        TypeAction(selector=_id("login-username-input"), text="user<web_agent_id>"),
        ClickAction(selector=_id("login-password-input")),
        TypeAction(selector=_id("login-password-input"), text="Passw0rd!"),
        ClickAction(selector=_id("login-sign-in-button")),
        ClickAction(selector=_xp("//button[normalize-space()='Edit Movies']")),
        ClickAction(selector=_id("delete-movie-button")),
    ],
)

EDIT_FILM = _uc(
    "EDIT_FILM",
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your movie by setting year to 2021, duration to 120, and rating to 5.8.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_FILM}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_id("login-username-input")),
        TypeAction(selector=_id("login-username-input"), text="user<web_agent_id>"),
        ClickAction(selector=_id("login-password-input")),
        TypeAction(selector=_id("login-password-input"), text="Passw0rd!"),
        ClickAction(selector=_id("login-sign-in-button")),
        ClickAction(selector=_xp("//button[normalize-space()='Edit Movies']")),
        ClickAction(selector=_xp("(//label[contains(normalize-space(), 'Year')]/input)[1]")),
        TypeAction(selector=_xp("(//label[contains(normalize-space(), 'Year')]/input)[1]"), text="1966"),
        ClickAction(selector=_id("save-changes-button")),
    ],
)

EDIT_USER = _uc(
    "EDIT_USER",
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your profile: ensure your first_name equals 'Benjamin', your bio contains 'films', and your website not equals 'https://moviereviews.example.net'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_USER}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_id("login-username-input")),
        TypeAction(selector=_id("login-username-input"), text="user<web_agent_id>"),
        ClickAction(selector=_id("login-password-input")),
        TypeAction(selector=_id("login-password-input"), text="Passw0rd!"),
        ClickAction(selector=_id("login-sign-in-button")),
        ClickAction(selector=_id("profile-last-name-input")),
        TypeAction(selector=_id("profile-last-name-input"), text="Alexander"),
        ClickAction(selector=_id("profile-bio-textarea")),
        TypeAction(selector=_id("profile-bio-textarea"), text="cinema lover"),
        ClickAction(selector=_id("profile-website-input")),
        TypeAction(selector=_id("profile-website-input"), text="https://example.org"),
        ClickAction(selector=_id("save-profile-button")),
    ],
)

FILM_DETAIL = _uc(
    "FILM_DETAIL",
    prompt="Navigate to a movie page where the name CONTAINS 'ok' and the year is LESS THAN '2025'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_FILM_DETAIL}"),
        ClickAction(selector=_id("spotlight-view-details-btn-2")),
    ],
)

FILTER_FILM = _uc(
    "FILTER_FILM",
    prompt="Filter films where the genre_name equals 'Crime'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_FILTER_FILM}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[2]")),
        ClickAction(selector=_xp("//button[normalize-space()='Action']")),
    ],
)

LOGIN = _uc(
    "LOGIN",
    prompt="Please log in using username equals 'user<web_agent_id>' and password equals 'Passw0rd!'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_LOGIN}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_id("login-username-input")),
        TypeAction(selector=_id("login-username-input"), text="javier"),
        ClickAction(selector=_id("login-password-input")),
        TypeAction(selector=_id("login-password-input"), text="123456"),
        ClickAction(selector=_id("login-sign-in-button")),
    ],
)

LOGOUT = _uc(
    "LOGOUT",
    prompt="Please login using username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then logout.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_LOGOUT}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_id("login-username-input")),
        TypeAction(selector=_id("login-username-input"), text="AGENTE"),
        ClickAction(selector=_id("login-password-input")),
        TypeAction(selector=_id("login-password-input"), text="Passw0rd!"),
        ClickAction(selector=_id("login-sign-in-button")),
        ClickAction(selector=_xp("//html/body/header/div/nav/button")),
    ],
)

REGISTRATION = _uc(
    "REGISTRATION",
    prompt="Please register using username equals 'newuser<web_agent_id>', email equals 'newuser<web_agent_id>@gmail.com' and password equals 'Passw0rd!'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_REGISTRATION}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[5]")),
        ClickAction(selector=_id("register-username-input")),
        TypeAction(selector=_id("register-username-input"), text="javier"),
        ClickAction(selector=_id("register-email-input")),
        TypeAction(selector=_id("register-email-input"), text="javi@gmail.com"),
        ClickAction(selector=_id("register-password-input")),
        TypeAction(selector=_id("register-password-input"), text="123456"),
        ClickAction(selector=_id("register-confirm-password-input")),
        TypeAction(selector=_id("register-confirm-password-input"), text="123456"),
        ClickAction(selector=_id("create-account-button")),
    ],
)

REMOVE_FROM_WATCHLIST = _uc(
    "REMOVE_FROM_WATCHLIST",
    prompt="Login with the username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then remove from watchlist a movie that does NOT contain the genre 'Comedy' and has a rating GREATER THAN or EQUAL to '5.0' and does NOT contain 'cwz'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_REMOVE_FROM_WATCHLIST}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[6]")),
        ClickAction(selector=_xp('//*[@id="login-username-input"]')),
        TypeAction(selector=_xp('//*[@id="login-username-input"]'), text="user<web_agent_id>"),
        ClickAction(selector=_xp('//*[@id="login-password-input"]')),
        TypeAction(selector=_xp('//*[@id="login-password-input"]'), text="Passw0rd!"),
        ClickAction(selector=_id("login-sign-in-button")),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[1]")),
        ClickAction(selector=_id("featured-movie-view-details-btn")),
        ClickAction(selector=_id("watchlist-button")),
        ClickAction(selector=_id("watchlist-button")),
    ],
)

SEARCH_FILM = _uc(
    "SEARCH_FILM",
    prompt="Search for a movie where the query is NOT '1917'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SEARCH_FILM}"),
        ClickAction(selector=_id("input")),
        TypeAction(selector=_id("input"), text="La La Land"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

SHARE_MOVIE = _uc(
    "SHARE_MOVIE",
    prompt="Share details for a movie where the name equals 'Spider-Man: No Way Home'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SHARE_MOVIE}"),
        ClickAction(selector=_id("input")),
        TypeAction(selector=_id("input"), text="ethan Coen"),
        ClickAction(selector=_id("search-submit-button")),
        ClickAction(selector=_id("view-details-button")),
        ClickAction(selector=_id("share-button")),
    ],
)

WATCH_TRAILER = _uc(
    "WATCH_TRAILER",
    prompt="Watch the trailer for a movie where the name does NOT contain 'odm'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_WATCH_TRAILER}"),
        ClickAction(selector=_id("featured-movie-view-details-btn")),
        ClickAction(selector=_id("watch-trailer-button")),
        ClickAction(selector=_xp('//*[@id="movie_player"]/div[1]/video')),
    ],
)


def load_autocinema_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "ADD_COMMENT": ADD_COMMENT,
        "ADD_FILM": ADD_FILM,
        "ADD_TO_WATCHLIST": ADD_TO_WATCHLIST,
        "CONTACT": CONTACT,
        "DELETE_FILM": DELETE_FILM,
        "EDIT_FILM": EDIT_FILM,
        "EDIT_USER": EDIT_USER,
        "FILM_DETAIL": FILM_DETAIL,
        "FILTER_FILM": FILTER_FILM,
        "LOGIN": LOGIN,
        "LOGOUT": LOGOUT,
        "REGISTRATION": REGISTRATION,
        "REMOVE_FROM_WATCHLIST": REMOVE_FROM_WATCHLIST,
        "SEARCH_FILM": SEARCH_FILM,
        "SHARE_MOVIE": SHARE_MOVIE,
        "WATCH_TRAILER": WATCH_TRAILER,
    }
