import cv2
from .utils import BaseDetector


class FrasesDetector(BaseDetector):
    """Detector de frases en lenguaje de señas"""

    def __init__(self):
        super().__init__()
        self.frases_config = {
            "Frase - Te amo": [1, 1, 1, 0, 0, 1],
            "Frase - Bueno": [0, 0, 1, 1, 1, 1],
            "Frase - HOLA": [1, 1, 1, 1, 1, 1],
            "Frase - Gracias": [0, 1, 1, 1, 1, 1],
            "Frase - Por favor": [0, 1, 0, 1, 0, 1],
            "Frase - Lo siento": [1, 0, 1, 0, 1, 0],
        }

    def detect_phrase(self, dedos, frame):
        """Detectar frase basada en configuración de dedos"""
        font = self.get_font(50)  # Fuente apropiada para frases

        color_correcto = (0, 255, 0)  # Verde
        color_incorrecto = (250, 128, 114)  # Rojo
        color = color_incorrecto
        frase_detectada = 'Identificando frase...'

        for frase, config in self.frases_config.items():
            if dedos == config:
                color = color_correcto
                frase_detectada = frase
                print(frase)
                break

        return self.utils.draw_detection_box(frame, frase_detectada, color, font)

    def generate_video(self):
        """Generar stream de video para detección de frases"""
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

                    # Detectar frases
                    frame = self.detect_phrase(dedos, frame)

                # Dibujar landmarks
                frame = self.utils.draw_landmarks(frame, results, pose_results)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
