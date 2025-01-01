import cv2
import face_recognition
import numpy as np
import os

class FaceRecognitionUtil:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.dataset_path = 'media/student_images/'

    def load_student_images(self):
        for student_folder in os.listdir(self.dataset_path):
            student_path = os.path.join(self.dataset_path, student_folder)
            if os.path.isdir(student_path):
                for image_file in os.listdir(student_path):
                    if image_file.endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(student_path, image_file)
                        image = face_recognition.load_image_file(image_path)
                        encoding = face_recognition.face_encodings(image)[0]
                        self.known_face_encodings.append(encoding)
                        self.known_face_names.append(student_folder)

    def recognize_faces(self, image_path):
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        recognized_students = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding)
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
                recognized_students.append(name)

        return recognized_students 