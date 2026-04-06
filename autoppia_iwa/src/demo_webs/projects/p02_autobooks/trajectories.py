from __future__ import annotations

import re
from typing import Any

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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Register with username, email and password placeholders.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Look for the book 'Lolita'",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Filter books released in the year 2021",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Fill and submit the contact form.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username and password.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login and logout.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login and delete one assigned book.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login and add a new book.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Open a book and add a comment.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login and edit user profile fields.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Navigate to '1984' book page",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username: <username> and password: <password>. Edit a book by changing the rating to 4.8.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username: <username> and password: <password>. After logging in, purchase the book 'The Silent Patient'.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Open detail and share the book.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Open detail and start preview.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username: <username> and password: <password>. Add 'The Iliad' to your reading list.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username: <username> and password: <password>. Remove 'The Iliad' from your reading list.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username: <username> and password: <password>. After logging in, view your shopping cart.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username: <username> and password: <password>. After logging in, add 'Romeo and Juliet' to your shopping cart.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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
        "url": "http://localhost:8001/?seed=1",
        "prompt": "Login with username: <username> and password: <password>. After logging in, remove 'Romeo and Juliet' from your shopping cart.",
        "actions": [
            {
                "url": "http://localhost:8001/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8001/?seed=1",
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


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


REGISTRATION_BOOK = _uc(
    "REGISTRATION_BOOK",
    prompt="Register with username, email and password placeholders.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Look for the book 'Lolita'",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
    ],
)

FILTER_BOOK = _uc(
    "FILTER_BOOK",
    prompt="Filter books released in the year 2021",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Fill and submit the contact form.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login with username and password.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
    ],
)

LOGOUT_BOOK = _uc(
    "LOGOUT_BOOK",
    prompt="Login and logout.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
        ClickAction(selector=_xp("//a[normalize-space()='Login']")),
        TypeAction(selector=_id("username-input"), text="<username>"),
        TypeAction(selector=_id("password-input"), text="<password>"),
        ClickAction(selector=_id("login-submit-button")),
        ClickAction(selector=_xp("//button[normalize-space()='Logout']")),
    ],
)

DELETE_BOOK = _uc(
    "DELETE_BOOK",
    prompt="Login and delete one assigned book.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login and add a new book.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Open a book and add a comment.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login and edit user profile fields.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Navigate to '1984' book page",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
        ClickAction(selector=_xp("//a[contains(@href,'/search')]")),
        TypeAction(selector=_xp("//*[@id='search-field' or @id='search-input']"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("//*[@id='submit-btn' or @id='search-submit-button' or @id='search-button']")),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_xp("//*[@id='share-detail-button']")),
    ],
)

EDIT_BOOK = _uc(
    "EDIT_BOOK",
    prompt="Login with username: <username> and password: <password>. Edit a book by changing the rating to 4.8.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login with username: <username> and password: <password>. After logging in, purchase the book 'The Silent Patient'.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Open detail and share the book.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_id("share-detail-button")),
    ],
)

OPEN_PREVIEW = _uc(
    "OPEN_PREVIEW",
    prompt="Open detail and start preview.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
        ClickAction(selector=_xp("(//a[contains(@href,'/books/')])[1]")),
        ClickAction(selector=_id("read-book-button")),
    ],
)

ADD_TO_READING_LIST = _uc(
    "ADD_TO_READING_LIST",
    prompt="Login with username: <username> and password: <password>. Add 'The Iliad' to your reading list.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login with username: <username> and password: <password>. Remove 'The Iliad' from your reading list.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login with username: <username> and password: <password>. After logging in, view your shopping cart.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login with username: <username> and password: <password>. After logging in, add 'Romeo and Juliet' to your shopping cart.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
    prompt="Login with username: <username> and password: <password>. After logging in, remove 'Romeo and Juliet' from your shopping cart.",
    actions=[
        NavigateAction(url="http://localhost:8001/?seed=1"),
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
