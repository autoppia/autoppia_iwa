# Config Schema

`python -m modules.web_verification.entrypoints.generate_module` accepts either **YAML** (`.yml`/`.yaml`) or
**JSON** configs with the following structure. All fields are required unless
noted.

```yaml
project:
  slug: string               # lowercase identifier (used as folder name)
  name: string               # human-friendly name
  deck_id: string            # must match existing Autoppia deck id
  owner: string              # GitHub handle or email
  summary: string            # 1-2 sentence overview
  contact: string            # maintainer contact
  seed_notes: string         # optional notes describing dynamic seeds
deployment:
  frontend_url: string       # absolute URL OR omit to use port indexes
  backend_url: string
  frontend_port_index: int   # optional Autoppia port index helper
  backend_port_index: int
events:
  - name: string             # matches deck use case event_name
    description: string
    fields:                  # fields emitted by backend payload
      - name: string
        type: str|int|float|bool
        source: string       # key inside backend event.data
        optional: bool       # default false
    validation:              # optional, defaults to all fields
      - field: string        # references `fields.name`
use_cases:
  - name: string
    event: string            # references events[].name
    description: string
    additional_prompt_info: string
    prompts:
      - prompt: string
        template: string     # used for task generation
    constraints:             # optional – generates helper in generation_functions.py
      operator: equals|not_equals|contains|gt|gte|lt|lte
      examples:
        - field: string
          value: string|int|float|bool|list
pages:                       # optional (mirrors deck required pages)
  - id: string
    title: string
    url_patterns: [string]
    required_elements:
      - selector: string
        text_contains: string
        description: string
```

## Notes

- If `deployment.frontend_url`/`backend_url` are omitted, the generator will
  emit `get_frontend_url(index=frontend_port_index)` helpers so the project can
  run behind Autoppia’s shared endpoint.
- `constraints.examples` are baked into simple helper functions. For advanced
  behavior contributors can leave the section empty and plug a custom generator
  later.
- Additional sections can be added, but unknown keys are ignored.
