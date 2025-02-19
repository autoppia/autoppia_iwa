import io
from flask import Flask, request, jsonify
import torch
from transformers import pipeline
from PIL import Image

app = Flask(__name__)

# Use GPU if available, otherwise CPU
device = 0 if torch.cuda.is_available() else -1

# Initialize the pipeline once at startup
ui_parser = pipeline("image-to-text", model="microsoft/OmniParser-v2.0", device=device)


@app.route('/summarize', methods=['POST'])
def summarize_ui():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    try:
        image = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return jsonify({"error": "Invalid image file"}), 400

    result = ui_parser(image)
    return jsonify({"summary": result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
