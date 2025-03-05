import argparse

import torch
from PIL import Image
from transformers import Blip2ForConditionalGeneration, Blip2Processor


def main():
    # 1. Parse command-line arguments
    parser = argparse.ArgumentParser(description="Use BLIP-2 to classify screenshot content.")
    parser.add_argument("--filename", required=True, help="Path to the screenshot image file.")
    args = parser.parse_args()

    # 2. Load the BLIP-2 model and processor
    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b")

    # 3. Load your screenshot
    image = Image.open(args.filename).convert("RGB")

    # 4. Define our “labels” in a single question/prompt
    #    We'll ask BLIP-2 to pick which statement (1 or 2) is correct.
    prompt = (
        "Question: Which of the following statements best describes the screenshot?\n"
        "1) The user is correctly logged in into the website.\n"
        "2) The user is NOT correctly logged in into the website.\n"
        "Answer with '1' or '2'."
    )

    # 5. Preprocess the input for BLIP-2
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device)

    # 6. Generate an answer
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=20)
    generated_text = processor.tokenizer.decode(generated_ids[0], skip_special_tokens=True).strip()

    # 7. Print out the raw generated answer
    print("BLIP-2 raw answer:", generated_text)

    # 8. (Optional) Basic parsing of the answer:
    #    If BLIP-2 returns "1" or "2", pick the corresponding label.
    #    You can also do more complex logic, e.g., searching for keywords in the text.
    if "1" in generated_text:
        predicted_label = "The user is correctly logged in into the website"
    elif "2" in generated_text:
        predicted_label = "The user is NOT correctly logged in into the website"
    else:
        predicted_label = "Could not determine (check BLIP-2 output)"

    print(f"Predicted: {predicted_label}")


if __name__ == "__main__":
    main()
