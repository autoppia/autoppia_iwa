"""JSON schema and prompting templates for LLM-backed semantic labels."""

SCHEMA_JSON = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "page_type": {
            "type": "string",
            "enum": [
                "home",
                "search",
                "listing",
                "product",
                "cart",
                "checkout",
                "form",
                "unknown",
            ],
        },
        "goal_progress": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "affordances": {
            "type": "object",
            "properties": {
                "can_go_back": {"type": "boolean"},
                "can_search": {"type": "boolean"},
                "can_filter": {"type": "boolean"},
                "can_add_to_cart": {"type": "boolean"},
                "can_submit_form": {"type": "boolean"},
            },
            "required": [
                "can_go_back",
                "can_search",
                "can_filter",
                "can_add_to_cart",
                "can_submit_form",
            ],
            "additionalProperties": {"type": "boolean"},
        },
        "nav_depth": {"type": "integer", "minimum": 0},
        "item_count": {"type": "integer", "minimum": 0},
        "price_present": {"type": "boolean"},
        "pagination_state": {
            "type": "string",
            "enum": ["none", "has_next", "has_prev", "both"],
        },
        "salient_entities": {"type": "array", "items": {"type": "string"}},
        "is_on_wrong_product": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["page_type", "goal_progress", "affordances"],
}


SYSTEM_PROMPT = (
    "You are a precise web-state analyst. Given a URL and a cleaned DOM excerpt, "
    "produce semantic labels following the provided JSON schema. Report only what "
    "the evidence supports. When unsure, fall back to safe defaults (item_count=0, "
    "price_present=false, confidence≈0.5)."
)


USER_TEMPLATE = (
    "URL: {url}\n\n"
    "DOM (cleaned, <=3KB):\n{dom}\n\n"
    "Respond strictly with JSON matching the schema and fill every field."
)
