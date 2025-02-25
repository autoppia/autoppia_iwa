import time
import requests
import json


def make_request():
    url = "http://127.0.0.1:6000/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "input": {
            "text": [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": "Give me a short introduction to large language model."}
            ],
            "ctx": 256,
            "generation_kwargs": {}
        }
    }
    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end_time = time.time()
    return end_time - start_time


def main():
    for i in range(1, 101):
        req_time = make_request()
        print(f"Request {i} - {req_time:.2f}s")


if __name__ == "__main__":
    main()
