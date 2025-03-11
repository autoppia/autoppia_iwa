import argparse
import gc
import json
import sys
import threading  # << NEW
import time  # For timing

from flask import Flask, request
from flask_cors import CORS
from json_repair import repair_json
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# A global lock to ensure only one request is processed at a time.
lock = threading.Lock()  # << NEW

# ---------------------------------------------------------------------------
# The model name as per Qwen docs (Adjust if you prefer Qwen2-7B-Instruct, etc.)
# ---------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct"

# Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map="auto")
model.eval()

# ---------------------------------------------------------------------------
# Global counters (optional)
# ---------------------------------------------------------------------------
counters = {"total_requests": 0, "json_requests": 0, "json_correctly_formatted": 0, "json_repair_succeeded": 0}


def generate_data(messages, temperature, max_tokens, json_format=False, schema=None):
    """
    Generate text using Qwen with the given parameters (single sequence).
    If json_format=True, attempts to repair and return valid JSON.
    If schema is provided, instruct the model to follow it strictly.

    Returns (response_text, tokens_in, tokens_out).
    """
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
        tokens_in = model_inputs.input_ids.shape[1]  # Count how many tokens enter

        # Generate
        generated_ids = model.generate(**model_inputs, max_new_tokens=max_tokens, temperature=temperature)
        # Remove the prompt part so we only decode newly generated tokens
        generated_ids = [output_ids[len(input_ids) :] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
        tokens_out = len(generated_ids[0])  # Number of generated tokens

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

        return response_text, tokens_in, tokens_out

    except Exception as e:
        print("[generate_data] Exception occurred:", e, file=sys.stderr)
        return f"Generation error: {e}", 0, 0

    finally:
        gc.collect()


def generate_data_batch(requests, temperature, max_tokens):
    """
    Generate text for multiple conversation "requests" in *one* batch.
    Each element of `requests` is expected to be a dict containing:
      - "messages": list of messages
      - optionally "json_format": bool
      - optionally "schema": dict

    Returns:
      outputs (list of response_texts),
      total_tokens_in (int),
      total_tokens_out (int),
      per_request_json_flags (list of bool) - to track which requests demanded JSON
    """

    # Prepare prompts
    text_prompts = []
    # We'll store extra meta for each request so we can do JSON repair individually
    meta_info = []
    for req in requests:
        messages = req.get("messages", [])
        json_format = bool(req.get("json_format", False))
        schema = req.get("schema", None)

        # If we have a JSON schema, prepend an instruction
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
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, chat_format=None)
        text_prompts.append(prompt)
        meta_info.append((json_format, schema))

    # Tokenize in one batch
    model_inputs = tokenizer(text_prompts, return_tensors="pt", padding=True).to(model.device)

    # Count tokens_in for each request individually (sum them up)
    batch_size = model_inputs.input_ids.shape[0]
    tokens_in_list = [len(model_inputs.input_ids[i]) for i in range(batch_size)]
    total_tokens_in = sum(tokens_in_list)

    # Generate in a single batch
    generated = model.generate(**model_inputs, max_new_tokens=max_tokens, temperature=temperature)

    # For each request in the batch, slice off the original prompt
    outputs = []
    tokens_out_list = []
    for i in range(batch_size):
        # Original input length
        orig_len = len(model_inputs.input_ids[i])
        # All tokens for this request in the batch
        output_ids = generated[i]
        # Remove prompt tokens to get newly generated
        gen_ids = output_ids[orig_len:]
        tokens_out = len(gen_ids)
        tokens_out_list.append(tokens_out)

        # Decode
        text = tokenizer.decode(gen_ids, skip_special_tokens=True)

        # Possibly do JSON repair if needed
        json_format, _ = meta_info[i]
        if json_format:
            counters["json_requests"] += 1
            try:
                json.loads(text)
                counters["json_correctly_formatted"] += 1
            except Exception:
                try:
                    repaired_text = repair_json(text, ensure_ascii=False)
                    repaired_obj = json.loads(repaired_text)
                    text = json.dumps(repaired_obj, ensure_ascii=False)
                    counters["json_repair_succeeded"] += 1
                except Exception:
                    pass

        outputs.append(text)

    total_tokens_out = sum(tokens_out_list)
    return outputs, total_tokens_in, total_tokens_out


@app.route("/generate", methods=["POST"])
def handler():
    """
    Single-request endpoint: processes exactly one list-of-messages.
    """
    # Ensure only one request is processed at a time
    with lock:  # << NEW
        counters["total_requests"] += 1
        request_number = counters["total_requests"]

        try:
            data = request.json or {}

            messages = data.get("messages", [])
            temperature = float(data.get("temperature", 0.1))
            max_tokens = int(data.get("max_tokens", 256))
            json_format = bool(data.get("json_format", False))
            schema = data.get("schema", None)

            start_time = time.time()

            output, tokens_in, tokens_out = generate_data(messages=messages, temperature=temperature, max_tokens=max_tokens, json_format=json_format, schema=schema)

            end_time = time.time()
            time_per_request = end_time - start_time
            tokens_per_second = tokens_out / time_per_request if time_per_request > 0 else 0

            # Logging
            print("[handler] Single-request stats:")
            print(f"  Request number:       {request_number}")
            print(f"  temperature:          {temperature}")
            print(f"  max_tokens:           {max_tokens}")
            print(f"  json_format:          {json_format}")
            print(f"  total token input:    {tokens_in}")
            print(f"  total token output:   {tokens_out}")
            print(f"  tokens per second:    {tokens_per_second:.2f}")
            print(f"  time per petition:    {time_per_request:.2f} s")

            print(f"[handler] Final Answer:\n{output}")

            return {"output": output}

        except ValueError as ve:
            print("[handler] ValueError occurred:", ve, file=sys.stderr)
            return {"error": str(ve)}, 400
        except Exception as e:
            print("[handler] Exception occurred:", e, file=sys.stderr)
            return {"error": str(e)}, 500
        finally:
            print("\n=== Current Counter Stats ===")
            print(f"Total requests answered: {counters['total_requests']}")
            print(f"JSON requests: {counters['json_requests']}")
            print(f"JSON originally valid: {counters['json_correctly_formatted']}")
            print(f"JSON repaired successfully: {counters['json_repair_succeeded']}")
            print("=================================")


@app.route("/generate_parallel", methods=["POST"])
def handler_parallel():
    """
    Batch-request endpoint: can process multiple sets of messages (requests) in one shot.
    This is useful to compare throughput (tokens/second) vs many single requests.
    Expected JSON format:
    {
      "requests": [
        {"messages": [...], "json_format": false, "schema": null},
        {"messages": [...], "json_format": true,  "schema": {...}},
        ...
      ],
      "temperature": 0.1,
      "max_tokens": 1024
    }
    """
    # Ensure only one request is processed at a time
    with lock:  # << NEW
        counters["total_requests"] += 1
        request_number = counters["total_requests"]

        try:
            data = request.json or {}
            requests_list = data.get("requests", [])

            # Fallback if no requests given
            if not isinstance(requests_list, list) or len(requests_list) == 0:
                return {"error": "No requests provided."}, 400

            temperature = float(data.get("temperature", 0.1))
            max_tokens = int(data.get("max_tokens", 1024))

            start_time = time.time()

            # Generate results in one batch
            outputs, total_tokens_in, total_tokens_out = generate_data_batch(requests_list, temperature=temperature, max_tokens=max_tokens)

            end_time = time.time()
            total_time = end_time - start_time

            # Throughput: total tokens out per second
            tokens_per_second = total_tokens_out / total_time if total_time > 0 else 0
            # Average time per request
            avg_time_per_request = total_time / len(requests_list) if len(requests_list) > 0 else 0

            # Logging
            print("[handler_parallel] Batch-request stats:")
            print(f"  Batch Request number:     {request_number}")
            print(f"  Number of sub-requests:   {len(requests_list)}")
            print(f"  temperature (global):     {temperature}")
            print(f"  max_tokens (global):      {max_tokens}")
            print(f"  total token input (sum):  {total_tokens_in}")
            print(f"  total token output (sum): {total_tokens_out}")
            print(f"  total time:               {total_time:.2f} s")
            print(f"  tokens per second:        {tokens_per_second:.2f}")
            print(f"  avg time per sub-request: {avg_time_per_request:.2f} s")

            # Return a list of outputs
            return {
                "outputs": outputs,
                "stats": {
                    "total_tokens_in": total_tokens_in,
                    "total_tokens_out": total_tokens_out,
                    "tokens_per_second": tokens_per_second,
                    "total_time": total_time,
                    "avg_time_per_request": avg_time_per_request,
                },
            }

        except ValueError as ve:
            print("[handler_parallel] ValueError occurred:", ve, file=sys.stderr)
            return {"error": str(ve)}, 400
        except Exception as e:
            print("[handler_parallel] Exception occurred:", e, file=sys.stderr)
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
