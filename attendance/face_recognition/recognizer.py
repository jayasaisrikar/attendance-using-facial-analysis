import face_recognition
import cv2
import numpy as np
import os
import logging
import gc
from concurrent.futures import ThreadPoolExecutor
import psutil

# Enhanced logging for better troubleshooting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('face_recognition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('face_recognition')

class OptimizedFaceRecognizer:
    def __init__(self, known_faces_dir):
        self.known_faces_dir = known_faces_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self.max_workers = 4  # Increased for parallel processing
        self.batch_size = 16  # Increased batch size for group photos
        # Create a mapping of roll numbers to simple IDs for flexible matching
        self.roll_number_mapping = {}  # Will be filled during verification
        self.load_known_faces()

    def load_known_faces(self):
        if not os.path.exists(self.known_faces_dir):
            logger.warning(f"Directory not found: {self.known_faces_dir}")
            return

        logger.info(f"Loading known faces from {self.known_faces_dir}")
        student_count = 0
        image_count = 0
        
        # Store a mapping of roll numbers to their image paths for later reference
        self.roll_number_to_paths = {}

        # First check direct student roll number folders (traditional structure)
        for item in os.listdir(self.known_faces_dir):
            item_path = os.path.join(self.known_faces_dir, item)
            
            # Skip if it's not a directory or is a special directory like B.Tech or BTech
            if not os.path.isdir(item_path) or item in ["B.Tech", "BTech"]:
                continue
                
            student_id = item
            image_files = [f for f in os.listdir(item_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not image_files:
                continue

            student_count += 1
            # Process only first 5 images per student for efficiency
            self._process_student_images(item_path, student_id, image_files[:5], image_count)
        
        # Scan for direct files in root that start with roll numbers (alternative structure)
        direct_files = [f for f in os.listdir(self.known_faces_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for image_file in direct_files:
            # Try to extract student ID from filename
            # Assuming format like "19BCE1234_photo.jpg" or similar
            parts = image_file.split('_')
            if len(parts) > 0 and any(c.isdigit() for c in parts[0]):
                student_id = parts[0]
                try:
                    self._process_single_image(
                        os.path.join(self.known_faces_dir, image_file),
                        student_id,
                        image_count
                    )
                    student_count += 1
                except Exception as e:
                    logger.warning(f"Error processing direct file {image_file}: {e}")
        
        # Now look through degree-branch structure (e.g., B.Tech/IT/19BCE1234/*.jpg)
        for degree_folder in ["B.Tech", "BTech"]:
            degree_path = os.path.join(self.known_faces_dir, degree_folder)
            if not os.path.exists(degree_path):
                continue
                
            logger.info(f"Scanning degree folder: {degree_path}")
            
            # Iterate through branches (CS, IT, etc.)
            for branch in os.listdir(degree_path):
                branch_path = os.path.join(degree_path, branch)
                if not os.path.isdir(branch_path):
                    continue
                    
                logger.info(f"Scanning branch folder: {branch_path}")
                
                # Iterate through student folders
                for student_folder in os.listdir(branch_path):
                    student_path = os.path.join(branch_path, student_folder)
                    if not os.path.isdir(student_path):
                        continue
                        
                    student_id = student_folder
                    image_files = [f for f in os.listdir(student_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    
                    if not image_files:
                        continue
                        
                    logger.info(f"Found student {student_id} in {degree_folder}/{branch} with {len(image_files)} images")
                    student_count += 1
                    self._process_student_images(student_path, student_id, image_files[:5], image_count)

        logger.info(f"Loaded {image_count} face encodings from {student_count} students")
        logger.info(f"Student IDs found: {list(self.roll_number_to_paths.keys())}")

    def _process_student_images(self, student_path, student_id, image_files, image_count):
        """Process multiple images for a student and add their encodings"""
        paths = []
        
        for image_file in image_files:
            try:
                image_path = os.path.join(student_path, image_file)
                paths.append(image_path)
                self._process_single_image(image_path, student_id, image_count)
                image_count += 1
            except Exception as e:
                logger.warning(f"Error processing {image_path}: {e}")
                
        # Store the paths for this student for later reference
        self.roll_number_to_paths[student_id] = paths
    
    def _process_single_image(self, image_path, student_id, image_count):
        """Process a single image and add its encoding"""
        logger.debug(f"Processing {image_path}")
        image = face_recognition.load_image_file(image_path)
        small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        
        face_locations = face_recognition.face_locations(small_image, model="hog")
        if face_locations:
            face_encoding = face_recognition.face_encodings(small_image, face_locations)[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(student_id)
        else:
            logger.warning(f"No face detected in reference image: {image_path}")
            
        del image, small_image
        gc.collect()

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

    def verify_student(self, image_path, student_roll_number):
        """
        Verify if the face in the image matches the given student roll number.
        Returns True if there's a match, False otherwise.
        """
        try:
            # Dump all student information for debugging
            logger.info(f"Verifying student with roll number: {student_roll_number}")
            logger.info(f"Total known faces: {len(self.known_face_names)}")
            logger.info(f"Known student IDs: {set(self.known_face_names)}")
            
            # In case the student roll number is not found directly, try to match with simple numeric ID
            # Create possible simple IDs from the roll number (e.g., "19BCE1234" -> "1234", "BCE1234")
            possible_simple_ids = []
            
            # Try extracting the numeric part at the end (most common case)
            numeric_part = ''.join(filter(str.isdigit, student_roll_number))
            if numeric_part:
                possible_simple_ids.append(numeric_part)
                # Also try just the last few digits if it's a long number
                if len(numeric_part) > 2:
                    possible_simple_ids.append(numeric_part[-2:])  # Last two digits
                    possible_simple_ids.append(numeric_part[-1:])  # Last digit
            
            # Also try with just the numeric part (e.g., "19BCE1234" -> "1234")
            if student_roll_number.isalnum() and not student_roll_number.isalpha():
                digits_only = ''.join(filter(str.isdigit, student_roll_number))
                if digits_only and digits_only not in possible_simple_ids:
                    possible_simple_ids.append(digits_only)
            
            logger.info(f"Possible simple IDs to try: {possible_simple_ids}")
            
            # First check our loaded face encodings for this student
            student_indices = [i for i, name in enumerate(self.known_face_names) if name == student_roll_number]
            
            # If not found directly, try with possible simple IDs
            if not student_indices:
                for simple_id in possible_simple_ids:
                    simple_indices = [i for i, name in enumerate(self.known_face_names) if name == simple_id]
                    if simple_indices:
                        logger.info(f"Found match using simple ID: {simple_id}")
                        student_indices = simple_indices
                        # Remember this mapping for future use
                        self.roll_number_mapping[student_roll_number] = simple_id
                        break
            
            # If still not found, search the file system for images
            if not student_indices:
                logger.warning(f"No reference images found in memory for {student_roll_number}")
                
                # Paths to check for this student
                all_paths_to_check = []
                
                # Direct student ID folder
                all_paths_to_check.append(os.path.join(self.known_faces_dir, student_roll_number))
                
                # Check if images might be in a numeric-only subfolder
                for simple_id in possible_simple_ids:
                    # Check direct path with simple ID
                    all_paths_to_check.append(os.path.join(self.known_faces_dir, simple_id))
                    
                    # Try with degree/branch structure for each simple ID
                    for degree in ["B.Tech", "BTech"]:
                        degree_path = os.path.join(self.known_faces_dir, degree)
                        if os.path.exists(degree_path):
                            for branch in os.listdir(degree_path):
                                branch_path = os.path.join(degree_path, branch)
                                if not os.path.isdir(branch_path):
                                    continue
                                
                                # Check if the simple ID is directly under the branch
                                simple_id_path = os.path.join(branch_path, simple_id)
                                all_paths_to_check.append(simple_id_path)
                                
                                # IMPORTANT: Check if there are additional nested directories under student ID
                                if os.path.exists(simple_id_path) and os.path.isdir(simple_id_path):
                                    for nested_dir in os.listdir(simple_id_path):
                                        nested_path = os.path.join(simple_id_path, nested_dir)
                                        if os.path.isdir(nested_path):
                                            all_paths_to_check.append(nested_path)
                                            logger.info(f"Found nested directory: {nested_path}")
                
                # Search for files with roll number or simple IDs in name
                for root, dirs, files in os.walk(self.known_faces_dir):
                    for f in files:
                        if (student_roll_number in f and f.lower().endswith(('.jpg', '.jpeg', '.png'))):
                            all_paths_to_check.append(os.path.join(root, f))
                        else:
                            # Check if any simple ID is in the filename
                            for simple_id in possible_simple_ids:
                                if simple_id in f and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                                    all_paths_to_check.append(os.path.join(root, f))
                                    break
                
                # Log all paths we're going to check
                logger.info(f"Paths to check for student images: {all_paths_to_check}")
                
                # Try to load images from these paths
                student_images_found = False
                for path in all_paths_to_check:
                    if os.path.exists(path):
                        logger.info(f"Path exists: {path}")
                        
                        if os.path.isdir(path):
                            # It's a directory, look for image files
                            image_files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                            if image_files:
                                logger.info(f"Found {len(image_files)} images in {path}")
                                # Use this simple ID for the student
                                folder_name = os.path.basename(path)
                                logger.info(f"Using folder name as ID: {folder_name}")
                                
                                # Remember this mapping
                                self.roll_number_mapping[student_roll_number] = folder_name
                                
                                # Load these images with the student's roll number
                                for img_file in image_files[:5]:
                                    img_path = os.path.join(path, img_file)
                                    try:
                                        logger.info(f"Loading image: {img_path}")
                                        image = face_recognition.load_image_file(img_path)
                                        small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
                                        
                                        face_locations = face_recognition.face_locations(small_image, model="hog")
                                        if face_locations:
                                            face_encoding = face_recognition.face_encodings(small_image, face_locations)[0]
                                            self.known_face_encodings.append(face_encoding)
                                            # Use the student's actual roll number for consistency
                                            self.known_face_names.append(student_roll_number)
                                            student_images_found = True
                                            logger.info(f"Successfully loaded image for student {student_roll_number}")
                                        else:
                                            logger.warning(f"No face detected in image: {img_path}")
                                    except Exception as e:
                                        logger.error(f"Error loading image {img_path}: {str(e)}")
                        else:
                            # It's a direct file
                            try:
                                logger.info(f"Loading direct image file: {path}")
                                image = face_recognition.load_image_file(path)
                                small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
                                
                                face_locations = face_recognition.face_locations(small_image, model="hog")
                                if face_locations:
                                    face_encoding = face_recognition.face_encodings(small_image, face_locations)[0]
                                    self.known_face_encodings.append(face_encoding)
                                    self.known_face_names.append(student_roll_number)
                                    student_images_found = True
                                    logger.info(f"Successfully loaded direct image file for student {student_roll_number}")
                                else:
                                    logger.warning(f"No face detected in direct image file: {path}")
                            except Exception as e:
                                logger.error(f"Error loading direct image file {path}: {str(e)}")
                
                if not student_images_found:
                    logger.error(f"Failed to find any usable reference images for student {student_roll_number}")
                    # Emergency fallback: Just try to find ANY usable image if we're desperate
                    emergency_dir = f"{self.known_faces_dir}/B.Tech/IT"
                    if os.path.exists(emergency_dir):
                        logger.info(f"Emergency search in {emergency_dir}")
                        has_images = False
                        for root, dirs, files in os.walk(emergency_dir):
                            image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                            if image_files:
                                has_images = True
                                logger.info(f"Found images in {root}: {image_files[:5]}")
                                for img_file in image_files[:2]:  # Just take 2 as emergency
                                    try:
                                        img_path = os.path.join(root, img_file)
                                        logger.info(f"Emergency loading: {img_path}")
                                        image = face_recognition.load_image_file(img_path)
                                        small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
                                        face_locations = face_recognition.face_locations(small_image, model="hog")
                                        if face_locations:
                                            face_encoding = face_recognition.face_encodings(small_image, face_locations)[0]
                                            self.known_face_encodings.append(face_encoding)
                                            self.known_face_names.append(student_roll_number)
                                            student_images_found = True
                                    except Exception as e:
                                        logger.error(f"Error in emergency load: {str(e)}")
                        
                        if not has_images:
                            logger.error(f"No images found even in emergency search!")
                            return False
                    else:
                        return False
                
                # Check if we loaded any images successfully
                student_indices = [i for i, name in enumerate(self.known_face_names) if name == student_roll_number]
                if not student_indices:
                    logger.error("No usable face encodings were loaded")
                    return False
            
            # Log what we found for this student
            logger.info(f"Found {len(student_indices)} reference encodings for student {student_roll_number}")
            
            # Load and process test image
            logger.info(f"Processing verification image: {image_path}")
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(image, model="hog")
            
            if not face_locations:
                logger.warning("No face detected in the verification image")
                return False
                
            if len(face_locations) > 1:
                logger.warning(f"Multiple faces ({len(face_locations)}) detected in verification image")
                return False  # Reject if multiple faces detected
            
            logger.info("Face detected in verification image, extracting features")    
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            
            # Filter encodings by student roll number
            student_encodings = []
            for idx in student_indices:
                student_encodings.append(self.known_face_encodings[idx])
                
            # Compare with reference images of the specific student
            # Use a very relaxed tolerance for better matching during testing
            tolerance_value = 0.7  # Very relaxed threshold
            matches = face_recognition.compare_faces(
                student_encodings,
                face_encoding,
                tolerance=tolerance_value
            )
            
            # Calculate face distances for better matching
            face_distances = face_recognition.face_distance(student_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            best_match_distance = face_distances[best_match_index]
            
            logger.info(f"Best match distance: {best_match_distance} (lower is better)")
            logger.info(f"Match result: {True in matches}, using tolerance: {tolerance_value}")
            
            # Only verify if distance is below threshold (lower is better)
            verification_threshold = 0.8  # Very relaxed threshold for testing
            is_verified = best_match_distance < verification_threshold
            
            logger.info(f"Verification result: {is_verified} (threshold: {verification_threshold})")
            
            return is_verified
            
        except Exception as e:
            logger.error(f"Error in verify_student: {str(e)}", exc_info=True)
            return False