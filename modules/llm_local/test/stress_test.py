#!/usr/bin/env python3

"""
stress_test.py

A script to stress test the /generate endpoint of a Flask inference service.

What this script does:
1. Sends a variety of requests (both simple and more complex).
2. Sends multiple requests concurrently (configurable).
3. Validates each response to ensure it is not corrupt or contains known error messages.
4. If a known generation error or invalid response is encountered, it stops and prints debug info.
5. Reports basic statistics on successes/failures and response times.

Usage example:
    python stress_test.py \
      --url http://localhost:6000/generate \
      --concurrency 5 \
      --total_requests 20
"""

import argparse
import concurrent.futures
import json
import random
import time
import requests

# ============================================================================================
# Some example requests to send.
# We'll randomly choose among them to ensure variety.
# Feel free to add or modify requests as needed.
# ============================================================================================

EXAMPLE_REQUESTS = [
    # Simple request: short question
    {
        "messages": [
            {
                "role": "system",
                "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 128
    },
    # JSON-format request with a schema (somewhat simpler)
    {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You must respond in **valid JSON** with the following schema:\n"
                    "{\n"
                    "  \"type\": \"object\",\n"
                    "  \"properties\": {\n"
                    "    \"title\": {\"type\": \"string\"},\n"
                    "    \"description\": {\"type\": \"string\"}\n"
                    "  },\n"
                    "  \"required\": [\"title\", \"description\"]\n"
                    "}"
                )
            },
            {
                "role": "user",
                "content": "Provide a short JSON object describing the Mona Lisa painting."
            }
        ],
        "temperature": 0.5,
        "max_tokens": 256,
        "json_format": True,
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["title", "description"]
        }
    },
    # Longer text request:
    {
        "messages": [
            {
                "role": "system",
                "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
            },
            {
                "role": "user",
                "content": (
                    "Please provide a detailed explanation of how Large Language Models are trained, "
                    "including information on tokenization, neural network architectures, training "
                    "objectives, and typical hardware requirements."
                )
            }
        ],
        "temperature": 0.8,
        "max_tokens": 512
    },
    # Potentially complex JSON request with user-provided schema
    {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You must respond in **valid JSON** that meets the following schema.\n"
                    "Do not include extra keys. Output **only** the JSON object.\n"
                    "{\n"
                    "  \"type\": \"object\",\n"
                    "  \"properties\": {\n"
                    "    \"one_phrase_summary\": {\n"
                    "      \"type\": \"string\",\n"
                    "      \"description\": \"A concise one-sentence summary.\"\n"
                    "    },\n"
                    "    \"details\": {\n"
                    "      \"type\": \"string\",\n"
                    "      \"description\": \"Longer explanation.\"\n"
                    "    }\n"
                    "  },\n"
                    "  \"required\": [\"one_phrase_summary\", \"details\"]\n"
                    "}"
                )
            },
            {
                "role": "system",
                "content": (
                    "You are an expert content reviewer who only returns valid JSON. "
                    "No extra fields, no text outside JSON."
                )
            },
            {
                "role": "user",
                "content": (
                    "Summarize the pros and cons of using an advanced language model in "
                    "a customer service chat application."
                )
            }
        ],
        "temperature": 0.6,
        "max_tokens": 300,
        "json_format": True,
        "schema": {
            "type": "object",
            "properties": {
                "one_phrase_summary": {"type": "string"},
                "details": {"type": "string"}
            },
            "required": ["one_phrase_summary", "details"]
        }
    },
]


def send_request(url, request_data, request_id):
    """
    Sends a single request to the given URL with the JSON payload.
    Returns a tuple: (request_id, success_bool, response_time, error_message, response_text)
      - request_id: identifier of the request
      - success_bool: True if the request got a 200 and the output is presumably valid
      - response_time: how many seconds the request took
      - error_message: a string describing any error encountered (or None if success_bool is True)
      - response_text: the 'output' field from the JSON response if present
    """
    start = time.time()
    try:
        resp = requests.post(url, json=request_data, timeout=300)  # 5-minute timeout
        elapsed = time.time() - start

        if resp.status_code != 200:
            return (request_id, False, elapsed, f"HTTP {resp.status_code}", None)

        # We expect a JSON with either {"output": "..."} or {"error": "..."}
        try:
            content = resp.json()
        except json.JSONDecodeError:
            return (request_id, False, elapsed, "Response not valid JSON", None)

        # Check if there's an error in the response
        if "error" in content:
            return (request_id, False, elapsed, f"Error in response: {content['error']}", None)

        if "output" not in content:
            return (request_id, False, elapsed, "No 'output' key in response JSON", None)

        output_text = content["output"]

        # Check for known "Generation error" messages
        # We will look for "Generation error:" substring, or any mention of "CUDA error"
        # or the known "probability tensor contains either `inf`, `nan`" snippet.
        error_substrings = [
            "Generation error:",
            "CUDA error",
            "probability tensor contains either `inf`, `nan`"
        ]
        for sub in error_substrings:
            if sub in output_text:
                # We treat it as a failure
                return (request_id, False, elapsed, f"Model generation error: {output_text}", output_text)

        # If we made it this far, we consider it a success.
        return (request_id, True, elapsed, None, output_text)

    except Exception as e:
        # Something else went wrong
        elapsed = time.time() - start
        return (request_id, False, elapsed, f"Exception: {str(e)}", None)


def generate_random_request():
    """
    Picks one of the EXAMPLE_REQUESTS at random.
    Could be extended to randomize temperature/max_tokens, etc.
    """
    base = random.choice(EXAMPLE_REQUESTS)
    # Create a shallow copy so as not to mutate the original example
    data = dict(base)
    # Slight random variations on temperature or max_tokens if desired
    data["temperature"] = round(random.uniform(0.1, 1.0), 2)
    data["max_tokens"] = random.choice([512, 1024, 2048])
    # Return a new request
    return data


def main():
    parser = argparse.ArgumentParser(description="Stress test a Qwen inference endpoint.")
    parser.add_argument("--url", type=str, default="http://localhost:6000/generate",
                        help="Full URL of the /generate endpoint.")
    parser.add_argument("--concurrency", type=int, default=5,
                        help="Number of concurrent threads.")
    parser.add_argument("--total_requests", type=int, default=20,
                        help="Total number of requests to send.")
    args = parser.parse_args()

    url = args.url
    concurrency = args.concurrency
    total_requests = args.total_requests

    print(f"== Starting Stress Test ==\n"
          f"Endpoint: {url}\n"
          f"Concurrency: {concurrency}\n"
          f"Total requests: {total_requests}\n")

    # We'll store the results here
    results = []
    request_counter = 0

    # Use a ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_request = {}
        for _ in range(total_requests):
            request_counter += 1
            data = generate_random_request()
            future = executor.submit(send_request, url, data, request_counter)
            future_to_request[future] = request_counter

        # As soon as each future completes, we process the result
        for future in concurrent.futures.as_completed(future_to_request):
            req_id = future_to_request[future]
            try:
                (request_id, success, resp_time, error_msg, output_text) = future.result()
                results.append((request_id, success, resp_time, error_msg, output_text))

                # Print a log for each finished request
                print(f"Request #{request_id} finished in {resp_time:.2f}s. Success: {success}")

                # If we detect an error, we print debug info and stop immediately
                if not success:
                    print("\n--- ERROR DETECTED ---")
                    print(f"Request #{request_id} failed.")
                    print(f"Error Message: {error_msg}")
                    print(f"Response text: {output_text}")
                    print("\nAborting the stress test now.")
                    # Print partial summary
                    summarize_results(results)
                    exit(1)

            except Exception as e:
                # Catch any unexpected exception
                results.append((req_id, False, 0.0, str(e), None))
                print("\n--- EXCEPTION DETECTED ---")
                print(f"Request #{req_id} triggered an exception: {e}")
                print("\nAborting the stress test now.")
                summarize_results(results)
                exit(1)

    # If we get here, all requests succeeded
    summarize_results(results)


def summarize_results(results):
    """
    Prints a summary of test outcomes, including average time, success/failure counts, etc.
    """
    total = len(results)
    failures = [r for r in results if not r[1]]
    successes = [r for r in results if r[1]]
    avg_time = sum(r[2] for r in results) / total if total > 0 else 0.0

    print("\n=== Test Summary ===")
    print(f"Total Requests: {total}")
    print(f"Successful:     {len(successes)}")
    print(f"Failed:         {len(failures)}")
    print(f"Average time:   {avg_time:.2f}s per request\n")

    if failures:
        print("Failures detail:")
        for (req_id, _, t, err, out) in failures:
            print(f"  - Request #{req_id} took {t:.2f}s, error = {err}")


if __name__ == "__main__":
    main()
