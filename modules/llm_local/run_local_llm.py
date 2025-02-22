import argparse
import gc
import logging
import json
from json_repair import repair_json

from flask import Flask, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# The model name as per Qwen docs (Adjust if you prefer Qwen2-7B-Instruct, etc.)
# ---------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-14B-Instruct"

logger.info(f"Loading the tokenizer and model from '{MODEL_NAME}'...")
print(f"Loading model {MODEL_NAME}")

# Load model + tokenizer
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
    "total_requests": 0,               # How many requests have been answered
    "json_requests": 0,                # How many requests asked for JSON output
    "json_correctly_formatted": 0,     # How many times JSON was already valid
    "json_repair_succeeded": 0         # How many times the JSON was successfully repaired
}


def generate_data(message_payload, max_new_tokens=10000, generation_kwargs=None):
    """
    Generates a response using Qwen's chat template if the input is a list of messages,
    otherwise uses a default system + user prompt for a simple string.
    """
    if generation_kwargs is None:
        generation_kwargs = {}

    # Extract custom keys if present
    chat_format = generation_kwargs.pop("chat_format", None)
    response_format = generation_kwargs.pop("response_format", None)

    try:
        # Build messages array
        if isinstance(message_payload, list) and all(isinstance(msg, dict) for msg in message_payload):
            messages = message_payload
        else:
            messages = [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": str(message_payload)}
            ]

        # If a response_format was provided, instruct model to produce valid JSON
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

        # Convert to a single text prompt with Qwen's chat template
        # if chat_format:
        print("APLYYING CHAT TEMPLATE!!!")
        text_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            chat_format=chat_format
        )
        # else:
        #     text_prompt = tokenizer.apply_chat_template(
        #         messages,
        #         tokenize=False,
        #         add_generation_prompt=True
        #     )

        # -------------------------------------------------------------------
        # Print the exact text entering the LLM
        # -------------------------------------------------------------------
        print("\n=== TEXT ENTERING THE LLM ===")
        print(text_prompt)
        print("=============================\n")

        # Tokenize
        model_inputs = tokenizer([text_prompt], return_tensors="pt").to(model.device)

        # Generate
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            **generation_kwargs
        )

        # Qwen docs: subtract the prompt tokens so we only decode new tokens
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # Decode
        response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # -------------------------------------------------------------------
        # Print the exact raw text output from the LLM
        # -------------------------------------------------------------------
        print("\n=== RAW LLM OUTPUT (Before JSON Repair) ===")
        print(response_text)
        print("==========================================\n")

        # -------------------------------------------------------------------
        # Handle JSON checks/repair if needed
        # -------------------------------------------------------------------
        if response_format and response_format.get("type") == "json_object":
            # We've got a request for JSON.
            counters["json_requests"] += 1

            # Check if the original response_text is already valid JSON
            originally_valid = False
            try:
                json.loads(response_text)
                originally_valid = True
                counters["json_correctly_formatted"] += 1
            except Exception:
                pass

            # If the original wasn't valid, attempt to repair it:
            if not originally_valid:
                try:
                    repaired_text = repair_json(response_text, ensure_ascii=False)
                    # Verify the repaired text is valid JSON
                    repaired_obj = json.loads(repaired_text)
                    # Re-encode into a standard JSON string
                    response_text = json.dumps(repaired_obj, ensure_ascii=False)
                    counters["json_repair_succeeded"] += 1

                    print("\n=== REPAIRED JSON OUTPUT ===")
                    print(response_text)
                    print("===========================\n")

                except Exception as rep_ex:
                    logger.warning(f"JSON repair failed: {rep_ex}")

        # Print the final text being returned by the function
        print("\n=== FINAL LLM OUTPUT (Returned) ===")
        print(response_text)
        print("===================================\n")

        return response_text

    except Exception as e:
        logger.error(f"Error generating data: {e}")
        return f"Generation error: {e}"

    finally:
        gc.collect()


@app.route("/generate", methods=["POST"])
def handler():
    """
    Handle incoming POST requests to generate data using the model.
    """
    # Increment total requests
    counters["total_requests"] += 1

    try:
        inputs = request.json or {}
        input_data = inputs.get("input", {})

        message_payload = input_data.get("text", "")
        if not message_payload:
            raise ValueError("Input 'text' is missing or empty")

        max_new_tokens = int(input_data.get("ctx", 10000))

        # The original "generation_kwargs"
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
        logger.error(f"Invalid input value: {ve}")
        return {"error": str(ve)}, 400
    except Exception as e:
        logger.error(f"Error handling event: {e}")
        return {"error": str(e)}, 500

    finally:
        # After every request, print the counters
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

    # IMPORTANT: In production, set debug=False
    app.run(host="0.0.0.0", port=args.port, debug=True, use_reloader=False)
