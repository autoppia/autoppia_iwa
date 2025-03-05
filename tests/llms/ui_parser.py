# file: ui_parser_service.py

import torch
from PIL import Image
from transformers import pipeline


class UIParserService:
    def __init__(self):
        device = 0 if torch.cuda.is_available() else -1
        self.ui_parser = pipeline("image-to-text", model="microsoft/OmniParser-v2.0", device=device)

    def summarize_image(self, image: Image.Image) -> str:
        try:
            result = self.ui_parser(image)
            if result and len(result) > 0:
                return result[0].get("generated_text", "")
        except Exception as e:
            print(f"UIParserService error: {e}")
        return ""
