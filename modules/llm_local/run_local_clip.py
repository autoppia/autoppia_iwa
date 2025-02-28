import argparse
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel


def main():
    # 1. Parse command-line arguments
    parser = argparse.ArgumentParser(description="Use CLIP to classify screenshot content.")
    parser.add_argument("--filename", required=True, help="Path to the screenshot image file.")
    args = parser.parse_args()

    # 2. Load the pre-trained CLIP model and processor
    model_name = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)

    # 3. Load your screenshot
    image = Image.open(args.filename).convert("RGB")

    # 4. Define text labels for your use case
    labels = [
        "The user is logged in",
        "The user is not logged in"
    ]

    # 5. Process inputs for CLIP
    inputs = processor(
        text=labels,
        images=image,
        return_tensors="pt",
        padding=True
    )

    # 6. Forward pass: get similarity logits for image-text pairs
    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image  # shape: [batch_size, num_labels]

    # 7. Convert logits to probabilities
    probs = logits_per_image.softmax(dim=1)  # shape: [1, num_labels]

    # 8. Print out probabilities for each label
    for label, prob in zip(labels, probs[0].tolist()):
        print(f"{label}: {prob:.4f}")

    # Optionally, pick the label with the highest probability
    predicted_idx = logits_per_image.argmax(dim=1).item()
    predicted_label = labels[predicted_idx]
    print(f"\nPredicted: {predicted_label}")


if __name__ == "__main__":
    main()
