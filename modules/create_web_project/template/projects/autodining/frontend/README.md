
# Autodining Template – Fullstack (Next.js)

This is the **canonical template** for creating new web projects for IWA. It is a complete copy of the production `web_4_autodining` project, including:

- ✅ **Dynamic System (v1/v2/v3)**: Complete anti-scraping implementation
  - V1: DOM structure modification (add-wrap-decoy, change-order-elements)
  - V3: Attribute and text variation (IDs, classes, texts via variant-selector)
  - Shared: Core functions (selectVariantIndex, hashString)
- ✅ **Seed System**: URL-based seed management with SeedContext
- ✅ **Event Logging**: Backend integration for event tracking (100% coverage)
- ✅ **Tests**: Automated validation tests for dynamic system and events
  - `tests/test-dynamic-system.js` - Validates dynamic system (7 tests)
  - `tests/test-events.js` - Validates event coverage (100% required)

Built using **Next.js** (App Router), styled with **TailwindCSS**, and fully Dockerized.

**Note**: This template is a functional copy of `web_4_autodining`. All tests pass and the dynamic system is fully implemented in the codebase.

---
## Prerequisites

Ensure the following tools are installed:

- **Node.js v20+** (use [nvm](https://github.com/nvm-sh/nvm) for version management)
- **npm v9+** or **yarn**
- **Git**
- **Unix-like shell** (macOS, Linux, or WSL on Windows)
- **Permission** to execute scripts (`chmod +x entrypoint.sh`)

**Optional but recommended:**

- **VS Code** with [TailwindCSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)
- **Postman** or any HTTP client for API testing

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/autoppia/autoppia_webs_demo.git

cd web_4_autodining
```
## Installation & Deployment
<pre> ```docker-compose up --build ``` </pre>

## Incase of any issues with Docker, RUN
<pre> ```docker-compose down -v ``` </pre>

---
## Event-log.json
- All the events will be stored in the file which is named as event-log.json


## Project Structure

```
frontend/
├── src/
│   ├── dynamic/              # Dynamic anti-scraping system
│   │   ├── v1/               # DOM structure modification
│   │   ├── v2-data/          # Data loading with seeds
│   │   ├── v3/               # Attribute/text variation
│   │   └── shared/           # Core functions (selectVariantIndex, etc.)
│   ├── context/
│   │   └── SeedContext.tsx   # Seed management
│   ├── library/
│   │   └── events.ts         # Event logging
│   └── app/                  # Next.js pages
├── tests/                    # Automated tests
│   ├── test-dynamic-system.js
│   ├── test-events.js
│   └── README.md
└── docker-compose.yml
```

## Running Tests

```bash
# Test dynamic system
node tests/test-dynamic-system.js

# Test event coverage
node tests/test-events.js
```

## Entrypoint Script – entrypoint.sh
This script is executed automatically when the container starts. It:
- **Removes old build artifacts (.next, package-lock.json)**
- **Installs dependencies via npm install**
- **Launches the Next.js dev server on port 8003**
