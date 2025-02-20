import argparse
import gc
import logging

from flask import Flask, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# The following model determines the intelligence of everything
# -----------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2-7B-Instruct"

logger.info(f"Loading the tokenizer and model from '{MODEL_NAME}'...")
print(f"Loading model {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
# If you have a GPU available, uncomment the next line:
model.to("cuda")
model.eval()


def flatten_openai_messages(messages):
    """
    Converts a list of OpenAI-style messages into a single string.

    Example:
    [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ]

    becomes something like:
    "SYSTEM: You are a helpful assistant.\n\nUSER: Hello, how are you?"
    """
    flattened = []
    for msg in messages:
        role = msg.get("role", "").upper()
        content = msg.get("content", "")
        flattened.append(f"{role}: {content}")
    return "\n\n".join(flattened)


def generate_data(
    message_payload: str,
    max_new_tokens: int = 256,
    generation_kwargs: dict = None,
) -> str:
    if generation_kwargs is None:
        generation_kwargs = {}

    try:
        # Prepare the input tensor
        inputs = tokenizer(message_payload, return_tensors="pt")
        # Move them to GPU
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

        # Generate text
        output_tokens = model.generate(
            **inputs, max_new_tokens=max_new_tokens, **generation_kwargs
        )

        # Decode the output
        output_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)

        return output_text

    except Exception as e:
        logger.error(f"Error generating data: {e}")
        return f"Generation error: {e}"

    finally:
        gc.collect()


@app.route("/generate", methods=["POST"])
def handler():
    """
    Handle incoming POST requests to generate data using the model.

    Possible JSON formats:

    1) Simple string payload:
       {
         "input": {
           "text": "Your prompt here",
           "ctx": 256,
           "generation_kwargs": {...}
         }
       }

    2) OpenAI-style chat payload:
       {
         "input": {
           "text": [
             {"role": "system", "content": "System content"},
             {"role": "user", "content": "User content"}
           ],
           "ctx": 256,
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

        # Detect if message_payload is a list of OpenAI-style messages
        if isinstance(message_payload, list) and all(isinstance(msg, dict) for msg in message_payload):
            message_payload = flatten_openai_messages(message_payload)

        max_new_tokens = int(input_data.get("ctx", 256))
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
    parser = argparse.ArgumentParser(description="Run Hugging Face LLM service.")
    parser.add_argument("--port", type=int, default=6000, help="Port to run the service on")
    args = parser.parse_args()

    app.run(host="0.0.0.0", port=args.port, debug=True)
