# emotion_demo_webcam.py

# Webcam enabled emotion recognition only demo using FER for RS2 Lecture Robots for Good.
# https://github.com/justinshenk/fer/tree/master for fer information.
########### Instructions ##############
# See Github for more: to fill in.....
# Make sure you are using versions stated in requirements.txt
# Run Command: python scripts/emotion_demo_webcam.py
# Webcam will open and emotions will be recognised. Press Q to quit the webcam feed.
# Press SPACE to lock in the latest valid detected emotion.
# The results & robot response will print to terminal.

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" # hiding tensor warnings

import warnings
# hiding another warning from keras
warnings.filterwarnings(
    "ignore",
    message="The structure of `inputs` doesn't match the expected structure."
)

import time
import random
from typing import Optional

import cv2
from fer import FER

CAMERA_INDEX = 0 # if errors can change to 1 or 2, 0 is usually built-in webcam

# You can add more lines of dialogue here, it will randomly choose 1 depending on the emotion
ROBOT_DIALOGUE = {
    "angry": [
        "I think you might be feeling angry.",
        "You seem angry, I will give you some space."
    ],
    "disgust": [
        "You seem uncomfortable.",
        "I will stay calm and give you a moment."
    ],
    "fear": [
        "You look worried. Are you okay?",
        "Do not worry. I am here with you."
    ],
    "happy": [
        "You seem happy today!",
        "It is nice to see you smiling."
    ],
    "sad": [
        "You seem a little sad, do you want to talk?",
        "Oh you look sad, would you like some support?"
    ],
    "surprise": [
        "Oh, you look surprised!",
        "Something seems to have caught your attention."
    ],
    "neutral": [
        "You seem calm.",
        "I am ready when you are."
    ],
}


def pick_robot_line(emotion: str) -> str:
    lines = ROBOT_DIALOGUE.get(emotion, ["I noticed an emotion."])
    return random.choice(lines)


def draw_status_text(
    frame,
    latest_emotion: Optional[str],
    latest_score: Optional[float]
) -> None:
    instruction = "SPACE = accept latest emotion | Q = quit"
    cv2.putText(
        frame,
        instruction,
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )

    if latest_emotion is not None and latest_score is not None:
        text = f"Latest valid emotion: {latest_emotion} ({latest_score:.2f})"
    else:
        text = "Latest valid emotion: none yet"

    cv2.putText(
        frame,
        text,
        (10, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )


def main():
    detector = FER(mtcnn=False) # if you wanted a better face detector instead of opencv
    cap = cv2.VideoCapture(CAMERA_INDEX) 

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    latest_valid_emotion: Optional[str] = None
    latest_valid_score: Optional[float] = None
    min_confidence = 0.40

    print("\n" + "=" * 40)
    print("Webcam started.")
    print("Show a facial expression to the camera.")
    print("Press SPACE to accept the latest valid detected emotion.")
    print("Press Q to quit.")
    print("=" * 40 + "\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Warning: Could not read frame from webcam.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.detect_emotions(rgb_frame)

        if results:
            # Use the first detected face
            result = results[0]
            x, y, w, h = result["box"]
            emotions = result["emotions"]

            top_emotion = max(emotions, key=emotions.get)
            top_score = emotions[top_emotion]

            # Draw box around detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Show current frame prediction
            cv2.putText(
                frame,
                f"{top_emotion} ({top_score:.2f})",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2,
                cv2.LINE_AA
            )

            # Save latest valid emotion only if confidence is above threshold
            if top_score >= min_confidence:
                latest_valid_emotion = top_emotion
                latest_valid_score = top_score

        draw_status_text(frame, latest_valid_emotion, latest_valid_score)
        cv2.imshow("Emotion Demo", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Quit requested.")
            break

        elif key == 32:  # SPACE
            if latest_valid_emotion is None:
                print("No valid emotion detected yet. Try again.")
                continue

            print("\n" + "=" * 40)
            print("Emotion locked in:")
            print(f"  emotion: {latest_valid_emotion}")
            print(f"  score:   {latest_valid_score:.2f}")
            print("\n")

            robot_line = pick_robot_line(latest_valid_emotion)
            print(f"Robot says: {robot_line}")
            print("\n")
            print("Waiting 2 seconds...")
            print("=" * 40 + "\n")
            time.sleep(2)
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
