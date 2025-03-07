import requests
import json
import time
import argparse

# Large message to be used in each sub-request:
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
                "      ],\\n"
                "      \\"items\\": {\\n"
                "        \\"type\\": \\"object\\",\\n"
                "        \\"properties\\": {\\n"
                "          \\"type\\": {\\n"
                "            \\"type\\": \\"string\\"\\n"
                "          },\\n"
                "          \\"attributes\\": {\\n"
                "            \\"type\\": \\"array\\",\\n"
                "            \\"items\\": {\\n"
                "              \\"type\\": \\"string\\"\\n"
                "            }\\n"
                "          }\\n"
                "        },\\n"
                "        \\"required\\": [\\n"
                "          \\"type\\",\\n"
                "          \\"attributes\\"\\n"
                "        ]\\n"
                "      },\\n"
                "      \\"description\\": \\"A list of relevant fields or attributes for the element, or null if not applicable.\\"\\n"
                "    },\\n"
                "    \\"curiosities\\": {\\n"
                "      \\"type\\": [\\n"
                "        \\"string\\",\\n"
                "        \\"null\\"\\n"
                "      ],\\n"
                "      \\"description\\": \\"Unique or remarkable aspects of the element, or null if none are applicable.\\"\\n"
                "    },\\n"
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
                "- The output must be valid JSON that can be directly parsed by `json.loads` without modification.\\n"
                "- Use double quotes for all keys and string values.\\n"
                "- Do not include trailing commas.\\n"
                "- Do not include any text or explanation outside of the JSON object.\\n"
                "- If something is not relevant, omit it entirely rather than returning empty lists or objects.\\n"
                "- Do not include comments or additional text outside the JSON.\\n"
                "- Do not include code fences (```).\\n\\n"
                "If the input cannot be summarized into a valid JSON object, return an empty JSON object: {}."
            )
        },
        {
            "role": "user",
            "content": (
                "Summarize the content and functionality of this HTML element:{...} (example truncated)"
            )
        }
    ],
}
"""

# The mapping of total tokens_in => number of sub-requests to send in one batch.
# We do NOT exceed these parallel counts to avoid running out of memory.
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


def test_parallel_map(url, temperature, max_tokens):
    """
    For each (tokens_in -> subrequests) in parallel_map:
      - Create subrequests of 'base_user_content'
      - Post them all in ONE request to /generate_parallel
      - Measure time, parse stats, and store them.
      - Print a summary table at the end.
    """
    headers = {"Content-Type": "application/json"}
    results = []

    for tokens_in, sub_count in parallel_map.items():
        # Build the sub_count subrequests, each with 1 user message
        subrequests = []
        for sub_id in range(1, sub_count + 1):
            subrequests.append({
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            base_user_content
                            + f"\n\n(This is sub-request #{sub_id} of {sub_count}, simulating ~{tokens_in} tokens in total.)"
                        )
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
        total_time = stats.get("total_time")  # server's measure (may differ from our measurement)
        tokens_per_second = stats.get("tokens_per_second")
        # We'll rely on our own measured elapsed time for consistency

        # The actual requests/second from our side:
        requests_per_second = sub_count / elapsed

        results.append({
            "tokens_in": tokens_in,
            "sub_count": sub_count,
            "elapsed_time_s": elapsed,
            "requests_per_second": requests_per_second,
            "server_tokens_in": total_tokens_in,
            "server_total_time": total_time,
            "server_tokens_per_second": tokens_per_second
        })

    # Print a table of results
    print("\n===== Summary Table =====")
    print("tokens_in | sub_requests | elapsed_time_s | requests/s | server_total_tokens_in | server_total_time | server_tokens/s")
    for r in results:
        print(f"{r['tokens_in']:>9} | {r['sub_count']:>12} | {r['elapsed_time_s']:>14.2f} | "
              f"{r['requests_per_second']:>10.2f} | {str(r['server_tokens_in']):>22} | "
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
