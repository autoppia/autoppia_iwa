from __future__ import annotations

import re
from typing import Any

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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Add a comment to the movie_name that is NOT 'The Godfather' with a content that is NOT 'couldn't look away'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Insert a new film with genres equals 'Thriller'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Login with the username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then add to watchlist a film with rating less equal 5.0 and duration less than 124 minutes long",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/contact?seed=1",
        "prompt": "Fill out the contact form with a name NOT 'Lisa', an email that contains 'in@d', and a subject that does NOT contain 'mwg'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Then, delete your movie.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your movie by setting year to '1966'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your profile: ensure your first_name contains 'mes', your website does NOT contain 'nhl', and your location does NOT contain 'evc'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Take me directly to the interstellar film details page",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Filter for Action movies",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Please login using username equals 'user<web_agent_id>' and password equals 'Passw0rd!'.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Please login using username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then logout.",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Please register using username equals 'newuser<web_agent_id>', email equals 'newuser<web_agent_id>@gmail.com' and password equals 'Passw0rd!'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and remove a movie from watchlist",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Search for the movie 'La La Land'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Share a movie directed by one of 'Ethan Coen', 'Lana Wachowski', 'Fernando Meirelles' that is NOT named 'Schindler's List'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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
        "url": "http://localhost:8000/?seed=1",
        "prompt": "Watch the trailer for a movie with a duration NOT EQUALS '118' minutes that has a rating GREATER EQUAL '5.0'",
        "actions": [
            {
                "url": "http://localhost:8000/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8000/?seed=1",
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


def _normalize_field_name(raw_field: str) -> str:
    field = raw_field.strip().lower().replace(" ", "_")
    aliases = {
        "movie_name": "name",
        "film_name": "name",
    }
    return aliases.get(field, field)


def _parse_value_token(raw_value: str) -> Any:
    value = raw_value.strip().strip(".")
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _maybe_add_operator_criterion(criteria: dict[str, Any], field: str, operator: str, raw_value: str) -> None:
    criteria[_normalize_field_name(field)] = {
        "operator": operator,
        "value": _parse_value_token(raw_value),
    }


def _extract_event_criteria_from_prompt(prompt: str) -> dict[str, Any]:
    # Conservative parser: if prompt looks complex/ambiguous, return empty criteria.
    lowered = prompt.lower()
    tricky_markers = (" one of ", " or ", " either ", " directly ", " then ")
    if any(marker in lowered for marker in tricky_markers):
        return {}

    criteria: dict[str, Any] = {}

    not_equals_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+is\s+not\s+'([^']+)'",
        r"\b([a-zA-Z_ ]+?)\s+not\s+'([^']+)'",
    ]
    contains_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+contains\s+'([^']+)'",
    ]
    not_contains_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+does\s+not\s+contain\s+'([^']+)'",
        r"\b([a-zA-Z_ ]+?)\s+not\s+contain\s+'([^']+)'",
    ]
    equals_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+equals\s+'([^']+)'",
    ]
    less_equal_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+less\s+equal\s+'?([0-9]+(?:\.[0-9]+)?)'?",
        r"\b([a-zA-Z_ ]+?)\s+less\s+than\s+or\s+equal\s+to\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    greater_equal_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+greater\s+equal\s+'?([0-9]+(?:\.[0-9]+)?)'?",
        r"\b([a-zA-Z_ ]+?)\s+greater\s+than\s+or\s+equal\s+to\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    less_than_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+less\s+than\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    greater_than_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+greater\s+than\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]

    for pattern in not_contains_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "not_contains", value)

    for pattern in contains_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "contains", value)

    for pattern in not_equals_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "not_equals", value)

    for pattern in equals_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            criteria[_normalize_field_name(field)] = _parse_value_token(value)

    for pattern in less_equal_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "less_equal", value)

    for pattern in greater_equal_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "greater_equal", value)

    for pattern in less_than_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "less_than", value)

    for pattern in greater_than_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "greater_than", value)

    return criteria


def _build_raw_tests_from_actions(actions_data: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    raw_tests: dict[str, list[dict[str, Any]]] = {}
    for item in actions_data:
        use_case = str(item.get("use_case", "")).strip()
        if not use_case:
            continue
        prompt = str(item.get("prompt", ""))
        criteria = _extract_event_criteria_from_prompt(prompt)
        raw_tests[use_case] = [
            {
                "type": "CheckEventTest",
                "event_name": use_case,
                "event_criteria": criteria,
                "description": "Check if specific event was triggered",
            }
        ]
    return raw_tests


_RAW_TESTS: dict[str, list[dict[str, Any]]] = _build_raw_tests_from_actions(ACTIONS)
_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS.get(use_case, []))


BASE = "http://localhost:8000"
SEED_DEFAULT = 1


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


ADD_COMMENT = _uc(
    "ADD_COMMENT",
    prompt="Add a comment to the movie_name that is NOT 'The Godfather' with a content that is NOT 'couldn't look away'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Insert a new film with genres equals 'Thriller'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Login with the username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and then add to watchlist a film with rating less equal 5.0 and duration less than 124 minutes long",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Fill out the contact form with a name NOT 'Lisa', an email that contains 'in@d', and a subject that does NOT contain 'mwg'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your movie by setting year to '1966'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!'. Edit your profile: ensure your first_name contains 'mes', your website does NOT contain 'nhl', and your location does NOT contain 'evc'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Take me directly to the interstellar film details page",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
        ClickAction(selector=_id("spotlight-view-details-btn-2")),
    ],
)

FILTER_FILM = _uc(
    "FILTER_FILM",
    prompt="Filter for Action movies",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
        ClickAction(selector=_xp("//html/body/header/div/nav/a[2]")),
        ClickAction(selector=_xp("//button[normalize-space()='Action']")),
    ],
)

LOGIN = _uc(
    "LOGIN",
    prompt="Please login using username equals 'user<web_agent_id>' and password equals 'Passw0rd!'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Login with username equals 'user<web_agent_id>' and password equals 'Passw0rd!' and remove a movie from watchlist",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
    prompt="Search for the movie 'La La Land'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
        ClickAction(selector=_id("input")),
        TypeAction(selector=_id("input"), text="La La Land"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

SHARE_MOVIE = _uc(
    "SHARE_MOVIE",
    prompt="Share a movie directed by one of 'Ethan Coen', 'Lana Wachowski', 'Fernando Meirelles' that is NOT named 'Schindler's List'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
        ClickAction(selector=_id("input")),
        TypeAction(selector=_id("input"), text="ethan Coen"),
        ClickAction(selector=_id("search-submit-button")),
        ClickAction(selector=_id("view-details-button")),
        ClickAction(selector=_id("share-button")),
    ],
)

WATCH_TRAILER = _uc(
    "WATCH_TRAILER",
    prompt="Watch the trailer for a movie with a duration NOT EQUALS '118' minutes that has a rating GREATER EQUAL '5.0'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DEFAULT}"),
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
