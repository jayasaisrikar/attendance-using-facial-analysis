import face_recognition
import cv2
import numpy as np
import os
import logging
import gc
from concurrent.futures import ThreadPoolExecutor
import psutil

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('face_recognition')

class OptimizedFaceRecognizer:
    def __init__(self, known_faces_dir):
        self.known_faces_dir = known_faces_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self.max_workers = 4  # Increased for parallel processing
        self.batch_size = 16  # Increased batch size for group photos
        self.load_known_faces()

    def load_known_faces(self):
        if not os.path.exists(self.known_faces_dir):
            logger.warning(f"Directory not found: {self.known_faces_dir}")
            return

        for root, _, files in os.walk(self.known_faces_dir):
            student_id = os.path.basename(root)
            image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not image_files:
                continue

            # Process only first 5 images per student for efficiency
            for image_file in image_files[:5]:
                try:
                    image_path = os.path.join(root, image_file)
                    image = face_recognition.load_image_file(image_path)
                    small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
                    
                    face_locations = face_recognition.face_locations(small_image, model="hog")
                    if face_locations:
                        face_encoding = face_recognition.face_encodings(small_image, face_locations)[0]
                        self.known_face_encodings.append(face_encoding)
                        self.known_face_names.append(student_id)
                        
                    del image, small_image
                    gc.collect()
                    
                except Exception as e:
                    logger.warning(f"Error processing {image_path}: {e}")

    def mark_attendance(self, image_path, output_path=None):
        try:
            # Load and process image
            image = face_recognition.load_image_file(image_path)
            
            # Calculate optimal scale based on image size
            height, width = image.shape[:2]
            scale_factor = min(1.0, 1600/max(height, width))
            
            if scale_factor < 1.0:
                small_image = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)
            else:
                small_image = image.copy()
            
            # Use HOG for initial face detection
            face_locations = face_recognition.face_locations(
                small_image, 
                model="hog",
                number_of_times_to_upsample=2  # Increased for better detection
            )
            
            if not face_locations:
                logger.warning("No faces detected in the image")
                return []
            
            logger.info(f"Detected {len(face_locations)} faces")
            
            # Process face encodings in batches
            recognized_students = set()
            face_encodings = []
            
            # Process in smaller batches to manage memory
            for i in range(0, len(face_locations), self.batch_size):
                batch_locations = face_locations[i:i + self.batch_size]
                batch_encodings = face_recognition.face_encodings(
                    small_image,
                    batch_locations,
                    num_jitters=1  # Increased for better accuracy
                )
                face_encodings.extend(batch_encodings)
                
                # Process recognition in current batch
                for face_encoding, (top, right, bottom, left) in zip(batch_encodings, batch_locations):
                    # Compare with known faces using lower tolerance for better accuracy
                    matches = face_recognition.compare_faces(
                        self.known_face_encodings,
                        face_encoding,
                        tolerance=0.5  # Adjusted tolerance
                    )
                    
                    if True in matches:
                        # Use face distance to find best match
                        face_distances = face_recognition.face_distance(
                            self.known_face_encodings,
                            face_encoding
                        )
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            student_id = self.known_face_names[best_match_index]
                            recognized_students.add(student_id)
                            
                            # Scale coordinates back to original size
                            scale = 1/scale_factor
                            cv2.rectangle(
                                image, 
                                (int(left * scale), int(top * scale)),
                                (int(right * scale), int(bottom * scale)),
                                (0, 255, 0), 
                                2
                            )
                            cv2.putText(
                                image,
                                student_id,
                                (int(left * scale), int(top * scale) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.75,
                                (0, 255, 0),
                                2
                            )
                
                # Clean up batch memory
                gc.collect()
            
            # Save annotated image
            if output_path and recognized_students:
                cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            
            # Clean up
            del image, small_image
            gc.collect()
            
            logger.info(f"Recognized {len(recognized_students)} students")
            return list(recognized_students)
            
        except Exception as e:
            logger.error(f"Error in mark_attendance: {e}")
            return []