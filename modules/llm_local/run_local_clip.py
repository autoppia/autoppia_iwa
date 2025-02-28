from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

# 1. Load the pre-trained CLIP model and processor
model_name = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

# 2. Load your screenshot (replace with your local file path or URL)
image_path = "screenshot.png"
image = Image.open(image_path).convert("RGB")

# 3. Define text labels for your use case
labels = [
    "The user is logged in",
    "The user is not logged in"
]

# 4. Process inputs for CLIP
inputs = processor(
    text=labels,
    images=image,
    return_tensors="pt",
    padding=True
)

# 5. Forward pass: get similarity logits for image-text pairs
with torch.no_grad():
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image  # shape: [batch_size, num_labels]

# 6. Convert logits to probabilities
probs = logits_per_image.softmax(dim=1)  # shape: [1, num_labels]

# 7. Print out probabilities for each label
for label, prob in zip(labels, probs[0].tolist()):
    print(f"{label}: {prob:.4f}")

# Optionally, pick the label with the highest probability
predicted_idx = logits_per_image.argmax(dim=1).item()
predicted_label = labels[predicted_idx]
print(f"\nPredicted: {predicted_label}")
