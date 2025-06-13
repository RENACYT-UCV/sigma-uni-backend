import cv2
import numpy as np
from .utils import BaseDetector

class NumerosDetector(BaseDetector):
    """Detector de números en lenguaje de señas"""
    def __init__(self):
        super().__init__()
        self.numeros_config = {
            "Número - 0": [0, 0, 0, 0, 0, 0],
            "Número - 1": [1, 1, 0, 0, 0, 0],
            "Número - 2": [1, 1, 0, 0, 0, 1],
            "Número - 3": [1, 1, 0, 0, 1, 1],
            "Número - 4": [1, 1, 0, 1, 1, 1],
            "Número - 5": [1, 1, 1, 1, 1, 1],
            "Número - 6": [0, 1, 1, 1, 1, 0],
            "Número - 7": [0, 1, 0, 1, 1, 0],
            "Número - 8": [0, 1, 0, 0, 1, 0],
            "Número - 9": [0, 1, 0, 0, 0, 0],
        }

    def match_fingers(self, input_fingers, target_fingers, tolerance=1):
        return sum(abs(a - b) for a, b in zip(input_fingers, target_fingers)) <= tolerance

    def detect_number(self, dedos, frame):
        font = self.get_font(70)
        correct_color = (0, 255, 0)
        incorrect_color = (250, 128, 114)
        color = incorrect_color
        numero_detectado = 'Identificando número...'

        for numero, config in self.numeros_config.items():
            if self.match_fingers(dedos, config):
                color = correct_color
                numero_detectado = numero
                print(numero)
                break

        return self.utils.draw_detection_box(frame, numero_detectado, color, font)

    def generate_video(self):
        with self.utils.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.75
        ) as hands, \
        self.utils.mp_pose.Pose(min_detection_confidence=0.75) as pose, \
        self.utils.mp_face_mesh.FaceMesh(min_detection_confidence=0.75) as face_mesh:

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                height, width, _ = frame.shape
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = hands.process(frame_rgb)
                pose_results = pose.process(frame_rgb)
                face_mesh_results = face_mesh.process(frame_rgb)

                if results.multi_hand_landmarks:
                    angulosid = self.utils.obtener_angulos(results, width, height)
                    dedos = self.process_finger_angles(angulosid)
                    frame = self.detect_number(dedos, frame)
                    cv2.putText(frame, str(dedos), (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

                frame = self.utils.draw_landmarks(frame, results, pose_results, face_mesh_results)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')