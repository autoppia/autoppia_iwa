import requests
import json
import time
import argparse


def generate_test_content(num_tokens):
    """
    Generate pseudo-content of approximately `num_tokens` tokens
    to simulate a user prompt of that size.
    We'll just repeat a short phrase enough times to reach that length.
    This is NOT exact, but close enough for testing.
    """
    token_chunk = "token "
    repeated_chunk = token_chunk * num_tokens
    content = (
        "You are to analyze the following text:\n\n" 
        + repeated_chunk
        + "\n\nReturn a single JSON with any summarization or analysis you see fit."
    )
    return content


def test_fixed_parallel_request(url, temperature, max_tokens_response, tokens_count, parallel_count):
    """
    Send exactly `parallel_count` sub-requests in a single batch,
    each sub-request containing ~`tokens_count` tokens of content.

    Returns:
      {
        'tokens_count': tokens_count,
        'parallel_count': parallel_count,
        'elapsed_time': elapsed_time,
        'requests_per_second': requests_per_second
      }
    """
    headers = {"Content-Type": "application/json"}
    base_user_content = generate_test_content(tokens_count)

    # Build sub-requests
    subrequests = []
    for sub_id in range(1, parallel_count):
        subrequests.append({
            "messages": [
                {
                    "role": "user",
                    "content": base_user_content + f"\n(This is sub-request #{sub_id} of {parallel_count}.)"
                }
            ],
            "json_format": False,
            "schema": None
        })

    data = {
        "requests": subrequests,
        "temperature": temperature,
        "max_tokens": max_tokens_response
    }

    print(f"\n=== Testing ~{tokens_count} tokens per request with {parallel_count} parallel sub-requests ===")
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Request failed with exception: {e}")
        return {
            'tokens_count': tokens_count,
            'parallel_count': parallel_count,
            'elapsed_time': -1,
            'requests_per_second': 0.0
        }
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Attempt to parse JSON
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        print("Could not parse JSON from server response.")
        return {
            'tokens_count': tokens_count,
            'parallel_count': parallel_count,
            'elapsed_time': -1,
            'requests_per_second': 0.0
        }

    # Check if there's an error reported
    if "error" in response_json:
        print(f"Server returned error: {response_json['error']}")
        return {
            'tokens_count': tokens_count,
            'parallel_count': parallel_count,
            'elapsed_time': -1,
            'requests_per_second': 0.0
        }

    # If no error, it's successful
    requests_per_second = 0.0
    if elapsed_time > 0:
        requests_per_second = parallel_count / elapsed_time

    print(f"  -> Success: {parallel_count} sub-requests in {elapsed_time:.2f} s, ~{requests_per_second:.2f} req/s")

    return {
        'tokens_count': tokens_count,
        'parallel_count': parallel_count,
        'elapsed_time': elapsed_time,
        'requests_per_second': requests_per_second
    }


def main():
    parser = argparse.ArgumentParser(
        description="Test fixed parallel sub-requests for specified token sizes."
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
    args = parser.parse_args()

    # According to your note:
    # - For 1000 tokens, test 37 parallel sub-requests.
    # - For 2000 tokens, test 16 parallel sub-requests.
    # - For 3000 tokens, test 12 parallel sub-requests.
    # - "...and so on."
    #
    # Below is an example mapping. Adjust as needed:
    parallel_map = {
        # 1000: 37,
        2000: 2,
        3000: 2,
        4000: 2,
        5000: 7,
        6000: 6,
        7000: 5,
        8000: 4,
        9000: 3,
        10000: 3,
        20000: 2,
        30000: 1,
        37000: 1
    }

    results = []
    for tok_size, pcount in parallel_map.items():
        res = test_fixed_parallel_request(
            url=args.url,
            temperature=args.temperature,
            max_tokens_response=args.max_tokens_response,
            tokens_count=tok_size,
            parallel_count=pcount
        )
        results.append(res)

    # Print summary table
    print("\nComparative Table (Tokens vs Parallel Requests vs Speed):")
    print("=======================================================================")
    print(f"{'Tokens':<10} | {'ParallelReqs':<12} | {'Time(s)':<8} | {'Req/s':<8}")
    print("-----------------------------------------------------------------------")
    for r in results:
        if r['elapsed_time'] < 0:
            time_str = "ERROR"
            rps_str = "0.00"
        else:
            time_str = f"{r['elapsed_time']:.2f}"
            rps_str = f"{r['requests_per_second']:.2f}"
        print(
            f"{r['tokens_count']:<10} | "
            f"{r['parallel_count']:<12} | "
            f"{time_str:<8} | "
            f"{rps_str:<8}"
        )


if __name__ == "__main__":
    main()
