from __future__ import annotations

import re
from typing import Any

PROJECT_NUMBER = 6
WEB_PROJECT_ID = "automail"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    NavigateAction,
    TypeAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

ACTIONS = [
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Search for query containing 'Weekly Newsletter'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "SEARCH_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Open the email templates page.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "sidebar-templates",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "VIEW_TEMPLATES",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Select the template where template_name equals 'Meeting Recap'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "sidebar-templates",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__TEMPLATE_OPTION__",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "TEMPLATE_SELECTED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Update the body text of the template where template_name equals 'Warm Introduction'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "sidebar-templates",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__TEMPLATE_OPTION__",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-body' or @id='template-content' or @aria-label='Body']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_BODY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-body' or @id='template-content' or @aria-label='Body']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-body' or @id='template-content' or @aria-label='Body']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "TEMPLATE_BODY_EDITED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Send an email using the template where template_name equals 'Friendly Follow Up' and to equals 'john.doe@gmail.com'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "sidebar-templates",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__TEMPLATE_OPTION__",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-to' or @id='template-recipient' or @aria-label='To']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_TO__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-to' or @id='template-recipient' or @aria-label='To']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-send' or @id='send-button' or @aria-label='Send' or normalize-space()='Send']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "TEMPLATE_SENT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Save the template as draft where template_name equals 'Meeting Recap' and to equals 'alice@company.com'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "sidebar-templates",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__TEMPLATE_OPTION__",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-to' or @id='template-recipient' or @aria-label='To']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_TO__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-to' or @id='template-recipient' or @aria-label='To']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-save' or @id='save-draft-button' or @aria-label='Save draft' or normalize-space()='Save draft']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "TEMPLATE_SAVED_DRAFT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Cancel changes on the template where template_name equals 'Thank You'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "sidebar-templates",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__TEMPLATE_OPTION__",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-to' or @id='template-recipient' or @aria-label='To']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_TO__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-to' or @id='template-recipient' or @aria-label='To']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='template-cancel' or @id='cancel-button' or @aria-label='Cancel' or normalize-space()='Cancel']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "TEMPLATE_CANCELED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Go to the next page of emails.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='next-page-button' or @data-testid='next-page-button' or @aria-label='Next page' or @title='Next page'] | //*[@data-testid='email-list']//button[2]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "EMAILS_NEXT_PAGE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Go back to the previous page of emails.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@data-testid='email-list']/div[1]/div[2]/div/button[2]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@data-testid='email-list']/div[1]/div[2]/div/button[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "EMAILS_PREV_PAGE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Clear the current selection.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='email-card']/div[1]/button)[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@aria-label='Clear Selection' or @id='clear-selection-button' or @data-testid='clear-selection-button'] | //*[@data-testid='email-list']/div[2]/button[6]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "CLEAR_SELECTION",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Create a label named 'Work' with color 'blue'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "label-selector-trigger",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='label-selector-menu']//input[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__LABEL_NAME__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='label-selector-menu']//input[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "label-color-4285f4",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "create-label-button",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "CREATE_LABEL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Apply dark mode appearance",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[@aria-label='User account menu' or .//span[normalize-space()='U']])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__THEME_BUTTON__",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "THEME_CHANGED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Add the label 'Work' to the email from 'eric.baker@management.com'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__ADD_LABEL_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='email-label-selector']//*[self::button][1] | //*[@id='label-selector' or @id='tag-selector' or @id='label-picker'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "__ADD_LABEL_OPTION__",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "ADD_LABEL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Send the email to john.doe@gmail.com with subject 'Project Timeline Update'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[@aria-label='Compose' or normalize-space()='Compose'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_TO__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_SUBJECT__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_BODY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[@id='send-button' or @id='deliver-button' or @id='dispatch-button' or @aria-label='Send' or normalize-space()='Send']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "SEND_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Save the email as draft where email equals jane.doe@example.com",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[@aria-label='Compose' or normalize-space()='Compose'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_TO__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_SUBJECT__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_BODY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[@id='save-draft-button' or @id='draft-button' or @id='store-draft-button' or @aria-label='Save draft' or normalize-space()='Save draft']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "EMAIL_SAVE_AS_DRAFT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Edit the draft email where to equals 'jane.doe@example.com' and subject equals 'Client Proposal Updates'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[@aria-label='Compose' or normalize-space()='Compose'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_TO__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_SUBJECT__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_BODY__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[@id='save-draft-button' or @id='draft-button' or @id='store-draft-button' or @aria-label='Save draft' or normalize-space()='Save draft']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='sidebar-drafts' or @id='sidebar-drafts-item' or @id='nav-drafts' or @aria-label='Navigate to Drafts']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='edit-draft-button' or @id='email-edit-draft' or @aria-label='Edit this draft email']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "EDIT_DRAFT_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Reply to the email where from_email equals 'eric.baker@management.com' and subject equals 'Year-End Review Meeting - Schedule'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__REPLY_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='email-reply' or @id='reply-button' or @id='respond-button' or @id='answer-button' or @aria-label='Reply to this email']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[@id='send-button' or @id='deliver-button' or @id='dispatch-button' or @aria-label='Send' or normalize-space()='Send']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "REPLY_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Forward the email where from_email equals 'eric.baker@management.com' and subject equals 'Year-End Review Meeting - Schedule' and to equals 'john.doe@gmail.com'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__FORWARD_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='email-forward' or @id='forward-button' or @id='share-button' or @aria-label='Forward this email']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__EMAIL_TO__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//button[@id='send-button' or @id='deliver-button' or @id='dispatch-button' or @aria-label='Send' or normalize-space()='Send']",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "FORWARD_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "View the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "VIEW_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Star the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='star-button' or @id='email-star' or contains(@id,'star-button') or contains(@id,'email-star') or (@aria-label='Mark as important' and (contains(@title,'star') or contains(@title,'Star')))]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "STAR_AN_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Mark the email as important where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='important-button' or @id='email-important' or contains(@id,'important-button') or contains(@id,'email-important') or (contains(@title,'important') and contains(@aria-label,'important'))]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "MARK_EMAIL_AS_IMPORTANT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Mark the email as unread where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='email-mark-unread' or @id='mark-unread-button' or contains(@id,'mark-unread') or @aria-label='Mark unread' or contains(@title,'unread')]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "MARK_AS_UNREAD",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Delete the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='email-delete' or @id='delete-button' or contains(@id,'email-delete') or contains(@id,'delete-email') or @aria-label='Delete' or contains(@title,'Delete')]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "DELETE_EMAIL",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Mark the email as spam where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='view-email'])[1]",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='email-mark-spam' or @id='mark-spam-button' or contains(@id,'mark-spam') or contains(@id,'email-mark-spam') or @aria-label='Mark spam' or contains(@title,'spam')]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "MARK_AS_SPAM",
        "has_success": False,
    },
    {
        "url": "http://localhost:8005/?seed=1",
        "prompt": "Archive the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=1",
                "type": "NavigateAction",
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "TypeAction",
                "text": "__SEARCH_QUERY__",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//*[@id='archive-button' or contains(@id,'archive-button') or contains(@id,'archive_button')])[1]",
                    "case_sensitive": False,
                },
            },
        ],
        "use_case": "ARCHIVE_EMAIL",
        "has_success": False,
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


SEARCH_EMAIL = _uc(
    "SEARCH_EMAIL",
    prompt="Search for query containing 'Weekly Newsletter'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
    ],
)

VIEW_TEMPLATES = _uc(
    "VIEW_TEMPLATES",
    prompt="Open the email templates page.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("sidebar-templates")),
    ],
)

TEMPLATE_SELECTED = _uc(
    "TEMPLATE_SELECTED",
    prompt="Select the template where template_name equals 'Meeting Recap'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
    ],
)

TEMPLATE_BODY_EDITED = _uc(
    "TEMPLATE_BODY_EDITED",
    prompt="Update the body text of the template where template_name equals 'Warm Introduction'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
        ClickAction(selector=_xp("//*[@id='template-body' or @id='template-content' or @aria-label='Body']")),
        TypeAction(selector=_xp("//*[@id='template-body' or @id='template-content' or @aria-label='Body']"), text="__EMAIL_BODY__"),
        ClickAction(selector=_xp("//*[@id='template-body' or @id='template-content' or @aria-label='Body']")),
    ],
)

TEMPLATE_SENT = _uc(
    "TEMPLATE_SENT",
    prompt="Send an email using the template where template_name equals 'Friendly Follow Up' and to equals 'john.doe@gmail.com'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
        ClickAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']")),
        TypeAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//*[@id='template-send' or @id='send-button' or @aria-label='Send' or normalize-space()='Send']")),
    ],
)

TEMPLATE_SAVED_DRAFT = _uc(
    "TEMPLATE_SAVED_DRAFT",
    prompt="Save the template as draft where template_name equals 'Meeting Recap' and to equals 'alice@company.com'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
        ClickAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']")),
        TypeAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//*[@id='template-save' or @id='save-draft-button' or @aria-label='Save draft' or normalize-space()='Save draft']")),
    ],
)

TEMPLATE_CANCELED = _uc(
    "TEMPLATE_CANCELED",
    prompt="Cancel changes on the template where template_name equals 'Thank You'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
        ClickAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']")),
        TypeAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//*[@id='template-cancel' or @id='cancel-button' or @aria-label='Cancel' or normalize-space()='Cancel']")),
    ],
)

EMAILS_NEXT_PAGE = _uc(
    "EMAILS_NEXT_PAGE",
    prompt="Go to the next page of emails.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_xp("//*[@id='next-page-button' or @data-testid='next-page-button' or @aria-label='Next page' or @title='Next page'] | //*[@data-testid='email-list']//button[2]")),
    ],
)

EMAILS_PREV_PAGE = _uc(
    "EMAILS_PREV_PAGE",
    prompt="Go back to the previous page of emails.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_xp("//*[@data-testid='email-list']/div[1]/div[2]/div/button[2]")),
        ClickAction(selector=_xp("//*[@data-testid='email-list']/div[1]/div[2]/div/button[1]")),
    ],
)

CLEAR_SELECTION = _uc(
    "CLEAR_SELECTION",
    prompt="Clear the current selection.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_xp("(//*[@id='email-card']/div[1]/button)[1]")),
        ClickAction(selector=_xp("//*[@aria-label='Clear Selection' or @id='clear-selection-button' or @data-testid='clear-selection-button'] | //*[@data-testid='email-list']/div[2]/button[6]")),
    ],
)

CREATE_LABEL = _uc(
    "CREATE_LABEL",
    prompt="Create a label named 'Work' with color 'blue'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("label-selector-trigger")),
        ClickAction(selector=_xp("//*[@id='label-selector-menu']//input[1]")),
        TypeAction(selector=_xp("//*[@id='label-selector-menu']//input[1]"), text="__LABEL_NAME__"),
        ClickAction(selector=_id("label-color-4285f4")),
        ClickAction(selector=_id("create-label-button")),
    ],
)

THEME_CHANGED = _uc(
    "THEME_CHANGED",
    prompt="Apply dark mode appearance",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_xp("(//button[@aria-label='User account menu' or .//span[normalize-space()='U']])[1]")),
        ClickAction(selector=_xp("__THEME_BUTTON__")),
    ],
)

ADD_LABEL = _uc(
    "ADD_LABEL",
    prompt="Add the label 'Work' to the email from 'eric.baker@management.com'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__ADD_LABEL_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("(//*[@id='email-label-selector']//*[self::button][1] | //*[@id='label-selector' or @id='tag-selector' or @id='label-picker'])[1]")),
        ClickAction(selector=_xp("__ADD_LABEL_OPTION__")),
    ],
)

SEND_EMAIL = _uc(
    "SEND_EMAIL",
    prompt="Send the email to john.doe@gmail.com with subject 'Project Timeline Update'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_xp("(//button[@aria-label='Compose' or normalize-space()='Compose'])[1]")),
        ClickAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']")),
        TypeAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']")),
        TypeAction(selector=_xp("//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']"), text="__EMAIL_SUBJECT__"),
        ClickAction(selector=_xp("//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']")),
        TypeAction(selector=_xp("//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']"), text="__EMAIL_BODY__"),
        ClickAction(selector=_xp("//button[@id='send-button' or @id='deliver-button' or @id='dispatch-button' or @aria-label='Send' or normalize-space()='Send']")),
    ],
)

EMAIL_SAVE_AS_DRAFT = _uc(
    "EMAIL_SAVE_AS_DRAFT",
    prompt="Save the email as draft where email equals jane.doe@example.com",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_xp("(//button[@aria-label='Compose' or normalize-space()='Compose'])[1]")),
        ClickAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']")),
        TypeAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']")),
        TypeAction(selector=_xp("//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']"), text="__EMAIL_SUBJECT__"),
        ClickAction(selector=_xp("//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']")),
        TypeAction(selector=_xp("//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']"), text="__EMAIL_BODY__"),
        ClickAction(selector=_xp("//button[@id='save-draft-button' or @id='draft-button' or @id='store-draft-button' or @aria-label='Save draft' or normalize-space()='Save draft']")),
    ],
)

EDIT_DRAFT_EMAIL = _uc(
    "EDIT_DRAFT_EMAIL",
    prompt="Edit the draft email where to equals 'jane.doe@example.com' and subject equals 'Client Proposal Updates'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_xp("(//button[@aria-label='Compose' or normalize-space()='Compose'])[1]")),
        ClickAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']")),
        TypeAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']")),
        TypeAction(selector=_xp("//input[@id='subject-input' or @id='topic-input' or @id='mail-subject' or @aria-label='Subject']"), text="__EMAIL_SUBJECT__"),
        ClickAction(selector=_xp("//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']")),
        TypeAction(selector=_xp("//textarea[@id='body-input' or @id='message-textarea' or @id='content-textarea' or @id='mail-body' or @aria-label='Type your message...']"), text="__EMAIL_BODY__"),
        ClickAction(selector=_xp("//button[@id='save-draft-button' or @id='draft-button' or @id='store-draft-button' or @aria-label='Save draft' or normalize-space()='Save draft']")),
        ClickAction(selector=_xp("//*[@id='sidebar-drafts' or @id='sidebar-drafts-item' or @id='nav-drafts' or @aria-label='Navigate to Drafts']")),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("//*[@id='edit-draft-button' or @id='email-edit-draft' or @aria-label='Edit this draft email']")),
    ],
)

REPLY_EMAIL = _uc(
    "REPLY_EMAIL",
    prompt="Reply to the email where from_email equals 'eric.baker@management.com' and subject equals 'Year-End Review Meeting - Schedule'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__REPLY_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("//*[@id='email-reply' or @id='reply-button' or @id='respond-button' or @id='answer-button' or @aria-label='Reply to this email']")),
        ClickAction(selector=_xp("//button[@id='send-button' or @id='deliver-button' or @id='dispatch-button' or @aria-label='Send' or normalize-space()='Send']")),
    ],
)

FORWARD_EMAIL = _uc(
    "FORWARD_EMAIL",
    prompt="Forward the email where from_email equals 'eric.baker@management.com' and subject equals 'Year-End Review Meeting - Schedule' and to equals 'john.doe@gmail.com'.",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__FORWARD_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("//*[@id='email-forward' or @id='forward-button' or @id='share-button' or @aria-label='Forward this email']")),
        ClickAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']")),
        TypeAction(selector=_xp("//input[@id='to-input' or @id='recipient-input' or @id='mail-to' or @aria-label='Recipient email address']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//button[@id='send-button' or @id='deliver-button' or @id='dispatch-button' or @aria-label='Send' or normalize-space()='Send']")),
    ],
)

VIEW_EMAIL = _uc(
    "VIEW_EMAIL",
    prompt="View the email where subject contains 'Project'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
    ],
)

STAR_AN_EMAIL = _uc(
    "STAR_AN_EMAIL",
    prompt="Star the email where subject contains 'Project'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(
            selector=_xp(
                "//*[@id='star-button' or @id='email-star' or contains(@id,'star-button') or contains(@id,'email-star') or (@aria-label='Mark as important' and (contains(@title,'star') or contains(@title,'Star')))]"
            )
        ),
    ],
)

MARK_EMAIL_AS_IMPORTANT = _uc(
    "MARK_EMAIL_AS_IMPORTANT",
    prompt="Mark the email as important where subject contains 'Project'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(
            selector=_xp(
                "//*[@id='important-button' or @id='email-important' or contains(@id,'important-button') or contains(@id,'email-important') or (contains(@title,'important') and contains(@aria-label,'important'))]"
            )
        ),
    ],
)

MARK_AS_UNREAD = _uc(
    "MARK_AS_UNREAD",
    prompt="Mark the email as unread where subject contains 'Project'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("//*[@id='email-mark-unread' or @id='mark-unread-button' or contains(@id,'mark-unread') or @aria-label='Mark unread' or contains(@title,'unread')]")),
    ],
)

DELETE_EMAIL = _uc(
    "DELETE_EMAIL",
    prompt="Delete the email where subject contains 'Project'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(
            selector=_xp("//*[@id='email-delete' or @id='delete-button' or contains(@id,'email-delete') or contains(@id,'delete-email') or @aria-label='Delete' or contains(@title,'Delete')]")
        ),
    ],
)

MARK_AS_SPAM = _uc(
    "MARK_AS_SPAM",
    prompt="Mark the email as spam where subject contains 'Project'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(
            selector=_xp("//*[@id='email-mark-spam' or @id='mark-spam-button' or contains(@id,'mark-spam') or contains(@id,'email-mark-spam') or @aria-label='Mark spam' or contains(@title,'spam')]")
        ),
    ],
)

ARCHIVE_EMAIL = _uc(
    "ARCHIVE_EMAIL",
    prompt="Archive the email where subject contains 'Project'",
    actions=[
        NavigateAction(url="http://localhost:8005/?seed=1"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='archive-button' or contains(@id,'archive-button') or contains(@id,'archive_button')])[1]")),
    ],
)


def load_automail_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "SEARCH_EMAIL": SEARCH_EMAIL,
        "VIEW_TEMPLATES": VIEW_TEMPLATES,
        "TEMPLATE_SELECTED": TEMPLATE_SELECTED,
        "TEMPLATE_BODY_EDITED": TEMPLATE_BODY_EDITED,
        "TEMPLATE_SENT": TEMPLATE_SENT,
        "TEMPLATE_SAVED_DRAFT": TEMPLATE_SAVED_DRAFT,
        "TEMPLATE_CANCELED": TEMPLATE_CANCELED,
        "EMAILS_NEXT_PAGE": EMAILS_NEXT_PAGE,
        "EMAILS_PREV_PAGE": EMAILS_PREV_PAGE,
        "CLEAR_SELECTION": CLEAR_SELECTION,
        "CREATE_LABEL": CREATE_LABEL,
        "THEME_CHANGED": THEME_CHANGED,
        "ADD_LABEL": ADD_LABEL,
        "SEND_EMAIL": SEND_EMAIL,
        "EMAIL_SAVE_AS_DRAFT": EMAIL_SAVE_AS_DRAFT,
        "EDIT_DRAFT_EMAIL": EDIT_DRAFT_EMAIL,
        "REPLY_EMAIL": REPLY_EMAIL,
        "FORWARD_EMAIL": FORWARD_EMAIL,
        "VIEW_EMAIL": VIEW_EMAIL,
        "STAR_AN_EMAIL": STAR_AN_EMAIL,
        "MARK_EMAIL_AS_IMPORTANT": MARK_EMAIL_AS_IMPORTANT,
        "MARK_AS_UNREAD": MARK_AS_UNREAD,
        "DELETE_EMAIL": DELETE_EMAIL,
        "MARK_AS_SPAM": MARK_AS_SPAM,
        "ARCHIVE_EMAIL": ARCHIVE_EMAIL,
    }
