from .base_exercise import BaseExercise

class LateralRaise(BaseExercise):
    def __init__(self):
        super().__init__("Lateral Raise")
        self.state = "down"
        self.feedback = "Ready"
        self.angle_buffer = []
        self.buffer_limit = 5

    def evaluate(self, landmarks, angles):
        shoulder_angle = angles["shoulder"]

        # NOISE FILTERING
        self.angle_buffer.append(shoulder_angle)
        if len(self.angle_buffer) > self.buffer_limit:
            self.angle_buffer.pop(0)

        is_gradual_up = all(x < y for x, y in zip(self.angle_buffer, self.angle_buffer[1:])) if len(self.angle_buffer) >= 3 else False
        
        # WRIST CHECK
        wrist_shoulder_dist = abs(landmarks[15][1] - landmarks[11][1])

        if 40 < angles["shoulder"] < 80:
            if wrist_shoulder_dist > 0.30: 
                self.feedback = "Keep wrists in line with shoulders"

        # BOTTOM: Reset state.
        if shoulder_angle < 30:
            self.state = "down"
            self.feedback = "Ready"

        # TOO HIGH
        elif shoulder_angle > 100:
            self.feedback = "Too high"
            
        # TOP: Rep Completion.
        elif 80 <= shoulder_angle <= 100:
            if self.state == "down" and is_gradual_up:
                self.rep_count += 1
                self.state = "up" 
                self.feedback = "Great Rep!"
            elif self.state == "up":
                self.feedback = "Great Rep!"
            else:
                self.feedback = "Hold at top"
        else:
            if self.state == "down":
                self.feedback = "Raise higher"
            else:
                self.feedback = "Good Form"