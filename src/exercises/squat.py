from .base_exercise import BaseExercise

class Squat(BaseExercise):
    def __init__(self):
        super().__init__("Squat")
        self.state = "up"
        self.feedback = "Ready"
        self.angle_buffer = [] 
        self.buffer_limit = 5 

    def evaluate(self, landmarks, angles):
        knee_angle = angles["knee"]
        
        # NOISE FILTERING
        self.angle_buffer.append(knee_angle)
        if len(self.angle_buffer) > self.buffer_limit:
            self.angle_buffer.pop(0)
            
        is_gradual_up = all(x < y for x, y in zip(self.angle_buffer, self.angle_buffer[1:])) if len(self.angle_buffer) >= 3 else False

        # BOTTOM: Depth Check.
        if knee_angle < 120:
            self.state = "down"
            self.feedback = "Good Depth!"

        # TOP: Rep Completion.
        elif knee_angle > 160:
            if self.state == "down" and is_gradual_up:
                self.rep_count += 1
                self.state = "up" 
                self.feedback = "Great Rep!"
            elif self.state == "up":
                self.feedback = "Ready"
        else:
            if self.state == "up":
                self.feedback = "Lower your hips"
            else:
                self.feedback = "Good Form"