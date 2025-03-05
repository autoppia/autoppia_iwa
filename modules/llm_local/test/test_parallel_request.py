import argparse
import json
import time

import requests


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
        requests_list.append(
            {
                "messages": [
                    {"role": "system", "content": (f"You are Qwen, created by Alibaba Cloud. " f"You are a helpful assistant. (Sub-request {i + 1})")},
                    {
                        "role": "user",
                        "content": """"
                                    You are a test analyzer for web automation testing. Review the tests below and decide which ones to keep.

                                    TASK CONTEXT:
                                    - Task Prompt: example task prompt
                                    - Success Criteria: example success critera
                                    TESTS TO REVIEW:
                                    example test

                                    GUIDELINES:
                                    1. Backend tests (CheckEventTest) are preferred over frontend tests or checkUrl tests as they are more reliable. Only in case they try to validate the same thing.
                                    2. Intelligent judgment tests (JudgeBaseOnHTML, JudgeBaseOnScreenshot) are useful for complex criteria
                                    3. Avoid keeping tests that check for the same thing in different ways
                                    4. Prioritize tests that directly verify the success criteria
                                    5. Aim to keep 1-3 high-quality tests in total
                                    6. Delete tests that make up parameters like making up event_names in CheckEventTest, or making up keywords in FindInHtmlTest.
                                    7. Judge Tests like JudgeBaseOnHTML or JudgeBaseOnScreenshot should be use if all the other tests do not validate completely the task or there are no more tests. This are fallback tests.

                                    RESPOND WITH A JSON ARRAY of decisions, one for each test, like this:
                                    [
                                    {{
                                        "index": 0,
                                        "keep": true,
                                        "reason": "High quality backend test that verifies core success criteria"
                                    }},
                                    {{
                                        "index": 1,
                                        "keep": false,
                                        "reason": "Redundant with test #0 which is more reliable"
                                    }}
                                    ]

                                    For EACH test in the input, include a decision object with:
                                    - "index": The original index of the test
                                    - "keep": true/false decision
                                    - "reason": Brief explanation of your decision

                                    Return ONLY the JSON array, no additional text.

                                    Extra Class-Specific Data:
                                    example extra data
                                    """,
                    },
                ],
                "json_format": False,
                "schema": None,
            }
        )

    # Global parameters for the entire batch
    data = {"requests": requests_list, "temperature": 0.1, "max_tokens": 256}

    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end_time = time.time()

    # Parse JSON response
    try:
        response_json = response.json()
    except Exception:
        response_json = {"error": "Unable to parse JSON from server response"}

    return end_time - start_time, response_json


def main():
    parser = argparse.ArgumentParser(description="Test parallel requests to /generate_parallel.")
    parser.add_argument("--number_request", type=int, default=5, help="Number of sub-requests to batch in one call")
    args = parser.parse_args()

    # Number of sub-requests to batch in one call
    N = args.number_request

    elapsed, result = make_parallel_request(N)
    print(f"Parallel request with {N} sub-requests took {elapsed:.2f}s\n")
    print("Full result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
