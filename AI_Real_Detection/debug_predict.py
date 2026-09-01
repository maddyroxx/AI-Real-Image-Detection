import requests

url = 'http://127.0.0.1:5002/predict'
file_path = r'C:/Users/Madhav/.gemini/antigravity/brain/67c74e6e-1b77-4d5b-894d-787254bc31a0/uploaded_image_1767961715511.jpg'

try:
    with open(file_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
        data = response.json()
        print("FULL RESPONSE:", data)
        scores = data.get('all_scores', {})
        print(f"DEBUG - Face Real: {scores.get('Debug_Face_Real')}")
        print(f"DEBUG - Gen Fake: {scores.get('Debug_General_Fake')}")
        print(f"DEBUG - Analysis: {data.get('analysis_points')}")
        print(f"Prediction: {data.get('prediction')}")
except Exception as e:
    print(f"Error: {e}")
