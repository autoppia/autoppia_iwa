import argparse
import gc
import logging
from typing import Dict, List

from flask import Flask, request
from flask_cors import CORS
from llama_cpp import Llama

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MODEL_PATH = "qwen2.5-coder-14b-instruct-q4_k_m.gguf"


def generate_data(
    model_path: str,
    message_payload: List[Dict[str, str]],
    ctx: int,
    llm_kwargs: dict = None,
    chat_completion_kwargs: dict = None,
) -> str:
    """
    Generate data using the Llama model.

    :param model_path: Path to the Llama model file.
    :param message_payload: The input text for model generation.
    :param ctx: The context length for the model.
    :param llm_kwargs: Additional keyword arguments for Llama initialization.
    :param chat_completion_kwargs: Additional keyword arguments for chat completion.
    :return: Generated response from the model or None if an error occurred.
    """
    llm = None
    try:
        llm = Llama(
            model_path=model_path,
            n_ctx=ctx,
            n_gpu_layers=-1,
            **llm_kwargs,
        )

        response = llm.create_chat_completion(messages=message_payload, **chat_completion_kwargs)

        return response["choices"][0]["message"]["content"]
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating data: {e}")
        return None
    finally:
        if llm:
            llm.reset()
            del llm
            gc.collect()


@app.route("/generate", methods=["POST"])
def handler():
    """
    Handle incoming POST requests to generate data using the model.

    :return: A JSON response containing the output or error message.
    """
    try:
        inputs = request.json
        message_payload = inputs.get("input", {}).get("text", "")
        ctx = int(inputs.get("input", {}).get("ctx", 32768))

        if not message_payload:
            raise ValueError("Input 'text' is missing or empty")

        llm_kwargs = inputs.get("input", {}).get("llm_kwargs", {})
        chat_completion_kwargs = inputs.get("input", {}).get("chat_completion_kwargs", {})

        output = generate_data(
            model_path=MODEL_PATH,
            message_payload=message_payload,
            ctx=ctx,
            llm_kwargs=llm_kwargs,
            chat_completion_kwargs=chat_completion_kwargs,
        )

        return {"output": output}
    except ValueError as ve:
        logger.error(f"Invalid input value: {ve}")
        return {"error": str(ve)}, 400
    except Exception as e:
        logger.error(f"Error handling event: {e}")
        return {"error": str(e)}, 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLM service.")
    parser.add_argument("--port", type=int, default=6000, help="Port to run the service on")
    args = parser.parse_args()

    app.run(host="0.0.0.0", port=args.port, debug=True)
