from .base_exercise import BaseExercise

class ShoulderPress(BaseExercise):
    def __init__(self):
        super().__init__("Shoulder Press")
        self.state = "down" 
        self.feedback = "Ready"
        self.angle_buffer = []
        self.buffer_limit = 5

    def evaluate(self, landmarks, angles):
        elbow_angle = angles["elbow"]
        
        # NOISE FILTERING
        self.angle_buffer.append(elbow_angle)
        if len(self.angle_buffer) > self.buffer_limit:
            self.angle_buffer.pop(0)
            
        is_gradual_up = all(x < y for x, y in zip(self.angle_buffer, self.angle_buffer[1:])) if len(self.angle_buffer) >= 3 else False
        
        # WRIST CHECK
        wrist_elbow_dist = abs(landmarks[15][1] - landmarks[13][1])

        if 110 < angles["elbow"] < 155:
            if wrist_elbow_dist > 0.25:
                self.feedback = "Keep wrists over elbows"
        
        # BOTTOM: Reset state.
        if elbow_angle < 105:
            self.state = "down"
            self.feedback = "Ready"

        # TOP: Rep Completion.
        elif elbow_angle > 165:
            if self.state == "down" and is_gradual_up:
                self.rep_count += 1
                self.state = "up" 
                self.feedback = "Great Rep!"
            elif self.state == "up":
                self.feedback = "Great Rep!"
        else:
            wrist_elbow_dist = abs(landmarks[15][1] - landmarks[13][1])
            if wrist_elbow_dist > 0.30: 
                self.feedback = "Keep wrists over elbows"
            else:
                self.feedback = "Good Form"