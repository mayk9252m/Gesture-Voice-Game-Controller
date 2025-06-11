# Gesture-Voice-Game-Controller
A multimodal game controller using hand gestures, eye tracking, and voice commands built with OpenCV, MediaPipe, cvzone, and speech recognition.

# Gesture + Eye + Voice Game Controller 🎮🖐️👁️🗣️

A multimodal game controller that enables users to control games using:
- **Hand gestures**
- **Eye movements**
- **Voice commands**

Built using `OpenCV`, `MediaPipe`, `cvzone`, and `speech_recognition` in Python.

## 🚀 Features

- 🤚 **Hand Gesture Recognition** to map specific finger states to keyboard inputs.
- 👁️ **Eye Tracking** to detect left, right, and upward gaze and simulate key presses.
- 🎙️ **Voice Command Interface** with a mic toggle to control the game via spoken instructions.
- 🖱️ **Mouse control** with hand tracking including click and scroll gestures.

## 🧠 Technologies Used

- Python
- OpenCV
- MediaPipe
- cvzone
- pynput
- SpeechRecognition (Google API)

## 🎮 Key Controls

| Input Type | Action         | Command/Gesture      |
|------------|----------------|----------------------|
| Voice      | Jump           | "jump"               |
| Voice      | Move Left      | "left"               |
| Voice      | Move Right     | "right"              |
| Voice      | Shoot          | "shoot"              |
| Voice      | Forward (5s)   | "forward"            |
| Eye        | Jump           | Look up              |
| Eye        | Move Left/Right| Look left/right      |
| Gesture    | Custom Mapping | Based on finger pose |

## 📷 UI Preview

The UI includes:
- Webcam feed with gesture overlay
- Mic toggle button (on/off)

## 🛠️ Installation

1. Clone the repository:
   ```bash
   https://github.com/mayk9252m/Gesture-Voice-Game-Controller.git
   cd Gesture-Voice-Game-Controller

# Install dependencies:
pip install opencv-python cvzone mediapipe pynput SpeechRecognition

# Run the application:
python "Game Controller.py"
