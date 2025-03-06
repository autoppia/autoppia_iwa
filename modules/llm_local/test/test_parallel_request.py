import requests
import json
import time
import argparse


def build_messages(num_messages, sub_request_id=1):
    """
    Build a list of messages repeated `num_messages` times.
    In this simplified version, we typically call build_messages(1).
    """
    base_user_content = (
        "You are a test analyzer for web automation testing. "
        "Review the tests below and decide which ones to keep. "
        "Return ONLY a JSON array, no additional text."
    )

    messages = []
    for i in range(num_messages):
        # First message can be system
        if i == 0:
            messages.append({
                "role": "system",
                "content": f"You are Qwen, created by Alibaba Cloud. "
                           f"(Sub-request #{sub_request_id}, message #{i+1})"
            })
        else:
            # In this simplified example, we won't usually get here if num_messages=1
            messages.append({
                "role": "user",
                "content": base_user_content
            })
    return messages


def test_increasing_subrequests(url, max_subrequests, temperature, max_tokens):
    """
    For i in [1..max_subrequests]:
      - Build an array of i sub-requests (each sub-request is just 1 message).
      - Send one request to /generate_parallel.
      - Print the stats and partial output.
    """
    headers = {"Content-Type": "application/json"}

    for i in range(1, max_subrequests + 1):
        # Build i sub-requests, each with build_messages(1)
        subrequests = []
        for sub_request_id in range(1, i + 1):
            subrequests.append({
                "messages": build_messages(1, sub_request_id=sub_request_id),
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
            return
        end_time = time.time()
        elapsed = end_time - start_time

        # Parse response
        try:
            response_json = response.json()
        except Exception as e:
            print(f"Could not parse JSON for request with {i} sub-requests: {e}")
            return

        if "error" in response_json:
            print(f"Server returned error for request with {i} sub-requests: {response_json['error']}")
            return

        # Extract stats
        stats = response_json.get("stats", {})
        total_tokens_in = stats.get("total_tokens_in")
        total_tokens_out = stats.get("total_tokens_out")
        tokens_per_second = stats.get("tokens_per_second")
        total_time = stats.get("total_time")
        avg_time_per_request = stats.get("avg_time_per_request")

        print(f"  -> Response time:          {elapsed:.2f} s")
        print(f"  -> total_tokens_in:        {total_tokens_in}")
        print(f"  -> total_tokens_out:       {total_tokens_out}")
        if total_time is not None:
            print(f"  -> total_time (batch):     {total_time:.2f} s")
        if tokens_per_second is not None:
            print(f"  -> tokens_per_second:      {tokens_per_second:.2f}")
        if avg_time_per_request is not None:
            print(f"  -> avg_time_per_request:   {avg_time_per_request:.2f}")

        # Show partial output for the first sub-request
        outputs = response_json.get("outputs", [])
        print(f"  -> # of outputs returned:  {len(outputs)}")
        if outputs:
            print(f"  -> Partial output[0]: {outputs[0][:200]} ...")


def main():
    parser = argparse.ArgumentParser(description="Send a single request each time, with increasing sub-requests.")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:6000/generate_parallel",
                        help="The /generate_parallel endpoint URL.")
    parser.add_argument("--max_subrequests", type=int, default=5,
                        help="How many sub-requests to test up to (from 1..max_subrequests).")
    parser.add_argument("--temperature", type=float, default=0.1,
                        help="Temperature for generation.")
    parser.add_argument("--max_tokens", type=int, default=256,
                        help="Max tokens to generate.")
    args = parser.parse_args()

    test_increasing_subrequests(
        url=args.url,
        max_subrequests=args.max_subrequests,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )


if __name__ == "__main__":
    main()
