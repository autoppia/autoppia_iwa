import argparse
import gc
import json
from json_repair import repair_json

from flask import Flask, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ---------------------------------------------------------------------------
# The model name as per Qwen docs (Adjust if you prefer Qwen2-7B-Instruct, etc.)
# ---------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct"

# Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto"
)
model.eval()

# ---------------------------------------------------------------------------
# Global counters
# ---------------------------------------------------------------------------
counters = {
    "total_requests": 0,
    "json_requests": 0,
    "json_correctly_formatted": 0,
    "json_repair_succeeded": 0
}


def generate_data(message_payload, max_new_tokens=10000, generation_kwargs=None):
    if generation_kwargs is None:
        generation_kwargs = {}

    chat_format = generation_kwargs.pop("chat_format", None)
    response_format = generation_kwargs.pop("response_format", None)

    try:
        # Prepare messages
        if isinstance(message_payload, list) and all(isinstance(msg, dict) for msg in message_payload):
            messages = message_payload
        else:
            messages = [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": str(message_payload)}
            ]

        # Insert JSON schema instruction if needed
        if response_format and response_format.get("type") == "json_object":
            schema_text = json.dumps(response_format.get("schema", {}), indent=2)
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": (
                        "You must respond in **valid JSON** that meets the following schema.\n\n"
                        "Do not include extra keys. Output **only** the JSON object.\n\n"
                        f"{schema_text}"
                    ),
                },
            )

        text_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            chat_format=chat_format
        )

        model_inputs = tokenizer([text_prompt], return_tensors="pt").to(model.device)
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            **generation_kwargs
        )

        # Subtract the prompt tokens so we only decode the newly generated tokens
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # JSON validation & repair if requested
        if response_format and response_format.get("type") == "json_object":
            counters["json_requests"] += 1

            try:
                json.loads(response_text)
                counters["json_correctly_formatted"] += 1
            except:
                try:
                    repaired_text = repair_json(response_text, ensure_ascii=False)
                    repaired_obj = json.loads(repaired_text)
                    response_text = json.dumps(repaired_obj, ensure_ascii=False)
                    counters["json_repair_succeeded"] += 1
                except:
                    pass

        return response_text

    except Exception as e:
        return f"Generation error: {e}"
    finally:
        gc.collect()


@app.route("/generate", methods=["POST"])
def handler():
    counters["total_requests"] += 1

    try:
        inputs = request.json or {}
        input_data = inputs.get("input", {})

        message_payload = input_data.get("text", "")
        if not message_payload:
            raise ValueError("Input 'text' is missing or empty")

        max_new_tokens = int(input_data.get("ctx", 10000))
        base_generation_kwargs = input_data.get("generation_kwargs", {})
        llm_kwargs = input_data.get("llm_kwargs", {})
        chat_completion_kwargs = input_data.get("chat_completion_kwargs", {})

        merged_generation_kwargs = {
            **base_generation_kwargs,
            **llm_kwargs,
            **chat_completion_kwargs
        }

        output = generate_data(
            message_payload=message_payload,
            max_new_tokens=max_new_tokens,
            generation_kwargs=merged_generation_kwargs,
        )
        return {"output": output}

    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Only print the counters
        print("=== Current Counter Stats ===")
        print(f"Total requests answered: {counters['total_requests']}")
        print(f"JSON requests: {counters['json_requests']}")
        print(f"JSON originally valid: {counters['json_correctly_formatted']}")
        print(f"JSON repaired successfully: {counters['json_repair_succeeded']}")
        print("=================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Hugging Face Qwen LLM service.")
    parser.add_argument("--port", type=int, default=6000, help="Port to run the service on")
    args = parser.parse_args()

    app.run(host="0.0.0.0", port=args.port, debug=True, use_reloader=False)
