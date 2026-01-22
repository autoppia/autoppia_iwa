
## 📘 **README — Task Generation API**

### 🧩 Overview

The **Task Generation API** provides an endpoint for generating benchmark tasks for demo web projects in the **Autoppia IWA** platform.

It uses **FastAPI** and integrates with `autoppia_iwa.entrypoints.benchmark.task_generation` to dynamically create project-specific benchmark tasks across multiple runs.

---

### ⚙️ **Endpoint**

#### **POST** `/generate-tasks`

Generate benchmark tasks for one or more demo web projects.

Each project’s results are grouped by **use case**, and multiple runs are combined together — meaning prompts from each run are appended to the same use-case group.

---

### 🧾 **Request Body**

| Parameter              | Type        | Default | Description                                                        |
| ---------------------- | ----------- | ------- | ------------------------------------------------------------------ |
| `projects`             | `List[str]` | —       | List of project IDs to generate tasks for.                         |
| `prompts_per_use_case` | `int`       | `1`     | Number of prompts to generate per use case.                        |
| `selective_use_cases`  | `List[str]` | `[]`    | Specific use cases to include. If empty, uses all available use cases. |
| `runs`                 | `int`       | `1`     | Number of times to regenerate tasks (results grouped across runs). |

---

### 🧪 **Example Request**

```bash
curl --location 'http://localhost:5080/generate-tasks' \
--header 'Content-Type: application/json' \
--data '{
  "projects": ["autoconnect", "autolodge"],
  "selective_use_cases": ["VIEW_HOTEL", "VIEW_USER_PROFILE"],
  "runs": 2
}'
```

---

### ✅ **Example Response**

```json
{
    "generated_tasks": [
        {
            "project_id": "autoconnect",
            "tasks": {
                "VIEW_USER_PROFILE": [
                    "Retrieve details of the user where the user's name does NOT CONTAIN 'fmm'.",
                    "View the profile of a user where the user's name does NOT contain 'vud'."
                ]
            }
        },
        {
            "project_id": "autolodge",
            "tasks": {
                "VIEW_HOTEL": [
                    "Show details for a hotel with the title equal to 'Bohemian Loft', where the amenities are NOT in the list ['Business ready', 'WiFi included'], the location does NOT contain 'vbv', and the reviews are less than 86.",
                    "Show details for a hotel where the price is GREATER THAN or EQUAL to '185', the title CONTAINS 'e', the amenities CONTAINS 'Eiffel Views', the reviews are GREATER THAN or EQUAL to '212', the rating is GREATER THAN or EQUAL to '4.8', and the host_name CONTAINS 'mil'."
                ]
            }
        }
    ]
}
```

> 💡 Each `use_case` key contains **prompts combined from all runs**, ensuring diverse generation results across multiple iterations.

---

### 🧱 **Project Structure**

```
autoppia_iwa/
└── entrypoints/
    └── generate_tasks/
        ├── generate_tasks_endpoint.py   # FastAPI endpoint implementation
        └── deploy_service.sh            # PM2 deployment script
```

---

### 🖥️ **Run Locally**

#### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

#### 3. Start the FastAPI service

```bash
python -m autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint --port 5080
```

Open your browser at:

👉 **[http://localhost:5080/docs](http://localhost:5080/docs)** — interactive Swagger UI
👉 **[http://localhost:5080/redoc](http://localhost:5080/redoc)** — alternative documentation view

---

### 🚀 **Deploy with PM2**

You can run the API persistently using the included **`deploy_service.sh`** script.

#### Run Deployment

```bash
chmod +x deploy_service.sh
./deploy_service.sh 5080
```

This script will:

* Stop any existing service on the same port
* Start a new instance using PM2
* Name the process as `generate-tasks-<port>`
* Save the PM2 process list for auto-restart on reboot

Example:

```bash
./deploy_service.sh 5090
```

#### View Status

```bash
pm2 status
```

#### View Logs

```bash
pm2 logs generate-tasks-5080
```

#### Stop the Service

```bash
pm2 delete generate-tasks-5080
```

---

### 🔧 **Environment Variables**

| Variable            | Description                               | Default |
| ------------------- | ----------------------------------------- | ------- |
| `UVICORN_LOG_LEVEL` | Logging verbosity (`info`, `debug`, etc.) | `info`  |

Example:

```bash
export UVICORN_LOG_LEVEL=debug
./deploy_service.sh 5080
```

---

### 🧰 **Tech Stack**

* **FastAPI** — modern async web framework
* **Uvicorn** — lightning-fast ASGI server
* **Pydantic** — input validation and documentation generation
* **PM2** — process manager for production deployment

---

### 📄 **License**

This API component is part of the **Autoppia IWA** project and follows the same license terms as the parent repository.
