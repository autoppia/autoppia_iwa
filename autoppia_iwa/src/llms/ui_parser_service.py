# import torch
# from transformers import pipeline
# from PIL import Image


class UIParserService:
    def __init__(self):
        pass

    def summarize_image(self, file):
        return ""


# class UIParserService:
#     def __init__(self):
#         pass
#         device = 0 if torch.cuda.is_available() else -1
#         self.ui_parser = pipeline("image-to-text", model="microsoft/OmniParser-v2.0", device=device)

#     def summarize_image(self, file):
#         try:
#             image = Image.open(file.stream).convert("RGB")
#         except Exception:
#             return None, "Invalid image file"

#         result = self.ui_parser(image)
#         return result, None
