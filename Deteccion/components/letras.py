import cv2
import mediapipe
import torch
import pandas as pd
import numpy as np
from .CNNModel import CNNModel

class LetrasDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.model = CNNModel()
        self.model.load_state_dict(torch.load("CNN_model_alphabet_SIBI.pth"))
        self.model.eval()

        self.handTracker = mediapipe.solutions.hands
        self.drawing = mediapipe.solutions.drawing_utils
        self.drawingStyles = mediapipe.solutions.drawing_styles

        self.handDetector = self.handTracker.Hands(
            static_image_mode=True,
            min_detection_confidence=0.2
        )

        self.classes = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5,
            'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11,
            'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17,
            'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23,
            'Y': 24, 'Z': 25
        }
        self.reverse_classes = {v: k for k, v in self.classes.items()}

    def generate_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            height, width, _ = frame.shape
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgMediapipe = self.handDetector.process(frameRGB)

            coordinates = []
            x_Coordinates = []
            y_Coordinates = []
            z_Coordinates = []

            if imgMediapipe.multi_hand_landmarks:
                for handLandmarks in imgMediapipe.multi_hand_landmarks:
                    self.drawing.draw_landmarks(
                        frame, handLandmarks, self.handTracker.HAND_CONNECTIONS,
                        self.drawingStyles.get_default_hand_landmarks_style(),
                        self.drawingStyles.get_default_hand_connections_style()
                    )

                    data = {}
                    for i in range(len(handLandmarks.landmark)):
                        lm = handLandmarks.landmark[i]
                        x_Coordinates.append(lm.x)
                        y_Coordinates.append(lm.y)
                        z_Coordinates.append(lm.z)

                    for i, landmark in enumerate(self.handTracker.HandLandmark):
                        lm = handLandmarks.landmark[i]
                        data[f'{landmark.name}_x'] = lm.x - min(x_Coordinates)
                        data[f'{landmark.name}_y'] = lm.y - min(y_Coordinates)
                        data[f'{landmark.name}_z'] = lm.z - min(z_Coordinates)
                    coordinates.append(data)

                x1 = int(min(x_Coordinates) * width) - 10
                y1 = int(min(y_Coordinates) * height) - 10
                x2 = int(max(x_Coordinates) * width) + 10
                y2 = int(max(y_Coordinates) * height) + 10

                coordinates = pd.DataFrame(coordinates)
                coordinates = np.reshape(coordinates.values, (coordinates.shape[0], 63, 1))
                coordinates = torch.from_numpy(coordinates).float()

                with torch.no_grad():
                    outputs = self.model(coordinates)
                    _, predicted = torch.max(outputs.data, 1)
                    predictions = predicted.cpu().numpy()

                predicted_character = self.reverse_classes[predictions[0]]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                cv2.putText(frame, predicted_character, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
