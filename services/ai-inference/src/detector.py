import numpy as np
import cv2
from typing import List, Dict, Optional, Tuple
import structlog

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

from config import settings, CLASS_NAMES, PPE_CLASSES, VIOLATION_CLASSES

logger = structlog.get_logger()


class Detector:
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        conf_threshold: float = 0.5,
        use_onnx: bool = True
    ):
        self.conf_threshold = conf_threshold
        self.nms_threshold = settings.NMS_THRESHOLD
        self.class_names = CLASS_NAMES
        self.model = None
        self.session = None
        self.backend = None
        
        model_path = model_path or settings.MODEL_PATH
        
        if use_onnx and ONNX_AVAILABLE and model_path.endswith('.onnx'):
            self._load_onnx(model_path)
        elif ULTRALYTICS_AVAILABLE:
            fallback = settings.MODEL_FALLBACK_PATH
            self._load_pytorch(fallback if not model_path.endswith('.pt') else model_path)
        else:
            raise RuntimeError("No inference backend available")
        
        logger.info("detector_initialized", backend=self.backend, model=model_path)
    
    def _load_onnx(self, model_path: str):
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        if settings.USE_TENSORRT:
            providers.insert(0, 'TensorrtExecutionProvider')
        
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.backend = "onnx"
        
        input_info = self.session.get_inputs()[0]
        self.input_name = input_info.name
        self.input_shape = input_info.shape
        
        logger.info("onnx_loaded", providers=self.session.get_providers())
    
    def _load_pytorch(self, model_path: str):
        self.model = YOLO(model_path)
        self.backend = "pytorch"
        logger.info("pytorch_loaded", model=model_path)
    
    def preprocess(self, frame: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int], float]:
        original_shape = frame.shape[:2]
        
        input_size = 640
        scale = min(input_size / original_shape[0], input_size / original_shape[1])
        new_h, new_w = int(original_shape[0] * scale), int(original_shape[1] * scale)
        
        resized = cv2.resize(frame, (new_w, new_h))
        
        padded = np.full((input_size, input_size, 3), 114, dtype=np.uint8)
        padded[:new_h, :new_w] = resized
        
        blob = padded.astype(np.float32) / 255.0
        blob = blob.transpose(2, 0, 1)
        blob = np.expand_dims(blob, 0)
        
        return blob, original_shape, scale
    
    def postprocess(
        self,
        outputs: np.ndarray,
        original_shape: Tuple[int, int],
        scale: float
    ) -> List[Dict]:
        predictions = outputs[0].T
        
        boxes = predictions[:, :4]
        scores = predictions[:, 4:]
        
        class_ids = np.argmax(scores, axis=1)
        confidences = scores[np.arange(len(scores)), class_ids]
        
        mask = confidences > self.conf_threshold
        boxes = boxes[mask]
        class_ids = class_ids[mask]
        confidences = confidences[mask]
        
        if len(boxes) == 0:
            return []
        
        x_center, y_center, width, height = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        x1 = (x_center - width / 2) / scale
        y1 = (y_center - height / 2) / scale
        x2 = (x_center + width / 2) / scale
        y2 = (y_center + height / 2) / scale
        
        x1 = np.clip(x1, 0, original_shape[1])
        y1 = np.clip(y1, 0, original_shape[0])
        x2 = np.clip(x2, 0, original_shape[1])
        y2 = np.clip(y2, 0, original_shape[0])
        
        detections = []
        for i in range(len(boxes)):
            detections.append({
                'class_id': int(class_ids[i]),
                'class_name': self.class_names[class_ids[i]],
                'confidence': float(confidences[i]),
                'bbox': [int(x1[i]), int(y1[i]), int(x2[i]), int(y2[i])]
            })
        
        return detections
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        if self.backend == "onnx":
            return self._detect_onnx(frame)
        else:
            return self._detect_pytorch(frame)
    
    def _detect_onnx(self, frame: np.ndarray) -> List[Dict]:
        blob, original_shape, scale = self.preprocess(frame)
        outputs = self.session.run(None, {self.input_name: blob})
        return self.postprocess(outputs[0], original_shape, scale)
    
    def _detect_pytorch(self, frame: np.ndarray) -> List[Dict]:
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                detections.append({
                    'class_id': class_id,
                    'class_name': self.class_names[class_id],
                    'confidence': float(box.conf[0]),
                    'bbox': [int(x) for x in box.xyxy[0].tolist()]
                })
        
        return detections
    
    def check_safety(self, detections: List[Dict]) -> Dict:
        violations = []
        people_count = 0
        violation_count = 0
        
        for det in detections:
            class_name = det['class_name']
            if class_name == 'Person':
                people_count += 1
            elif class_name in VIOLATION_CLASSES:
                violations.append(class_name)
                violation_count += 1
        
        compliant = max(0, people_count - violation_count)
        rate = (compliant / people_count * 100) if people_count > 0 else 100.0
        
        return {
            'has_violations': len(violations) > 0,
            'violations': violations,
            'people_count': people_count,
            'violation_count': violation_count,
            'compliant_count': compliant,
            'compliance_rate': round(rate, 1)
        }
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        annotated = frame.copy()
        
        COLOR_SAFE = (0, 255, 0)
        COLOR_VIOLATION = (0, 0, 255)
        COLOR_NEUTRAL = (255, 200, 0)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class_name']
            confidence = det['confidence']
            track_id = det.get('track_id')
            
            if class_name.startswith('NO-'):
                color = COLOR_VIOLATION
            elif class_name in PPE_CLASSES:
                color = COLOR_SAFE
            else:
                color = COLOR_NEUTRAL
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            label = f"{class_name} {confidence:.2f}"
            if track_id is not None:
                label = f"[{track_id}] {label}"
            
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, y1 - h - 8), (x1 + w + 4, y1), color, -1)
            cv2.putText(annotated, label, (x1 + 2, y1 - 4),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
