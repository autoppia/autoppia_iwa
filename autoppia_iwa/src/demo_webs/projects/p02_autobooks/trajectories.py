from __future__ import annotations

PROJECT_NUMBER = 2
WEB_PROJECT_ID = "autobooks"

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
        "url": "http://localhost:8001/?seed=802",
        "prompt": "Register with username, email and password placeholders.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=802",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=802",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Register']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Register']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SIGNUP_USERNAME__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SIGNUP_USERNAME__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "signup-email-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "signup-email-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SIGNUP_EMAIL__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "signup-email-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SIGNUP_EMAIL__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "signup-email-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SIGNUP_PASSWORD__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SIGNUP_PASSWORD__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "confirm-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "confirm-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SIGNUP_PASSWORD__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "confirm-password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SIGNUP_PASSWORD__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "confirm-password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "signup-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "signup-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "REGISTRATION_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=569",
        "prompt": "Look for the book 'Lolita'",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=569",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=569",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SEARCH_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "SEARCH_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=909",
        "prompt": "Filter books released in the year 2021",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=909",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=909",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__year_select__",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "__year_select__",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "__YEAR_KEY_1__",
                ],
                "attributes": {
                    "keys": [
                        "__YEAR_KEY_1__",
                    ],
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "__YEAR_KEY_2__",
                ],
                "attributes": {
                    "keys": [
                        "__YEAR_KEY_2__",
                    ],
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "__YEAR_KEY_3__",
                ],
                "attributes": {
                    "keys": [
                        "__YEAR_KEY_3__",
                    ],
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "__YEAR_KEY_4__",
                ],
                "attributes": {
                    "keys": [
                        "__YEAR_KEY_4__",
                    ],
                },
            },
            {
                "type": "SendKeysAction",
                "keys": [
                    "Enter",
                ],
                "attributes": {
                    "keys": [
                        "Enter",
                    ],
                },
            },
        ],
        "use_case": "FILTER_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=585",
        "prompt": "Fill and submit the contact form.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=585",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=585",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Contact']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Contact']",
                        "case_sensitive": False,
                    },
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
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__CONTACT_NAME__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__CONTACT_NAME__",
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
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__CONTACT_EMAIL__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-email-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__CONTACT_EMAIL__",
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
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__CONTACT_SUBJECT__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-subject-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__CONTACT_SUBJECT__",
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
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__CONTACT_MESSAGE__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "contact-message-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__CONTACT_MESSAGE__",
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
                    },
                },
            },
        ],
        "use_case": "CONTACT_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=512",
        "prompt": "Login with username and password.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=512",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=512",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "LOGIN_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=494",
        "prompt": "Login and logout.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=494",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=494",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[normalize-space()='Logout']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//button[normalize-space()='Logout']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "LOGOUT_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=720",
        "prompt": "Login and delete one assigned book.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=720",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=720",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/profile')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/profile')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-tab-books",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-tab-books",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[starts-with(@id,'delete-book-button')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[starts-with(@id,'delete-book-button')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "DELETE_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=385",
        "prompt": "Login and add a new book.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=385",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=385",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "profile-tab-add-books",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "profile-tab-add-books",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__AUTHOR__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(),'Author')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__AUTHOR__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(),'Author')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__YEAR__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(),'Year')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__YEAR__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(),'Year')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__PAGES__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(),'Pages')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__PAGES__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(),'Pages')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__RATING__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(),'Rating')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__RATING__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(),'Rating')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__GENRE__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//input[@placeholder='Custom genre list'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__GENRE__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//input[@placeholder='Custom genre list'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[normalize-space()='Add Book'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[normalize-space()='Add Book'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "ADD_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=362",
        "prompt": "Open a book and add a comment.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=362",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=362",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SEARCH_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "comment-author-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "comment-author-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__COMMENTER_NAME__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "comment-author-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__COMMENTER_NAME__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "comment-author-input",
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
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__COMMENT_MESSAGE__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "comment-message-textarea",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__COMMENT_MESSAGE__",
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
                    },
                },
            },
        ],
        "use_case": "ADD_COMMENT_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=411",
        "prompt": "Login and edit user profile fields.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=411",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=411",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "first-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "first-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__FIRST_NAME__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "first-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__FIRST_NAME__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "first-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "last-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "last-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__LAST_NAME__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "last-name-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__LAST_NAME__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "last-name-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "website-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "website-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__WEBSITE__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "website-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__WEBSITE__",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "website-input",
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
                    },
                },
            },
        ],
        "use_case": "EDIT_USER_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=310",
        "prompt": "Navigate to '1984' book page",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=310",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=310",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SEARCH_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='share-detail-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='share-detail-button']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "BOOK_DETAIL",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=858",
        "prompt": "Login with username: <username> and password: <password>. Edit a book by changing the rating to 4.8.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=858",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=858",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='books-view-tab' or @id='profile-tab-books']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='books-view-tab' or @id='profile-tab-books']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__RATING__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(),'Rating')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__RATING__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(),'Rating')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(),'Pages')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(),'Pages')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__PAGES__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//label[contains(normalize-space(),'Pages')]/input)[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__PAGES__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//label[contains(normalize-space(),'Pages')]/input)[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//input[@placeholder='Custom genre list'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//input[@placeholder='Custom genre list'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__GENRE__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//input[@placeholder='Custom genre list'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__GENRE__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//input[@placeholder='Custom genre list'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//form[.//label[contains(normalize-space(),'Rating')]]//button[@type='submit'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//form[.//label[contains(normalize-space(),'Rating')]]//button[@type='submit'])[1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "EDIT_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=512",
        "prompt": "Login with username: <username> and password: <password>. After logging in, purchase the book 'The Silent Patient'.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=512",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=512",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__SEARCH_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/cart')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/cart')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='purchase-button' or @id='buy-now-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='purchase-button' or @id='buy-now-button']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "PURCHASE_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=426",
        "prompt": "Open detail and share the book.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=426",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=426",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "share-detail-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "share-detail-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "SHARE_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=921",
        "prompt": "Open detail and start preview.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=921",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=921",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "read-book-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "read-book-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "OPEN_PREVIEW",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=426",
        "prompt": "Login with username: <username> and password: <password>. Add 'The Iliad' to your reading list.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=426",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=426",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__READING_LIST_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__READING_LIST_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='reading-list-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='reading-list-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='reading-list-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='reading-list-button']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "ADD_TO_READING_LIST",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=763",
        "prompt": "Login with username: <username> and password: <password>. Remove 'The Iliad' from your reading list.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=763",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=763",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__READING_LIST_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__READING_LIST_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='reading-list-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='reading-list-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='reading-list-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='reading-list-button']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "REMOVE_FROM_READING_LIST",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=99",
        "prompt": "Login with username: <username> and password: <password>. After logging in, view your shopping cart.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=99",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=99",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/cart')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/cart')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')][1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')][1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "VIEW_CART_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=534",
        "prompt": "Login with username: <username> and password: <password>. After logging in, add 'Romeo and Juliet' to your shopping cart.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=534",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=534",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__CART_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__CART_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "ADD_TO_CART_BOOK",
        "has_success": True,
    },
    {
        "url": "http://localhost:8001/?seed=331",
        "prompt": "Login with username: <username> and password: <password>. After logging in, remove 'Romeo and Juliet' from your shopping cart.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=331",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=331",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[normalize-space()='Login']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[normalize-space()='Login']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<username>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "username-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<username>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "username-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "<password>",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "password-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "<password>",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "password-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "login-submit-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "login-submit-button",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/search')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/search')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "__CART_QUERY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='search-field' or @id='search-input']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "__CART_QUERY__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='search-field' or @id='search-input']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//a[contains(@href,'/books/')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//a[contains(@href,'/books/')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//a[contains(@href,'/cart')]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//a[contains(@href,'/cart')]",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[contains(@id,'remove-from-cart-button') or contains(@id,'delete-cart-item-button') or contains(@id,'remove-cart')])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//*[contains(@id,'remove-from-cart-button') or contains(@id,'delete-cart-item-button') or contains(@id,'remove-cart')])[1]",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "REMOVE_FROM_CART_BOOK",
        "has_success": True,
    },
]


# CheckEventTest payloads aligned with autobook_tasks.json (per use_case.name).
_RAW_TESTS: dict[str, list[dict]] = {
    "REGISTRATION_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "REGISTRATION_BOOK",
            "event_criteria": {"username": "<signup_username>", "email": "<signup_email>", "password": "<signup_password>"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_BOOK",
            "event_criteria": {"query": {"operator": "not_equals", "value": "The Silent Patient"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "FILTER_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "FILTER_BOOK",
            "event_criteria": {"genres": "Drama", "year": {"operator": "less_equal", "value": 1605}},
            "description": "Check if specific event was triggered",
        }
    ],
    "CONTACT_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "CONTACT_BOOK",
            "event_criteria": {"subject": {"operator": "not_contains", "value": "Complaint"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "LOGIN_BOOK": [
        {"type": "CheckEventTest", "event_name": "LOGIN_BOOK", "event_criteria": {"username": "<username>", "password": "<password>"}, "description": "Check if specific event was triggered"}
    ],
    "LOGOUT_BOOK": [
        {"type": "CheckEventTest", "event_name": "LOGOUT_BOOK", "event_criteria": {"username": "<username>", "password": "<password>"}, "description": "Check if specific event was triggered"}
    ],
    "DELETE_BOOK": [
        {"type": "CheckEventTest", "event_name": "DELETE_BOOK", "event_criteria": {"username": "<username>", "password": "<password>"}, "description": "Check if specific event was triggered"}
    ],
    "ADD_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_BOOK",
            "event_criteria": {"username": "<username>", "password": "<password>", "year": 2012, "rating": {"operator": "greater_equal", "value": 2.5}, "page_count": 1059},
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_COMMENT_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_COMMENT_BOOK",
            "event_criteria": {"content": "a true literary experience", "commenter_name": {"operator": "not_contains", "value": "Emily"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_USER_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_USER_BOOK",
            "event_criteria": {"username": "<username>", "password": "<password>", "first_name": {"operator": "contains", "value": "book"}, "website": {"operator": "contains", "value": "blue"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "BOOK_DETAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "BOOK_DETAIL",
            "event_criteria": {"genres": {"operator": "not_contains", "value": "Postmodern"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_BOOK",
            "event_criteria": {"username": "<username>", "password": "<password>", "book_author": "Franz Kafka", "book_year": 1975},
            "description": "Check if specific event was triggered",
        }
    ],
    "PURCHASE_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "PURCHASE_BOOK",
            "event_criteria": {"name": {"operator": "not_equals", "value": "The Stand"}, "username": "<username>", "password": "<password>"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SHARE_BOOK": [
        {"type": "CheckEventTest", "event_name": "SHARE_BOOK", "event_criteria": {"rating": {"operator": "not_equals", "value": 4.7}}, "description": "Check if specific event was triggered"}
    ],
    "OPEN_PREVIEW": [
        {
            "type": "CheckEventTest",
            "event_name": "OPEN_PREVIEW",
            "event_criteria": {"price": 12.99, "name": {"operator": "contains", "value": "icide"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_TO_READING_LIST": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_READING_LIST",
            "event_criteria": {
                "genres": {"operator": "not_in_list", "value": ["Fantasy", "Thriller"]},
                "rating": {"operator": "greater_equal", "value": 4.7},
                "username": "<username>",
                "password": "<password>",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "REMOVE_FROM_READING_LIST": [
        {
            "type": "CheckEventTest",
            "event_name": "REMOVE_FROM_READING_LIST",
            "event_criteria": {"name": {"operator": "contains", "value": "yr"}, "page_count": {"operator": "not_equals", "value": 417}, "username": "<username>", "password": "<password>"},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_CART_BOOK": [{"type": "CheckEventTest", "event_name": "VIEW_CART_BOOK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "ADD_TO_CART_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_CART_BOOK",
            "event_criteria": {"genres": {"operator": "not_in_list", "value": ["War", "Classic"]}, "username": "<username>", "password": "<password>"},
            "description": "Check if specific event was triggered",
        }
    ],
    "REMOVE_FROM_CART_BOOK": [
        {
            "type": "CheckEventTest",
            "event_name": "REMOVE_FROM_CART_BOOK",
            "event_criteria": {
                "author": {"operator": "not_equals", "value": "Kathryn Stockett"},
                "rating": 4.4,
                "year": {"operator": "not_equals", "value": 2019},
                "username": "<username>",
                "password": "<password>",
            },
            "description": "Check if specific event was triggered",
        }
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


BASE = "http://localhost:8001"
# From autobook_tasks.json (?seed= in each task URL)
SEED_REGISTRATION_BOOK = 802
SEED_SEARCH_BOOK = 569
SEED_FILTER_BOOK = 909
SEED_CONTACT_BOOK = 585
SEED_LOGIN_BOOK = 512
SEED_LOGOUT_BOOK = 494
SEED_DELETE_BOOK = 720
SEED_ADD_BOOK = 385
SEED_ADD_COMMENT_BOOK = 362
SEED_EDIT_USER_BOOK = 411
SEED_BOOK_DETAIL = 310
SEED_EDIT_BOOK = 858
SEED_PURCHASE_BOOK = 512
SEED_SHARE_BOOK = 426
SEED_OPEN_PREVIEW = 921
SEED_ADD_TO_READING_LIST = 426
SEED_REMOVE_FROM_READING_LIST = 763
SEED_VIEW_CART_BOOK = 99
SEED_ADD_TO_CART_BOOK = 534
SEED_REMOVE_FROM_CART_BOOK = 331

REGISTRATION_BOOK = _uc(
    "REGISTRATION_BOOK",
    prompt="Register with the following username: '<signup_username>', email: '<signup_email>' and password: '<signup_password>'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_REGISTRATION_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Register']")),
        ClickAction(selector=_id("username-input")),
        TypeAction(selector=_id("username-input"), text="__SIGNUP_USERNAME__"),
        ClickAction(selector=_id("signup-email-input")),
        TypeAction(selector=_id("signup-email-input"), text="__SIGNUP_EMAIL__"),
        ClickAction(selector=_id("password-input")),
        TypeAction(selector=_id("password-input"), text="__SIGNUP_PASSWORD__"),
        ClickAction(selector=_id("confirm-password-input")),
        TypeAction(selector=_id("confirm-password-input"), text="__SIGNUP_PASSWORD__"),
        ClickAction(selector=_id("signup-submit-button")),
    ],
)

SEARCH_BOOK = _uc(
    "SEARCH_BOOK",
    prompt="Search for the book 'The Silent Patient' in the database",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SEARCH_BOOK}"),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
    ],
)

FILTER_BOOK = _uc(
    "FILTER_BOOK",
    prompt="Show me details about books where the genres equals 'Drama' and the year is less equal '1605'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_FILTER_BOOK}"),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        ClickAction(selector=_xp("__year_select__")),
        SendKeysIWAAction(keys="__YEAR_KEY_1__"),
        SendKeysIWAAction(keys="__YEAR_KEY_2__"),
        SendKeysIWAAction(keys="__YEAR_KEY_3__"),
        SendKeysIWAAction(keys="__YEAR_KEY_4__"),
        SendKeysIWAAction(keys="Enter"),
    ],
)

CONTACT_BOOK = _uc(
    "CONTACT_BOOK",
    prompt="Go to the contact page and submit a form where the subject does NOT contain 'Complaint'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CONTACT_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Contact']")),
        ClickAction(selector=_id("contact-name-input")),
        TypeAction(selector=_id("contact-name-input"), text="__CONTACT_NAME__"),
        ClickAction(selector=_id("contact-email-input")),
        TypeAction(selector=_id("contact-email-input"), text="__CONTACT_EMAIL__"),
        ClickAction(selector=_id("contact-subject-input")),
        TypeAction(selector=_id("contact-subject-input"), text="__CONTACT_SUBJECT__"),
        ClickAction(selector=_id("contact-message-textarea")),
        TypeAction(selector=_id("contact-message-textarea"), text="__CONTACT_MESSAGE__"),
        ClickAction(selector=_id("send-message-button")),
    ],
)

LOGIN_BOOK = _uc(
    "LOGIN_BOOK",
    prompt="Login with a specific username:'<username>' and password:'<password>'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_LOGIN_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
    ],
)

LOGOUT_BOOK = _uc(
    "LOGOUT_BOOK",
    prompt="Login with a specific username:'<username>' and password:'<password>', then logout",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_LOGOUT_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//button[normalize-space()='Logout']")),
    ],
)

DELETE_BOOK = _uc(
    "DELETE_BOOK",
    prompt="Login with username equals <username> and password equals <password>. Then, delete your book.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DELETE_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//a[contains(@href,'/profile')]")),
        ClickAction(selector=_id("profile-tab-books")),
        ClickAction(selector=_xp("(//*[starts-with(@id,'delete-book-button')])[1]")),
    ],
)

ADD_BOOK = _uc(
    "ADD_BOOK",
    prompt="First, authenticate with username '<username>' and password '<password>'. Then, add a book whose year equals 2012, rating is greater equal 2.5, and page_count equals 1059.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_id("profile-tab-add-books")),
        TypeAction(selector=_xp("(//label[contains(normalize-space(),'Author')]/input)[1]"), text="__AUTHOR__"),
        TypeAction(selector=_xp("(//label[contains(normalize-space(),'Year')]/input)[1]"), text="__YEAR__"),
        TypeAction(selector=_xp("(//label[contains(normalize-space(),'Pages')]/input)[1]"), text="__PAGES__"),
        TypeAction(selector=_xp("(//label[contains(normalize-space(),'Rating')]/input)[1]"), text="__RATING__"),
        TypeAction(selector=_xp("(//input[@placeholder='Custom genre list'])[1]"), text="__GENRE__"),
        ClickAction(selector=_xp("(//button[normalize-space()='Add Book'])[1]")),
    ],
)

ADD_COMMENT_BOOK = _uc(
    "ADD_COMMENT_BOOK",
    prompt="Add a comment to a book with a comment whose content equals a true literary experience and a commenter_name that does NOT contain 'Emily'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_COMMENT_BOOK}"),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_id("comment-author-input")),
        TypeAction(selector=_id("comment-author-input"), text="__COMMENTER_NAME__"),
        ClickAction(selector=_id("comment-message-textarea")),
        TypeAction(selector=_id("comment-message-textarea"), text="__COMMENT_MESSAGE__"),
        ClickAction(selector=_id("share-feedback-button")),
    ],
)

EDIT_USER_BOOK = _uc(
    "EDIT_USER_BOOK",
    prompt="Login for the following username:<username> and password:<password>. Update your profile to modify your first name to include the word 'book' and ensure your website contains 'blue'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_USER_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_id("first-name-input")),
        TypeAction(selector=_id("first-name-input"), text="__FIRST_NAME__"),
        ClickAction(selector=_id("last-name-input")),
        TypeAction(selector=_id("last-name-input"), text="__LAST_NAME__"),
        ClickAction(selector=_id("website-input")),
        TypeAction(selector=_id("website-input"), text="__WEBSITE__"),
        ClickAction(selector=_id("save-profile-button")),
    ],
)

BOOK_DETAIL = _uc(
    "BOOK_DETAIL",
    prompt="Go to the book details page for a book where genres NOT CONTAINS 'Postmodern'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_BOOK_DETAIL}"),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_xp("//*[@id='share-detail-button']")),
    ],
)

EDIT_BOOK = _uc(
    "EDIT_BOOK",
    prompt="First, authenticate with username '<username>' and password '<password>'. Then, edit your book by setting book_author to 'Franz Kafka', book_year to '1975'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//*[@id='books-view-tab' or @id='profile-tab-books']")),
        TypeAction(selector=_xp("(//label[contains(normalize-space(),'Rating')]/input)[1]"), text="__RATING__"),
        ClickAction(selector=_xp("(//label[contains(normalize-space(),'Pages')]/input)[1]")),
        TypeAction(selector=_xp("(//label[contains(normalize-space(),'Pages')]/input)[1]"), text="__PAGES__"),
        ClickAction(selector=_xp("(//input[@placeholder='Custom genre list'])[1]")),
        TypeAction(selector=_xp("(//input[@placeholder='Custom genre list'])[1]"), text="__GENRE__"),
        ClickAction(selector=_xp("(//form[.//label[contains(normalize-space(),'Rating')]]//button[@type='submit'])[1]")),
    ],
)

PURCHASE_BOOK = _uc(
    "PURCHASE_BOOK",
    prompt="First, authenticate with username '<username>' and password '<password>'. Then, proceed to checkout for the book whose name is NOT 'The Stand'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_PURCHASE_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_xp("//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']")),
        ClickAction(selector=_xp("//a[contains(@href,'/cart')]")),
        ClickAction(selector=_xp("//*[@id='purchase-button' or @id='buy-now-button']")),
    ],
)

SHARE_BOOK = _uc(
    "SHARE_BOOK",
    prompt="Share book details for a book with a rating NOT EQUALS '4.7'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SHARE_BOOK}"),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_id("share-detail-button")),
    ],
)

OPEN_PREVIEW = _uc(
    "OPEN_PREVIEW",
    prompt="Open preview of book where the price equals '12.99' and the name contains 'icide'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_OPEN_PREVIEW}"),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_id("read-book-button")),
    ],
)

ADD_TO_READING_LIST = _uc(
    "ADD_TO_READING_LIST",
    prompt="First, login for the following username:'<username>' and password:'<password>' and then add to reading list a book that is NOT in the genres 'Fantasy' or 'Thriller' with a rating of 4.7 or higher",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_TO_READING_LIST}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__READING_LIST_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_xp("//*[@id='reading-list-button']")),
        ClickAction(selector=_xp("//*[@id='reading-list-button']")),
    ],
)

REMOVE_FROM_READING_LIST = _uc(
    "REMOVE_FROM_READING_LIST",
    prompt="First, login for the following username:'<username>' and password:'<password>' and then remove from reading list a book whose name CONTAINS 'yr' and has a page_count NOT EQUALS 417",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_REMOVE_FROM_READING_LIST}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__READING_LIST_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_xp("//*[@id='reading-list-button']")),
        ClickAction(selector=_xp("//*[@id='reading-list-button']")),
    ],
)

VIEW_CART_BOOK = _uc(
    "VIEW_CART_BOOK",
    prompt="First, authenticate with username '<username>' and password '<password>'. Then, view the shopping cart to see items added.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_VIEW_CART_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//a[contains(@href,'/cart')]")),
        ClickAction(selector=_xp("//a[contains(@href,'/search')][1]")),
    ],
)

ADD_TO_CART_BOOK = _uc(
    "ADD_TO_CART_BOOK",
    prompt="First, authenticate with username '<username>' and password '<password>'. After successful login, add a book to the shopping cart where the genres is NOT one of ['War', 'Classic'].",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_TO_CART_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__CART_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_xp("//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']")),
    ],
)

REMOVE_FROM_CART_BOOK = _uc(
    "REMOVE_FROM_CART_BOOK",
    prompt="First, authenticate with username '<username>' and password '<password>'. After successful login, remove from the shopping cart any book that has an author NOT EQUALS 'Kathryn Stockett', a rating EQUALS '4.4', a year NOT EQUALS '2019'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_REMOVE_FROM_CART_BOOK}"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__CART_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_xp("//*[@id='add-to-cart-detail-button' or @id='add-cart-button' or @id='cart-button']")),
        ClickAction(selector=_xp("//a[contains(@href,'/cart')]")),
        ClickAction(selector=_xp("(//*[contains(@id,'remove-from-cart-button') or contains(@id,'delete-cart-item-button') or contains(@id,'remove-cart')])[1]")),
    ],
)


def load_autobooks_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "REGISTRATION_BOOK": REGISTRATION_BOOK,
        "SEARCH_BOOK": SEARCH_BOOK,
        "FILTER_BOOK": FILTER_BOOK,
        "CONTACT_BOOK": CONTACT_BOOK,
        "LOGIN_BOOK": LOGIN_BOOK,
        "LOGOUT_BOOK": LOGOUT_BOOK,
        "DELETE_BOOK": DELETE_BOOK,
        "ADD_BOOK": ADD_BOOK,
        "ADD_COMMENT_BOOK": ADD_COMMENT_BOOK,
        "EDIT_USER_BOOK": EDIT_USER_BOOK,
        "BOOK_DETAIL": BOOK_DETAIL,
        "EDIT_BOOK": EDIT_BOOK,
        "PURCHASE_BOOK": PURCHASE_BOOK,
        "SHARE_BOOK": SHARE_BOOK,
        "OPEN_PREVIEW": OPEN_PREVIEW,
        "ADD_TO_READING_LIST": ADD_TO_READING_LIST,
        "REMOVE_FROM_READING_LIST": REMOVE_FROM_READING_LIST,
        "VIEW_CART_BOOK": VIEW_CART_BOOK,
        "ADD_TO_CART_BOOK": ADD_TO_CART_BOOK,
        "REMOVE_FROM_CART_BOOK": REMOVE_FROM_CART_BOOK,
    }
