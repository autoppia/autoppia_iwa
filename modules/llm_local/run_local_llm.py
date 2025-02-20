import argparse
import gc
import logging

from flask import Flask, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# The model name as per Qwen docs (Adjust if you prefer Qwen2-7B-Instruct,
# Qwen2.5-3B-Instruct, etc.)
# ---------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-32B-Instruct"

logger.info(f"Loading the tokenizer and model from '{MODEL_NAME}'...")
print(f"Loading model {MODEL_NAME}")

# Load model + tokenizer as recommended for Qwen
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",   # lets HF set an optimal dtype (usually FP16 or BF16 if supported)
    device_map="auto"     # automatically place the model on GPU(s)
)
model.eval()


def generate_data(message_payload, max_new_tokens=10000, generation_kwargs=None):
    """
    Generates a response using Qwen's chat template if the input is a list of messages,
    otherwise uses a default system + user prompt for a simple string.
    """
    if generation_kwargs is None:
        generation_kwargs = {}

    try:
        # 1) Build messages array
        if isinstance(message_payload, list) and all(isinstance(msg, dict) for msg in message_payload):
            # Already chat-style messages
            messages = message_payload
        else:
            # Fallback if user passed a single string, wrap with a default system & user
            messages = [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": str(message_payload)}
            ]

        # 2) Convert to a single text prompt with Qwen's chat template
        text_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True  # adds the "Assistant:" part
        )

        # 3) Tokenize
        model_inputs = tokenizer([text_prompt], return_tensors="pt").to(model.device)

        # 4) Generate
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
            **generation_kwargs
        )
        # Qwen docs: subtract the prompt tokens so we only decode new tokens
        # (optional, but helps avoid reprinting the entire prompt)
        # But if you want the full text, you can skip this slicing step.
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # 5) Decode
        response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
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

    JSON formats:

    1) Simple string payload:
       {
         "input": {
           "text": "Your prompt here",
           "ctx": 10000,
           "generation_kwargs": {...}
         }
       }

    2) OpenAI-style chat payload:
       {
         "input": {
           "text": [
             {"role": "system", "content": "System content"},
             {"role": "user",   "content": "User content"}
           ],
           "ctx": 10000,
           "generation_kwargs": {...}
         }
       }
    """
    try:
        inputs = request.json or {}
        input_data = inputs.get("input", {})

        message_payload = input_data.get("text", "")
        if not message_payload:
            raise ValueError("Input 'text' is missing or empty")

        max_new_tokens = int(input_data.get("ctx", 10000))
        generation_kwargs = input_data.get("generation_kwargs", {})

        output = generate_data(
            message_payload=message_payload,
            max_new_tokens=max_new_tokens,
            generation_kwargs=generation_kwargs,
        )
        return {"output": output}

    except ValueError as ve:
        logger.error(f"Invalid input value: {ve}")
        return {"error": str(ve)}, 400
    except Exception as e:
        logger.error(f"Error handling event: {e}")
        return {"error": str(e)}, 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Hugging Face Qwen LLM service.")
    parser.add_argument("--port", type=int, default=6000, help="Port to run the service on")
    args = parser.parse_args()

    # IMPORTANT: If you're using a production environment, you typically set debug=False.
    app.run(host="0.0.0.0", port=args.port, debug=True, use_reloader=False)
