import requests
import json
import time
import argparse

# Large message to be used in each sub-request (unit chunk = ~1000 tokens):
base_user_content = """data = {
    "request_number": 381,
    "timestamp": 1740840474.1822062,
    "messages": [
        {
            "role": "system",
            "content": (
                "You must respond in **valid JSON** that meets the following schema.\\n\\n"
                "Do not include extra keys. Output **only** the JSON object.\\n\\n"
                "{\\n"
                "  \\"type\\": \\"object\\",\\n"
                "  \\"properties\\": {\\n"
                "    \\"one_phrase_summary\\": {\\n"
                "      \\"type\\": \\"string\\",\\n"
                "      \\"description\\": \\"A concise one-sentence summary of the element's purpose.\\"\\n"
                "    },\\n"
                "    \\"summary\\": {\\n"
                "      \\"type\\": \\"string\\",\\n"
                "      \\"description\\": \\"A brief description of the element's purpose and functionality.\\"\\n"
                "    },\\n"
                "    \\"categories\\": {\\n"
                "      \\"type\\": \\"array\\",\\n"
                "      \\"items\\": {\\n"
                "        \\"type\\": \\"string\\"\\n"
                "      },\\n"
                "      \\"description\\": \\"An array of relevant categories for this element, focusing on its content and use.\\"\\n"
                "    },\\n"
                "    \\"functionality\\": {\\n"
                "      \\"type\\": \\"array\\",\\n"
                "      \\"items\\": {\\n"
                "        \\"type\\": \\"string\\"\\n"
                "      },\\n"
                "      \\"description\\": \\"An array describing the potential functionalities and use cases of the element.\\"\\n"
                "    },\\n"
                "    \\"media_files_description\\": {\\n"
                "      \\"type\\": [\\n"
                "        \\"array\\",\\n"
                "        \\"null\\"\\n"
                "      ],\\n"
                "      \\"items\\": {\\n"
                "        \\"type\\": \\"object\\",\\n"
                "        \\"properties\\": {\\n"
                "          \\"tag\\": {\\n"
                "            \\"type\\": \\"string\\"\\n"
                "          },\\n"
                "          \\"src\\": {\\n"
                "            \\"type\\": \\"string\\"\\n"
                "          },\\n"
                "          \\"alt\\": {\\n"
                "            \\"type\\": \\"string\\"\\n"
                "          }\\n"
                "        },\\n"
                "        \\"required\\": [\\n"
                "          \\"tag\\",\\n"
                "          \\"src\\",\\n"
                "          \\"alt\\"\\n"
                "        ]\\n"
                "      },\\n"
                "      \\"description\\": \\"A detailed description of images or videos within the element, or null if none are present.\\"\\n"
                "    },\\n"
                "    \\"key_words\\": {\\n"
                "      \\"type\\": \\"array\\",\\n"
                "      \\"items\\": {\\n"
                "        \\"type\\": \\"string\\"\\n"
                "      },\\n"
                "      \\"description\\": \\"An array of key phrases or words relevant to the element for search purposes.\\"\\n"
                "    },\\n"
                "    \\"relevant_fields\\": {\\n"
                "      \\"type\\": [\\n"
                "        \\"array\\",\\n"
                "        \\"null\\"\\n"
                "    \\"accessibility\\": {\\n"
                "      \\"type\\": [\\n"
                "        \\"array\\",\\n"
                "        \\"null\\"\\n"
                "      ],\\n"
                "      \\"items\\": {\\n"
                "        \\"type\\": \\"string\\"\\n"
                "      },\\n"
                "      \\"description\\": \\"Accessibility considerations for the element, or null if none exist.\\"\\n"
                "    }\\n"
                "}\\n"
            )
        },
        {
            "role": "system",
            "content": (
                "You are an expert JSON content reviewer tasked with analyzing the given RAW JSON/Unstructured\\n"
                " segment of a webpage and providing a strictly valid JSON-formatted analysis.\\n\\n"
                "Important Requirements:\\n"
                "- Return only one JSON object (no arrays, no multiple objects).\\n"
                "- Do not include code fences (```).\\n\\n"
                "If the input cannot be summarized into a valid JSON object, return an empty JSON object: {}."
            )
        },
        {
            "role": "user",
            "content": "Summarize the content and functionality of this HTML element:{...} (example truncated)"
        }
    ],
}
"""

# The mapping: each 'tokens_in' means "repeat base_user_content enough times to reach ~this many tokens"
# and then create 'sub_count' sub-requests in one single batch to /generate_parallel.
parallel_map = {
    1000: 37,
    2000: 16,
    3000: 12,
    4000: 9,
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


def build_content_for_tokens_in(tokens_in):
    """
    Naive approach: For each 1000 tokens, we replicate base_user_content 1 time.
    So 2000 tokens => 2 times; 3000 => 3 times, etc.
    """
    # This assumes tokens_in is a multiple of 1000 in parallel_map
    repeat_count = tokens_in // 1000
    return base_user_content * repeat_count


def test_parallel_map(url, temperature, max_tokens):
    """
    For each (tokens_in -> subrequests) in parallel_map:
      - build subrequests each with ~ tokens_in worth of content
      - post them all in ONE request to /generate_parallel
      - measure time, parse stats, store them
      - print the summary table at the end
    """
    headers = {"Content-Type": "application/json"}
    results = []

    for tokens_in, sub_count in parallel_map.items():
        # Build the repeated content to target 'tokens_in' per sub-request
        repeated_base = build_content_for_tokens_in(tokens_in)

        subrequests = []
        for sub_id in range(1, sub_count + 1):
            content = (
                repeated_base
                + f"\n\n(This is sub-request #{sub_id} of {sub_count}, targeting ~{tokens_in} tokens.)"
            )
            subrequests.append({
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "json_format": False,
                "schema": None
            })

        data = {
            "requests": subrequests,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        print(f"\n--- Testing {tokens_in} tokens_in with {sub_count} sub-requests in parallel ---")
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=data)
        except Exception as e:
            print(f"Request with {sub_count} sub-requests failed: {e}")
            continue
        end_time = time.time()
        elapsed = end_time - start_time

        # Attempt to parse response JSON:
        try:
            response_json = response.json()
        except Exception as e:
            print(f"Could not parse JSON for request with {sub_count} sub-requests: {e}")
            continue

        if "error" in response_json:
            print(f"Server returned error: {response_json['error']}")
            continue

        # We can also extract any server stats if provided:
        stats = response_json.get("stats", {})
        total_tokens_in = stats.get("total_tokens_in")
        total_time = stats.get("total_time")
        tokens_per_second = stats.get("tokens_per_second")

        # requests/s based on sub_count and our measured elapsed
        requests_per_second = sub_count / elapsed

        results.append({
            "tokens_in": tokens_in,
            "sub_count": sub_count,
            "elapsed_time_s": elapsed,
            "requests_per_second": requests_per_second,
            "server_total_tokens_in": total_tokens_in,
            "server_total_time": total_time,
            "server_tokens_per_second": tokens_per_second
        })

    # Print a table of results
    print("\n===== Summary Table =====")
    print("tokens_in | sub_requests | elapsed_time_s | requests/s | server_total_tokens_in | server_total_time | server_tokens/s")
    for r in results:
        print(f"{r['tokens_in']:>9} | {r['sub_count']:>12} | {r['elapsed_time_s']:>14.2f} | "
              f"{r['requests_per_second']:>10.2f} | {str(r['server_total_tokens_in']):>22} | "
              f"{str(r['server_total_time']):>17} | {str(r['server_tokens_per_second']):>15}")


def main():
    parser = argparse.ArgumentParser(description="Send batch requests to /generate_parallel using parallel_map.")
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
        "--max_tokens",
        type=int,
        default=2000,
        help="Max tokens to generate in the response."
    )
    args = parser.parse_args()

    test_parallel_map(
        url=args.url,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )


if __name__ == "__main__":
    main()
