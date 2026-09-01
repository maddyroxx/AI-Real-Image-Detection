
from transformers import AutoModelForImageClassification
import sys

model_name = 'yevvonlim/DistilDIRE'
try:
    print(f"Attempting to load {model_name}...")
    model = AutoModelForImageClassification.from_pretrained(model_name)
    print("Success!")
    print("Labels:", model.config.id2label)
except Exception as e:
    print(f"Error loading {model_name}: {e}")

# Check Organika as backup
model_name_2 = 'Organika/SDXL-Detector'
try:
    print(f"Attempting to load {model_name_2}...")
    model2 = AutoModelForImageClassification.from_pretrained(model_name_2)
    print("Success Organika!")
    print("Labels:", model2.config.id2label)
except Exception as e:
    print(f"Error loading {model_name_2}: {e}")
