class BaseExercise:
    def __init__(self, name): 
        self.name = name
        self.rep_count = 0
        self.stage = "neutral"
        self.feedback = "Ready"
        self.form_score = 100

    def reset(self):
        self.rep_count = 0
        self.stage = "neutral"
        self.feedback = "Ready"
        self.form_score = 100