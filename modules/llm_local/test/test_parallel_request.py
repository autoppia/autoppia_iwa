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
                "Summarize the content and functionality of this HTML element:{'tag': 'header', 'attributes': {}, "
                "'textContent': 'Home\\n\\nMenu\\n\\n\\n\\n\\nHome (current)\\n\\n\\nAbout Us\\n\\n\\nContact\\n"
                "\\n\\nRegister\\n                            \\n\\nEmployee\\nEmployers\\n\\n\\n\\n\\nLogin', 'children': [{'tag': 'nav', "
                "'attributes': {}, 'textContent': 'Home\\n\\nMenu\\n\\n\\n\\n\\nHome (current)\\n\\n\\nAbout Us\\n\\n\\nContact\\n"
                "\\n\\nRegister\\n                            \\n\\nEmployee\\nEmployers\\n\\n\\n\\n\\nLogin', "
                "'children': [{'tag': 'div', 'attributes': {}, 'textContent': 'Home\\n\\nMenu\\n\\n\\n\\n\\nHome (current)\\n\\n\\n"
                "About Us\\n\\n\\nContact\\n\\n\\nRegister\\n                            \\n\\nEmployee\\nEmployers\\n\\n\\n\\n\\nLogin', "
                "'children': [{'tag': 'a', 'attributes': {'href': '/'}, 'textContent': 'Home', 'children': [{'tag': 'img', "
                "'attributes': {'src': '/static/img/itsourcecodes.jpg', 'alt': 'logo'}, 'textContent': '', 'children': [], "
                "'id': None, 'element_id': 5, 'parent_element_id': 4, 'path': '//1/2/3/4/5', 'events_triggered': [], "
                "'analysis': None}, {'tag': 'span', 'attributes': {}, 'textContent': 'Home', 'children': [], 'id': None, "
                "'element_id': 6, 'parent_element_id': 4, 'path': '//1/2/3/4/6', 'events_triggered': [], 'analysis': None}], "
                "'id': None, 'element_id': 4, 'parent_element_id': 3, 'path': '//1/2/3/4', 'events_triggered': [], "
                "'analysis': None}, {'tag': 'button', 'attributes': {'type': 'button', 'aria-controls': 'navbarSupportedContent', "
                "'aria-expanded': 'false', 'aria-label': 'Toggle navigation'}, 'textContent': 'Menu', 'children': [], 'id': None, "
                "'element_id': 7, 'parent_element_id': 3, 'path': '//1/2/3/7', 'events_triggered': [], 'analysis': None}, "
                "{'tag': 'div', 'attributes': {'id': 'navbarSupportedContent'}, 'textContent': 'Home (current)\\n\\n\\nAbout Us\\n\\n\\nContact\\n"
                "\\n\\nRegister\\n                            \\n\\nEmployee\\nEmployers\\n\\n\\n\\n\\nLogin', 'children': "
                "[{'tag': 'ul', 'attributes': {}, 'textContent': 'Home (current)\\n\\n\\nAbout Us\\n\\n\\nContact\\n\\n\\nRegister\\n"
                "                            \\n\\nEmployee\\nEmployers\\n\\n\\n\\n\\nLogin', 'children': [{'tag': 'li', 'attributes': {}, "
                "'textContent': 'Home (current)', 'children': [{'tag': 'a', 'attributes': {'href': '/'}, 'textContent': 'Home (current)', "
                "'children': [{'tag': 'span', 'attributes': {}, 'textContent': '(current)', 'children': [], 'id': None, 'element_id': 12, "
                "'parent_element_id': 11, 'path': '//1/2/3/8/9/10/11/12', 'events_triggered': [], 'analysis': None}], 'id': None, "
                "'element_id': 11, 'parent_element_id': 10, 'path': '//1/2/3/8/9/10/11', 'events_triggered': [], 'analysis': None}], "
                "'id': None, 'element_id': 10, 'parent_element_id': 9, 'path': '//1/2/3/8/9/10', 'events_triggered': [], 'analysis': None}, "
                "{'tag': 'li', 'attributes': {}, 'textContent': 'About Us', 'children': [{'tag': 'a', 'attributes': {'href': '/about/'}, "
                "'textContent': 'About Us', 'children': [], 'id': None, 'element_id': 14, 'parent_element_id': 13, 'path': '//1/2/3/8/9/13/14', "
                "'events_triggered': [], 'analysis': None}], 'id': None, 'element_id': 13, 'parent_element_id': 9, "
                "'path': '//1/2/3/8/9/13', 'events_triggered': [], 'analysis': None}, {'tag': 'li', 'attributes': {}, 'textContent': 'Contact', "
                "'children': [{'tag': 'a', 'attributes': {'href': '/contact/'}, 'textContent': 'Contact', 'children': [], 'id': None, "
                "'element_id': 16, 'parent_element_id': 15, 'path': '//1/2/3/8/9/15/16', 'events_triggered': [], 'analysis': None}], "
                "'id': None, 'element_id': 15, 'parent_element_id': 9, 'path': '//1/2/3/8/9/15', 'events_triggered': [], 'analysis': None}, "
                "{'tag': 'li', 'attributes': {}, 'textContent': 'Register\\n                            \\n\\nEmployee\\nEmployers', "
                "'children': [{'tag': 'a', 'attributes': {\\"id\\": \\"pages\\", \\"href\\": \\"#\\", \\"aria-haspopup\\": \\"true\\", \\"aria-expanded\\": \\"false\\"}, "
                "'textContent': 'Register', 'children': [], 'id': 'pages', 'element_id': 18, 'parent_element_id': 17, "
                "'path': '//1/2/3/8/9/17/18', 'events_triggered': [], 'analysis': None}, {'tag': 'div', 'attributes': {\\"aria-labelledby\\": \\"pages\\"}, "
                "'textContent': 'Employee\\nEmployers', 'children': [{'tag': 'a', 'attributes': {\\"href\\": \\"/employee/register\\"}, 'textContent': 'Employee', "
                "'children': [], 'id': None, 'element_id': 20, 'parent_element_id': 19, 'path': '//1/2/3/8/9/17/19/20', 'events_triggered': [], "
                "'analysis': None}, {'tag': 'a', 'attributes': {\\"href\\": \\"/employer/register\\"}, 'textContent': 'Employers', 'children': [], "
                "'id': None, 'element_id': 21, 'parent_element_id': 19, 'path': '//1/2/3/8/9/17/19/21', 'events_triggered': [], 'analysis': None}], "
                "'id': None, 'element_id': 19, 'parent_element_id': 17, 'path': '//1/2/3/8/9/17/19', 'events_triggered': [], 'analysis': None}], "
                "'id': None, 'element_id': 17, 'parent_element_id': 9, 'path': '//1/2/3/8/9/17', 'events_triggered': [], 'analysis': None}, "
                "{'tag': 'li', 'attributes': {}, 'textContent': 'Login', 'children': [{'tag': 'a', 'attributes': {'href': '/login'}, "
                "'textContent': 'Login', 'children': [], 'id': None, 'element_id': 23, 'parent_element_id': 22, 'path': '//1/2/3/8/9/22/23', "
                "'events_triggered': [], 'analysis': None}], 'id': None, 'element_id': 22, 'parent_element_id': 9, 'path': '//1/2/3/8/9/22', "
                "'events_triggered': [], 'analysis': None}], 'id': None, 'element_id': 9, 'parent_element_id': 8, 'path': '//1/2/3/8/9', "
                "'events_triggered': [], 'analysis': None}], 'id': 'navbarSupportedContent', 'element_id': 8, 'parent_element_id': 3, "
                "'path': '//1/2/3/8', 'events_triggered': [], 'analysis': None}], 'id': None, 'element_id': 3, 'parent_element_id': 2, "
                "'path': '//1/2/3', 'events_triggered': [], 'analysis': None}], 'id': None, 'element_id': 2, 'parent_element_id': 1, "
                "'path': '//1/2', 'events_triggered': [], 'analysis': None}], 'id': None, 'element_id': 1, 'parent_element_id': None, "
                "'path': '//1', 'events_triggered': [], 'analysis': None}Include the following fields for each element:- one_phrase_summary: "
                "Provide a one-sentence summary of the element.- summary: Provide a brief description of the element's purpose and use.- "
                "categories: Suggest some categories for this section as if it were part of a blog.- functionality: Describe all possible "
                "functionalities in this section. List potential use cases for this section, including user interactions and typical behaviors.- "
                "media_files_description: Describe what the images or videos might contain, individually.- key_words: Provide a list of key words "
                "or phrases relevant to the element, focusing on what a user might search for in this section.- relevant_fields: List relevant fields "
                "or attributes based on the element type:    For form fields, list their attributes (e.g., type, name, placeholder, required).    "
                "For links, provide the href and target attributes.    For images, provide the src and alt attributes.- curiosities: Highlight any "
                "remarkable aspects that make this section unique and important.- accessibility: Highlight any accessibility features or considerations "
                "for this section.Do not add boilerplate or not useful information. Only add quality information that adds value and insights to the "
                "understanding of the web.If something do not add value set it as nullONLY INCLUDE THIS FIELDS AND NOT THE ELEMENT ITSELFPlease provide "
                "the JSON output in the format specified above."
            )
        }
    ],
}
"""


def test_increasing_subrequests(url, start_subrequests, max_subrequests, temperature, max_tokens):
    """
    For i in [start_subrequests..max_subrequests] (stepping by 5 or 10):
      - We create an array of i sub-requests.
      - Each sub-request has 1 user message containing 'base_user_content'.
      - Send them all in ONE POST to /generate_parallel.
      - Print the stats the server returns.
    """
    headers = {"Content-Type": "application/json"}

    # Step by 10, starting from start_subrequests up to max_subrequests (inclusive)
    for i in range(start_subrequests, max_subrequests + 1, 5):
        # Build i sub-requests; each sub-request has a single user message
        subrequests = []
        for sub_id in range(1, i + 1):
            subrequests.append({
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            base_user_content
                            + f"\n\n(This is sub-request #{sub_id} of {i} in this batch.)"
                        )
                    }
                ],
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
            break
        end_time = time.time()
        elapsed = end_time - start_time

        # Parse response
        try:
            response_json = response.json()
        except Exception as e:
            print(f"Could not parse JSON for request with {i} sub-requests: {e}")
            break

        if "error" in response_json:
            print(f"Server returned error for request with {i} sub-requests: {response_json['error']}")
            break

        # Extract stats
        stats = response_json.get("stats", {})
        total_tokens_in = stats.get("total_tokens_in")
        total_tokens_out = stats.get("total_tokens_out")
        tokens_per_second = stats.get("tokens_per_second")
        total_time = stats.get("total_time")
        avg_time_per_request = stats.get("avg_time_per_request")

        # Print stats
        print(f"  -> Response time:          {elapsed:.2f} s")
        print(f"  -> total_tokens_in:        {total_tokens_in}")
        print(f"  -> total_tokens_out:       {total_tokens_out}")
        if total_time is not None:
            print(f"  -> total_time (batch):     {total_time:.2f} s")
        if tokens_per_second is not None:
            print(f"  -> tokens_per_second:      {tokens_per_second:.2f}")
        if avg_time_per_request is not None:
            print(f"  -> avg_time_per_request:   {avg_time_per_request:.2f}")

        # Show partial output for the first sub-request in the batch
        outputs = response_json.get("outputs", [])
        print(f"  -> # of outputs returned:  {len(outputs)}")
        if outputs:
            # Print the first 200 characters of the first output
            print(f"  -> Partial output[0]: {outputs[0][:200]} ...")


def main():
    parser = argparse.ArgumentParser(description="Send an increasing number of sub-requests to /generate_parallel.")
    parser.add_argument(
        "--url",
        type=str,
        default="http://127.0.0.1:6000/generate_parallel",
        help="The /generate_parallel endpoint URL."
    )
    parser.add_argument(
        "--start_subrequests",
        type=int,
        default=1,
        help="Starting number of sub-requests."
    )
    parser.add_argument(
        "--max_subrequests",
        type=int,
        default=100,
        help="Maximum number of sub-requests (stepping by 10)."
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

    test_increasing_subrequests(
        url=args.url,
        start_subrequests=args.start_subrequests,
        max_subrequests=args.max_subrequests,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )


if __name__ == "__main__":
    main()
