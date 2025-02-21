import cv2
import numpy as np
import face_recognition
import os
import logging
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('face_recognition')

class OptimizedFaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def preprocess_image(self, image):
        # Basic image enhancement
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        return enhanced

    def detect_faces(self, image_path):
        try:
            # Read and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Resize for faster processing
            height, width = image.shape[:2]
            max_dimension = 800
            if max(height, width) > max_dimension:
                scale = max_dimension / max(height, width)
                image = cv2.resize(image, None, fx=scale, fy=scale)
            
            # Enhance image
            enhanced_image = self.preprocess_image(image)
            gray = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using Haar Cascade
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Convert to face_recognition format
            face_locations = []
            for (x, y, w, h) in faces:
                face_locations.append((y, x + w, y + h, x))
            
            return face_locations, enhanced_image
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return [], None

class FaceRecognizer:
    def __init__(self, known_faces_dir):
        self.known_faces_dir = known_faces_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self.batch_size = 8
        self.detector = OptimizedFaceDetector()
        self._load_known_faces()
        
        # Set up signal handler
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.warning("Interrupting face recognition process...")
        sys.exit(0)

    def _process_image(self, image_path, student_id):
        try:
            image = face_recognition.load_image_file(image_path)
            small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_image, model="hog")
            
            if face_locations:
                face_encoding = face_recognition.face_encodings(small_image, face_locations)[0]
                return (face_encoding, student_id)
                
        except Exception as e:
            logger.warning(f"Error processing {image_path}: {e}")
        return None

    def _load_known_faces(self):
        if not os.path.exists(self.known_faces_dir):
            logger.warning(f"Directory not found: {self.known_faces_dir}")
            return

        image_paths = []
        student_ids = []
        
        # Collect all image paths first
        for root, _, files in os.walk(self.known_faces_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(root, file)
                    student_id = os.path.basename(os.path.dirname(image_path))
                    image_paths.append(image_path)
                    student_ids.append(student_id)

        # Process images in parallel with timeout
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            future_to_path = {
                executor.submit(self._process_image, path, sid): (path, sid)
                for path, sid in zip(image_paths, student_ids)
            }
            
            for future in future_to_path:
                try:
                    result = future.result(timeout=30)  # 30 second timeout per image
                    if result:
                        encoding, student_id = result
                        self.known_face_encodings.append(encoding)
                        self.known_face_names.append(student_id)
                except Exception as e:
                    logger.warning(f"Failed to process image: {e}")

        logger.info(f"Loaded {len(self.known_face_encodings)} face encodings")

    def recognize_faces(self, image_path):
        image = face_recognition.load_image_file(image_path)
        small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        
        face_locations = face_recognition.face_locations(small_image, 
                                                       model="hog")  # Using HOG for speed
        face_encodings = face_recognition.face_encodings(small_image, face_locations)

        recognized_students = set()
        
        for i in range(0, len(face_encodings), self.batch_size):
            batch_encodings = face_encodings[i:i + self.batch_size]
            
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                batch_encodings,
                tolerance=0.45
            )
            
            face_distances = face_recognition.face_distance(
                self.known_face_encodings,
                batch_encodings
            )
            
            for match_set, distances in zip(matches, face_distances):
                if True in match_set:
                    best_match_index = np.argmin(distances)
                    if match_set[best_match_index]:
                        student_id = self.known_face_names[best_match_index]
                        recognized_students.add(student_id)

        return list(recognized_students)

    def mark_attendance(self, image_path, output_path=None):
        try:
            image = face_recognition.load_image_file(image_path)
            small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_image, model="hog")
            face_encodings = face_recognition.face_encodings(small_image, face_locations)
            
            recognized_students = []
            
            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.45
                )
                
                if True in matches:
                    best_match_index = matches.index(True)
                    student_id = self.known_face_names[best_match_index]
                    recognized_students.append(student_id)
                    
                    # Scale coordinates back up
                    scale = 4
                    cv2.rectangle(image, 
                                (left * scale, top * scale),
                                (right * scale, bottom * scale),
                                (0, 255, 0),
                                2)
                    cv2.putText(image,
                              student_id,
                              (left * scale, top * scale - 10),
                              cv2.FONT_HERSHEY_SIMPLEX,
                              0.75,
                              (0, 255, 0),
                              2)
            
            if output_path:
                cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            
            return recognized_students
            
        except Exception as e:
            logger.error(f"Error in mark_attendance: {e}")
            return []