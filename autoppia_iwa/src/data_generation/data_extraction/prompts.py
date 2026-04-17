# Used when there is only a verify field (no question_fields_and_values): ask directly for the value of that field.
# E.g. date/time/people dropdown use cases: "What date is selected?", "What time is shown?", "How many guests?"
DATA_EXTRACTION_TASK_GENERATION_PROMPT_VERIFY_FIELD_ONLY = """
SYNTHETIC DATA-EXTRACTION QUESTION GENERATION PROTOCOL

## USE CASE DETAILS
- Name: {use_case_name}
- Description: {use_case_description}

## GOAL
You generate a SINGLE natural-language QUESTION that asks for the VALUE of a single field shown on the page.
There is no entity identifier; the question must ask what value is displayed or selected for this field.

## FIELD TO ASK FOR (verify field)
The question MUST ask for the value of: **{verify_field}**

Examples of valid question styles (adapt to the actual verify_field):
- For date: "What date is selected?", "What is the current date shown on page?"
- For time: "What time is displayed?", "What time is selected in the dropdown?"
- For people/guests: "How many guests are selected in dropdown?", "What is the number of selected people?"

You MUST:
- Ask specifically for the value of **{verify_field}** (what is shown/selected on the page).
- Keep the question short and natural.
- NOT include any entity identifier or extra constraints; only ask for this field's value.

## ADDITIONAL INFO
{additional_prompt_info}

## OUTPUT FORMAT
- Output MUST be a JSON array with a single string element.
- That string is the final user-facing QUESTION.
- Do NOT include any explanation, markdown, or other wrapper text.

Example (when verify_field is date):
[
  "What date is selected?"
]
"""

# Used when the generator provides question_fields_and_values (entity identifier for data_extraction_only).
# verify_field is the single fact to ask for; the LLM must generate a question that asks for this field's value.
DATA_EXTRACTION_TASK_GENERATION_PROMPT_WITH_QUESTION_FIELDS = """
SYNTHETIC DATA-EXTRACTION QUESTION GENERATION PROTOCOL

## USE CASE DETAILS
- Name: {use_case_name}
- Description: {use_case_description}

## GOAL
You generate a SINGLE natural-language QUESTION whose answer can be extracted directly
from the target web page. The question must:
1) Identify WHICH entity using the fields and values below.
2) Ask for the value of this specific field: **{verify_field}**

Examples of valid question styles (replace with the actual verify_field and entity identifier):
- "What is the accountType of the account that rank is 5?"
- "What is the balance of the account with rank 3?"
- "What is the stakedAmount of the account that rank is 1?"

## FIELD TO ASK FOR (verify field)
The question MUST ask for the value of: **{verify_field}**

## ENTITY IDENTIFIER
The entity to ask about is identified by the following fields and values (use these in the question):
{question_fields_info}

You MUST:
- Refer to the entity using these field(s) and value(s) (e.g. "the account that rank is 5").
- Ask specifically for the value of **{verify_field}** (e.g. "What is the {verify_field} of the account that ...").
- Keep the question short and natural.

## ADDITIONAL INFO
{additional_prompt_info}

## OUTPUT FORMAT
- Output MUST be a JSON array with a single string element.
- That string is the final user-facing QUESTION.
- Do NOT include any explanation, markdown, or other wrapper text.

Example (when verify_field is accountType):
[
  "What is the accountType of the account that rank is 5?"
]
"""
