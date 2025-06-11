import cv2
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
import time
import mediapipe as mp
import speech_recognition as sr

# Initialize Speech Recognition
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen_for_command():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙️ Listening for voice command...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            command = recognizer.recognize_google(audio)
            print("🎧 You said:", command)
            return command.lower()
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            print("❌ Could not understand or timed out")
        except sr.RequestError as e:
            print("⚠️ Could not request results; {0}".format(e))
    return ""  # Always return something

# Initialize Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

cv2.namedWindow("Gesture + Eye Controller")

# GUI Mic Button
mic_enabled = True
mic_button_rect = (10, 10, 120, 40)  # x, y, width, height

def mouse_callback(event, x, y, flags, param):
    global mic_enabled
    if event == cv2.EVENT_LBUTTONDOWN:
        x1, y1, w, h = mic_button_rect
        if x1 <= x <= x1 + w and y1 <= y <= y1 + h:
            mic_enabled = not mic_enabled
            print(f"🎤 Voice command {'enabled' if mic_enabled else 'disabled'}")

cv2.setMouseCallback("Gesture + Eye Controller", mouse_callback)

# Initialize Hand Detector
detector = HandDetector(detectionCon=0.7, maxHands=2)

# Initialize Keyboard and Mouse Controller
keyboard = KeyboardController()
mouse = MouseController()
pressed_keys = set()
controller_active = True
last_toggle_time = time.time()
last_voice_check = time.time()

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

# Key Mappings
left_hand_controls = {
    (0, 1, 1, 0, 0): 'w',
    (1, 0, 0, 0, 0): 'a',
    (0, 0, 0, 0, 1): 'p',
    (0, 1, 1, 1, 1): 'a',
    (0, 0, 1, 1, 1): 'v',
}

right_hand_controls = {
    (0, 1, 1, 0, 0): 's',
    (1, 0, 0, 0, 0): 'd',
    (0, 0, 0, 0, 1): 'c',
    (0, 1, 1, 1, 1): 'r',
    (0, 0, 1, 1, 1): '2',
}

toggle_gesture = (1, 1, 1, 1, 1)

def get_eye_direction(landmarks):
    left_eye_outer = landmarks[33]
    right_eye_outer = landmarks[362]
    nose_tip = landmarks[1]
    eye_center_x = (left_eye_outer.x + right_eye_outer.x) / 2

    if eye_center_x < 0.4:
        return "left"
    elif eye_center_x > 0.6:
        return "right"
    elif nose_tip.y < 0.4:
        return "up"
    else:
        return "center"

# Main Loop
while True:
    success, img = cap.read()
    current_pressed_keys = set()
    hands, img = detector.findHands(img)

    # Process face mesh for eye tracking
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_img)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            direction = get_eye_direction(face_landmarks.landmark)
            if controller_active:
                if direction == "left":
                    keyboard.press('q')
                    current_pressed_keys.add('q')
                elif direction == "right":
                    keyboard.press('e')
                    current_pressed_keys.add('e')
                elif direction == "up":
                    keyboard.press(Key.space)
                    current_pressed_keys.add(Key.space)

    if hands:
        for hand in hands:
            hand_type = hand["type"]
            finger_state = tuple(detector.fingersUp(hand))

            if finger_state == toggle_gesture:
                if time.time() - last_toggle_time > 1:
                    controller_active = not controller_active
                    print(f"🟢 Controller {'Activated' if controller_active else 'Deactivated'} 🛑")
                    last_toggle_time = time.time()
                continue

            if controller_active:
                controls = left_hand_controls if hand_type == "Left" else right_hand_controls
                if finger_state in controls:
                    key = controls[finger_state]
                    keyboard.press(key)
                    current_pressed_keys.add(key)

                if hand_type == "Right":
                    lmList = hand["lmList"]
                    if len(lmList) > 8:
                        index_finger = lmList[8][:2]
                        screen_w, screen_h = 1920, 1080
                        mouse_x = int((index_finger[0] / 640) * screen_w)
                        mouse_y = int((index_finger[1] / 480) * screen_h)
                        mouse.position = (mouse_x, mouse_y)

                    if finger_state == (0, 1, 0, 0, 0):
                        mouse.click(Button.left, 1)
                    elif finger_state == (0, 1, 1, 0, 0):
                        mouse.click(Button.right, 1)
                    elif finger_state == (0, 1, 1, 1, 1):
                        mouse.scroll(0, 1)  
                    elif finger_state == (0, 0, 0, 1, 1):
                        mouse.scroll(0, -1)

    # Voice command every 2 seconds if enabled
    if mic_enabled and time.time() - last_voice_check > 2:
        last_voice_check = time.time()
        command = listen_for_command()

        if "jump" in command:
            keyboard.press(Key.space)
            keyboard.release(Key.space)
        elif "left" in command:
            keyboard.press('a')
            keyboard.release('a')
        elif "right" in command:
            keyboard.press('d')
            keyboard.release('d')
        elif "shoot" in command:
            keyboard.press('c')
            keyboard.release('c')
        elif "forward" in command:
            keyboard.press('w')
            time.sleep(5)
            keyboard.release('w')
        elif "stop" in command:
            keyboard.press('s')
            keyboard.release('s')
        elif "activate" in command:
            mic_enabled = True
            print("🎤 Voice command re-enabled.")
        elif "deactivate" in command:
            mic_enabled = False
            print("🎤 Voice command disabled.")

    # Release unpressed keys
    for key in pressed_keys - current_pressed_keys:
        keyboard.release(key)

    pressed_keys = current_pressed_keys

    # Draw Mic Toggle Button
    button_color = (0, 255, 0) if mic_enabled else (0, 0, 255)
    cv2.rectangle(img, mic_button_rect[:2],
                  (mic_button_rect[0] + mic_button_rect[2], mic_button_rect[1] + mic_button_rect[3]),
                  button_color, -1)
    cv2.putText(img, "Mic: ON" if mic_enabled else "Mic: OFF",
                (mic_button_rect[0] + 10, mic_button_rect[1] + 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show Frame
    small_img = cv2.resize(img, (720, 480))
    cv2.imshow("Gesture + Eye Controller", small_img)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()