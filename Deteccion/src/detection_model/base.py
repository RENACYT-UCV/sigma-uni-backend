import cv2
import mediapipe as mp
import numpy as np
from math import degrees, acos


class BaseDetector:
    """Clase base para detectores de lenguaje de señas"""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def draw_landmarks(self, frame, results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )

        return frame

    def draw_detection_box(self, frame, *, text, color, font):
        height, width,  _ = frame.shape
        # frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # draw = ImageDraw.Draw(frame_pil)

        rect_width = 600
        rect_height = 120
        rect_start = (int((width - rect_width) / 2), height - rect_height)
        rect_end = (int((width + rect_width) / 2), height)
        # draw.rectangle([rect_start, rect_end], fill=color, outline=(255, 255, 255), width=5)

        cv2.rectangle(frame, rect_start, rect_end, color, thickness=cv2.FILLED)
        cv2.putText(frame, text, (rect_start[0] + 20, rect_start[1] + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5)

        # draw.text(text_position, text, font=f..ont, fill=(0, 0, 0, 255))  # Texto

        # frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

        return frame

    def get_finger_angles(self, result, width, height):
        finger_angles = []

        coords = {
            "pinky": [(self.mp_hands.HandLandmark.PINKY_TIP, self.mp_hands.HandLandmark.PINKY_PIP, self.mp_hands.HandLandmark.PINKY_MCP)],
            "ring": [(self.mp_hands.HandLandmark.RING_FINGER_TIP, self.mp_hands.HandLandmark.RING_FINGER_PIP, self.mp_hands.HandLandmark.RING_FINGER_MCP)],
            "middle": [(self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP, self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP)],
            "index": [(self.mp_hands.HandLandmark.INDEX_FINGER_TIP, self.mp_hands.HandLandmark.INDEX_FINGER_PIP, self.mp_hands.HandLandmark.INDEX_FINGER_MCP)],
            "thumb_outer": [(self.mp_hands.HandLandmark.THUMB_TIP, self.mp_hands.HandLandmark.THUMB_IP, self.mp_hands.HandLandmark.THUMB_MCP)],
            "thumb_inner": [(self.mp_hands.HandLandmark.THUMB_TIP, self.mp_hands.HandLandmark.THUMB_MCP, self.mp_hands.HandLandmark.WRIST)]
        }

        for hand_landmarks in result.multi_hand_landmarks:
            for _, value in coords.items():
                x1, y1 = [int(hand_landmarks.landmark[value[0][0]].x * width), int(hand_landmarks.landmark[value[0][0]].y * height)]
                x2, y2 = [int(hand_landmarks.landmark[value[0][1]].x * width), int(hand_landmarks.landmark[value[0][1]].y * height)]
                x3, y3 = [int(hand_landmarks.landmark[value[0][2]].x * width), int(hand_landmarks.landmark[value[0][2]].y * height)]

                p1 = np.array([x1, y1])
                p2 = np.array([x2, y2])
                p3 = np.array([x3, y3])

                l1 = np.linalg.norm(p2 - p3)
                l2 = np.linalg.norm(p1 - p3)
                l3 = np.linalg.norm(p1 - p2)

                num_den = (l1**2 + l3**2 - l2**2) / (2 * l1 * l3)
                num_den = np.clip(num_den, -1.0, 1.0)
                angulo = degrees(acos(num_den))
                finger_angles.append(angulo)

        return finger_angles
