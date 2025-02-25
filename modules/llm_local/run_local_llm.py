import argparse
import gc
import json
from json_repair import repair_json
import sys

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
# Global counters (optional)
# ---------------------------------------------------------------------------
counters = {
    "total_requests": 0,
    "json_requests": 0,
    "json_correctly_formatted": 0,
    "json_repair_succeeded": 0
}


def generate_data(messages, temperature, max_tokens, json_format=False, schema=None):
    """
    Generate text using Qwen with the given parameters.
    If json_format=True, attempts to repair and return valid JSON.
    If schema is provided, instruct the model to strictly follow it.

    Debugging statements added to show parameters and partial process.
    """
    # Debug: Print out the parameters
    print("\n[generate_data] Called with:")
    print(f"  messages: {messages}")
    print(f"  temperature: {temperature}")
    print(f"  max_tokens: {max_tokens}")
    print(f"  json_format: {json_format}")
    print(f"  schema: {schema}")

    try:
        # If we have a JSON schema, prepend an instruction to produce valid JSON
        if json_format and schema:
            schema_text = json.dumps(schema, indent=2)
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

        # Subtract the prompt tokens so we only decode the newly generated tokens
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # If JSON format is requested, try to validate or repair
        if json_format:
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
        # Debug: Print out the exception
        print("[generate_data] Exception occurred:", e, file=sys.stderr)
        return f"Generation error: {e}"

    finally:
        gc.collect()


@app.route("/generate", methods=["POST"])
def handler():
    # Increase total request count
    counters["total_requests"] += 1

    # Debug: Print raw incoming request data
    print("\n[handler] Raw request data:", request.data)

    try:
        data = request.json or {}
        # Debug: Print parsed JSON body
        print("[handler] Parsed JSON data:", data)

        # Extract the fields
        messages = data.get("messages", [])
        temperature = float(data.get("temperature", 0.1))
        max_tokens = int(data.get("max_tokens", 256))
        json_format = bool(data.get("json_format", False))
        schema = data.get("schema", None)

        # Debug: Print the final parameters used
        print("[handler] Final parameters:")
        print(f"  messages: {messages}")
        print(f"  temperature: {temperature}")
        print(f"  max_tokens: {max_tokens}")
        print(f"  json_format: {json_format}")
        print(f"  schema: {schema}")

        # Generate the response
        output = generate_data(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_format=json_format,
            schema=schema
        )

        # Debug: Print final answer
        print(f"[handler] Final Answer:\n{output}")

        return {"output": output}

    except ValueError as ve:
        print("[handler] ValueError occurred:", ve, file=sys.stderr)
        return {"error": str(ve)}, 400
    except Exception as e:
        print("[handler] Exception occurred:", e, file=sys.stderr)
        return {"error": str(e)}, 500
    finally:
        # Print counters for debugging
        print("\n=== Current Counter Stats ===")
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
