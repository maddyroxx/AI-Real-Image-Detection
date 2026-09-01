import os
import torch
from datasets import load_dataset, ClassLabel, Image
from transformers import (
    ViTImageProcessor,
    ViTForImageClassification,
    TrainingArguments,
    Trainer,
    DefaultDataCollator,
)
import evaluate
from torchvision.transforms import (
    CenterCrop,
    Compose,
    Normalize,
    RandomRotation,
    RandomResizedCrop,
    RandomHorizontalFlip,
    RandomAdjustSharpness,
    Resize,
    ToTensor,
)
import numpy as np

# --- Configuration ---
MODEL_NAME = "google/vit-base-patch16-224"
DATASET_DIR = "./dataset"
OUTPUT_DIR = "./model"
BATCH_SIZE = 16
NUM_EPOCHS = 3
LEARNING_RATE = 2e-5

def main():
    # 1. Load Dataset
    print("Loading dataset...")
    # Expects dataset structure: dataset/train/LABEL and dataset/test/LABEL
    data_files = {}
    if os.path.exists(os.path.join(DATASET_DIR, "train")):
        data_files["train"] = os.path.join(DATASET_DIR, "train")
    if os.path.exists(os.path.join(DATASET_DIR, "test")):
        data_files["test"] = os.path.join(DATASET_DIR, "test")
    
    if not data_files:
        print(f"Error: No data found in {DATASET_DIR}. Please organize data in 'train' and 'test' folders.")
        print("Expected structure: ./dataset/train/REAL, ./dataset/train/FAKE, etc.")
        return

    # Use evaluate load logic or simplified imagefolder loading
    # Ideally use Hugging Face datasets ImageFolder builder which is automatic if we point to directory
    dataset = load_dataset("imagefolder", data_dir=DATASET_DIR)
    
    # 2. Labels
    labels = dataset["train"].features["label"].names
    id2label = {str(i): c for i, c in enumerate(labels)}
    label2id = {c: str(i) for i, c in enumerate(labels)}
    print(f"Labels found: {labels}")

    # 3. Preprocessing
    processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
    image_mean = processor.image_mean
    image_std = processor.image_std
    size = processor.size["height"]

    normalize = Normalize(mean=image_mean, std=image_std)

    _train_transforms = Compose([
        RandomResizedCrop(size),
        RandomHorizontalFlip(),
        RandomAdjustSharpness(2),
        ToTensor(),
        normalize,
    ])

    _val_transforms = Compose([
        Resize(size),
        CenterCrop(size),
        ToTensor(),
        normalize,
    ])

    def train_transforms(examples):
        examples["pixel_values"] = [_train_transforms(image.convert("RGB")) for image in examples["image"]]
        return examples

    def val_transforms(examples):
        examples["pixel_values"] = [_val_transforms(image.convert("RGB")) for image in examples["image"]]
        return examples

    # Apply transforms
    print("Applying transforms...")
    dataset["train"].set_transform(train_transforms)
    if "test" in dataset:
        dataset["test"].set_transform(val_transforms)
    
    # 4. Model
    print(f"Loading model {MODEL_NAME}...")
    model = ViTForImageClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True 
    )

    # 5. Metrics
    metric = evaluate.load("accuracy")
    def compute_metrics(eval_pred):
        predictions = np.argmax(eval_pred.predictions, axis=1)
        return metric.compute(predictions=predictions, references=eval_pred.label_ids)

    # 6. Training Arguments
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        remove_unused_columns=False,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=NUM_EPOCHS,
        warmup_ratio=0.1,
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        push_to_hub=False,
    )

    collator = DefaultDataCollator()

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"] if "test" in dataset else None,
        tokenizer=processor,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )

    # 7. Train
    print("Starting training...")
    trainer.train()

    # 8. Save
    print(f"Saving model to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    processor.save_pretrained(OUTPUT_DIR)
    print("Done!")

if __name__ == "__main__":
    main()
