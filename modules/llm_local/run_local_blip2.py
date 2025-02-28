import argparse
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration


def main():
    # 1. Parse command-line arguments
    parser = argparse.ArgumentParser(description="Use BLIP to generate captions for an image.")
    parser.add_argument("--filename", required=True, help="Path to the local image file.")
    args = parser.parse_args()

    # 2. Load the BLIP model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    # 3. Load your local image
    image = Image.open(args.filename).convert("RGB")

    # 4. Conditional image captioning
    text_prompt = "a photography of"
    conditional_inputs = processor(image, text_prompt, return_tensors="pt")
    with torch.no_grad():
        conditional_out = model.generate(**conditional_inputs)
    conditional_caption = processor.decode(conditional_out[0], skip_special_tokens=True)
    print(f"Conditional caption (prompt='{text_prompt}'): {conditional_caption}")

    # 5. Unconditional image captioning
    unconditional_inputs = processor(image, return_tensors="pt")
    with torch.no_grad():
        unconditional_out = model.generate(**unconditional_inputs)
    unconditional_caption = processor.decode(unconditional_out[0], skip_special_tokens=True)
    print(f"Unconditional caption: {unconditional_caption}")


if __name__ == "__main__":
    main()
