import argparse
import time

import requests

# The new base_user_content (~1600 tokens)
base_user_content = """[{'content': 'You must respond with JSON that matches this schema: {'type': 'object', 'properties': {'task_completed': {'type': 'boolean', 'description': 'Indicates whether the task was successfully completed based on the HTML comparison.'}, 'reason': {'type': 'string', 'description': 'A brief explanation of why the task was determined to be completed or not.'}, 'changes_detected': {'type': 'array', 'items': {'type': 'string'}, 'description': 'List of significant changes detected in the HTML before and after the action.'}}, 'required': ['task_completed', 'reason', 'changes_detected']}', 'role': 'system'}, {'content': 'You are a professional web page analyzer. Your task is to determine whether the given task was completed  \nwith the action given, by analyzing the HTML before and after the action.', 'role': 'system'}, {'content': 'Current action: type='ClickAction' selector=Selector(type=<SelectorType.ATTRIBUTE_VALUE_SELECTOR: 'attributeValueSelector'>, attribute='href', value='/login', case_sensitive=False) x=None y=None\nHTML Before:\n<body>\n <header>\n  <nav>\n   <div>\n    <a href=\"/\">\n     <span>\n      Home\n     </span>\n    </a>\n    <button aria-controls=\"navbarSupportedContent\" aria-expanded=\"false\" aria-label=\"Toggle navigation\" data-target=\"#navbarSupportedContent\" data-toggle=\"collapse\" type=\"button\">\n     Menu\n    </button>\n    <div>\n     <ul>\n      <li>\n       <a href=\"/\">\n        Home\n        <span>\n         (current)\n        </span>\n       </a>\n      </li>\n      <li>\n       <a href=\"/about/\">\n        About Us\n       </a>\n      </li>\n      <li>\n       <a href=\"/contact/\">\n        Contact\n       </a>\n      </li>\n      <li>\n       <a aria-expanded=\"false\" aria-haspopup=\"true\" data-toggle=\"dropdown\" href=\"#\">\n        Register\n       </a>\n       <div aria-labelledby=\"pages\">\n        <a href=\"/employee/register\">\n         Employee\n        </a>\n        <a href=\"/employer/register\">\n         Employers\n        </a>\n       </div>\n      </li>\n      <li>\n       <a href=\"/login\">\n        Login\n       </a>\n      </li>\n     </ul>\n    </div>\n   </div>\n  </nav>\n </header>\n <div>\n  <section>\n   <div>\n    <div>\n     <div>\n      <div>\n       <h2>\n        Find a job that will fit to your expertise.\n       </h2>\n       <form action=\"/search\" method=\"get\">\n        <div>\n         <div>\n          <div>\n           <div>\n            <label for=\"profession\">\n             Position\n            </label>\n           </div>\n          </div>\n          <div>\n           <div>\n            <label for=\"location\">\n             Location\n            </label>\n           </div>\n          </div>\n          <div>\n           <button type=\"submit\">\n           </button>\n          </div>\n         </div>\n        </div>\n       </form>\n      </div>\n     </div>\n    </div>\n   </div>\n  </section>\n  <section>\n   <div>\n    <h3>\n     Featured jobs\n    </h3>\n   </div>\n  </section>\n  <section>\n   <div>\n    <h4>\n     Trending this month\n    </h4>\n   </div>\n  </section>\n  <section>\n   <div>\n    <div>\n     <div>\n      <p>\n       Start searching for your new job now!\n      </p>\n      <p>\n       <a href=\"/jobs\">\n        See our job offers\n       </a>\n      </p>\n     </div>\n    </div>\n   </div>\n  </section>\n </div>\n <footer>\n  <div>\n   <div>\n    <div>\n     <div>\n      <h4>\n       About Jobs\n      </h4>\n      <p>\n       A job, employment, work or occupation, is a person's role in society. More specifically, a job\n                        is an activity, often regular and often performed in exchange for payment. Many people have\n                        multiple jobs. A person can begin a job by becoming an employee, volunteering, starting a\n                        business, or becoming a parent.\n      </p>\n     </div>\n    </div>\n   </div>\n  </div>\n  <div>\n   <div>\n    <div>\n     <div>\n      <p>\n       Online Itsourcecode Portal Jobs System 2021\n      </p>\n     </div>\n    </div>\n   </div>\n  </div>\n </footer>\n</body>\n\n\nHTML After:\n<body>\n <header>\n  <nav>\n   <div>\n    <a href=\"/\">\n     <span>\n      Home\n     </span>\n    </a>\n    <button aria-controls=\"navbarSupportedContent\" aria-expanded=\"false\" aria-label=\"Toggle navigation\" data-target=\"#navbarSupportedContent\" data-toggle=\"collapse\" type=\"button\">\n     Menu\n    </button>\n    <div>\n     <ul>\n      <li>\n       <a href=\"/\">\n        Home\n        <span>\n         (current)\n        </span>\n       </a>\n      </li>\n      <li>\n       <a href=\"/about/\">\n        About Us\n       </a>\n      </li>\n      <li>\n       <a href=\"/contact/\">\n        Contact\n       </a>\n      </li>\n      <li>\n       <a aria-expanded=\"false\" aria-haspopup=\"true\" data-toggle=\"dropdown\" href=\"#\">\n        Register\n       </a>\n       <div aria-labelledby=\"pages\">\n        <a href=\"/employee/register\">\n         Employee\n        </a>\n        <a href=\"/employer/register\">\n         Employers\n        </a>\n       </div>\n      </li>\n      <li>\n       <a href=\"/login\">\n        Login\n       </a>\n      </li>\n     </ul>\n    </div>\n   </div>\n  </nav>\n </header>\n <div>\n  <div>\n   <div>\n    <h3>\n     Login\n    </h3>\n    <p>\n     Already our have account?\n    </p>\n    <form action=\"\" method=\"post\">\n     <div>\n      <label for=\"id_email\">\n       Email\n      </label>\n     </div>\n     <div>\n      <label for=\"id_password\">\n       Password\n      </label>\n     </div>\n     <div>\n      <button type=\"submit\">\n       Log in\n      </button>\n     </div>\n    </form>\n   </div>\n  </div>\n </div>\n <footer>\n  <div>\n   <div>\n    <div>\n     <div>\n      <h4>\n       About Jobs\n      </h4>\n      <p>\n       A job, employment, work or occupation, is a person's role in society. More specifically, a job\n                        is an activity, often regular and often performed in exchange for payment. Many people have\n                        multiple jobs. A person can begin a job by becoming an employee, volunteering, starting a\n                        business, or becoming a parent.\n      </p>\n     </div>\n    </div>\n   </div>\n  </div>\n  <div>\n   <div>\n    <div>\n     <div>\n      <p>\n       Online Itsourcecode Portal Jobs System 2021\n      </p>\n     </div>\n    </div>\n   </div>\n  </div>\n </footer>\n</body>\n', 'role': 'user'}]"""

# Updated parallel_map with 1600-tokens base user content:
parallel_map = {
    1600: 40,
}


def build_content_for_tokens_in(tokens_in):
    """
    Each base_user_content is ~1600 tokens.
    So to get tokens_in, we do replicate_count = tokens_in // 1600
    """
    replicate_count = tokens_in // 1600
    return base_user_content * replicate_count


def test_parallel_map(url, temperature, max_tokens):
    """
    For each (tokens_in -> subrequests) in parallel_map:
      - build subrequests each with ~ tokens_in worth of content
      - post them all in ONE request to /generate_parallel
      - measure time, parse stats, store them
      - print summary at the end
    """
    headers = {"Content-Type": "application/json"}
    results = []

    for tokens_in, sub_count in parallel_map.items():
        # Build repeated content to approximate 'tokens_in' tokens per sub-request
        repeated_base = build_content_for_tokens_in(tokens_in)

        subrequests = []
        for sub_id in range(1, sub_count + 1):
            content = repeated_base + f"\n\n(This is sub-request #{sub_id} of {sub_count}, targeting ~{tokens_in} tokens.)"
            subrequests.append({"messages": [{"role": "user", "content": content}], "json_format": False, "schema": None})

        data = {"requests": subrequests, "temperature": temperature, "max_tokens": max_tokens}

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

        # Extract possible server stats if provided
        stats = response_json.get("stats", {})
        total_tokens_in = stats.get("total_tokens_in")
        total_time = stats.get("total_time")
        tokens_per_second = stats.get("tokens_per_second")

        # Calculate requests/s based on sub_count and elapsed time
        requests_per_second = sub_count / elapsed

        results.append(
            {
                "tokens_in": tokens_in,
                "sub_count": sub_count,
                "elapsed_time_s": elapsed,
                "requests_per_second": requests_per_second,
                "server_total_tokens_in": total_tokens_in,
                "server_total_time": total_time,
                "server_tokens_per_second": tokens_per_second,
            }
        )

    # Print a final table of results
    print("\n===== Summary Table =====")
    print("tokens_in | sub_requests | elapsed_time_s | requests/s | server_total_tokens_in | server_total_time | server_tokens/s")
    for r in results:
        print(
            f"{r['tokens_in']:>9} | {r['sub_count']:>12} | {r['elapsed_time_s']:>14.2f} | "
            f"{r['requests_per_second']:>10.2f} | {str(r['server_total_tokens_in']):>22} | "
            f"{str(r['server_total_time']):>17} | {str(r['server_tokens_per_second']):>15}"
        )


def main():
    parser = argparse.ArgumentParser(description="Send batch requests to /generate_parallel using parallel_map (1600-token base).")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:6000/generate_parallel", help="The /generate_parallel endpoint URL.")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature for generation.")
    parser.add_argument("--max_tokens", type=int, default=2000, help="Max tokens to generate in the response.")
    args = parser.parse_args()

    test_parallel_map(url=args.url, temperature=args.temperature, max_tokens=args.max_tokens)


if __name__ == "__main__":
    main()
