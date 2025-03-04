import time

import cv2


class LivenessDetector:
    def __init__(self):
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.blink_threshold = 0.3
        
    def detect_blink(self, eye_region):
        eye_aspect_ratio = self.calculate_eye_aspect_ratio(eye_region)
        return eye_aspect_ratio < self.blink_threshold
        
    def verify_liveness(self, face_frame, required_blinks=2):
        blink_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 5:  # 5-second verification window
            eyes = self.eye_cascade.detectMultiScale(face_frame)
            for eye in eyes:
                if self.detect_blink(eye):
                    blink_count += 1
                    if blink_count >= required_blinks:
                        return True
        return False 