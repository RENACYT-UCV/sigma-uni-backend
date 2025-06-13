import cv2
import mediapipe as mp
import numpy as np
from math import degrees, acos
from PIL import ImageFont, ImageDraw, Image

class MediaPipeUtils:
    """Utilidades compartidas para MediaPipe"""
    
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def obtener_angulos(self, results, width, height):
        """Función para obtener los ángulos de las articulaciones de los dedos"""
        angulos_dedos = []
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
                angulos_dedos.append(angulo)

        return angulos_dedos
    
    def draw_detection_box(self, frame, text, color, font):
        """Función compartida para dibujar el cuadro de detección"""
        height, width, _ = frame.shape
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(frame_pil)

        # Dibujar el rectángulo central inferior más grande
        rect_width = 600  # Aumentado de 500 a 600
        rect_height = 120  # Aumentado de 100 a 120
        rect_start = (int((width - rect_width) / 2), height - rect_height)
        rect_end = (int((width + rect_width) / 2), height)
        draw.rectangle([rect_start, rect_end], fill=color, outline=(255, 255, 255), width=5)

        # Dibujar borde alrededor del texto
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_position = (int((width - text_width) / 2), height - rect_height + int((rect_height - text_height) / 2))
        border_color = (255, 255, 255)  # blanco
        offsets = [(-2, -2), (2, -2), (-2, 2), (2, 2)]  # Borde más grueso
        for offset in offsets:
            draw.text((text_position[0] + offset[0], text_position[1] + offset[1]), text, font=font, fill=border_color)

        # Dibujar texto
        draw.text(text_position, text, font=font, fill=(0, 0, 0, 255))  # Texto negro para mejor contraste

        frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
        return frame
    
    def draw_landmarks(self, frame, results, pose_results, face_mesh_results):
        """Dibujar todos los landmarks en el frame"""
        # Dibujar landmarks de manos
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())

        # Dibujar landmarks de pose
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                pose_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))

        # Dibujar face mesh
        if face_mesh_results.multi_face_landmarks:
            for face_landmarks in face_mesh_results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(frame, face_landmarks, self.mp_face_mesh.FACEMESH_TESSELATION, 
                                             self.mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=1, circle_radius=1))
        
        return frame

class BaseDetector:
    """Clase base para todos los detectores"""
    
    def __init__(self):
        self.utils = MediaPipeUtils()
        self.cap = None
        self.lectura_actual = 0
        self.setup_camera()
    
    def setup_camera(self):
        """Configurar la cámara"""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)  # wCam
        self.cap.set(4, 720)   # hCam
    
    def get_font(self, size=60):  # Aumentar tamaño por defecto de 50 a 60
        """Obtener fuente para el texto"""
        try:
            return ImageFont.truetype("DINRoundPro.ttf", size)  # Buscar en directorio raíz
        except IOError:
            try:
                return ImageFont.truetype("./DINRoundPro.ttf", size)  # Ruta alternativa
            except IOError:
                return ImageFont.load_default()
    
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
