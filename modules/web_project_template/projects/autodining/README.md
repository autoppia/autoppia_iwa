# Autodining Reference Project

This folder contains the full **project 4 (Autodining)** Next.js frontend used in
production. It serves as the canonical example of how a contributor repository
should look when targeting the Autodining deck.

Structure:

```
projects/autodining/
├── config.yaml            # Deck-level metadata for module extraction
├── docker-compose.yml     # Runs the frontend pointing to AUTOPPIA_BACKEND_URL
└── frontend/              # Real Next.js application (copied from project 4)
```

To run locally:

```bash
cd projects/autodining
AUTOPPIA_BACKEND_URL=http://localhost:8090 docker compose up --build
```

To regenerate the IWA module from this config:

```bash
python -m modules.web_verification.entrypoints.generate_module \
  --config web_project_template/projects/autodining/config.yaml \
  --output-root modules/web_verification/sandbox_analysis/generated_projects \
  --force
```

Then diff the generated module with the existing `dining_4` code inside the
main repo to validate parity.
