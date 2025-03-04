import argparse
import gc
import json
import sys
import threading
import time

from flask import Flask, request
from flask_cors import CORS
from json_repair import repair_json
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# A global lock to ensure only one request is processed at a time.
lock = threading.Lock()

MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct"

# Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map={"": 0})
model.eval()

# Global counters (optional)
counters = {"total_requests": 0, "json_requests": 0, "json_correctly_formatted": 0, "json_repair_succeeded": 0}


def append_to_file(filepath, data_obj):
    """
    Append a single JSON object to a file as a new line.
    """
    with open(filepath, 'a', encoding='utf-8') as f:
        json.dump(data_obj, f, ensure_ascii=False)
        f.write("\n")


def generate_data(messages, temperature, max_tokens, json_format=False, schema=None):
    """
    Generate text using Qwen with the given parameters.
    If json_format=True, attempts to repair and return valid JSON.
    If schema is provided, instruct the model to strictly follow it.

    Returns (response_text, tokens_in, tokens_out, text_prompt).
    """
    text_prompt = None
    try:
        # If we have a JSON schema, prepend an instruction to produce valid JSON
        if json_format and schema:
            schema_text = json.dumps(schema, indent=2)
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": ("You must respond in **valid JSON** that meets the following schema.\n\n" "Do not include extra keys. Output **only** the JSON object.\n\n" f"{schema_text}"),
                },
            )

        # Convert messages to a single text prompt
        text_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, chat_format=None)

        model_inputs = tokenizer([text_prompt], return_tensors="pt").to(model.device)
        # Count how many tokens go into the model
        tokens_in = model_inputs.input_ids.shape[1]

        # Generate
        generated_ids = model.generate(**model_inputs, max_new_tokens=max_tokens, temperature=temperature, top_p=0.9)

        # Subtract the prompt tokens so we only decode newly generated tokens
        generated_ids = [output_ids[len(input_ids) :] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]

        # Count how many tokens were generated
        tokens_out = len(generated_ids[0])

        response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # If JSON format is requested, try to validate or repair
        if json_format:
            counters["json_requests"] += 1
            try:
                json.loads(response_text)
                counters["json_correctly_formatted"] += 1
            except Exception:
                try:
                    repaired_text = repair_json(response_text, ensure_ascii=False)
                    repaired_obj = json.loads(repaired_text)
                    response_text = json.dumps(repaired_obj, ensure_ascii=False)
                    counters["json_repair_succeeded"] += 1
                except Exception:
                    pass

        return response_text, tokens_in, tokens_out, text_prompt

    except Exception as e:
        print("[generate_data] Exception occurred:", e, file=sys.stderr)
        return f"Generation error: {e}", 0, 0, text_prompt
    finally:
        gc.collect()


@app.route("/generate", methods=["POST"])
def handler():
    # Ensure only one request is processed at a time
    with lock:
        counters["total_requests"] += 1
        request_number = counters["total_requests"]

        # Prepare a dict to record everything about the request (and eventually response)
        log_data = {"request_number": request_number, "timestamp": time.time()}  # Or use time.ctime() if you want a human-readable string

        try:
            data = request.json or {}

            # Extract the fields
            messages = data.get("messages", [])
            temperature = float(data.get("temperature", 0.1))
            max_tokens = int(data.get("max_tokens", 256))
            json_format = bool(data.get("json_format", False))
            schema = data.get("schema", None)

            # Keep them in the log
            log_data.update({"messages": messages, "temperature": temperature, "max_tokens": max_tokens, "json_format": json_format, "schema": schema})

            # Time the generation process
            start_time = time.time()

            # Generate the response
            output, tokens_in, tokens_out, text_prompt = generate_data(messages=messages, temperature=temperature, max_tokens=max_tokens, json_format=json_format, schema=schema)

            end_time = time.time()
            time_per_request = end_time - start_time
            tokens_per_second = tokens_out / time_per_request if time_per_request > 0 else 0

            # Store final stats & parameters in the log
            log_data.update(
                {
                    "text_prompt": text_prompt,  # The full text sent into the LLM
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "time_per_request": time_per_request,
                    "tokens_per_second": tokens_per_second,
                    "output": output,
                }
            )

            # Print final parameters & stats (optional debug)
            print("[handler] Final parameters & stats:")
            print(f"  Request number:       {request_number}")
            print(f"  temperature:          {temperature}")
            print(f"  max_tokens:           {max_tokens}")
            print(f"  json_format:          {json_format}")
            print(f"  total token input:    {tokens_in}")
            print(f"  total token output:   {tokens_out}")
            print(f"  tokens per second:    {tokens_per_second:.2f}")
            print(f"  time per petition:    {time_per_request:.2f} s")

            # Debug: Print final answer
            print(f"[handler] Final Answer:\n{output}")

            # This request ended successfully, so we log to "correct_requests.json"
            append_to_file("correct_requests.json", log_data)

            return {"output": output}

        except ValueError as ve:
            # Log the error
            log_data["error"] = str(ve)
            append_to_file("errored_requests.json", log_data)
            print("[handler] ValueError occurred:", ve, file=sys.stderr)
            return {"error": str(ve)}, 400

        except Exception as e:
            # Log the error
            log_data["error"] = str(e)
            append_to_file("errored_requests.json", log_data)
            print("[handler] Exception occurred:", e, file=sys.stderr)
            return {"error": str(e)}, 500

        finally:
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

    # Run Flask so it only processes one request at a time
    # by disabling threading.
    app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False, threaded=False)
