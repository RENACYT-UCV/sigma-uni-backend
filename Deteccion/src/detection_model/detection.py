import cv2

from .base import BaseDetector


class Dectector:
    """Clase para manejar la detección de lenguaje de señas"""

    w_camera = 1280
    h_camera = 720

    hands = None

    def __init__(self):
        self.base = BaseDetector()
        self.cap = None
        self.setup_camera()

        self.hands = self.base.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.75
        )

    def setup_camera(self):
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.w_camera)
            self.cap.set(4, self.h_camera)

        # pass

    def process_finger_angles(self, angulosid):
        """Procesar ángulos para determinar estado de dedos"""
        dedos = []

        if angulosid[5] > 125:
            dedos.append(1)
        else:
            dedos.append(0)

        if angulosid[4] > 150:
            dedos.append(1)
        else:
            dedos.append(0)

        for id in range(4):
            if angulosid[id] > 90:
                dedos.append(1)
            else:
                dedos.append(0)

        return dedos
