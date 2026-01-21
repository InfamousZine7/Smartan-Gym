# Gym Assistant: Pose & Form Evaluation

A fitness tracker using MediaPipe and OpenCV to identify exercises, count repetitions accurately, and provide biomechanical form feedback.

## Project Structure

*   **main.py:** Core application loop handling video stream and UI.
*   **src/pose\_module.py:** Handles MediaPipe PoseLandmarker initialization and background person filtering.
*   **src/rules.py:** Contains the Evaluator class for exercise identification and posture logic.
*   **src/exercises/:** Modular classes for each exercise (Squat, Shoulder Press, etc.).
*   **src/utils.py:** Geometric helpers for calculating joint angles.
    

## Installation & Setup

1. Clone the repository.
2. Install requirments

```
pip install -r requirements.txt
```
    
3. Place **pose\_landmarker\_heavy.task** in the project root directory.
    
4.  Run
```
python main.py
```    

## Core Logic & Features

**Angle-Based Tracking**: Moves away from unstable pixel coordinates to pure joint angles (e.g., Elbow, Knee, Shoulder) for camera-agnostic tracking.
    
**Trend Smoothing**: Utilizes a 5-frame median filter and trend verification (is\_gradual\_up) to prevent sensor "noise" from double-counting reps.
    
**Identification Priority**: Specifically prioritizes lower-body movement to prevent Squats from being misidentified as upper-body exercises.