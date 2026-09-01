import cv2
import numpy as np
import os

class IdentityRiskAnalyzer:
    def __init__(self):
        # Load Haar Cascades
        cascade_path = cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(os.path.join(cascade_path, 'haarcascade_frontalface_default.xml'))
        self.eye_cascade = cv2.CascadeClassifier(os.path.join(cascade_path, 'haarcascade_eye.xml'))
        # Smile cascade is often less reliable, but we can try if available, or skip expression strictness.
        # self.smile_cascade = cv2.CascadeClassifier(os.path.join(cascade_path, 'haarcascade_smile.xml'))

    def analyze(self, pil_image):
        """
        Analyzes a PIL Image for identity theft risk using OpenCV.
        """
        # Convert PIL to CV2 (BGR)
        img_np = np.array(pil_image)
        if img_np.shape[2] == 4: # RGBA to RGB
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
        
        # OpenCV expects BGR
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        results = {
            "is_high_risk": False,
            "risk_score": 0.0,
            "details": [],
            "passed_criteria": []
        }

        # 1. Face Visibility & Count
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            results["details"].append("No face detected.")
            return results
        
        if len(faces) > 1:
            results["details"].append("Multiple faces detected.")
            return results
        
        results["passed_criteria"].append("Single face visible")
        
        # Get Face ROI
        (x, y, fw, fh) = faces[0]
        face_roi_gray = gray[y:y+fh, x:x+fw]
        
        face_ratio = (fw * fh) / (w * h)
        if face_ratio < 0.05:
             results["details"].append("Face too small relative to image.")
        
        # 2. Alignment (Eyes)
        eyes = self.eye_cascade.detectMultiScale(face_roi_gray)
        
        if len(eyes) >= 2:
            # Sort by x position to get left and right eye
            eyes = sorted(eyes, key=lambda e: e[0])
            (ex1, ey1, ew1, eh1) = eyes[0]
            (ex2, ey2, ew2, eh2) = eyes[-1] # Farthest right
            
            # Check Angle (Roll)
            dy = (ey2 + eh2/2) - (ey1 + eh1/2)
            dx = (ex2 + ew2/2) - (ex1 + ew1/2)
            angle = np.degrees(np.arctan2(dy, dx))
            
            if abs(angle) > 10:
                results["details"].append(f"Face tilted (Angle: {angle:.1f}°).")
            else:
                results["passed_criteria"].append("Face vertically aligned")
                
            # Check Centering (Yaw/Translation)
            face_center_x = x + fw/2
            img_center_x = w/2
            deviation = abs(face_center_x - img_center_x)
            
            if deviation > w * 0.15:
                results["details"].append("Face not centered.")
            else:
                results["passed_criteria"].append("Face centered")
        else:
             # Can't see both eyes -> Maybe side profile or hair?
             # For High Risk ID, we NEED eyes visible.
             results["details"].append("Eyes not clearly visible or aligned.")

        # 3. Image Quality (Blur)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 50:
             results["details"].append("Image too blurry.")
        else:
             results["passed_criteria"].append("High resolution/sharp")

        # 4. Lighting & Background
        margin = int(min(w, h) * 0.1)
        if margin < 1: margin = 1
        
        # Check top corners for background uniformity
        top_strip = gray[0:margin, :]
        bg_var = np.var(top_strip)
        bg_mean = np.mean(top_strip)
        
        if bg_var > 2500: # Relaxed threshold for "real world" plain walls
             results["details"].append("Background not plain/uniform.")
        elif bg_mean < 80: # Too dark
             results["details"].append("Background too dark.")
        else:
             results["passed_criteria"].append("Plain light-colored background")

        # 5. Expression (Heuristic)
        # Without landmarks, checking "neutral" is hard. 
        # But we can skip strict Smile check as user requested leniency.
        # We assume if it passes eye alignment and is frontal, it's risky enough.
        results["passed_criteria"].append("Expression check skipped (Lenient)")

        # Final Scoring
        # High Risk if NO details (failures).
        
        if len(results["details"]) == 0:
            results["is_high_risk"] = True
            results["risk_score"] = 0.95
        else:
             # Special Case: If only Background failed? No, ID photo needs plain BG.
             results["is_high_risk"] = False

        return results
