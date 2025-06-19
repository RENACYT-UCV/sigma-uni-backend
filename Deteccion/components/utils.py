# utils.py
import cv2
import mediapipe as mp
import numpy as np
from math import degrees, acos
from PIL import ImageFont, ImageDraw, Image

class BaseDetector:
    def __init__(self):
        pass

    def generate_video(self):
        raise NotImplementedError("Debe implementar generate_video")

class MediaPipeUtils:
    def __init__(self):
        self.mp_hands = mp.solutions.hands

    def obtener_angulos(self, results, width, height):
        angulos_dedos = []
        if not results.multi_hand_landmarks:
            return []

        for hand_landmarks in results.multi_hand_landmarks:
            coords = {
                "pinky": [(self.mp_hands.HandLandmark.PINKY_TIP, self.mp_hands.HandLandmark.PINKY_PIP, self.mp_hands.HandLandmark.PINKY_MCP)],
                "ring": [(self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.RING_FINGER_PIP, self.mp_hands.HandLandmark.RING_FINGER_MCP)],
                "middle": [(self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP)],
                "index": [(self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.INDEX_FINGER_PIP, self.mp_hands.HandLandmark.INDEX_FINGER_MCP)],
                "thumb_outer": [(self.mp_hands.HandLandmark.THUMB_TIP, self.mp_hands.HandLandmark.THUMB_IP, self.mp_hands.HandLandmark.THUMB_MCP)],
                "thumb_inner": [(self.mp_hands.HandLandmark.THUMB_TIP, self.mp_hands.HandLandmark.THUMB_MCP, self.mp_hands.HandLandmark.WRIST)]
            }

            for key, value in coords.items():
                try:
                    x1, y1 = [int(hand_landmarks.landmark[value[0][0]].x * width), int(hand_landmarks.landmark[value[0][0]].y * height)]
                    x2, y2 = [int(hand_landmarks.landmark[value[0][1]].x * width), int(hand_landmarks.landmark[value[0][1]].y * height)]
                    x3, y3 = [int(hand_landmarks.landmark[value[0][2]].x * width), int(hand_landmarks.landmark[value[0][2]].y * height)]

                    p1 = np.array([x1, y1])
                    p2 = np.array([x2, y2])
                    p3 = np.array([x3, y3])

                    l1 = np.linalg.norm(p2 - p3)
                    l2 = np.linalg.norm(p1 - p3)
                    l3 = np.linalg.norm(p1 - p2)

                    cos_ang = (l1**2 + l3**2 - l2**2) / (2 * l1 * l3)
                    cos_ang = np.clip(cos_ang, -1.0, 1.0)
                    angulo = degrees(acos(cos_ang))
                    angulos_dedos.append(angulo)
                except:
                    angulos_dedos.append(0.0)

        return angulos_dedos
