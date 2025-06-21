import cv2
import mediapipe as mp


class HandDetection:
    def __init__(self, *,
                 mode=False,
                 max_hands=2,
                 detection_confidence=0.5,
                 tracking_confidence=0.5
                 ):
        self.results = None
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def find_hands(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(frame_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )

        return frame, self.results

    def find_position(self, frame, hand_no=0, draw=True):
        landmark_list = []
        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[hand_no]
            for id, landmark in enumerate(hand_landmarks.landmark):
                height, width, _ = frame.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                landmark_list.append([id, cx, cy])
                if draw:
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        return landmark_list
    
    def find_position_hand(self, frame, results, draw=True):
        hands_data = []

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label  # 'Left' or 'Right'
                landmark_list = []
                height, width, _ = frame.shape

                for id, landmark in enumerate(hand_landmarks.landmark):
                    cx, cy = int(landmark.x * width), int(landmark.y * height)
                    landmark_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

                hands_data.append((label, landmark_list))

        return hands_data
