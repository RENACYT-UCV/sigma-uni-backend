import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from .utils import BaseDetector


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

        for letra, config in self.letras_config.items():
            if dedos == config:
                color = correct_color
                letra_detectada = letra
                print(letra)
                break

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

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
