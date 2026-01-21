from .base_exercise import BaseExercise

class BicepCurl(BaseExercise):
    def __init__(self):
        super().__init__("Bicep Curl")
        self.state = "down"
        self.feedback = "Ready"

    def evaluate(self, landmarks, angles):
        elbow_angle = angles["elbow"]
        # 11=Shoulder, 13=Elbow, 15=Wrist
        
        # ELBOW CHECK
        elbow_flare = abs(landmarks[11][1] - landmarks[13][1])
                
        # WRIST CHECK
        wrist_flare = abs(landmarks[11][1] - landmarks[15][1])

        if 60 < angles["elbow"] < 150:
            if wrist_flare > 0.20:
                self.feedback = "Don't flare wrists"
        
        # BOTTOM: Reset for a new rep.
        if elbow_angle > 155:
            self.state = "down"
            self.feedback = "Ready"

        # MIDDLE: Movement Feedback.
        elif 75 <= elbow_angle <= 155:
            if elbow_flare > 90:
                self.feedback = "Elbow to be tucked"
            else:
                self.feedback = "Good Form"

        # TOP: Rep Completion.
        if elbow_angle < 150:
            if elbow_angle < 50:
                if self.state == "down":
                    self.rep_count += 1
                    self.state = "up" 
                self.feedback = "Great Rep!"
            else:
                self.feedback = "Rise higher"