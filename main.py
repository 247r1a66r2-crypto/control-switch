import cv2
import mediapipe as mp
import serial
import time

# CHANGE COM PORT
arduino = serial.Serial('COM9', 9600)
time.sleep(2)

# Access MediaPipe solutions; some installs don't expose `mp.solutions`
try:
    mp_hands_module = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except Exception:
    from mediapipe.python import solutions as _mp_solutions
    mp_hands_module = _mp_solutions.hands
    mp_draw = _mp_solutions.drawing_utils

hands = mp_hands_module.Hands(max_num_hands=1)

cap = cv2.VideoCapture(0)

# 3 buttons layout
buttons = {
    "1": (80, 100, 260, 200),
    "2": (300, 100, 480, 200),
    "3": (520, 100, 700, 200)
}

cooldown = 1
last_click = time.time()

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Draw buttons
    for key, (x1, y1, x2, y2) in buttons.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, f"LED {key}", (x1+40, y1+60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            # Index finger tip
            x = int(handLms.landmark[8].x * frame.shape[1])
            y = int(handLms.landmark[8].y * frame.shape[0])

            cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

            for key, (x1, y1, x2, y2) in buttons.items():
                if x1 < x < x2 and y1 < y < y2:
                    if time.time() - last_click > cooldown:
                        arduino.write(key.encode())
                        print(f"LED {key} toggled")
                        last_click = time.time()

    cv2.imshow("Virtual 3-LED Switch", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
