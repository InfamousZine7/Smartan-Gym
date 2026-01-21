import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

class PoseDetector:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(os.path.dirname(current_dir), 'pose_landmarker_heavy.task')
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        
        # filtering out background figures
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.6,
            min_pose_presence_confidence=0.6,
            num_poses=3
        )
        
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.results = None

    def find_person(self, img, timestamp_ms):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        self.results = self.detector.detect_for_video(mp_image, timestamp_ms)
        return self.results

    def get_pivot_points(self, img):
        if not self.results or not self.results.pose_landmarks:
            return []

        h, w, _ = img.shape
        best_person_idx = -1
        max_area = 0

        # BACKGROUND FILTERING  
        for i, person in enumerate(self.results.pose_landmarks):
            x_coords = [lm.x for lm in person]
            y_coords = [lm.y for lm in person]
            
            # Calculate rough bounding box area
            area = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
 
            hip_visibility = person[23].presence 

            if area > max_area and hip_visibility > 0.5:
                max_area = area
                best_person_idx = i

        # If no prominent person found, return empty
        if best_person_idx == -1:
            return []

        # Process closest person
        landmarks_dict = {} 
        for idx, landmark in enumerate(self.results.pose_landmarks[best_person_idx]):
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            landmarks_dict[idx] = [idx, cx, cy]
        
        return landmarks_dict