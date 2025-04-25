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
   - All **specific values** used in constraints (e.g., names, strings) MUST be enclosed in **single quotes ('')
   - Example: "director is NOT 'Robert Zemeckis'", not just "director is not Robert Zemeckis"

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

## CURRENT CONSTRAINT SET
{constraints_info}

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

- Generate {number_of_prompts} prompts that are 100% constraint-compliant,
  using varied but precise language that captures the EXACT constraints.
"""
