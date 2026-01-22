from .base_exercise import BaseExercise

class TricepPushdown(BaseExercise):
    def __init__(self):
        super().__init__("Tricep Pushdown")
        self.state = "up"
        self.feedback = "Ready"
        self.angle_buffer = []
        self.buffer_limit = 5

    def evaluate(self, landmarks, angles):
        elbow_angle = angles["elbow"]
        
        # NOISE FILTERING
        self.angle_buffer.append(elbow_angle)
        if len(self.angle_buffer) > self.buffer_limit:
            self.angle_buffer.pop(0)
            
        is_extending = all(x < y for x, y in zip(self.angle_buffer, self.angle_buffer[1:])) if len(self.angle_buffer) >= 3 else False

        # TOP: Reset.
        if elbow_angle < 90:
            self.state = "down" 
            self.feedback = "Ready"

        # BOTTOM: Rep Completion.
        elif elbow_angle > 160:
            if self.state == "down" and is_extending:
                self.rep_count += 1
                self.state = "up" 
                self.feedback = "Great Rep!"
            elif self.state == "up":
                self.feedback = "Great Rep!"
        else:
            if self.state == "down":
                self.feedback = "Push all the way down"
            else:
                self.feedback = "Control the weight up"