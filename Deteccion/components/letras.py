import cv2
import mediapipe as mp
from .utils import BaseDetector  # ✅ Correcto


class LetrasDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mpHands = mp.solutions.hands
        self.last_prediction = None
        self.threshold = 10  # o el número que uses como umbral
        self.prediction_counter = 0  # inicializa el contador si lo usas

        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
            
            )
        self.mpDraw = mp.solutions.drawing_utils

    def reconocer_letra(self, landmarks):
        # Aquí deberías implementar tu lógica personalizada para detectar letras
        # Por ejemplo:
        if landmarks:
            # lógica de ejemplo
            return "A"
        return ""

    def generate_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            letra_actual = ""
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(frame, handLms, self.mpHands.HAND_CONNECTIONS)
                    letra_actual = self.reconocer_letra(handLms.landmark)

            # Control de estabilidad
            if letra_actual == self.last_prediction:
                self.prediction_counter += 1
            else:
                self.prediction_counter = 0
                self.last_prediction = letra_actual

            if self.prediction_counter >= self.threshold and letra_actual != "":
                cv2.putText(frame, f"Letra: {letra_actual}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
