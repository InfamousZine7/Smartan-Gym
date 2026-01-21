from .base_exercise import BaseExercise

class LatPulldown(BaseExercise):
    def __init__(self):
        super().__init__("Lat Pulldown")
        self.state = "up"
        self.feedback = "Ready"

    def evaluate(self, landmarks, angles):
        elbow_angle = angles["elbow"]
        # 0=Nose, 11=Shoulder, 13=Elbow, 15=Wrist
        
        # 1. RANGE OF MOTION (Wrist & Nose)
        wrist_y = landmarks[15][2]
        nose_y = landmarks[0][2]
        is_pulled_low = wrist_y > (nose_y - 0.05)

        # TOP: Reset for a new rep.
        if elbow_angle > 150:
            self.state = "up"
            self.feedback = "Good Form"

        # BOTTOM: Rep Completion 
        if elbow_angle < 75:
            if is_pulled_low:
                if self.state == "up":
                    self.rep_count += 1
                    self.state = "down" 
                self.feedback = "Great Rep!"
            else:
                self.feedback = "Pull lower"