import asyncio
import httpx
import random
import uuid
import json
from typing import Dict, Any, List

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8080"

# --- Data Generation ---

def generate_random_string(length: int = 10) -> str:
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length))

def generate_web_agent_id() -> str:
    return str(uuid.uuid4())

PREDEFINED_URLS = [
    "https://localhost:8000/page1",
    "https://example.com/page2",
    "https://anothersite.org/path/to/resource",
    "https://test-domain.net/products/123",
    "https://test-domain.net/products/456",
]

def generate_web_url() -> str:
    return random.choice(PREDEFINED_URLS)

def generate_event_data() -> Dict[str, Any]:
    """Generates diverse event data."""
    event_type = random.choice([
        "click", "page_view", "form_submission", "search",
        "add_to_cart", "purchase", "video_play"
    ])
    data: Dict[str, Any] = {"event_type": event_type, "timestamp": asyncio.get_event_loop().time()}

    if event_type == "click":
        data["element_id"] = f"btn-{generate_random_string(5)}"
        data["target_url"] = f"/{generate_random_string(8)}"
    elif event_type == "page_view":
        data["path"] = f"/{generate_random_string(10)}"
        data["referrer"] = random.choice([None, "https://google.com", "https://direct.link"])
        data["title"] = f"Page Title {generate_random_string(3)}"
    elif event_type == "form_submission":
        data["form_id"] = f"form-{generate_random_string(4)}"
        data["fields"] = {
            "name": "Test User " + generate_random_string(3),
            "email": f"{generate_random_string(5)}@example.com",
            "consent_given": random.choice([True, False]),
        }
    elif event_type == "search":
        data["query"] = f"search query {generate_random_string(12)}"
        data["results_count"] = random.randint(0, 100)
    elif event_type == "add_to_cart":
        data["product_id"] = generate_random_string(8).upper()
        data["quantity"] = random.randint(1,5)
        data["price"] = round(random.uniform(10.0, 500.0), 2)
    elif event_type == "purchase":
        data["order_id"] = str(uuid.uuid4())
        data["total_amount"] = round(random.uniform(50.0, 2000.0), 2)
        data["items"] = [
            {"product_id": generate_random_string(8).upper(), "quantity": random.randint(1,3)}
            for _ in range(random.randint(1,4))
        ]
        data["customer_details"] = {"loyalty_member": random.choice([True, False]), "segment": f"seg-{random.randint(1,5)}"}
    elif event_type == "video_play":
        data["video_id"] = f"vid_{generate_random_string(10)}"
        data["duration_watched_seconds"] = random.randint(1, 600)

    # Add some common metadata
    data["user_agent"] = "TestClient/1.0"
    data["screen_resolution"] = random.choice(["1920x1080", "1366x768", "2560x1440"])
    data["is_mobile"] = random.choice([True, False])
    if random.random() < 0.2: # 20% chance of having extra tags
        data["tags"] = [f"tag{i}" for i in range(random.randint(1,4))]
    if random.random() < 0.1: # 10% chance of having a slightly larger payload
        data["additional_info"] = {"detail_" + str(i): generate_random_string(20) for i in range(random.randint(3,7))}

    return data

def create_sample_event_payload() -> Dict[str, Any]:
    return {
        "web_agent_id": generate_web_agent_id(),
        "web_url": generate_web_url(),
        "data": generate_event_data(),
    }

# --- API Interaction Functions ---

async def check_health(client: httpx.AsyncClient):
    print("--- Checking Health ---")
    try:
        response = await client.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print(f"Health Check OK: {response.json()}")
        return True
    except httpx.HTTPStatusError as e:
        print(f"Health Check HTTP Error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Health Check Request Error: {e}")
    return False

async def save_single_event(client: httpx.AsyncClient, event_payload: Dict[str, Any]) -> Dict[str, Any] | None:
    print(f"\n--- Saving Single Event for URL: {event_payload['web_url']}, Agent: {event_payload['web_agent_id']} ---")
    try:
        response = await client.post(f"{BASE_URL}/save_events/", json=event_payload)
        response.raise_for_status()
        print(f"Save Event Response: {response.json()}")
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Save Event HTTP Error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Save Event Request Error: {e}")
    return None

async def get_events(client: httpx.AsyncClient, web_url: str, web_agent_id: str) -> List[Dict[str, Any]] | None:
    print(f"\n--- Getting Events for URL: {web_url}, Agent: {web_agent_id} ---")
    params = {"web_url": web_url, "web_agent_id": web_agent_id}
    try:
        response = await client.get(f"{BASE_URL}/get_events/", params=params)
        response.raise_for_status()
        events = response.json()
        print(f"Get Events Response (found {len(events)} events):")
        for event in events:
            # Pretty print part of the event data for brevity
            print(f"  ID: {event.get('id')}, Data: {json.dumps(event.get('data', {}), indent=2)[:200]}...")
        return events
    except httpx.HTTPStatusError as e:
        print(f"Get Events HTTP Error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Get Events Request Error: {e}")
    return None

async def reset_web_events(client: httpx.AsyncClient, web_url: str) -> Dict[str, Any] | None:
    print(f"\n--- Resetting Events for URL: {web_url} ---")
    params = {"web_url": web_url}
    try:
        response = await client.delete(f"{BASE_URL}/reset_events/", params=params)
        response.raise_for_status()
        print(f"Reset Events Response: {response.json()}")
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Reset Events HTTP Error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Reset Events Request Error: {e}")
    return None


# --- Main Test Orchestration ---
async def main():
    async with httpx.AsyncClient(timeout=20.0) as client:
        if not await check_health(client):
            print("Health check failed. Aborting tests.")
            return

        # --- Test Data Setup ---
        agent1_id = generate_web_agent_id()
        agent2_id = generate_web_agent_id()

        url1 = PREDEFINED_URLS[0]
        url2 = PREDEFINED_URLS[1]
        url3 = PREDEFINED_URLS[2] # Will be used for reset

        event1_payload = {
            "web_agent_id": agent1_id,
            "web_url": url1,
            "data": generate_event_data(),
        }
        event1_payload["data"]["custom_marker"] = "Event 1 for Agent 1 on URL 1"


        event2_payload = {
            "web_agent_id": agent1_id,
            "web_url": url1, # Same agent, same URL, different event
            "data": generate_event_data(),
        }
        event2_payload["data"]["custom_marker"] = "Event 2 for Agent 1 on URL 1"

        event3_payload = {
            "web_agent_id": agent2_id,
            "web_url": url1, # Different agent, same URL
            "data": generate_event_data(),
        }
        event3_payload["data"]["custom_marker"] = "Event 3 for Agent 2 on URL 1"


        event4_payload = {
            "web_agent_id": agent1_id,
            "web_url": url2, # Same agent, different URL
            "data": generate_event_data(),
        }
        event4_payload["data"]["custom_marker"] = "Event 4 for Agent 1 on URL 2"

        event5_payload_for_reset = {
            "web_agent_id": agent1_id,
            "web_url": url3,
            "data": generate_event_data(),
        }
        event5_payload_for_reset["data"]["custom_marker"] = "Event 5 for Agent 1 on URL 3 (to be reset)"

        event6_payload_for_reset = {
            "web_agent_id": agent2_id, # different agent on same URL to be reset
            "web_url": url3,
            "data": generate_event_data(),
        }
        event6_payload_for_reset["data"]["custom_marker"] = "Event 6 for Agent 2 on URL 3 (to be reset)"


        # 1. Save Events
        await save_single_event(client, event1_payload)
        await save_single_event(client, event2_payload)
        await save_single_event(client, event3_payload)
        await save_single_event(client, event4_payload)
        await save_single_event(client, event5_payload_for_reset)
        await save_single_event(client, event6_payload_for_reset)

        # Introduce a small delay if DB operations are very fast and caching might be tested
        # await asyncio.sleep(0.1)

        # 2. Get Events - Verification
        print("\nVERIFYING SAVED EVENTS:")
        # Get events for agent1 on url1 (should be 2 events)
        events_a1_u1 = await get_events(client, url1, agent1_id)
        assert events_a1_u1 is not None and len(events_a1_u1) >= 2, "Test Failed: Agent 1 on URL 1 should have at least 2 events"

        # Get events for agent2 on url1 (should be 1 event)
        events_a2_u1 = await get_events(client, url1, agent2_id)
        assert events_a2_u1 is not None and len(events_a2_u1) >= 1, "Test Failed: Agent 2 on URL 1 should have at least 1 event"

        # Get events for agent1 on url2 (should be 1 event)
        events_a1_u2 = await get_events(client, url2, agent1_id)
        assert events_a1_u2 is not None and len(events_a1_u2) >= 1, "Test Failed: Agent 1 on URL 2 should have at least 1 event"

        # Get events for agent1 on url3 (to be reset) (should be 1 event initially)
        events_a1_u3_before_reset = await get_events(client, url3, agent1_id)
        assert events_a1_u3_before_reset is not None and len(events_a1_u3_before_reset) >= 1, "Test Failed: Agent 1 on URL 3 should have at least 1 event before reset"

        # Get events for non-existent agent/url combination
        print("\nVERIFYING EMPTY RESULTS FOR NON-EXISTENT DATA:")
        await get_events(client, "https://nonexistent.com/foo", generate_web_agent_id()) # Should be empty or 404 if designed that way, currently returns empty list
        await get_events(client, url1, "non_existent_agent_id") # Should be empty

        # 3. Test Caching for get_events (call again)
        # Note: Programmatic cache verification is tricky without server-side logs or timing very carefully.
        # This call demonstrates hitting it again. If logs show cache hit or response is significantly faster, it's working.
        print("\n--- Getting Events for URL1, Agent1 AGAIN (testing cache if enabled & time elapsed < expire) ---")
        await get_events(client, url1, agent1_id)


        # 4. Reset Events for a specific URL (url3)
        print("\nPERFORMING RESET:")
        reset_result = await reset_web_events(client, url3)
        assert reset_result is not None and reset_result.get("deleted_count", 0) >= 2, f"Test Failed: Reset for {url3} should delete at least 2 events"


        # 5. Verify Reset
        print("\nVERIFYING RESET OPERATION:")
        # Try to get events for agent1 on url3 (should now be 0)
        events_a1_u3_after_reset = await get_events(client, url3, agent1_id)
        assert events_a1_u3_after_reset is not None and len(events_a1_u3_after_reset) == 0, "Test Failed: Agent 1 on URL 3 should have 0 events after reset"

        # Try to get events for agent2 on url3 (should also be 0 as reset is per URL)
        events_a2_u3_after_reset = await get_events(client, url3, agent2_id)
        assert events_a2_u3_after_reset is not None and len(events_a2_u3_after_reset) == 0, "Test Failed: Agent 2 on URL 3 should have 0 events after reset"

        # Verify other URLs are not affected by reset
        print("\nVERIFYING OTHER URLS UNAFFECTED BY RESET:")
        events_a1_u1_after_reset = await get_events(client, url1, agent1_id)
        assert events_a1_u1_after_reset is not None and len(events_a1_u1_after_reset) >= 2, "Test Failed: Agent 1 on URL 1 should still have its events after reset of URL 3"

        print("\n--- All specific tests completed ---")

        # Optional: Broad data testing loop
        print("\n--- Starting Broad Data Testing (saving a few random events) ---")
        for i in range(5): # Save 5 more completely random events
            random_payload = create_sample_event_payload()
            print(f"Broad Test {i+1}: Saving event for URL {random_payload['web_url']}, Agent {random_payload['web_agent_id']}")
            await save_single_event(client, random_payload)
            # Optionally, try to fetch this specific event back
            await get_events(client, random_payload['web_url'], random_payload['web_agent_id'])
        print("--- Broad Data Testing finished ---")


if __name__ == "__main__":
    # Ensure your FastAPI application is running before executing this script.
    # And that the DATABASE_URL environment variable is correctly set for the API.
    # And that you have fixed the prepared statement initialization in your API code.
    asyncio.run(main())
