import requests
import json
import time
import argparse


def build_messages(num_messages, sub_request_id=1):
    """
    Build a list of messages repeated `num_messages` times.
    Each message is somewhat large so that we can push the token count up.
    """
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

    messages = []
    for i in range(num_messages):
        # For demonstration, we alternate "user" and "system" roles or just keep them all user.
        # Here let's do a single system message plus repeated user messages to see how the LLM handles it.
        # The first message might be a system message:
        if i == 0:
            messages.append({
                "role": "system",
                "content": (
                    f"You are Qwen, created by Alibaba Cloud. You are a helpful assistant. "
                    f"(Sub-request {sub_request_id}, message #{i+1})"
                )
            })
        else:
            messages.append({
                "role": "user",
                "content": (
                    base_user_content
                    + f"\n\n(This is message #{i+1} out of {num_messages})"
                )
            })
    return messages


def test_parallel_increasing_messages(
    url, max_messages, temperature, max_tokens
):
    """
    For each i in [1..max_messages], sends exactly one sub-request with 'i' messages
    to /generate_parallel and prints the returned stats (including tokens_in, tokens_out).
    """
    headers = {"Content-Type": "application/json"}

    for i in range(1, max_messages + 1):
        # Build the single sub-request containing i messages
        single_request = {
            "messages": build_messages(num_messages=i),
            "json_format": False,
            "schema": None
        }

        data = {
            "requests": [single_request],  # Exactly one sub-request in the batch
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        print(f"\n--- Sending request with {i} messages ---")
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=data)
            end_time = time.time()
        except Exception as e:
            print(f"Request with {i} messages failed to complete: {e}")
            break

        elapsed = end_time - start_time

        # Try to parse the JSON
        try:
            response_json = response.json()
        except Exception as e:
            print(f"Could not parse JSON for request with {i} messages: {e}")
            break

        # Check if there's an error from the server
        if "error" in response_json:
            print(f"Server returned error for {i} messages: {response_json['error']}")
            break

        # Otherwise, read the stats
        stats = response_json.get("stats", {})
        total_tokens_in = stats.get("total_tokens_in", None)
        total_tokens_out = stats.get("total_tokens_out", None)
        tokens_per_second = stats.get("tokens_per_second", None)
        total_time = stats.get("total_time", None)
        avg_time_per_request = stats.get("avg_time_per_request", None)

        print(f"  -> Response time:          {elapsed:.2f} s")
        print(f"  -> total_tokens_in:        {total_tokens_in}")
        print(f"  -> total_tokens_out:       {total_tokens_out}")
        print(f"  -> total_time (batch):     {total_time:.2f} s" if total_time else "")
        print(f"  -> tokens_per_second:      {tokens_per_second:.2f}" if tokens_per_second else "")
        print(f"  -> avg_time_per_request:   {avg_time_per_request:.2f}" if avg_time_per_request else "")

        # Optionally print the first 200 chars of the output to see if it makes sense
        outputs = response_json.get("outputs", [])
        if outputs:
            print(f"  -> Partial output[0]: {outputs[0][:200]} ...")


def main():
    parser = argparse.ArgumentParser(description="Test /generate_parallel with increasing number of messages.")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:6000/generate_parallel",
                        help="URL endpoint for parallel generation.")
    parser.add_argument("--max_messages", type=int, default=250,
                        help="Max number of messages to test incrementally.")
    parser.add_argument("--temperature", type=float, default=0.1,
                        help="Temperature parameter for generation.")
    parser.add_argument("--max_tokens", type=int, default=256,
                        help="Max tokens to generate.")
    args = parser.parse_args()

    test_parallel_increasing_messages(
        url=args.url,
        max_messages=args.max_messages,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )


if __name__ == "__main__":
    main()
