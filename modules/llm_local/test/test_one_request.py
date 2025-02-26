import requests
import json


def make_request():
    url = "http://127.0.0.1:6000/generate"
    headers = {"Content-Type": "application/json"}

    # Instead of putting everything under "input": {...},
    # we send messages/temperature/max_tokens at the top level.
    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Give me a short introduction to large language model."
            }
        ],
        "temperature": 0.1,
        "max_tokens": 256
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.json())


if __name__ == "__main__":
    make_request()
