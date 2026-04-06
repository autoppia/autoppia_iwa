from __future__ import annotations

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
        "url": "http://localhost:8005/?seed=53",
        "prompt": "Search for query containing 'Weekly Newsletter'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=53",
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
        "url": "http://localhost:8005/?seed=919",
        "prompt": "Open the email templates page.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=919",
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
        "url": "http://localhost:8005/?seed=829",
        "prompt": "Select the template where template_name equals 'Meeting Recap'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=829",
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
        "url": "http://localhost:8005/?seed=336",
        "prompt": "Update the body text of the template where template_name equals 'Warm Introduction'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=336",
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
        "url": "http://localhost:8005/?seed=665",
        "prompt": "Send an email using the template where template_name equals 'Friendly Follow Up' and to equals 'john.doe@gmail.com'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=665",
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
        "url": "http://localhost:8005/?seed=879",
        "prompt": "Save the template as draft where template_name equals 'Meeting Recap' and to equals 'alice@company.com'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=879",
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
        "url": "http://localhost:8005/?seed=885",
        "prompt": "Cancel changes on the template where template_name equals 'Thank You'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=885",
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
        "url": "http://localhost:8005/?seed=779",
        "prompt": "Go to the next page of emails.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=779",
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
        "url": "http://localhost:8005/?seed=821",
        "prompt": "Go back to the previous page of emails.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=821",
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
        "url": "http://localhost:8005/?seed=344",
        "prompt": "Clear the current selection.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=344",
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
        "url": "http://localhost:8005/?seed=184",
        "prompt": "Create a label named 'Work' with color 'blue'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=184",
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
        "url": "http://localhost:8005/?seed=542",
        "prompt": "Apply dark mode appearance",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=542",
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
        "url": "http://localhost:8005/?seed=357",
        "prompt": "Add the label 'Work' to the email from 'eric.baker@management.com'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=357",
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
        "url": "http://localhost:8005/?seed=526",
        "prompt": "Send the email to john.doe@gmail.com with subject 'Project Timeline Update'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=526",
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
        "url": "http://localhost:8005/?seed=937",
        "prompt": "Save the email as draft where email equals jane.doe@example.com",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=937",
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
        "url": "http://localhost:8005/?seed=47",
        "prompt": "Edit the draft email where to equals 'jane.doe@example.com' and subject equals 'Client Proposal Updates'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=47",
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
        "url": "http://localhost:8005/?seed=311",
        "prompt": "Reply to the email where from_email equals 'eric.baker@management.com' and subject equals 'Year-End Review Meeting - Schedule'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=311",
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
        "url": "http://localhost:8005/?seed=903",
        "prompt": "Forward the email where from_email equals 'eric.baker@management.com' and subject equals 'Year-End Review Meeting - Schedule' and to equals 'john.doe@gmail.com'.",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=903",
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
        "url": "http://localhost:8005/?seed=669",
        "prompt": "View the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=669",
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
        "url": "http://localhost:8005/?seed=538",
        "prompt": "Star the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=538",
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
        "url": "http://localhost:8005/?seed=20",
        "prompt": "Mark the email as important where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=20",
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
        "url": "http://localhost:8005/?seed=912",
        "prompt": "Mark the email as unread where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=912",
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
        "url": "http://localhost:8005/?seed=373",
        "prompt": "Delete the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=373",
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
        "url": "http://localhost:8005/?seed=860",
        "prompt": "Mark the email as spam where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=860",
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
        "url": "http://localhost:8005/?seed=562",
        "prompt": "Archive the email where subject contains 'Project'",
        "actions": [
            {
                "url": "http://localhost:8005/?seed=562",
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


# CheckEventTest payloads aligned with automail_tasks.json (per use_case.name).
_RAW_TESTS: dict[str, list[dict]] = {
    "SEARCH_EMAIL": [
        {"type": "CheckEventTest", "event_name": "SEARCH_EMAIL", "event_criteria": {"query": {"operator": "not_equals", "value": "13"}}, "description": "Check if specific event was triggered"}
    ],
    "CLEAR_SELECTION": [{"type": "CheckEventTest", "event_name": "CLEAR_SELECTION", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "EMAILS_NEXT_PAGE": [{"type": "CheckEventTest", "event_name": "EMAILS_NEXT_PAGE", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "EMAILS_PREV_PAGE": [{"type": "CheckEventTest", "event_name": "EMAILS_PREV_PAGE", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "VIEW_TEMPLATES": [{"type": "CheckEventTest", "event_name": "VIEW_TEMPLATES", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "TEMPLATE_SELECTED": [
        {
            "type": "CheckEventTest",
            "event_name": "TEMPLATE_SELECTED",
            "event_criteria": {"template_name": {"operator": "not_contains", "value": "aui"}, "subject": "Quick follow-up on our last conversation"},
            "description": "Check if specific event was triggered",
        }
    ],
    "TEMPLATE_BODY_EDITED": [
        {
            "type": "CheckEventTest",
            "event_name": "TEMPLATE_BODY_EDITED",
            "event_criteria": {"subject": {"operator": "not_equals", "value": "Introduction & Next Steps"}, "template_name": {"operator": "not_equals", "value": "Friendly Follow Up"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "TEMPLATE_SENT": [
        {
            "type": "CheckEventTest",
            "event_name": "TEMPLATE_SENT",
            "event_criteria": {"template_name": {"operator": "not_contains", "value": "tke"}, "subject": {"operator": "contains", "value": "hank you for you"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "TEMPLATE_SAVED_DRAFT": [
        {
            "type": "CheckEventTest",
            "event_name": "TEMPLATE_SAVED_DRAFT",
            "event_criteria": {"template_name": {"operator": "contains", "value": "ank"}, "to": {"operator": "not_contains", "value": "pkc"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "TEMPLATE_CANCELED": [
        {
            "type": "CheckEventTest",
            "event_name": "TEMPLATE_CANCELED",
            "event_criteria": {
                "to": "harper.adams@newsdaily.com",
                "subject": "Recap: key notes from our meeting",
                "template_name": {"operator": "not_contains", "value": "kgd"},
                "body": {"operator": "not_contains", "value": "ivd"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_EMAIL",
            "event_criteria": {"from_email": "noah.turner@compliance.com", "subject": {"operator": "contains", "value": "cember"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ARCHIVE_EMAIL": [
        {"type": "CheckEventTest", "event_name": "ARCHIVE_EMAIL", "event_criteria": {"subject": "Weekly Newsletter - December 19"}, "description": "Check if specific event was triggered"}
    ],
    "STAR_AN_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "STAR_AN_EMAIL",
            "event_criteria": {"is_starred": False, "from_email": {"operator": "not_contains", "value": "vzc"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "MARK_EMAIL_AS_IMPORTANT": [
        {
            "type": "CheckEventTest",
            "event_name": "MARK_EMAIL_AS_IMPORTANT",
            "event_criteria": {"is_important": True, "from_email": {"operator": "not_equals", "value": "ashley.wright@outlook.com"}, "subject": "Hey! Long time no see"},
            "description": "Check if specific event was triggered",
        }
    ],
    "MARK_AS_UNREAD": [
        {
            "type": "CheckEventTest",
            "event_name": "MARK_AS_UNREAD",
            "event_criteria": {"is_read": False, "subject": {"operator": "contains", "value": "Ju"}, "from_email": {"operator": "contains", "value": "y.walker@offers.com"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "DELETE_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "DELETE_EMAIL",
            "event_criteria": {"from_email": {"operator": "contains", "value": "garcia@deals.com"}, "subject": {"operator": "contains", "value": "ly Digest - June"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "MARK_AS_SPAM": [
        {
            "type": "CheckEventTest",
            "event_name": "MARK_AS_SPAM",
            "event_criteria": {"is_spam": True, "subject": {"operator": "contains", "value": "nd pl"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_LABEL": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_LABEL",
            "event_criteria": {
                "label_name": {"operator": "not_equals", "value": "Finance"},
                "body": {"operator": "contains", "value": "zing day filled with joy and cele"},
                "subject": {"operator": "contains", "value": "Birthday"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CREATE_LABEL": [
        {"type": "CheckEventTest", "event_name": "CREATE_LABEL", "event_criteria": {"label_name": {"operator": "not_contains", "value": "bxn"}}, "description": "Check if specific event was triggered"}
    ],
    "SEND_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "SEND_EMAIL",
            "event_criteria": {
                "to": {"operator": "not_equals", "value": "jackson.evans@customsoft.dev"},
                "subject": {"operator": "not_equals", "value": "Special Offer - 30% Off"},
                "body": {"operator": "contains", "value": "ou"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EMAIL_SAVE_AS_DRAFT": [
        {
            "type": "CheckEventTest",
            "event_name": "EMAIL_SAVE_AS_DRAFT",
            "event_criteria": {"to": "ava.wilson@healthcare.org", "subject": {"operator": "contains", "value": "Apr"}, "body": {"operator": "contains", "value": "articles, and insights from"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_DRAFT_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_DRAFT_EMAIL",
            "event_criteria": {"to": "zoe.baker@civicgroup.org", "body": {"operator": "contains", "value": "customer, we're offering you 50% off an annual subscription. This offer ex"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "REPLY_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "REPLY_EMAIL",
            "event_criteria": {"to": {"operator": "not_equals", "value": "isabella.clark@freelancer.dev"}, "subject": {"operator": "contains", "value": "Welcome to TaskMas"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "FORWARD_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "FORWARD_EMAIL",
            "event_criteria": {"to": {"operator": "contains", "value": "inte"}, "body": {"operator": "contains", "value": "l on An"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "THEME_CHANGED": [{"type": "CheckEventTest", "event_name": "THEME_CHANGED", "event_criteria": {"theme": "light"}, "description": "Check if specific event was triggered"}],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


BASE = "http://localhost:8005"
# From automail_tasks.json (?seed= in each task URL)
SEED_SEARCH_EMAIL = 53
SEED_CLEAR_SELECTION = 344
SEED_EMAILS_NEXT_PAGE = 779
SEED_EMAILS_PREV_PAGE = 821
SEED_VIEW_TEMPLATES = 919
SEED_TEMPLATE_SELECTED = 829
SEED_TEMPLATE_BODY_EDITED = 336
SEED_TEMPLATE_SENT = 665
SEED_TEMPLATE_SAVED_DRAFT = 879
SEED_TEMPLATE_CANCELED = 885
SEED_VIEW_EMAIL = 669
SEED_ARCHIVE_EMAIL = 562
SEED_STAR_AN_EMAIL = 538
SEED_MARK_EMAIL_AS_IMPORTANT = 20
SEED_MARK_AS_UNREAD = 912
SEED_DELETE_EMAIL = 373
SEED_MARK_AS_SPAM = 860
SEED_ADD_LABEL = 357
SEED_CREATE_LABEL = 184
SEED_SEND_EMAIL = 526
SEED_EMAIL_SAVE_AS_DRAFT = 937
SEED_EDIT_DRAFT_EMAIL = 47
SEED_REPLY_EMAIL = 311
SEED_FORWARD_EMAIL = 903
SEED_THEME_CHANGED = 542

SEARCH_EMAIL = _uc(
    "SEARCH_EMAIL",
    prompt="Search for emails where the query is NOT '13'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SEARCH_EMAIL}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
    ],
)

VIEW_TEMPLATES = _uc(
    "VIEW_TEMPLATES",
    prompt="Open the email templates section.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_VIEW_TEMPLATES}"),
        ClickAction(selector=_id("sidebar-templates")),
    ],
)

TEMPLATE_SELECTED = _uc(
    "TEMPLATE_SELECTED",
    prompt="Select the template where template_name does NOT contain 'aui' and subject equals 'Quick follow-up on our last conversation'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_TEMPLATE_SELECTED}"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
    ],
)

TEMPLATE_BODY_EDITED = _uc(
    "TEMPLATE_BODY_EDITED",
    prompt="Edit the body of the template where subject is NOT 'Introduction & Next Steps' and template_name is NOT 'Friendly Follow Up'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_TEMPLATE_BODY_EDITED}"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
        ClickAction(selector=_xp("//*[@id='template-body' or @id='template-content' or @aria-label='Body']")),
        TypeAction(selector=_xp("//*[@id='template-body' or @id='template-content' or @aria-label='Body']"), text="__EMAIL_BODY__"),
        ClickAction(selector=_xp("//*[@id='template-body' or @id='template-content' or @aria-label='Body']")),
    ],
)

TEMPLATE_SENT = _uc(
    "TEMPLATE_SENT",
    prompt="Send email using the template where template_name not contains 'tke' and subject contains 'hank you for you'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_TEMPLATE_SENT}"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
        ClickAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']")),
        TypeAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//*[@id='template-send' or @id='send-button' or @aria-label='Send' or normalize-space()='Send']")),
    ],
)

TEMPLATE_SAVED_DRAFT = _uc(
    "TEMPLATE_SAVED_DRAFT",
    prompt="Save the template as draft where template_name contains 'ank' and to not contains 'pkc'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_TEMPLATE_SAVED_DRAFT}"),
        ClickAction(selector=_id("sidebar-templates")),
        ClickAction(selector=_xp("__TEMPLATE_OPTION__")),
        ClickAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']")),
        TypeAction(selector=_xp("//*[@id='template-to' or @id='template-recipient' or @aria-label='To']"), text="__EMAIL_TO__"),
        ClickAction(selector=_xp("//*[@id='template-save' or @id='save-draft-button' or @aria-label='Save draft' or normalize-space()='Save draft']")),
    ],
)

TEMPLATE_CANCELED = _uc(
    "TEMPLATE_CANCELED",
    prompt="Cancel template where to equals 'harper.adams@newsdaily.com' and subject equals 'Recap: key notes from our meeting' and template_name not contains 'kgd' and body not contains 'ivd'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_TEMPLATE_CANCELED}"),
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
        NavigateAction(url=f"{BASE}/?seed={SEED_EMAILS_NEXT_PAGE}"),
        ClickAction(selector=_xp("//*[@id='next-page-button' or @data-testid='next-page-button' or @aria-label='Next page' or @title='Next page'] | //*[@data-testid='email-list']//button[2]")),
    ],
)

EMAILS_PREV_PAGE = _uc(
    "EMAILS_PREV_PAGE",
    prompt="Go back to the previous page of emails.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EMAILS_PREV_PAGE}"),
        ClickAction(selector=_xp("//*[@data-testid='email-list']/div[1]/div[2]/div/button[2]")),
        ClickAction(selector=_xp("//*[@data-testid='email-list']/div[1]/div[2]/div/button[1]")),
    ],
)

CLEAR_SELECTION = _uc(
    "CLEAR_SELECTION",
    prompt="Clear the current selection of emails.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CLEAR_SELECTION}"),
        ClickAction(selector=_xp("(//*[@id='email-card']/div[1]/button)[1]")),
        ClickAction(selector=_xp("//*[@aria-label='Clear Selection' or @id='clear-selection-button' or @data-testid='clear-selection-button'] | //*[@data-testid='email-list']/div[2]/button[6]")),
    ],
)

CREATE_LABEL = _uc(
    "CREATE_LABEL",
    prompt="Create a new label with the name that does NOT contain 'bxn'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CREATE_LABEL}"),
        ClickAction(selector=_id("label-selector-trigger")),
        ClickAction(selector=_xp("//*[@id='label-selector-menu']//input[1]")),
        TypeAction(selector=_xp("//*[@id='label-selector-menu']//input[1]"), text="__LABEL_NAME__"),
        ClickAction(selector=_id("label-color-4285f4")),
        ClickAction(selector=_id("create-label-button")),
    ],
)

THEME_CHANGED = _uc(
    "THEME_CHANGED",
    prompt="Change the application theme to 'light' where the theme equals 'light'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_THEME_CHANGED}"),
        ClickAction(selector=_xp("(//button[@aria-label='User account menu' or .//span[normalize-space()='U']])[1]")),
        ClickAction(selector=_xp("__THEME_BUTTON__")),
    ],
)

ADD_LABEL = _uc(
    "ADD_LABEL",
    prompt="Add a label to the email where the label_name is NOT 'Finance', the body contains 'zing day filled with joy and cele', and the subject contains 'Birthday'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_LABEL}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__ADD_LABEL_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("(//*[@id='email-label-selector']//*[self::button][1] | //*[@id='label-selector' or @id='tag-selector' or @id='label-picker'])[1]")),
        ClickAction(selector=_xp("__ADD_LABEL_OPTION__")),
    ],
)

SEND_EMAIL = _uc(
    "SEND_EMAIL",
    prompt="Send an email to 'recipient@example.com', ensuring the recipient does NOT equal 'jackson.evans@customsoft.dev' and the subject does NOT equal 'Special Offer - 30% Off' and the body contains 'ou'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SEND_EMAIL}"),
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
    prompt="Save the email as a draft addressed to 'ava.wilson@healthcare.org' with the subject that CONTAINS 'Apr' and the body that CONTAINS 'articles, and insights from'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EMAIL_SAVE_AS_DRAFT}"),
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
    prompt="Edit the draft email where to equals 'zoe.baker@civicgroup.org' and body contains 'customer, we're offering you 50% off an annual subscription. This offer ex'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_DRAFT_EMAIL}"),
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
    prompt="Reply to the email where from_email NOT equals 'isabella.clark@freelancer.dev' and subject contains 'Welcome to TaskMas'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_REPLY_EMAIL}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__REPLY_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("//*[@id='email-reply' or @id='reply-button' or @id='respond-button' or @id='answer-button' or @aria-label='Reply to this email']")),
        ClickAction(selector=_xp("//button[@id='send-button' or @id='deliver-button' or @id='dispatch-button' or @aria-label='Send' or normalize-space()='Send']")),
    ],
)

FORWARD_EMAIL = _uc(
    "FORWARD_EMAIL",
    prompt="Forward the email where to contains 'inte' and body contains 'l on An'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_FORWARD_EMAIL}"),
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
    prompt="View the email where from_email equals 'noah.turner@compliance.com' and subject contains 'cember'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_VIEW_EMAIL}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
    ],
)

STAR_AN_EMAIL = _uc(
    "STAR_AN_EMAIL",
    prompt="Star the email where is_starred equals False and from_email not contains 'vzc'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_STAR_AN_EMAIL}"),
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
    prompt="Mark the email as important where is_important equals 'True' and from_email not equals 'ashley.wright@outlook.com' and subject equals 'Hey! Long time no see'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_MARK_EMAIL_AS_IMPORTANT}"),
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
    prompt="Mark the email as unread where is_read equals False and subject contains 'Ju' and from_email contains 'y.walker@offers.com'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_MARK_AS_UNREAD}"),
        ClickAction(selector=_id("search-input")),
        TypeAction(selector=_id("search-input"), text="__SEARCH_QUERY__"),
        ClickAction(selector=_xp("(//*[@id='view-email'])[1]")),
        ClickAction(selector=_xp("//*[@id='email-mark-unread' or @id='mark-unread-button' or contains(@id,'mark-unread') or @aria-label='Mark unread' or contains(@title,'unread')]")),
    ],
)

DELETE_EMAIL = _uc(
    "DELETE_EMAIL",
    prompt="Delete the email from sender whose email contains 'garcia@deals.com' with the subject containing 'ly Digest - June'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_DELETE_EMAIL}"),
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
    prompt="Mark as spam the email with subject that CONTAINS 'nd pl' and is_spam equals True.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_MARK_AS_SPAM}"),
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
    prompt="Archive the email whose subject equals 'Weekly Newsletter - December 19'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ARCHIVE_EMAIL}"),
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
