---
title: Coin Toss Detector
emoji: 🪙
colorFrom: blue
colorTo: yellow
sdk: docker
app_port: 7860
---

# COIN-TOSS: AI & Identity Risk Detection

## Overview

COIN-TOSS is an advanced web application designed to accurately detect AI-generated images and assess potential identity theft risks. By combining multiple state-of-the-art deep learning models with custom analysis logic ("Gap Trap V3"), it provides a reliable "Real" vs "AI" verdict without ambiguous percentages, while also identifying potential misuse of authentic images.

## Features

-   **High-Accuracy AI Detection**:
    -   Utilizes a hybrid ensemble of models (`dima806/ai_vs_real_image_detection` and `prithivMLmods/Deep-Fake-Detector-v2-Model`).
    -   **Gap Trap V3 Logic**: A specialized algorithm to catch "uncanny valley" images and properly classify filtered real photos vs. high-quality deepfakes.
    -   **Frequency Analysis**: Visualizes invisible noise patterns (FFT) to detect checkerboard artifacts common in diffusion models.
-   **Identity Theft Risk Analysis**:
    -   Analyzes "Real" images for biometric metrics (Face Visibility, Quality, etc.).
    -   Provides a risk assessment (Low/High) for using the image in sensitive contexts (KYC, Profiles).
-   **User-Friendly Interface**:
    -   Simple drag-and-drop upload.
    -   Instant "Real" or "AI" verdict.
    -   Detailed analysis points explaining the decision.

## Workflow

### Prerequisites

-   Python 3.8+
-   Git

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/madhavmullick2025/COIN-TOSS.git
    cd COIN-TOSS
    ```

2.  **Install Dependencies**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  **Start the Application**
    ```bash
    python app.py
    ```
    *Note: The first run may take a few moments to download the necessary model weights from HuggingFace.*

2.  **Access the Interface**
    Open your web browser and navigate to:
    ```
    http://localhost:5002
    ```

3.  **Analyze Images**
    -   Upload an image (JPG, PNG, WEBP).
    -   Click "Analyze" to see if it's Real or AI.
    -   If "Real", switch to the "Identity Risk" tab to see safety metrics.

## Tech Stack

-   **Backend**: Python, Flask, PyTorch, Transformers (HuggingFace).
-   **Frontend**: HTML5, CSS3, JavaScript.
-   **AI Models**: ViT (Vision Transformer) based image classifiers.
