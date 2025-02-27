import requests
import json
import time
import argparse


def make_parallel_request(N=5):
    """
    Sends a batch of N sub-requests to the /generate_parallel endpoint.
    Each sub-request has its own set of messages.
    """
    url = "http://127.0.0.1:6000/generate_parallel"
    headers = {"Content-Type": "application/json"}

    # Build the "requests" array with N copies (or variations) of the messages
    requests_list = []
    for i in range(N):
        requests_list.append({
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are Qwen, created by Alibaba Cloud. "
                        f"You are a helpful assistant. (Sub-request {i+1})"
                    )
                },
                {
                    "role": "user",
                    "content": "Give me a short introduction to large language model."
                }
            ],
            "json_format": False,
            "schema": None
        })

    # Global parameters for the entire batch
    data = {
        "requests": requests_list,
        "temperature": 0.1,
        "max_tokens": 256
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end_time = time.time()

    # Parse JSON response
    try:
        response_json = response.json()
    except:
        response_json = {"error": "Unable to parse JSON from server response"}

    return end_time - start_time, response_json


def main():
    parser = argparse.ArgumentParser(description="Test parallel requests to /generate_parallel.")
    parser.add_argument(
        "--number_request",
        type=int,
        default=5,
        help="Number of sub-requests to batch in one call"
    )
    args = parser.parse_args()

    # Number of sub-requests to batch in one call
    N = args.number_request

    elapsed, result = make_parallel_request(N)
    print(f"Parallel request with {N} sub-requests took {elapsed:.2f}s\n")
    print("Full result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
