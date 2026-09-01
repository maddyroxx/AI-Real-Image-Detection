
from transformers import AutoModelForImageClassification
model = AutoModelForImageClassification.from_pretrained("prithivMLmods/Deep-Fake-Detector-v2-Model")
print("LABELS:", model.config.id2label)
