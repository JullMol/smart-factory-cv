from ultralytics import YOLO
import numpy as np
import cv2
from typing import List, Dict


class SafetyDetector:
    
    def __init__(self, model_path: str, conf_threshold: float = 0.5):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
        self.class_names = [
            'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 
            'NO-Safety Vest', 'Person', 'Safety Cone', 
            'Safety Vest', 'machinery', 'vehicle'
        ]
        
    def detect(self, frame: np.ndarray) -> List[Dict]:
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detections.append({
                    'class_id': class_id,
                    'class_name': self.class_names[class_id],
                    'confidence': confidence,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        annotated = frame.copy()
        
        COLOR_SAFE = (0, 255, 0)
        COLOR_VIOLATION = (0, 0, 255)
        COLOR_NEUTRAL = (255, 255, 0)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class_name']
            confidence = det['confidence']
            
            if class_name.startswith('NO-'):
                color = COLOR_VIOLATION
            elif class_name in ['Hardhat', 'Mask', 'Safety Vest']:
                color = COLOR_SAFE
            else:
                color = COLOR_NEUTRAL
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            label = f"{class_name} {confidence:.2f}"
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                annotated, 
                (x1, y1 - label_h - baseline - 5), 
                (x1 + label_w, y1),
                color, -1
            )
            
            cv2.putText(
                annotated, label, (x1, y1 - baseline - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )
        
        return annotated
    
    def check_safety_violations(self, detections: List[Dict]) -> Dict:
        violations = []
        people_count = 0
        violation_count = 0
        
        for det in detections:
            class_name = det['class_name']
            
            if class_name == 'Person':
                people_count += 1
            elif class_name.startswith('NO-'):
                violations.append(class_name)
                violation_count += 1
        
        return {
            'has_violations': len(violations) > 0,
            'violations': violations,
            'people_count': people_count,
            'violation_count': violation_count,
            'compliant_count': people_count - violation_count
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python detector.py <model_path> [image_path]")
        sys.exit(1)
    
    model_path = sys.argv[1]
    detector = SafetyDetector(model_path)
    
    if len(sys.argv) > 2:
        image_path = sys.argv[2]
        frame = cv2.imread(image_path)
        
        if frame is None:
            print(f"Error: Could not load image {image_path}")
            sys.exit(1)
        
        detections = detector.detect(frame)
        annotated = detector.draw_detections(frame, detections)
        safety_check = detector.check_safety_violations(detections)
        
        print(f"\nDetections: {len(detections)}")
        for det in detections:
            print(f"  - {det['class_name']}: {det['confidence']:.2f}")
        
        print(f"\nSafety Check:")
        print(f"  People: {safety_check['people_count']}")
        print(f"  Violations: {safety_check['violation_count']}")
        print(f"  Compliant: {safety_check['compliant_count']}")
        if safety_check['violations']:
            print(f"  Types: {', '.join(safety_check['violations'])}")
        
        cv2.imshow("Detection Result", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Testing with webcam (Press 'q' to quit)")
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            detections = detector.detect(frame)
            annotated = detector.draw_detections(frame, detections)
            
            cv2.imshow("Live Detection", annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
