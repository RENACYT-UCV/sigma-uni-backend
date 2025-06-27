import cv2

from detection_model.detection import Dectector


class NumberDection:
    """Detector de números en lenguaje de señas"""

    __tip_ids = [4, 8, 12, 16, 20]  # Índices de las puntas de los dedos

    __config_finger_numbers = {
        "Número - 0": [0, 0, 0, 0, 0],
        "Número - 1": [0, 1, 0, 0, 0],
        "Número - 2": [0, 1, 1, 0, 0],
        "Número - 3": [1, 1, 1, 0, 0],
        "Número - 4": [0, 1, 1, 1, 1],
        "Número - 5": [1, 1, 1, 1, 1],
        "Número - 6": [0, 1, 1, 1, 0],
        "Número - 7": [0, 1, 1, 0, 1],
        "Número - 8": [0, 1, 0, 1, 1],
        "Número - 9": [0, 0, 1, 1, 1],
    }

    def __init__(self, detector: Dectector):
        if not detector or not isinstance(detector, Dectector):
            raise ValueError("A detector instance is required.")

        self.detector = detector

    def match_fingers(self, input_fingers, target_fingers, tolerance=1):
        return sum(abs(a - b) for a, b in zip(input_fingers, target_fingers)) <= tolerance

    def detect_number(self, dedos, frame):
        # font = self.get_font(70)
        correct_color = (0, 255, 0)
        incorrect_color = (250, 128, 114)
        color = incorrect_color
        identification_number = 'Identificando número...'

        for number, config in self.__config_finger_numbers.items():
            if self.match_fingers(dedos, config):
                color = correct_color
                identification_number = number
                break

        return self.detector.base.draw_detection_box(frame, text=identification_number, color=color, font=70)

    def generate_video(self):
        while True:
            ret, frame = self.detector.cap.read()
            if not ret:
                break

            height, _, _ = frame.shape
            frame = cv2.flip(frame, 1)

            frame, results = self.detector.hands.find_hands(frame)
            hands_info = self.detector.hands.find_position_hand(frame, results)

            for label, landmarks_list in hands_info:
                if len(landmarks_list) != 0:
                    fingers = []

                    is_finger_up =  landmarks_list[self.__tip_ids[0]][1] > landmarks_list[self.__tip_ids[0] - 1][1]

                    if label == "Right":
                        fingers.append(0 if is_finger_up else 1)
                    else:  # Left hand
                        fingers.append(1 if is_finger_up else 0)


                    for id in range(1, 5):
                        fingers.append(1 if landmarks_list[self.__tip_ids[id]][2] < landmarks_list[self.__tip_ids[id] - 2][2] else 0)

                    number_label = "Desconocido"
                    for key, pattern in self.__config_finger_numbers.items():
                        if pattern == fingers:
                            number_label = key
                            break

                    # Draw result on frame
                    frame = self.detector.base.draw_detection_box(
                        frame,
                        text=f'{number_label}',
                        color=(0, 255, 0),
                        font=30
                    )
                    cv2.putText(frame, number_label, (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
