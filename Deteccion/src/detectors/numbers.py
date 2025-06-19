import cv2

from detection_model.detection import Dectector


class NumberDection:
    """Detector de números en lenguaje de señas"""

    __config_finger_numbers = {
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
                # print(numero)
                break

        return self.detector.base.draw_detection_box(frame, text=identification_number, color=color, font=70)

    def generate_video(self):
        while True:
            ret, frame = self.detector.cap.read()
            if not ret:
                break

            height, width, _ = frame.shape
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = self.detector.hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                angles_id = self.detector.base.get_finger_angles(results, width, height)
                fingers = self.detector.process_finger_angles(angles_id)
                frame = self.detect_number(fingers, frame)
                cv2.putText(frame, "Detectando...", (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            #     for hand_landmarks in results.multi_hand_landmarks:
            #         fingers = self.detector.get_finger_positions(hand_landmarks)
            # frame = self.detect_number(fingers, frame)

            frame = self.detector.base.draw_landmarks(frame, results)
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
