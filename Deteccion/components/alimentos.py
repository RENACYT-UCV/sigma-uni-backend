import cv2
from .utils import BaseDetector


class AlimentosDetector(BaseDetector):
    """Detector de alimentos en lenguaje de señas"""
    
    def __init__(self):
        super().__init__()
        self.alimentos_config = {
            "Alimento - Cebolla": [0, 0, 0, 0, 0, 0],
            "Alimento - Ajo": [0, 0, 1, 1, 1, 1],
            "Alimento - Cereza": [1, 1, 1, 1, 1, 1],
            "Alimento - Uva": [0, 1, 0, 0, 1, 1],
            "Alimento - Manzana": [1, 1, 0, 0, 0, 1],
            "Alimento - Pan": [1, 0, 1, 1, 0, 1],
        }
    
    def detect_food(self, dedos, frame):
        """Detectar alimento basado en configuración de dedos"""
        font = self.get_font(60)  # Fuente grande para alimentos
        
        correct_color = (0, 255, 0)  # Verde
        incorrect_color = (250, 128, 114)  # Rojo
        color = incorrect_color
        alimento_detectado = 'Identificando alimento...'

        for alimento, config in self.alimentos_config.items():
            if dedos == config:
                color = correct_color
                alimento_detectado = alimento
                print(alimento)
                break

        return self.utils.draw_detection_box(frame, alimento_detectado, color, font)
    
    def generate_video(self):
        """Generar stream de video para detección de alimentos"""
        with self.utils.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.75) as hands, \
             self.utils.mp_pose.Pose(min_detection_confidence=0.75) as pose, \
             self.utils.mp_face_mesh.FaceMesh(min_detection_confidence=0.75) as face_mesh:
            
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
                face_mesh_results = face_mesh.process(frame_rgb)

                if results.multi_hand_landmarks:
                    angulosid = self.utils.obtener_angulos(results, width, height)
                    dedos = self.process_finger_angles(angulosid)
                    
                    # Detectar alimentos
                    frame = self.detect_food(dedos, frame)

                # Dibujar landmarks
                frame = self.utils.draw_landmarks(frame, results, pose_results, face_mesh_results)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
