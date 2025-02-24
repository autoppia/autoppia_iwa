import json

import requests


def make_request():
    url = "http://127.0.0.1:6000/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "input": {
            "text": [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": "Give me a short introduction to large language model."},
            ],
            "ctx": 256,
            "generation_kwargs": {},
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.json())


if __name__ == "__main__":
    make_request()
