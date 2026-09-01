from identity_risk import IdentityRiskAnalyzer
from PIL import Image
import os

# Path to the uploaded image
image_path = r"C:/Users/Madhav/.gemini/antigravity/brain/9cc8325c-cd76-426f-85e1-e3096464cb09/uploaded_image_1767977759111.png"

try:
    print(f"Loading image from: {image_path}")
    image = Image.open(image_path).convert("RGB")
    
    analyzer = IdentityRiskAnalyzer()
    print("Running analysis...")
    results = analyzer.analyze(image)
    
    print("\n--- ANALYSIS RESULTS ---")
    print(f"High Risk: {results['is_high_risk']}")
    print(f"Risk Score: {results['risk_score']}")
    
    print("\n[Passed Criteria (Risk Factors)]:")
    for item in results['passed_criteria']:
        print(f" - {item}")
        
    print("\n[Failed Criteria / Details (Safety Factors)]:")
    for item in results['details']:
        print(f" - {item}")

except Exception as e:
    print(f"Error: {e}")
