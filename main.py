import cv2
import time
from src.pose_module import PoseDetector
from src.rules import Evaluator

def main():
    bench_press = "/Users/guest1/Documents/Smartan-Gym/data/bench press_2.mp4"
    lat_pulldown = "/Users/guest1/Documents/Smartan-Gym/data/lat pulldown_1.mp4"
    lateral_raise = "/Users/guest1/Documents/Smartan-Gym/data/lateral raise_10.mp4"
    squat = "/Users/guest1/Documents/Smartan-Gym/data/squat_15.mp4"
    shoulder_press = "/Users/guest1/Documents/Smartan-Gym/data/shoulder press_15.mp4"
    tricep_pushdown = "/Users/guest1/Documents/Smartan-Gym/data/tricep pushdown_1.mp4"
    bicep_curl = "/Users/guest1/Documents/Smartan-Gym/data/barbell biceps curl_1.mp4"
    test = "/Users/guest1/Documents/Smartan-Gym/test_data/biceps.mp4"
    
    cap = cv2.VideoCapture(test) 

    detector = PoseDetector()
    evaluator = Evaluator()
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = 0

    while cap.isOpened():
        success, img = cap.read()
        if not success: break

        # Timestamp for Video Mode
        timestamp_ms = int((frame_count / fps) * 1000)
        frame_count += 1

        # 1. Detect Person
        detector.find_person(img, timestamp_ms)

        # 2. Get landmarks of the closest person
        landmarks = detector.get_pivot_points(img)

        if landmarks:
            # 3. Run Exercise Logic
            evaluator.evaluate(landmarks)
            
            # Pairs of landmarks to connect
            connections = [
                (11, 13), (13, 15), (12, 14), (14, 16), # Arms
                (11, 12), (12, 24), (24, 23), (23, 11), # Torso
                (23, 25), (25, 27), (24, 26), (26, 28)  # Legs
            ]

            color = (0, 255, 0) if evaluator.form_score > 80 else (0, 0, 255)

            for p1, p2 in connections:
                if p1 in landmarks and p2 in landmarks:
                    pt1 = (landmarks[p1][1], landmarks[p1][2])
                    pt2 = (landmarks[p2][1], landmarks[p2][2])
                    
                    cv2.line(img, pt1, pt2, color, 3)
                    cv2.circle(img, pt1, 5, (255, 255, 255), -1)
                    cv2.circle(img, pt2, 5, (255, 255, 255), -1)

            # DASHBOARD
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (650, 250), (20, 20, 20), -1) 
            img = cv2.addWeighted(overlay, 0.75, img, 0.25, 0)

            # 1. Exercise Name
            cv2.putText(img, f"EXERCISE: {evaluator.current_exercise or 'Detecting...'}", (30, 60), 
                        cv2.FONT_HERSHEY_TRIPLEX, 1.3, (255, 255, 255), 2)
            
            # 2. Rep Counter 
            cv2.circle(img, (85, 160), 55, color, 4) 
            cv2.putText(img, f"{evaluator.rep_count}", (58, 180), 
                        cv2.FONT_HERSHEY_TRIPLEX, 1.8, (255, 255, 255), 3)
            
            # 3. Form Feedback
            cv2.putText(img, f"FORM: {evaluator.feedback}", (170, 150), 
                        cv2.FONT_HERSHEY_TRIPLEX, 1.0, color, 2)
            
            # 4. Posture Info
            cv2.putText(img, f"POSTURE: {evaluator.posture}", (170, 205), 
                        cv2.FONT_HERSHEY_TRIPLEX, 0.9, (180, 180, 180), 2)

        cv2.imshow("Smartan-Gym", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()