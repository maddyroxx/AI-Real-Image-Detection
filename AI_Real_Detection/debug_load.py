
from transformers import AutoModelForImageClassification, AutoImageProcessor
try:
    print("Loading EfficientNet...")
    m = AutoModelForImageClassification.from_pretrained("Dafilab/ai-image-detector")
    p = AutoImageProcessor.from_pretrained("Dafilab/ai-image-detector")
    print("Success")
except Exception as e:
    print(f"FAILED: {e}")
