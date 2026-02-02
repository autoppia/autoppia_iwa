GLOBAL_TASK_GENERATION_PROMPT = """
SYNTHETIC PROMPT GENERATION PROTOCOL

## USE CASE DETAILS
- Name: {use_case_name}
- Description: {use_case_description}

## ABSOLUTE CONSTRAINT GENERATION RULES
🔍 CRITICAL REQUIREMENTS:
1. MANDATORY: Include ALL constraints - NO EXCEPTIONS
   - Every single constraint MUST be present
   - Use EXACT constraint wording
   - NO additional criteria allowed

2. PROMPT COMPOSITION GUIDELINES
   - Phrase as a natural language request
   - Use variations like:
     * "Show details for..."
     * "Give me information about..."
     * "Retrieve details of..."

3. CONSTRAINT VALUE FORMATTING
   - All **specific values** used in constraints (e.g., names, strings) MUST be enclosed in **single quotes ('')**
   - Example: "director is NOT 'Robert Zemeckis'", not just "director is not Robert Zemeckis"

4. INTERPRETING CONTAINS VS. EQUALS:
   - If the constraint includes the word **'contains'**, it means the specified word or phrase is **part of** the complete value (i.e., the full value can contain more than just the given word).
     - Example: "title contains 'Ring'" → matches "The Lord of the Rings"
   - If the constraint uses **'equals'**, literal word equals (or equal to) between the field name and the value and ensure that the full value is **exactly equal** to the specified one — no more, no less.
     - Example: "genre equals 'Romance'" → only matches books with genre equals 'Romance'

## CONSTRAINT REPRESENTATION EXAMPLE
If constraints are "director not_equals Robert Zemeckis AND year greater_than 2010":
✅ CORRECT:
- "Show me details about a movie NOT directed by 'Robert Zemeckis' that was released AFTER 2010"
- "Retrieve information for a film where the director is NOT 'Robert Zemeckis' and the release year EXCEEDS 2010"

❌ INCORRECT:
- "Show a movie directed by Christopher Nolan" (missing constraints)
- "Show a movie after 2010 with a high rating" (added unauthorized criteria)

If constraints are "director contains 'd Cop' AND duration less_equal 178":
✅ CORRECT:
- "Give me information about a movie directed by a director whose name CONTAINS 'd Cop' with a duration of 178 minutes or less"

❌ INCORRECT:
- "Give me information about a movie directed by d Cop with a duration of 178 minutes or less" (constraint is not clear - 'd Cop' is not the name of the director; you meant it should **contain** 'd Cop'. Be clear with constraints.)

Be clear with constraints, especially when referring to CONTAINS or NOT CONTAINS.

YOU HAVE TO MENTION ALWAYS THE FIELD WHICH APPEARS IN THE CONSTRAINT
✅ CORRECT:
Please book a table for 1 person at a restaurant which cuisine is Mexican on '2025-07-21'  at '1:00 PM'.
Please book a table for 2 person at a restaurant with name "Oak Beer" on '2025-07-21'  at '1:00 PM'.

❌ INCORRECT:
Please book a table for 1 person at a Mexican on '2025-07-21'  at '1:00 PM'.
Please book a table for 2 person at a "Oak Beer" restaurant on '2025-07-21'  at '1:00 PM'.

## CURRENT CONSTRAINT SET
{constraints_info}

Do not generate the constraint for this prompt if the constraint set above does not contains the constraints.
BE SPECIFIC WITH CONSTRAINTS TRY TO MENTION ALWAYS THE FIELD OF THE CONSTRAINT for instance NAME, DESCRIPTION ETC
DO NOT ADD TWO CONSTRAINTS ABOUT THE SAME FIELD, LIKE DIRECTION (EXAMPLE: "Scroll left in the carousel where the direction is 'RIGHT'") - THIS IS NOT ALLOWED.
## ADDITIONAL INFO
{additional_prompt_info}

## GENERATION PROTOCOL
- Format: JSON array of strings
- EACH PROMPT MUST:
  * Include ALL constraints verbatim
  * Wrap specific values in single quotes
  * Sound like a natural request
  * Match the use case description
  * EXCLUDE any additional criteria

- Generate 1 prompts that are 100% constraint-compliant,
  using varied but precise language that captures the EXACT constraints.
"""
