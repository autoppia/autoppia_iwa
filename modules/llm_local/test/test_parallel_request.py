import requests
import json
import time
import argparse

# The big text you wanted each message to contain:
base_user_content = (
    "You are a test analyzer for web automation testing. "
    "Review the tests below and decide which ones to keep.\n\n"
    "TASK CONTEXT:\n"
    "- Task Prompt: example task prompt\n"
    "- Success Criteria: example success critera\n"
    "TESTS TO REVIEW:\n"
    "example test\n\n"
    "GUIDELINES:\n"
    "1. Backend tests (CheckEventTest, CheckPageViewEventTest) are preferred over frontend tests.\n"
    "2. Intelligent judgment tests (JudgeBaseOnHTML, JudgeBaseOnScreenshot) are useful.\n"
    "3. Avoid keeping tests that check the same thing in different ways.\n"
    "4. Prioritize tests that directly verify the success criteria.\n"
    "5. Aim to keep 1-3 high-quality tests in total.\n"
    "6. Delete tests that make up parameters like making up event_names in CheckEventTest.\n"
    "7. Judge Tests like JudgeBaseOnHTML or JudgeBaseOnScreenshot are fallback tests.\n\n"
    "RESPOND WITH A JSON ARRAY of decisions, one for each test, like this:\n"
    "[\n"
    "  {\n"
    "    \"index\": 0,\n"
    "    \"keep\": true,\n"
    "    \"reason\": \"High quality backend test that verifies core success criteria\"\n"
    "  },\n"
    "  {\n"
    "    \"index\": 1,\n"
    "    \"keep\": false,\n"
    "    \"reason\": \"Redundant with test #0 which is more reliable\"\n"
    "  }\n"
    "]\n\n"
    "Return ONLY the JSON array, no additional text."
)


def test_increasing_subrequests(url, start_subrequests, max_subrequests, temperature, max_tokens):
    """
    For i in [start_subrequests..max_subrequests] (stepping by 5):
      - We create an array of i sub-requests.
      - Each sub-request has 1 user message containing 'base_user_content'.
      - Send them all in ONE POST to /generate_parallel.
      - Print the stats the server returns.
    """
    headers = {"Content-Type": "application/json"}

    # Step by 5, starting from start_subrequests up to max_subrequests (inclusive)
    for i in range(start_subrequests, max_subrequests + 1, 10):
        # Build i sub-requests; each sub-request has a single user message
        subrequests = []
        for sub_id in range(1, i + 1):
            subrequests.append({
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            base_user_content
                            + f"\n\n(This is sub-request #{sub_id} of {i} in this batch.)"
                        )
                    }
                ],
                "json_format": False,
                "schema": None
            })

        data = {
            "requests": subrequests,  # i sub-requests in one batch
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        print(f"\n--- Sending 1 request with {i} sub-requests ---")
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=data)
        except Exception as e:
            print(f"Request with {i} sub-requests failed: {e}")
            break
        end_time = time.time()
        elapsed = end_time - start_time

        # Parse response
        try:
            response_json = response.json()
        except Exception as e:
            print(f"Could not parse JSON for request with {i} sub-requests: {e}")
            break

        if "error" in response_json:
            print(f"Server returned error for request with {i} sub-requests: {response_json['error']}")
            break

        # Extract stats
        stats = response_json.get("stats", {})
        total_tokens_in = stats.get("total_tokens_in")
        total_tokens_out = stats.get("total_tokens_out")
        tokens_per_second = stats.get("tokens_per_second")
        total_time = stats.get("total_time")
        avg_time_per_request = stats.get("avg_time_per_request")

        # Print stats
        print(f"  -> Response time:          {elapsed:.2f} s")
        print(f"  -> total_tokens_in:        {total_tokens_in}")
        print(f"  -> total_tokens_out:       {total_tokens_out}")
        if total_time is not None:
            print(f"  -> total_time (batch):     {total_time:.2f} s")
        if tokens_per_second is not None:
            print(f"  -> tokens_per_second:      {tokens_per_second:.2f}")
        if avg_time_per_request is not None:
            print(f"  -> avg_time_per_request:   {avg_time_per_request:.2f}")

        # Show partial output for the first sub-request in the batch
        outputs = response_json.get("outputs", [])
        print(f"  -> # of outputs returned:  {len(outputs)}")
        if outputs:
            # Print the first 200 characters of the first output
            print(f"  -> Partial output[0]: {outputs[0][:200]} ...")


def main():
    parser = argparse.ArgumentParser(description="Send an increasing number of sub-requests to /generate_parallel.")
    parser.add_argument(
        "--url",
        type=str,
        default="http://127.0.0.1:6000/generate_parallel",
        help="The /generate_parallel endpoint URL."
    )
    parser.add_argument(
        "--start_subrequests",
        type=int,
        default=100,
        help="Starting number of sub-requests."
    )
    parser.add_argument(
        "--max_subrequests",
        type=int,
        default=250,
        help="Maximum number of sub-requests in the single request (incrementally, stepping by 5)."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Temperature for generation."
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=2000,
        help="Max tokens to generate in the response."
    )
    args = parser.parse_args()

    test_increasing_subrequests(
        url=args.url,
        start_subrequests=args.start_subrequests,
        max_subrequests=args.max_subrequests,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )


if __name__ == "__main__":
    main()
