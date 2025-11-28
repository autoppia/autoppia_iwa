# Web Project Submission Template

This template shows community contributors **exactly** what they must provide so
the Autoppia team can run IWA verification automatically. It now ships with a
full copy of **Project 4 (Autodining)** as the canonical example.

## Required Files

- `projects/<your_project>/config.yaml`: deck-aware metadata (see
  `projects/autodining/config.yaml`, which mirrors the production `dining_4`
  module).
- `projects/<your_project>/docker-compose.yml`: reproducible deployment of your
  frontend (all projects share the same backend endpoint; set
  `AUTOPPIA_BACKEND_URL` so the UI points to the shared validator backend).
- Drop your code under `projects/<your_project>/frontend/`. Duplicate
  `projects/autodining` for every new submission.

## Config Overview

| Section              | Purpose                                                    |
| -------------------- | ---------------------------------------------------------- |
| `project`            | Slug, human name, contact, seed instructions, deck id      |
| `deployment`         | Frontend/backend URLs, optional Autoppia port indexes      |
| `events`             | Structured event classes + backend payload mappings        |
| `use_cases`          | Canonical tasks that must emit those events                |
| `pages` *(optional)* | URL patterns + selectors that Playwright must validate     |

> The Autoppia team owns the decks. Contributors adapt their project to the deck
> and fill this config so the tooling can auto-generate the Python module.

## Workflow

1. Fork this template.
2. For each web project you submit, copy `projects/autodining` to
   `projects/<your_slug>` and customize:
   - Update `config.yaml`
    - Implement the frontend under that directory
   - Keep the per-project `docker-compose.yml` runnable locally
3. When ready, submit the repo. Autoppia’s pipeline will:
   - Clone the repo
   - Run `python -m modules.web_verification generate-module projects/<slug>/config.yaml`
   - Execute Phase 1/2 checks (deck + Playwright)
   - Deploy the Docker Compose stack to sandbox if both phases pass

If any step fails, the bot annotations will indicate which config values or
frontend selectors must be adjusted.

## Autodining Reference Config

To validate the extractor logic against a real project:

```bash
python -m modules.web_verification generate-module \
  --config web_project_template/projects/autodining/config.yaml \
  --output-root modules/web_verification/sandbox_analysis/generated_projects \
  --force

diff -ru autoppia_iwa/src/demo_webs/projects/dining_4 \
        modules/web_verification/sandbox_analysis/generated_projects/autodining
```

Expect differences wherever the hand-written module uses custom helper logic
(for example, dynamic constraint generators). The diff is still helpful to
verify that events, use cases, and prompts align with the real project.

## One-Shot Verification from Config

Once your repo exposes `config.yaml`, you (or the Autoppia bot) can run:

```bash
python -m modules.web_verification verify \
  --config web_project_template/projects/autodining/config.yaml \
  --deck path/to/deck.deck.json
```

`--config` generates the `main.py`/`events.py`/`use_cases.py` files on the fly
before running Phase 1/2 checks. Pass `--force-config` if you need to overwrite
an existing module directory with the generated output.
