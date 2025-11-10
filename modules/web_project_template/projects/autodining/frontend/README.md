
# Dining Hours – Fullstack (Next.js)

Dining Hours is a fullstack e-commerce web application built using **Next.js** (App Router), styled with **TailwindCSS**, and equipped with a custom event logging system that captures frontend interactions and writes them to a local file: `event-log.json`.

This version is fully Dockerized, allowing seamless setup and deployment with minimal local dependencies.

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


## Entrypoint Script – entrypoint.sh
This script is executed automatically when the container starts. It:
- **Removes old build artifacts (.next, package-lock.json)**
- **Installs dependencies via npm install**
- **Launches the Next.js dev server on port 8003**