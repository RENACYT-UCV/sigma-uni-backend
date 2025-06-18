import cv2
import mediapipe as mp


class BaseDetector:
    """Clase base para detectores de lenguaje de señas"""

    def __init__(self):
        self.mp_hands = mp.solutions.hands

    # def


class Dectector:
    """Clase para manejar la detección de lenguaje de señas"""

    w_camera = 1280
    h_camera = 720

    def __init__(self):
        self.detector = BaseDetector()
        self.cap = None
        self.setup_camera()

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.w_camera)
        self.cap.set(4, self.h_camera)

    # def generate_video(self):
    #     """Generar stream de video para detección"""
    #     with self.detector.mp_hands.Hands(
    #         static_image_mode=False,
    #         max_num_hands=1,
    #         min_detection_confidence=0.75
    #     ) as hands:
    #         while True:
    #             ret, frame = self.cap.read()
    #             if not ret:
    #                 break

    #             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #             results = hands.process(frame_rgb)

    #             if results.multi_hand_landmarks:
    #                 for hand_landmarks in results.multi_hand_landmarks:
    #                     # Aquí se pueden procesar los landmarks detectados
    #                     pass

    #             cv2.imshow('Detección de Lenguaje de Señas', frame)
    #             if cv2.waitKey(5) & 0xFF == 27:  # Presionar 'Esc' para salir
    #                 break

    #     self.cap.release()
    #     cv2.destroyAllWindows()
