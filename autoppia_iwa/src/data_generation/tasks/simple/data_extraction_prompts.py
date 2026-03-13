DATA_EXTRACTION_TASK_GENERATION_PROMPT = """
SYNTHETIC DATA-EXTRACTION QUESTION GENERATION PROTOCOL

## USE CASE DETAILS
- Name: {use_case_name}
- Description: {use_case_description}

## GOAL
You generate a SINGLE natural-language QUESTION whose answer can be extracted directly
from the target web page for this use case.

Examples of valid question styles:
- "When was the movie 'Gladiator' released?"
- "Who is the director of 'Inception'?"
- "What is the rating of the movie 'The Matrix'?"

## CONSTRAINT CONTEXT
You will receive a description of constraints that identify the specific entity
on the page (for example, which movie to open).

Current constraints:
{constraints_info}

You MUST:
- Use these constraints to decide WHICH entity you are asking about (e.g. which movie).
- NOT restate all constraints in the question; the question itself should be short and natural.
- Ask about a SINGLE concrete fact (year, director, rating, title, etc.) that is clearly visible on the page.

## ADDITIONAL INFO
{additional_prompt_info}

## OUTPUT FORMAT
- Output MUST be a JSON array with a single string element.
- That string is the final user-facing QUESTION.
- Do NOT include any explanation, markdown, or other wrapper text.

Example:
[
  "When was the movie 'Gladiator' released?"
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
