import math
import numpy as np

def calculate_angle(p1, p2, p3):
    x1, y1 = p1[1], p1[2]
    x2, y2 = p2[1], p2[2]
    x3, y3 = p3[1], p3[2]

def calculate_angle(a, b, c):
    # Calculate the angle at point b given points a, b, and c.
    a = np.array([a[1], a[2]]) 
    b = np.array([b[1], b[2]]) 
    c = np.array([c[1], c[2]]) 

    # Calculate vectors
    ba = a - b
    bc = c - b

    # Calculate cosine of the angle using dot product
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    return np.degrees(angle)

def smooth_value(current_val, previous_val, alpha=0.2):
    if previous_val is None:
        return current_val
    return alpha * current_val + (1 - alpha) * previous_val