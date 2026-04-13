# Robotics Studio 2: Robot for Good Demo
  
## Overview
This project contains the demos for the Robotics Studio 2: Robots for Good Lecture. The first project is a simple web-cam based facial emotion recognition demo.  
  
The current demo uses:
  - python virtual environment
  - OpenCV for webcam access and display
  - FER for facial emotion recognition
  - Tensorflow as the model backend
  
The script opens the webcam, detects emotions from the user's face, and prints a simple hardcoded robot response based on the detected emotion.

Acknowledgement: This project uses the Python Package FER from https://github.com/justinshenk/fer.git , this is a keras model pretrained with FER2013 by Pierre Luc Carrier and Aaron Courville. This package also builds upon the work from https://github.com/oarriaga/face_classification .

## Current Emotions Supported:
- Angry
- Disgust (hard to get)
- Fear
- Happy
- Sad
- Surprise
- Neutral

  
## Project Structure:
```
RS2_Robots4Good/
├── r4g_env/ 
├── requirements.txt
├── LICENSE
├── README.md
├── scripts/
│   ├── test_imports.py
│   └── emotion_demo_webcam.py
└── worlds/
```
Notes: 
- r4g_env is a python virtual environment, you create your own locally.
- scripts/ contains the python demo scripts.
- emotion_demo_webcam.py is a standalone version you can run directly, no simulation included.
- worlds/ is for Gazebo world files.
  
## Setup Instructions:
### 1. Install system packages
  
On Ubuntu 22.04, make sure python venv support is installed
```
sudo apt update
sudo apt install python3.10-venv
```
### 2. Git Clone
Clone the repository to your local machine:
```
git clone https://github.com/Katie-Alice/RS2_Robots4Good.git
```
     
### 3. Go to the project folder & create virtual environment
```
cd ~/RS2_Robots4Good
python3 -m venv r4g_env #or any name you want instead
# Activate
source r4g_env/bin/activate
```
You should now see (r4g_env) at the start of your terminal prompt.

### 4. Install Python dependencies
```
python -m pip install --upgrade pip wheel
python -m pip install -r requirements.txt
```

## Run Instructions:
For first time do all steps, otherwise skip to Step 3.
  
### 1. Activate the virtual environment
If not already done.
```
cd ~/robots4good
source r4g_env/bin/activate
```
  
### 2. Test the environment
Run the import test first:
```
python scripts/test_imports.py
```
If setup is correct, it should report everything was imported successfully and the fer detector was created successfully.
If not see troubleshooting below.
  
### 3. Run the webcam emotion demo
Once in your venv and project folder, run:
```
python scripts/emotion_demo_webcam.py
```
  
### 4. Controls
When the webcam window opens:
- make a facial expression for one of the emotions
- press SPACE to accept the latest detected emotion
- press Q to quit instead
  
### 5. Expected Behaviour
The demo should:
- open a webcam window
- detect a face
- show the current detected emotion on screen
- store the latest valid detected emotion with SPACE
- print a robot response
- wait 2 seconds and then close
  
### 6. Extra Notes
You can change the hardcoded responses from the robot in the code or add more as it will randomly choose 1 of the suitable options for the detected emotion.
  
You can also switch to MTCNN as a face detector instead of OpenCV but this is untested at this time.

## Troubleshooting
#### Webcam does not open
If the script cannot open the webcam, the camera index may be wrong. This can be changed at the top of the script: CAMERA_INDEX = 0   you can change to 1 or 2.
  
#### Face is detected poorly or emotion is unstable
Things that can help:
- use good lighting
- face the camera directly and be close enough
- have a plain or non-busy background
- hold the expression

#### Virtual environment could not be created
If you see an error about ensurepip or venv, install:
```
sudo apt update
sudo apt install python3.10-venv
```
Then recreate the environment.
  
#### ModuleNotFoundError: No module named 'pkg_resources'
This happens if setuptools is too new.
The project depends on:
```
setuptools<82
```
As shown in requirements.txt.
Do not upgrade setuptools beyond that version for this demo.
If needed, fix it with:
```
python -m pip install --force-reinstall "setuptools<82"
```
  
#### ModuleNotFoundError: No module named 'moviepy.editor'
This happens if MoviePy is too new.
The project depends on:
```
moviepy==1.0.3
```
As shown in requirements.txt.
Do not upgrade MoviePy unless the FER package is also updated accordingly.
```
python -m pip install --force-reinstall "moviepy==1.0.3"
```
  
#### ImportError: cannot import name 'FER' from 'fer'
This can happen with incompatible FER versions. We are using an older version than the latest due to compatibility issues, the version shown in requirements.txt is one we tested to work.
```
# If needed:
python -m pip install "fer==22.5.1"
```
  
#### OpenCV Issues
If the import_test.py comes back with errors and functions like VideoCapture, imshow, cvtColor, or data are missing, the OpenCV install may be broken. This can happen if leftover cv2 files remain after uninstalling/reinstalling OpenCV packages. A clean fix is:
```
python -m pip uninstall opencv-python opencv-contrib-python # these 2 can conflict
# make sure cv2 traces are gone
rm -rf ~/robots4good/r4g_env/lib/python3.10/site-packages/cv2
# reinstall
python -m pip install opencv-contrib-python==4.11.0.86
```
  
#### TensorFlow warnings about TensorRT or GPU libraries
These warnings can be ignored, within the code you will see code to suppress them. It just means TensorFlow is running on CPU instead of GPU.   
On CPU the demo may be slow, this is expected. TensorFlow-based emotion recognition may also take a moment to warm up the first time the script runs.
