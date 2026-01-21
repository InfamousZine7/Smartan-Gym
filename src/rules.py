import time
import numpy as np
from src.utils import calculate_angle
from src.exercises.bicep_curl import BicepCurl
from src.exercises.tricep_pushdown import TricepPushdown
from src.exercises.squat import Squat
from src.exercises.lateral_raise import LateralRaise
from src.exercises.shoulder_press import ShoulderPress
from src.exercises.lat_pulldown import LatPulldown

class Evaluator:
    def __init__(self):
        self.exercise_modules = {
            "Bicep Curl": BicepCurl(),
            "Tricep Pushdown": TricepPushdown(),
            "Squat": Squat(),
            "Lateral Raise": LateralRaise(),
            "Shoulder Press": ShoulderPress(),
            "Lat Pulldown": LatPulldown()
        }
        
        self.smooth_angles = {"elbow": [], "shoulder": [], "knee": [], "hip": []}
        self.history = {"elbow": [], "shoulder": [], "knee": [], "hip": []}
        self.coord_history = [] 
        self.window_size = 15 
        self.buffer_size = 5
        
        self.posture = "Scanning..." 
        self.prev_posture = None
        self.posture_start_time = None
        self.identification_delay = 1.2 

        # Idle Detection
        self.idle_start_time = None
        self.is_idle = True
        self.idle_threshold = 4.0 
        
        self.current_exercise = None
        self.is_locked = False
        self.rep_count = 0
        self.feedback = "Ready"
        self.form_score = 100
        
        self.reset_evaluator()

    def _get_smooth_val(self, key, val):
        self.smooth_angles[key].append(val)
        if len(self.smooth_angles[key]) > self.buffer_size:
            self.smooth_angles[key].pop(0)
        return np.median(self.smooth_angles[key])

    def _get_linear_displacement(self, angle_list):
        if len(angle_list) < self.window_size: return 0
        start_avg = np.mean(angle_list[:3])
        end_avg = np.mean(angle_list[-3:])
        return abs(end_avg - start_avg)

    def get_variance(self, angle_list):
        if len(angle_list) < 5: return 99 
        return max(angle_list) - min(angle_list)

    def evaluate(self, landmarks):
        self.coord_history.append(landmarks)
        if len(self.coord_history) > self.window_size:
            self.coord_history.pop(0)

        # CaAPTURE & SMOOTH ANGLES
        raw_e = calculate_angle(landmarks[11], landmarks[13], landmarks[15])
        raw_s = calculate_angle(landmarks[23], landmarks[11], landmarks[13])
        raw_k = calculate_angle(landmarks[23], landmarks[25], landmarks[27])
        raw_h = calculate_angle(landmarks[11], landmarks[23], landmarks[25])
        
        angles = {
            "elbow": self._get_smooth_val("elbow", raw_e),
            "shoulder": self._get_smooth_val("shoulder", raw_s),
            "knee": self._get_smooth_val("knee", raw_k),
            "hip": self._get_smooth_val("hip", raw_h)
        }
        
        for key in ["elbow", "shoulder", "knee", "hip"]:
            self.history[key].append(angles[key])
            if len(self.history[key]) > self.window_size: 
                self.history[key].pop(0)

        # IDLE DETECTION LOGIC ---
        v_e = self.get_variance(self.history["elbow"])
        v_s = self.get_variance(self.history["shoulder"])
        v_k = self.get_variance(self.history["knee"])
        current_movement = max(v_e, v_s, v_k)

        if current_movement < self.idle_threshold:
            if self.idle_start_time is None:
                self.idle_start_time = time.time()
            idle_duration = time.time() - self.idle_start_time
            if idle_duration > 2.0:
                self.is_idle = True
                if not self.is_locked:
                    self.feedback = f"Idle ({int(idle_duration)}s)"
        else:
            self.is_idle = False
            self.idle_start_time = None

        # POSTURE DETECTION
        dx = abs(landmarks[11][1] - landmarks[23][1])
        dy = abs(landmarks[11][2] - landmarks[23][2])

        if dy > (dx * 1.1):
            current_p = "Sitting" if angles["hip"] < 155 else "Standing"
        else:
            current_p = "Sitting" 

        if current_p != self.prev_posture:
            self.posture = current_p
            self.prev_posture = current_p
            self.posture_start_time = time.time()
        time_held = time.time() - self.posture_start_time if self.posture_start_time else 0

        # IDENTIFICATION HIERARCHY
        if not self.is_locked and not self.is_idle and time_held > self.identification_delay:
            lin_e = self._get_linear_displacement(self.history["elbow"])
            lin_s = self._get_linear_displacement(self.history["shoulder"])
            lin_k = self._get_linear_displacement(self.history["knee"])

            # 1. Squat
            if lin_k > 12.0:
                self.current_exercise = "Squat"
                self.is_locked = True

            # 2. Sitting (Shoulder Press / Lat Pulldown)
            elif not self.is_locked and self.posture == "Sitting" and lin_s > 8.0:
                s_angle_start = np.mean(self.history["shoulder"][:3])
                s_angle_end = np.mean(self.history["shoulder"][-3:])
                self.current_exercise = "Shoulder Press" if s_angle_end > (s_angle_start + 5.0) else "Lat Pulldown"
                self.is_locked = True

            # 3. Isolations (Bicep/Tricep)
            elif not self.is_locked and lin_e > 10.0 and lin_s < 7.0:
                e_angle_start = np.mean(self.history["elbow"][:3])
                e_angle_end = np.mean(self.history["elbow"][-3:])
                is_opening = e_angle_end > (e_angle_start + 5.0)

                if is_opening:
                    self.current_exercise = "Tricep Pushdown"
                else:
                    self.current_exercise = "Bicep Curl"
                self.is_locked = True
                        
            # 4. Lateral Raise
            elif lin_s > 10.0 and lin_e < 5.0:
                self.current_exercise = "Lateral Raise"
                self.is_locked = True

            if self.is_locked:
                self.history = {k: [] for k in self.history}
                self.smooth_angles = {k: [] for k in self.smooth_angles}

        #Hand-off
        if self.is_locked:
            module = self.exercise_modules[self.current_exercise]
            module.evaluate(landmarks, angles)
            self.rep_count = module.rep_count
            self.feedback = module.feedback
            self.form_score = module.form_score

    def reset_evaluator(self):
        self.current_exercise = None
        self.is_locked = False
        self.is_idle = True
        self.idle_start_time = None
        self.rep_count = 0
        self.posture_start_time = None
        self.prev_posture = None
        self.feedback = "Scanning..."
        self.posture = "Scanning..."
        self.form_score = 100
        self.coord_history = []
        for ex in self.exercise_modules.values():
            ex.reset()