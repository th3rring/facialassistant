import sys
import os
import dlib
import glob
import cv2
import json
import numpy as np

# Threshold to determine certainty in match
_CERTAINTY = 0.5

class Recognizer:
    def __init__(self):
        self.encodings = []
        self.names = []
        # Path of the main file
        PATH = os.path.abspath(__file__ + "/../..")
        self.enc_file = PATH + "/models/faces.dat"

        self.pose_predictor = dlib.shape_predictor(PATH + "/models/shape_predictor_5_face_landmarks.dat")
        self.face_encoder = dlib.face_recognition_model_v1(PATH + "/models/dlib_face_recognition_resnet_model_v1.dat")
        self.detector = dlib.get_frontal_face_detector()

    def load_models(self):
        """ Loads encodings from a json file """
        try:
            models = json.load(open(self.enc_file))
            for model in models:
                self.encodings.append(model["data"])
                self.names.append(model["name"])
            print(self.encodings)
            print(self.names)
        except FileNotFoundError:
            print("No encodings file")
            sys.exit(10)

    def write_models(self, name, face_encodering):
        """ Writes a face encoding to a json file """
        with open(self.enc_file, "w") as datafile:
            model_info = {"name" : name, "data" : None}
            model_info["data"] = face_encodering.tolist()
            encodings.append(model_info)
            json.dump(encodings, datafile)


    def draw_face(self, frame, face, landmarks):
        """ Modifies a frame to draw an oval aroud a face """
        x = int((face.right() - face.left()) / 2) + face.left()
        y = int((face.bottom() - face.top()) / 2) + face.top()

        # Get the raduis from the with of the square
        r = (face.right() - face.left()) / 2
        # Add 20% padding
        r = int(r + (r * 0.2))

        # Draw the Circle in green
        cv2.circle(frame, (x, y), r, (0, 0, 230), 2)

        eye_color = (0,255,0)
        # Draw right eye.
        cv2.circle(frame, tuple(landmarks[2]), 4, eye_color, -1)
        cv2.circle(frame, tuple(landmarks[3]), 4, eye_color, -1)

        # Draw left eye.
        cv2.circle(frame, tuple(landmarks[0]), 4, eye_color, -1)
        cv2.circle(frame, tuple(landmarks[1]), 4, eye_color, -1)

        
        return frame

    def find_faces(self, frame):
        """ Looks through frame and finds and encodes all faces """
        faces = self.detector(frame, 1)
        
        encodings = {}
        landmarks = {}

        for face in faces:

            face_landmark = self.pose_predictor(frame, face)
            face_encoding = np.array(self.face_encoder.compute_face_descriptor(frame, face_landmark, 1))
            encodings[face] = face_encoding

            cur_landmarks = np.zeros((face_landmark.num_parts, 2), dtype='i')

            # loop over all facial landmarks and convert them
            # to a 2-tuple of (x, y)-coordinates
            for i in range(0, face_landmark.num_parts):
                    cur_landmarks[i] = (face_landmark.part(i).x, face_landmark.part(i).y)

            landmarks[face] = cur_landmarks

        return encodings, landmarks

    def recognize(self, face_encodering):
        """ Matches face encoding with known faces """
        matches = np.linalg.norm(self.encodings - face_encodering, axis=1)
        match_index = np.argmin(matches)
        match = matches[match_index]

        if 0 < match < _CERTAINTY:
            return self.names[match_index]
        else:
            return "Not anybody I know"







