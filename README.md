# AI Real Image Detection

An AI-powered image authenticity detection system designed to identify whether passport-size and ID-style images are real or AI-generated/manipulated.

The system analyzes visual characteristics such as facial features, image quality, background patterns, and other image-level artifacts to determine the authenticity of an uploaded image.

## 🚀 Features

- Detects real vs. AI-generated/manipulated images
- Designed for passport-size and ID-style photographs
- Analyzes facial and background characteristics
- Image-based authenticity prediction
- Machine learning/deep learning based detection
- Web-based interface for image testing
- Hugging Face deployment support
- Testing and debugging utilities included

## 🧠 How It Works

The system follows an image analysis pipeline:

1. User uploads a passport-size or ID-style image.
2. The image is preprocessed for analysis.
3. Visual and facial characteristics are analyzed.
4. Background and image-level artifacts are examined.
5. The trained detection model generates a prediction.
6. The system determines whether the image is likely **Real** or **AI-Generated/Manipulated**.

## 🏗️ Project Structure

```text
AI-Real-Image-Detection/
│
├── AI_Real_Detection/
│   └── Core detection and model files
│
├── upload_to_huggingface/
│   ├── app.py
│   ├── train.py
│   ├── frequency_analysis.py
│   ├── identity_risk.py
│   ├── check_labels.py
│   ├── debug_predict.py
│   ├── debug_single_image.py
│   ├── templates/
│   ├── static/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── render.yaml
│
├── prepare_upload.bat
├── First hackathon.pdf
├── .gitignore
└── README.md
