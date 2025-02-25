import argparse
import gc
import json
from json_repair import repair_json
import sys
import time

from flask import Flask, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct"

# Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto"
)
model.eval()


def generate_data(messages, temperature, max_tokens, json_format=False, schema=None):
    """
    Generate text using Qwen with the given parameters.
    If json_format=True, attempts to repair and return valid JSON.
    If schema is provided, instruct the model to strictly follow it.

    Returns:
      (response_text, num_generated_tokens)
    """
    try:
        # If we have a JSON schema, prepend an instruction to produce valid JSON
        if json_format and schema:
            schema_text = json.dumps(schema)
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

        # Convert messages to a single text prompt
        text_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            chat_format=None
        )

        model_inputs = tokenizer([text_prompt], return_tensors="pt").to(model.device)

        # Generate
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_tokens,
            temperature=temperature
        )

        # Identify newly generated portion only
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # Decode
        response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # Number of tokens in the newly generated part
        num_generated_tokens = len(generated_ids[0])

        # If JSON format is requested, try to validate or repair
        if json_format:
            try:
                json.loads(response_text)
            except:
                try:
                    repaired_text = repair_json(response_text, ensure_ascii=False)
                    repaired_obj = json.loads(repaired_text)
                    response_text = json.dumps(repaired_obj, ensure_ascii=False)
                except:
                    pass

        return response_text, num_generated_tokens

    except Exception as e:
        return f"Generation error: {e}", 0

    finally:
        gc.collect()


@app.route("/generate", methods=["POST"])
def handler():
    # Measure time to track performance
    start_time = time.time()

    try:
        data = request.json or {}

        messages = data.get("messages", [])
        temperature = float(data.get("temperature", 0.1))
        max_tokens = int(data.get("max_tokens", 256))
        json_format = bool(data.get("json_format", False))
        schema = data.get("schema", None)

        # Generate response
        output, num_generated_tokens = generate_data(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_format=json_format,
            schema=schema
        )

        end_time = time.time()
        elapsed = end_time - start_time
        tokens_per_second = (
            num_generated_tokens / elapsed if elapsed > 0 else 0
        )

        # Print the minimal performance info
        # Message length is sum of lengths of message["content"]
        total_message_length = sum(len(m.get("content", "")) for m in messages)

        print(f"\n--- Request Info ---")
        print(f"Message length: {total_message_length}")
        print(f"Temperature: {temperature}")
        print(f"Max tokens: {max_tokens}")
        print(f"json_format: {json_format}")
        print(f"Time taken: {elapsed:.2f} seconds")
        print(f"Tokens/s: {tokens_per_second:.2f}")

        return {"output": output}

    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Hugging Face Qwen LLM service.")
    parser.add_argument("--port", type=int, default=6000, help="Port to run the service on")
    args = parser.parse_args()

    app.run(host="0.0.0.0", port=args.port, debug=True, use_reloader=False)
