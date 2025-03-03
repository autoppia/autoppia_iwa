import json
import time

import requests


def make_request():
    url = "http://127.0.0.1:22185/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": "Give me a short introduction to large language model."},
        ],
        "temperature": 0.1,
        "max_tokens": 256,
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end_time = time.time()

    # Optional: parse JSON result
    result_json = {}
    try:
        result_json = response.json()
    except Exception:
        pass

    return end_time - start_time, result_json


def main():
    for i in range(1, 1001):
        req_time, result = make_request()
        print(f"Request {i} - {req_time:.2f}s")
        # Optionally print the LLM output
        print("Output:", result.get("output", "No output found"), "\n")


if __name__ == "__main__":
    main()
