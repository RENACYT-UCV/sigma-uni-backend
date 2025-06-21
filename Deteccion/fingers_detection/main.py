import cv2
import time
import os
import hand_detection as htm

w_cam, h_cam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, w_cam)
cap.set(4, h_cam)

p_time = 0

detector = htm.handDetector(detectionCon=0.75)

tip_ids = [4, 8, 12, 16, 20]  # Index finger tip is at index 8

while True:
    success, img = cap.read()

    if not success:
        print("Error: Could not read frame.")
        break

    img = cv2.flip(img, 1)  # Flip the image horizontally

    img = detector.findHands(img)
    lm_list = detector.findPosition(img, draw=False)
    # print(lm_list)

    if len(lm_list) != 0:
        fingers = []

        if lm_list[tip_ids[0]][1] < lm_list[tip_ids[0] - 1][1]:  # Index finger tip is left of middle finger tip
            fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1, 5):
            # cv2.circle(img, (lm_list[tip_ids[id]][1], lm_list[tip_ids[id]][2]), 15, (255, 0, 255), cv2.FILLED)
            if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:  # Index finger tip is left of middle finger tip
                fingers.append(1)
            else:
                fingers.append(0)

        # print(fingers)
        total_fingers = fingers.count(1)
        # print(f'Total fingers: {total_fingers}')

        cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'Fingers:{total_fingers}', (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time

    cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Image', img)
    cv2.waitKey(1)
