import requests
import json
import time
import argparse


def generate_test_content(num_tokens):
    """
    Generate pseudo-content of approximately `num_tokens` tokens,
    to simulate a user prompt of that size.
    We'll just repeat a short phrase enough times to reach that length.
    This is NOT exact, but close enough for testing.
    """
    token_chunk = "token "
    # Each chunk ~1 token, so repeat enough times:
    repeated_chunk = token_chunk * num_tokens
    # Wrap the repeated chunk in a typical user request context
    # that simulates the structure from the original code:
    content = (
        "You are to analyze the following text:\n\n" 
        + repeated_chunk
        + "\n\nReturn a single JSON with any summarization or analysis you see fit."
    )
    return content


def test_parallel_requests_for_tokens(
    url, 
    temperature, 
    max_tokens_response, 
    tokens_count, 
    step=1, 
    max_parallel=100
):
    """
    For a given `tokens_count`, create sub-requests that each have a ~`tokens_count`-token message.
    We'll increase the number of sub-requests from 1 up to `max_parallel` by `step`, 
    stopping as soon as we hit an error or exceed `max_parallel`.

    Returns a dictionary with:
    {
      'tokens_count': int,
      'max_subrequests_handled': int,
      'time_for_max': float (time in seconds for the last successful batch),
      'requests_per_second_for_max': float
    }
    """
    headers = {"Content-Type": "application/json"}

    # The base content is the user prompt ~ tokens_count
    base_user_content = generate_test_content(tokens_count)

    max_subrequests_handled = 0
    time_for_max = 0.0

    for i in range(1, max_parallel + 1, step):
        # Build i sub-requests; each sub-request has one user message
        subrequests = []
        for sub_id in range(1, i + 1):
            subrequests.append({
                "messages": [
                    {
                        "role": "user",
                        "content": base_user_content + f"\n(This is sub-request #{sub_id} of {i} in this batch.)"
                    }
                ],
                "json_format": False,
                "schema": None
            })

        data = {
            "requests": subrequests,  # i sub-requests in one batch
            "temperature": temperature,
            "max_tokens": max_tokens_response
        }

        print(f"Testing {i} parallel sub-requests (~{tokens_count} tokens each)...")
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=data)
        except Exception as e:
            print(f"Request with {i} sub-requests failed with exception: {e}")
            break
        end_time = time.time()
        elapsed = end_time - start_time

        try:
            response_json = response.json()
        except json.JSONDecodeError as e:
            print(f"Could not parse JSON for request with {i} sub-requests: {e}")
            break

        if "error" in response_json:
            print(f"Server returned error for request with {i} sub-requests: {response_json['error']}")
            break

        # If we got this far, it means the server handled i subrequests successfully
        max_subrequests_handled = i
        time_for_max = elapsed

        print(f"  -> Success with {i} sub-requests in {elapsed:.2f} s")

    # If we never succeeded at all, max_subrequests_handled would be 0.
    # We'll compute requests_per_second_for_max with the last successful i
    if max_subrequests_handled > 0 and time_for_max > 0:
        rps = max_subrequests_handled / time_for_max
    else:
        rps = 0.0

    return {
        "tokens_count": tokens_count,
        "max_subrequests_handled": max_subrequests_handled,
        "time_for_max": time_for_max,
        "requests_per_second_for_max": rps
    }


def main():
    parser = argparse.ArgumentParser(
        description="Measure maximum parallel sub-requests that can be handled for increasing token sizes."
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://127.0.0.1:6000/generate_parallel",
        help="The /generate_parallel endpoint URL."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Temperature for generation."
    )
    parser.add_argument(
        "--max_tokens_response",
        type=int,
        default=2000,
        help="Max tokens in the response."
    )
    parser.add_argument(
        "--max_parallel",
        type=int,
        default=50,
        help="Maximum number of parallel sub-requests to test up to."
    )
    parser.add_argument(
        "--step",
        type=int,
        default=1,
        help="Step for increasing parallel sub-requests."
    )
    parser.add_argument(
        "--max_token_size",
        type=int,
        default=37000,
        help="Max token size to test (we assume crashes above ~37k)."
    )
    parser.add_argument(
        "--step_token_size",
        type=int,
        default=1000,
        help="Increment of token size to test in each iteration (e.g., 1000 => 1000, 2000, 3000, ...)."
    )

    args = parser.parse_args()

    # We'll test for multiples of 1000 tokens up to the specified max
    token_sizes = []
    current_tokens = 1000
    while current_tokens <= args.max_token_size:
        token_sizes.append(current_tokens)
        current_tokens += args.step_token_size

    results = []

    for tok_size in token_sizes:
        print(f"\n=== Testing for ~{tok_size} tokens per request ===")
        res = test_parallel_requests_for_tokens(
            url=args.url,
            temperature=args.temperature,
            max_tokens_response=args.max_tokens_response,
            tokens_count=tok_size,
            step=args.step,
            max_parallel=args.max_parallel
        )
        results.append(res)
        print(f"Result for {tok_size} tokens: {res}")

    print("\n\nSummary of Results:")
    for r in results:
        print(
            f" - {r['tokens_count']} tokens: "
            f"max_subrequests={r['max_subrequests_handled']}, "
            f"time={r['time_for_max']:.2f}s, "
            f"requests/s={r['requests_per_second_for_max']:.2f}"
        )

    # Generate a comparative table with (tokens_count) vs (requests_per_second_for_max)
    print("\nComparative Table (Tokens vs Requests/sec):")
    print("==============================================================")
    print(f"{'Tokens':<10} | {'MaxSubReqs':<12} | {'Time(s)':<8} | {'Req/s':<8}")
    print("--------------------------------------------------------------")
    for r in results:
        print(
            f"{r['tokens_count']:<10} | "
            f"{r['max_subrequests_handled']:<12} | "
            f"{r['time_for_max']:.2f}     | "
            f"{r['requests_per_second_for_max']:.2f}"
        )


if __name__ == "__main__":
    main()
