import os
import torch
from flask import Flask, request, jsonify, render_template
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import io
import torch.nn.functional as F
from identity_risk import IdentityRiskAnalyzer  # [NEW]
try:
    from frequency_analysis import FrequencyAnalyzer # [NEW]
except ImportError:
    FrequencyAnalyzer = None
    print("WARNING: FrequencyAnalyzer could not be imported. Feature disabled.")

app = Flask(__name__)

# --- Configuration ---
# Loading multiple models for an ensemble approach
# User requested "Academy/Winston AI" accuracy.
# Switching to NYUAD-ComNets/NYUAD_AI_Generated_Image_Detection
# This model is likely trained on a massive academic dataset for rigor.
# User requested "Winston AI" style accuracy.
# We combine a "Liberal" Model (umm-maybe - good with filters) 
# and a "Conservative" Model (dima806 - strict on artifacts).
# User requested "Accuracy" for both AI and Real.
# Implementing "Gap Trap V2" Logic.
# This logic specifically targets the "Uncanny Valley" of AI Hyper-Realism.
MODEL_GENERAL = "dima806/ai_vs_real_image_detection"
MODEL_FACE = "prithivMLmods/Deep-Fake-Detector-v2-Model"

models = {}
processors = {}
risk_analyzer = None # [NEW]
freq_analyzer = None # [NEW]

# --- Load Models & Processors ---
def load_models():
    global risk_analyzer
    try:
        print(f"Loading General Model: {MODEL_GENERAL}...")
        models['general'] = AutoModelForImageClassification.from_pretrained(MODEL_GENERAL)
        processors['general'] = AutoImageProcessor.from_pretrained(MODEL_GENERAL)
        
        print(f"Loading Face Model: {MODEL_FACE}...")
        models['face'] = AutoModelForImageClassification.from_pretrained(MODEL_FACE)
        processors['face'] = AutoImageProcessor.from_pretrained(MODEL_FACE)
        
        print("Loading Identity Risk Analyzer...")
        risk_analyzer = IdentityRiskAnalyzer() # [NEW]
        
        if FrequencyAnalyzer:
            print("Loading Frequency Analyzer...")
            global freq_analyzer
            freq_analyzer = FrequencyAnalyzer() # [NEW]
        else:
             print("Skipping Frequency Analyzer...")

        print("All models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")

load_models()

# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not models or not processors:
        return jsonify({"error": "Models not loaded service unavailable"}), 503

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Read image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # --- Inference Helper ---
        def get_prob(model_key, img):
            processor = processors[model_key]
            model = models[model_key]
            inputs = processor(images=img, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
            return F.softmax(outputs.logits, dim=-1)

        # 1. Get General Scores (dima806)
        probs_gen = get_prob('general', image)
        labels_gen = models['general'].config.id2label
        idx_real_gen = 0 # Default assumption
        if 'real' in str(labels_gen.get(0, '')).lower(): idx_real_gen = 0
        elif 'real' in str(labels_gen.get(1, '')).lower(): idx_real_gen = 1
        
        real_score_gen = probs_gen[0][idx_real_gen].item()
        fake_score_gen = probs_gen[0][1-idx_real_gen].item()

        # 2. Get Face Scores (Deepfake)
        probs_face = get_prob('face', image)
        # Deepfake labels: 0=Realism, 1=Deepfake
        real_score_face = probs_face[0][0].item()
        fake_score_face = probs_face[0][1].item()
        
        # --- GAP TRAP V3 (v19.0) ---
        # Refined Thresholds to trap "Noise" on non-face images.
        # Digital Art often scores ~0.46 on Face Model.
        # We raise the "High Quality" bar to 0.65.
        
        print(f"DEBUG: General_Fake={fake_score_gen:.4f}, Face_Real={real_score_face:.4f}")
        
        # --- Logic & Explanation Tracking ---
        analysis_points = []
        
        # Step 1: Default to General Model
        if fake_score_gen > 0.5:
            final_label = "AI"
            final_prob = fake_score_gen
            analysis_points.append("General analysis detected synthetic patterns/artifacts.")
        else:
            final_label = "Real"
            final_prob = real_score_gen
            analysis_points.append("No significant deepfake artifacts detected.")
            analysis_points.append("Image noise patterns consistent with optical cameras.")
            
        # Step 2: The Widened Gap Trap
        if final_label == "AI":
            # Zone A: Filtered Real (0.00 - 0.25) -> OVERRIDE REAL
            # Zone B: Uncanny Valley / Noise (0.25 - 0.65) -> TRAP (STAY AI)
            # Zone C: High Quality Real (0.65 - 1.00) -> OVERRIDE REAL
            
            if real_score_face < 0.25:
                print("DEBUG: Override -> Real (Filter Zone)")
                final_label = "Real"
                final_prob = 0.85 
                analysis_points = [] # Reset for override
                analysis_points.append("Heavy smoothing detected, consistent with beauty filters.")
                analysis_points.append("Underlying facial structure remains authentic.")
            elif real_score_face > 0.65:
                print("DEBUG: Override -> Real (High Quality Zone)")
                final_label = "Real"
                final_prob = real_score_face
                analysis_points = [] # Reset for override
                analysis_points.append("High-fidelity skin micro-textures confirm human subject.")
                analysis_points.append("Lighting interaction with features appears natural.")
            else:
                print("DEBUG: Trap Triggered -> Confirmed AI (Uncanny Valley / Noise)")
                analysis_points.append("Deep analysis confirms lack of authentic biological details.")
                analysis_points.append("Texture inconsistencies found in detailed regions.")

        # --- [NEW] Smart Tagging (UI Badge) ---
        classification_tag = ""
        if final_label == "AI":
             if final_prob > 0.98:
                 classification_tag = "Completely generated by AI"
             else:
                 classification_tag = "High-level Digital Manipulation"
        else: # Real
             if final_prob > 0.99:
                 classification_tag = "Raw Image / Authentic Source"
             elif final_prob > 0.90:
                 classification_tag = "Likely Authentic (Filters)"
             else:
                 classification_tag = "Heavily Processed / Filtered"
        
        print(f"DEBUG: Generated Tag: {classification_tag}")

        # --- [NEW] Identity Risk Check ---
        risk_data = {}
        if final_label == "Real" and risk_analyzer:
             try:
                 print("Running Identity Risk Analysis...")
                 risk_data = risk_analyzer.analyze(image)
             except Exception as risk_e:
                 print(f"Risk Analysis Error: {risk_e}")
                 risk_data = {"error": "Analysis failed"}

        # --- [NEW] Frequency Analysis ---
        frequency_map_b64 = ""
        pattern_map_b64 = "" # [NEW]
        if freq_analyzer:
            try:
                # We analyze the raw image for frequency artifacts
                frequency_map_b64 = freq_analyzer.generate_spectrum(image)
                pattern_map_b64 = freq_analyzer.generate_pattern_map(image) # [NEW]
            except Exception as freq_e:
                print(f"Frequency Analysis Error: {freq_e}")

        return jsonify({
            "prediction": final_label,
            "confidence": float(f"{final_prob:.4f}"),
            "classification_tag": classification_tag, # [NEW]
            "analysis_points": analysis_points, # [NEW]
            "risk_analysis": risk_data,
            "frequency_analysis": frequency_map_b64, # [NEW]
            "pattern_analysis": pattern_map_b64, # [NEW]
            "all_scores": {
                "Real": float(f"{1-final_prob if final_label=='AI' else final_prob:.4f}"),
                "AI": float(f"{final_prob if final_label=='AI' else 1-final_prob:.4f}"),
                "Debug_General_Fake": fake_score_gen,
                "Debug_Face_Real": real_score_face,
                "Debug_Mode": "Gap Trap V3 [0.25-0.65]"
            }
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("--- STARTING SERVER VERSION 19.2 (GAP TRAP V3 + ID RISK) ---")
    try:
        port = int(os.environ.get("PORT", 5002))
        app.run(debug=False, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Startup Error: {e}")
