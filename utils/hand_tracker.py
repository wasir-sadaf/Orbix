import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_x_if_two_fingers(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return None

        lm = results.multi_hand_landmarks[0].landmark

        # Index & middle finger up check
        index_up = lm[8].y < lm[6].y
        middle_up = lm[12].y < lm[10].y

        if index_up and middle_up:
            # Flip X for correct screen movement
            x_avg = 1.0 - ((lm[8].x + lm[12].x) / 2)
            return int(x_avg * self.screen_width)

        return None