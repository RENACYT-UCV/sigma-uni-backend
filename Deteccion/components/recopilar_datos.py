import cv2
import mediapipe as mp
import csv
import os

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Crear carpeta si no existe
os.makedirs("datos", exist_ok=True)
csv_file = open("datos/datos_señas.csv", mode="a", newline='')
csv_writer = csv.writer(csv_file)

cap = cv2.VideoCapture(0)
print("Presiona una tecla del 0 al 9 para guardar datos, o ESC para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            key = cv2.waitKey(10) & 0xFF
            if key == 27:  # ESC
                cap.release()
                csv_file.close()
                cv2.destroyAllWindows()
                break
            elif 48 <= key <= 57:  # 0 al 9
                label = chr(key)
                fila = [label]
                for lm in hand_landmarks.landmark:
                    fila.extend([lm.x, lm.y, lm.z])
                csv_writer.writerow(fila)
                print(f"Guardado {label}")

    cv2.imshow("Recolector de datos", frame)
