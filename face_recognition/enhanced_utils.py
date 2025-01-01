import cv2
import numpy as np
import os
import pickle
from pathlib import Path
from django.conf import settings

class EnhancedFaceRecognition:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Define paths
        self.models_dir = os.path.join(settings.MEDIA_ROOT, 'models')
        self.model_path = os.path.join(self.models_dir, 'face_model.yml')
        self.labels_path = os.path.join(self.models_dir, 'labels.pkl')
        
        # Create models directory
        os.makedirs(self.models_dir, exist_ok=True)
        print(f"Models directory: {self.models_dir}")
        
        # Initialize empty model if files don't exist
        if not os.path.exists(self.model_path) or not os.path.exists(self.labels_path):
            print("Initializing new model files")
            self.recognizer.write(self.model_path)
            with open(self.labels_path, 'wb') as f:
                pickle.dump({'label_to_num': {}, 'num_to_label': {}}, f)
        
        # Load or train the model
        self.load_or_train_model()

    def load_or_train_model(self):
        student_images_path = os.path.join(settings.MEDIA_ROOT, 'student_images')
        if not os.path.exists(student_images_path):
            os.makedirs(student_images_path)
            print("Created student_images directory")
            return

        faces = []
        labels = []
        label_mapping = {}
        
        print(f"Scanning directory: {student_images_path}")
        
        # Process all student folders
        for student_folder in os.listdir(student_images_path):
            folder_path = os.path.join(student_images_path, student_folder)
            if not os.path.isdir(folder_path):
                continue
            
            print(f"Processing student folder: {student_folder}")
            
            # Use student folder name (user ID) directly as the label
            label = student_folder
            label_mapping[label] = label
            
            # Process each image in student folder
            for img_name in os.listdir(folder_path):
                if not img_name.endswith(('.jpg', '.jpeg', '.png')):
                    continue
                    
                img_path = os.path.join(folder_path, img_name)
                print(f"Processing image: {img_path}")
                
                image = cv2.imread(img_path)
                if image is None:
                    print(f"Failed to load image: {img_path}")
                    continue
                    
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                detected_faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                for (x, y, w, h) in detected_faces:
                    faces.append(gray[y:y+h, x:x+w])
                    labels.append(label)
                    print(f"Face detected in {img_path}")

        if faces:
            # Convert labels to numeric format for training
            unique_labels = list(set(labels))
            label_to_num = {label: i for i, label in enumerate(unique_labels)}
            numeric_labels = [label_to_num[label] for label in labels]
            
            # Save both mappings
            with open(self.labels_path, 'wb') as f:
                pickle.dump({
                    'label_to_num': label_to_num, 
                    'num_to_label': {v: k for k, v in label_to_num.items()}
                }, f)
            
            # Train the model
            self.recognizer.train(faces, np.array(numeric_labels))
            self.recognizer.save(self.model_path)
            print(f"Model trained with {len(faces)} faces from {len(set(labels))} students")
        else:
            print("No faces found to train the model")

    def process_image(self, image_path, confidence_threshold=70):
        if not os.path.exists(self.model_path) or not os.path.exists(self.labels_path):
            print("Model or labels file not found")
            return []

        # Load mappings
        with open(self.labels_path, 'rb') as f:
            mappings = pickle.load(f)
            num_to_label = mappings['num_to_label']

        image = cv2.imread(image_path)
        if image is None:
            print("Failed to load image")
            return []
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        recognized_students = []
        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            label, confidence = self.recognizer.predict(face)
            
            if confidence < confidence_threshold and label in num_to_label:
                student_id = num_to_label[label]
                recognized_students.append({
                    'student_id': student_id,
                    'confidence': (100 - confidence),
                    'location': (x, y, w, h)
                })
                print(f"Recognized student {student_id} with confidence {100-confidence}%")

        return recognized_students

    def mark_attendance_image(self, image_path, recognized_students):
        image = cv2.imread(image_path)
        
        for student in recognized_students:
            x, y, w, h = student['location']
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            text = f"{student['student_id']} ({student['confidence']:.1f}%)"
            cv2.putText(image, text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        marked_path = f"{os.path.splitext(image_path)[0]}_marked.jpg"
        cv2.imwrite(marked_path, image)
        return marked_path 