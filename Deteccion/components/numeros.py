import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

class NumerosDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False,
                                        max_num_hands=1,
                                        min_detection_confidence=0.7,
                                        min_tracking_confidence=0.5)
        self.mpDraw = mp.solutions.drawing_utils

        # Cargar el modelo entrenado
        self.model = load_model("modelo_senas.h5")

        self.labels = [str(i) for i in range(10)]

        # Para estabilidad en predicción
        self.prediction_counter = 0
        self.last_prediction = ""
        self.threshold = 10

    def generate_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            numero_actual = ""
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(frame, handLms, self.mpHands.HAND_CONNECTIONS)
                    
                    # Extraer características
                    datos = []
                    for lm in handLms.landmark:
                        datos.extend([lm.x, lm.y, lm.z])
                    if len(datos) == 63:
                        datos_np = np.array(datos).reshape(1, -1)
                        prediction = self.model.predict(datos_np)
                        prediccion_index = np.argmax(prediction)
                        numero_actual = self.labels[prediccion_index]

            # Control de estabilidad
            if numero_actual == self.last_prediction:
                self.prediction_counter += 1
            else:
                self.prediction_counter = 0
                self.last_prediction = numero_actual

            if self.prediction_counter >= self.threshold and numero_actual != "":
                cv2.putText(frame, f"Número: {numero_actual}", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 4)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
