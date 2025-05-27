import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse

import asyncpg
import orjson
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import BaseModel, Field, validator

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/database")
DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", "10"))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", "50"))
GZIP_MIN_SIZE = int(os.getenv("GZIP_MIN_SIZE", "1000"))

# --- Helper Function for URL Trimming ---
def trim_url_to_origin(url: str) -> str:
    """Trims a URL to its scheme://host[:port] origin string."""
    parsed = urlparse(url)
    port_str = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{parsed.hostname}{port_str}"

# --- SQL Query Constants ---
INSERT_EVENT_SQL = """
                   INSERT INTO events (web_agent_id, web_url, event_data)
                   VALUES ($1, $2, $3) RETURNING id, created_at; \
                   """

SELECT_EVENTS_SQL = """
                    SELECT id, web_agent_id, web_url, event_data AS data, created_at
                    FROM events
                    WHERE web_url = $1
                      AND web_agent_id = $2
                    ORDER BY created_at DESC; \
                    """

DELETE_EVENTS_SQL = """
                    WITH deleted_rows AS (
                    DELETE
                    FROM events
                    WHERE web_url = $1 RETURNING id
    )
                    SELECT count(*)
                    FROM deleted_rows; \
                    """


# --- Pydantic Models ---
class EventInput(BaseModel):
    web_agent_id: str = Field(default="UNKNOWN_AGENT", max_length=255)
    web_url: str
    data: Dict[str, Any]

    @validator('web_url')
    def validate_url(cls, v):
        try:
            parsed = urlparse(v)
            if not all([parsed.scheme, parsed.hostname]):
                raise ValueError("Invalid URL format")
            return v
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps


class EventOutput(BaseModel):
    id: int
    web_agent_id: str
    web_url: str
    data: Dict[str, Any]
    created_at: datetime

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps


class ResetResponse(BaseModel):
    message: str
    web_url: str
    deleted_count: int


# --- Database Initialization ---
async def init_db_pool():
    """Initializes the database connection pool and prepared statements."""
    retry_count = 0
    max_retries = 5
    retry_delay = 5  # seconds

    while retry_count < max_retries:
        try:
            app.state.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=DB_POOL_MIN,
                max_size=DB_POOL_MAX,
                timeout=30,  # Connection acquisition timeout
                command_timeout=30  # Default timeout for commands on a connection
            )
            logger.success(f"Database connection pool established (min: {DB_POOL_MIN}, max: {DB_POOL_MAX})")
            return
        except asyncpg.PostgresError as e:
            retry_count += 1
            logger.warning(f"Database pool creation failed (attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count >= max_retries:
                logger.error("Failed to create database pool after multiple attempts.")
                raise RuntimeError("Database pool creation failed.")
            await asyncio.sleep(retry_delay)
        except Exception as e:
            retry_count += 1
            logger.error(
                f"An unexpected error occurred during database pool creation (attempt {retry_count}/{max_retries}): {e}")
            if retry_count >= max_retries:
                logger.error("Failed to create database pool after multiple attempts due to unexpected error.")
                raise RuntimeError("Database pool creation failed due to unexpected error.")
            await asyncio.sleep(retry_delay)


# --- Application Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db_pool()
    logger.info("Application startup complete.")
    yield
    # Shutdown
    if hasattr(app.state, "pool") and app.state.pool:
        # Check if pool has _closing attribute and if it's already set to avoid issues if close is called multiple times
        # or if it's not a standard pool object for some reason (defensive)
        pool_can_be_closed = True
        if hasattr(app.state.pool, '_closing') and app.state.pool._closing.is_set():
            logger.info("Database connection pool is already in closing process or closed.")
            pool_can_be_closed = False

        if pool_can_be_closed:
            try:
                await app.state.pool.close()
                logger.info("Database connection pool closed.")
            except Exception as e:
                logger.error(f"Error during database pool close: {e}")

    logger.info("Application shutdown complete.")


# --- FastAPI Application ---
app = FastAPI(
    title="Blazing Fast Event API",
    description="API for saving, retrieving, and resetting web agent events. Enhanced version.",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    redoc_url=None
)
app.add_middleware(GZipMiddleware, minimum_size=GZIP_MIN_SIZE)


# --- API Endpoints ---
@app.post("/save_events/", status_code=201, summary="Save a single event")
async def save_event_endpoint(event: EventInput):
    """
    Saves a single event using a prepared statement obtained from the pool.
    The web_url is stored as its origin (scheme://host[:port]).
    """
    if not hasattr(app.state, "pool") or not app.state.pool:
        logger.error("Database pool not available for saving event.")
        raise HTTPException(status_code=503, detail="Database service temporarily unavailable.")
    try:
        event_data_json_string = orjson.dumps(event.data).decode('utf-8')
        # --- Apply trimming before saving ---
        trimmed_url = trim_url_to_origin(event.web_url)

        result = await app.state.pool.fetchrow(
            INSERT_EVENT_SQL,
            event.web_agent_id,
            trimmed_url,
            event_data_json_string
        )
        if result:
            logger.info(f"Event saved successfully: {result}")
            return {
                "message": "Event saved successfully",
                "event_id": result["id"],
                "created_at": result["created_at"]
            }
        else:
            logger.error("Event save operation did not return expected result.")
            raise HTTPException(status_code=500, detail="Failed to save event due to unexpected DB response.")

    except asyncpg.PostgresError as e:
        # Log the specific SQL state and message
        logger.error(f"Database error during event save: {e} (SQLState: {e.sqlstate})")
        raise HTTPException(status_code=500, detail="Database operation failed during save.")
    except Exception as e:
        logger.error(f"Unexpected error during event save: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@app.get("/get_events/", response_model=List[EventOutput], summary="Get events for a web agent and URL")
async def get_events_endpoint(
        web_url: str = Query(..., description="The specific web URL to filter events for."),
        web_agent_id: str = Query(default="UNKNOWN_AGENT", max_length=255, description="The specific web agent ID to filter events for.")
):
    """
    Retrieves events, utilizing prepared statements.
    Filtering is done based on the origin (scheme://host[:port]) of the provided web_url.
    """
    if not hasattr(app.state, "pool") or not app.state.pool:
        logger.error("Database pool not available for fetching events.")
        raise HTTPException(status_code=503, detail="Database service temporarily unavailable.")

    # --- Apply trimming to the query parameter before using it in the WHERE clause ---
    trimmed_url = trim_url_to_origin(web_url)

    try:
        rows = await app.state.pool.fetch(
            SELECT_EVENTS_SQL,
            trimmed_url,
            web_agent_id
        )
        logger.debug("rows fetched: ",rows)

        processed_rows = []
        for row in rows:
            row_dict = dict(row)
            logger.debug("rows dict: ", rows)
            raw_data = row_dict.get('data')
            if isinstance(raw_data, str):
                try:
                    row_dict['data'] = orjson.loads(raw_data)
                except orjson.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON data for event ID {row_dict.get('id', 'unknown')}: {e}")
                    row_dict['data'] = {}
            elif raw_data is None:
                 row_dict['data'] = {}

            processed_rows.append(row_dict)

        logger.info(f"Retrieved {len(processed_rows)} events for trimmed URL: {trimmed_url}, Agent ID: {web_agent_id}")
        return processed_rows # Return list of dictionaries/records

    except asyncpg.PostgresError as e:
        logger.error(f"Database query failed for get_events: {e} (SQLState: {e.sqlstate})")
        raise HTTPException(status_code=500, detail="Database operation failed during event retrieval.")
    except Exception as e:
        logger.error(f"Unexpected error during get_events: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while fetching events.")


@app.delete("/reset_events/", response_model=ResetResponse, summary="Delete all events for a web URL")
async def reset_events_endpoint(
        web_url: str = Query(..., description="The web URL for which all events should be deleted.")):
    """
    Deletes all events for a given web_url using a prepared statement.
    Deletion is based on the origin (scheme://host[:port]) of the provided web_url.
    """
    if not hasattr(app.state, "pool") or not app.state.pool:
        logger.error("Database pool not available for resetting events.")
        raise HTTPException(status_code=503, detail="Database service temporarily unavailable.")

    # --- Apply trimming to the query parameter before using it in the WHERE clause ---
    trimmed_url = trim_url_to_origin(web_url)

    try:
        deleted_count = await app.state.pool.fetchval(
            DELETE_EVENTS_SQL,
            trimmed_url
        )
        actual_deleted_count = deleted_count if deleted_count is not None else 0
        logger.info(f"Successfully deleted {actual_deleted_count} events for trimmed URL: {trimmed_url}")
        return ResetResponse(
            message=f"Successfully deleted events for {web_url}",
            web_url=web_url,
            deleted_count=actual_deleted_count
        )
    except asyncpg.PostgresError as e:
        logger.error(f"Database deletion failed for reset_events: {e} (SQLState: {e.sqlstate})")
        raise HTTPException(status_code=500, detail="Database operation failed during event reset.")
    except Exception as e:
        logger.error(f"Unexpected error during reset_events: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while resetting events.")


# --- Health Check ---
@app.get("/health", summary="Perform a health check of the API")
async def health_check_endpoint():
    """
    Provides a basic health check, including the status of the database pool.
    """
    db_pool_initialized_and_not_explicitly_closed = False
    debug_message = "Database pool not found on app.state."

    if hasattr(app.state, "pool") and app.state.pool is not None:
        if hasattr(app.state.pool, '_closing') and isinstance(app.state.pool._closing, asyncio.Event):
            if not app.state.pool._closing.is_set():
                db_pool_initialized_and_not_explicitly_closed = True
                debug_message = "Database pool exists and is not in the explicit closing process."
            else:
                debug_message = "Database pool exists but is in the explicit closing process (close() was called)."
        else:
            db_pool_initialized_and_not_explicitly_closed = True
            debug_message = "Database pool exists; specific closing state undetermined (fallback)."

    logger.debug(f"Health check: {debug_message}")
    return {
        "status": "healthy",
        "database_pool_operational": db_pool_initialized_and_not_explicitly_closed
    }
