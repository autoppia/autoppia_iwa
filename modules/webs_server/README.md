
# AutoPPIA Web Events API

A high-performance API for managing web agent events, built with FastAPI and PostgreSQL.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the API](#running-the-api)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Features
- 🚀 High-performance event storage and retrieval using `asyncpg`
- 💾 Persists event data in PostgreSQL
- 📊 Basic health check endpoint
- 🔄 Automatic database connection pooling
- 📦 Docker-ready deployment
- ✨ Utilizes FastAPI's automatic validation and serialization (via Pydantic)

## Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+ (for local development, if not using Docker)

## Installation

### With Docker (Recommended)

Follow these steps to install and run the application using Docker Compose:

1.  Navigate to the project's `webs_server` directory where the `docker-compose.yaml` and `Dockerfile` are located:
    ```bash
    cd autoppia_iwa/modules/webs_server
    ```
2.  Create your environment configuration file from the provided template. This file (`.env`) contains crucial settings like database credentials and ports. **You must edit `.env` after copying to set your actual configuration values.**
    ```bash
    cp .env.template .env
    ```
3.  Build the Docker images (if they haven't been built or if you've made changes) and start the services defined in `docker-compose.yaml` in detached mode (in the background):
    ```bash
    docker-compose up --build -d
    ```
    > Note: Before doing it make sure the network is present by:
    ```bash
    docker network create app-network
    ```
4.  Verify that the services are running correctly:
    ```bash
    docker ps
    ```
    You should see output listing the `app` and `db` services with their status. Wait for the `db` service to show `(healthy)`.
    You can view the application logs with:
    ```bash
    docker logs -f webs_server-app-1
    ```

### Local Development
1.  Navigate to the `webs_server` directory.
2.  Create a Python virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    ```bash
    source venv/bin/activate  # Linux/MacOS
    venv\Scripts\activate  # Windows
    ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Ensure your PostgreSQL database is running and the `DATABASE_URL` environment variable is set correctly in your shell or a `.env` file read by your environment.
6.  Run the FastAPI application with Uvicorn:
    ```bash
    uvicorn server:app --reload --host 0.0.0.0 --port 8000 # Or your desired port
    ```
    *(Note: The docker-compose maps external port 8080 to container port 80. For local dev, choose an available port like 8000)*

## Running the API

### Deploy with Docker Compose
To run the API and PostgreSQL database in detached mode:
```bash
docker-compose up --build -d
````

The API will be accessible on port `8080`.

## API Endpoints

This section provides details about the available API endpoints. All responses use `ORJSONResponse` for fast JSON serialization.

### 1\. Health Check

Checks the API status and database connection pool.

  * **URL:** `/health`
  * **Method:** `GET`
  * **Summary:** Perform a health check of the API

**Response (200 OK):**
Indicates the service is running and the database pool status.

```json
{
  "status": "healthy",
  "database_pool_operational": true
}
```

*(Note: `database_pool_operational` might be `false` or the health check might fail if the database is unreachable)*

### 2\. Save Event

Saves a single web event to the database.

  * **URL:** `/save_events/`
  * **Method:** `POST`
  * **Summary:** Save a single event

**Request Body:**
A JSON object matching the `EventInput` model.

  * `web_agent_id` (`str`, required): Unique identifier for the web agent (e.g., browser session ID). Max 255 characters.
  * `web_url` (`HttpUrl`, required): The URL where the event occurred.
  * `data` (`Dict[str, Any]`, required): A JSON object containing the specific event details (type, timestamp, custom properties, etc.).

Example Request Body

```json
{
  "web_agent_id": "88b09cfd-8338-4b0d-8fbb-96449078c772",
  "web_url": "[https://example.com/page1](https://example.com/page1)",
  "data": {
    "event_type": "click",
    "element_id": "buy-button",
    "timestamp": 1678886400,
    "user_agent": "Mozilla/5.0...",
    "is_mobile": false
  }
}
```

**Responses:**

  * **201 Created:** Event saved successfully.

    Example Response Body (201)

    ```json
    {
      "message": "Event saved successfully",
      "event_id": 12345,
      "created_at": "2025-05-19T08:00:00.123456+00:00"
    }
    ```

  * **422 Unprocessable Entity:** The request body failed validation (e.g., missing fields, incorrect data types). Check the response `detail` for specific errors.

  * **500 Internal Server Error:** An unexpected error occurred on the server (e.g., database operation failed).

  * **503 Service Unavailable:** Database pool is not initialized or available.

### 3\. Get Events

Retrieves all events associated with a specific web agent on a specific URL, ordered by creation time (latest first).

  * **URL:** `/get_events/`
  * **Method:** `GET`
  * **Summary:** Get events for a web agent and URL

**Query Parameters:**

  * `web_url` (`HttpUrl`, required): The web URL to filter events for.
  * `web_agent_id` (`str`, required): The web agent ID to filter events for. Max 255 characters.

```
GET /get_events/?web_url=[https://example.com/page1&web_agent_id=88b09cfd-8338-4b0d-8fbb-96449078c772](https://example.com/page1&web_agent_id=88b09cfd-8338-4b0d-8fbb-96449078c772)
```

**Responses:**

  * **200 OK:** Returns a list of event objects matching the criteria. The list may be empty if no events are found. The `data` field in each event object is the parsed JSON data.

    Example Response Body (200)

    ```json
    [
      {
        "id": 12346,
        "web_agent_id": "88b09cfd-8338-4b0d-8fbb-96449078c772",
        "web_url": "[https://example.com/page1](https://example.com/page1)",
        "data": {
          "event_type": "page_view",
          "path": "/page1",
          "title": "My Page",
          "timestamp": 1678886410
        },
        "created_at": "2025-05-19T08:00:10.987654+00:00"
      },
      {
        "id": 12345,
        "web_agent_id": "88b09cfd-8338-4b0d-8fbb-96449078c772",
        "web_url": "[https://example.com/page1](https://example.com/page1)",
        "data": {
          "event_type": "click",
          "element_id": "buy-button",
          "timestamp": 1678886400
        },
        "created_at": "2025-05-19T08:00:00.123456+00:00"
      }
    ]
    ```


  * **422 Unprocessable Entity:** Query parameters failed validation.

  * **500 Internal Server Error:** An unexpected error occurred on the server (e.g., database query failed, failed to parse event data from DB).

  * **503 Service Unavailable:** Database pool is not initialized or available.

### 4\. Reset Events

Deletes all events associated with a specific web URL.

  * **URL:** `/reset_events/`
  * **Method:** `DELETE`
  * **Summary:** Delete all events for a web URL

**Query Parameter:**

  * `web_url` (`HttpUrl`, required): The web URL for which all events should be deleted.

Example Request URL

```
DELETE /reset_events/?web_url=[https://anothersite.org/path/to/resource](https://anothersite.org/path/to/resource)
```


**Responses:**

  * **200 OK:** Events deleted successfully.

    Example Response Body (200)

    ```json
    {
      "message": "Successfully deleted events for [https://anothersite.org/path/to/resource](https://anothersite.org/path/to/resource)",
      "web_url": "[https://anothersite.org/path/to/resource](https://anothersite.org/path/to/resource)",
      "deleted_count": 7
    }
    ```

  * **422 Unprocessable Entity:** Query parameter failed validation.

  * **500 Internal Server Error:** An unexpected error occurred on the server (e.g., database deletion failed).

  * **503 Service Unavailable:** Database pool is not initialized or available.

## Database Schema

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    web_agent_id VARCHAR(255) NOT NULL,
    web_url TEXT NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient lookup by URL and Agent ID
CREATE INDEX idx_events_web_url ON events(web_url);
CREATE INDEX idx_events_web_agent_id ON events(web_agent_id);
```

*(Note: Added comment clarifying `web_url` storage and potential combined index)*

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (Required) | PostgreSQL connection URL (e.g., `postgresql://user:password@host:port/database`) |
| `DB_POOL_MIN` | 10 | Minimum active database connections in the pool |
| `DB_POOL_MAX` | 50 | Maximum active database connections in the pool |
| `GZIP_MIN_SIZE` | 1000 | Minimum response size (in bytes) before applying GZIP compression |
| `LOG_LEVEL` | info | Logging level for the application (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |


## Troubleshooting

### General

  - **Check Container Status:** `docker-compose ps`
  - **View Application Logs:** `docker-compose logs -f app` (replace `app` with your service name if different)
