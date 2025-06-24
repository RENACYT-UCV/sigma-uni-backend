import cv2
import mediapipe
import torch
import pandas as pd
import numpy as np
from .CNNModel import CNNModel

<<<<<<< HEAD
class LetrasDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.model = CNNModel()
        self.model.load_state_dict(torch.load("CNN_model_alphabet_SIBI.pth"))
        self.model.eval()
=======

class LetrasDetector(BaseDetector):
    """Detector de letras en lenguaje de señas"""

    def __init__(self):
        super().__init__()
        self.letras_config = {
            "Letra - A": [1, 1, 0, 0, 0, 0],
            "Letra - B": [0, 0, 1, 1, 1, 1],
            "Letra - C": [1, 1, 1, 1, 1, 1],
            "Letra - D": [0, 0, 0, 0, 0, 1],
            "Letra - E": [0, 0, 0, 0, 0, 0],
            "Letra - F": [1, 1, 1, 1, 1, 0],
            "Letra - G": [1, 0, 0, 1, 1, 1],
            "Letra - H": [1, 0, 0, 0, 1, 1],
            "Letra - I": [0, 0, 1, 0, 0, 0],
            "Letra - K": [1, 1, 0, 0, 1, 1],
            "Letra - L": [1, 1, 0, 0, 0, 1],
            "Letra - M": [1, 1, 1, 0, 0, 0],
            "Letra - N": [0, 1, 0, 0, 1, 1],
            "Letra - O": [1, 0, 1, 0, 0, 0],
            "Letra - P": [0, 1, 1, 1, 1, 1],
            "Letra - Q": [1, 0, 0, 0, 0, 1],
            "Letra - R": [0, 1, 0, 0, 1, 0],
            "Letra - S": [1, 1, 1, 1, 1, 1],
            "Letra - T": [1, 1, 1, 1, 0, 1],
            "Letra - U": [0, 0, 1, 0, 0, 1],
            "Letra - V": [0, 1, 0, 0, 1, 1],
            "Letra - W": [0, 1, 0, 1, 1, 1],
            "Letra - X": [1, 0, 1, 1, 1, 1],
            "Letra - Y": [1, 1, 1, 0, 0, 0],
            "Letra - Z": [1, 0, 0, 1, 1, 0],
        }

    def detect_letter(self, dedos, frame):
        """Detectar letra basada en configuración de dedos"""
        font = self.get_font(150)  # Fuente más grande

        correct_color = (0, 255, 0)  # Verde
        incorrect_color = (250, 128, 114)  # Rojo
        color = incorrect_color
        letra_detectada = 'Identificando letra...'
>>>>>>> origin/main

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

<<<<<<< HEAD
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
=======
        return self.utils.draw_detection_box(frame, letra_detectada, color, font)

    def detect_j_movement(self, angulosid, dedos, frame, width, height):
        """Detectar letra J con movimiento"""
        pinky = angulosid[0:2]
        pinkY = sum(pinky)
        resta = pinkY - self.lectura_actual
        self.lectura_actual = pinkY

        if dedos == [0, 1, 0, 0, 1, 0] and abs(resta) > 30:
            font = self.get_font(70)  # Fuente más grande
            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(frame_pil)

            # Cuadro inferior central para J más grande
            rect_start = (int(width / 2) - 75, height - 120)
            rect_end = (int(width / 2) + 75, height)
            draw.rectangle([rect_start, rect_end], fill=(255, 255, 255))

            text_position = (int(width / 2) - 35, height - 100)
            draw.text(text_position, 'Letra - J', font=font, fill=(0, 0, 0, 255))
            frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
            print("Letra - J en movimiento")

        return frame

    def generate_video(self):
        """Generar stream de video para detección de letras"""
        with self.utils.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.75) as hands, \
                self.utils.mp_pose.Pose(min_detection_confidence=0.75) as pose:
            #  self.utils.mp_face_mesh.FaceMesh(min_detection_confidence=0.75) as face_mesh:

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                height, width, _ = frame.shape
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Procesar con MediaPipe
                results = hands.process(frame_rgb)
                pose_results = pose.process(frame_rgb)
                # face_mesh_results = face_mesh.process(frame_rgb)

                if results.multi_hand_landmarks:
                    angulosid = self.utils.obtener_angulos(results, width, height)
                    dedos = self.process_finger_angles(angulosid)

                    # Detectar letra J con movimiento
                    frame = self.detect_j_movement(angulosid, dedos, frame, width, height)

                    # Detectar otras letras
                    frame = self.detect_letter(dedos, frame)

                # Dibujar landmarks
                frame = self.utils.draw_landmarks(frame, results, pose_results, None)
>>>>>>> origin/main

                x1 = int(min(x_Coordinates) * width) - 10
                y1 = int(min(y_Coordinates) * height) - 10
                x2 = int(max(x_Coordinates) * width) + 10
                y2 = int(max(y_Coordinates) * height) + 10

<<<<<<< HEAD
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
=======
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
>>>>>>> origin/main
