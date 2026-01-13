import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
import structlog

try:
    from norfair import Detection, Tracker as NorfairTracker
    from norfair.distances import iou as iou_distance
    NORFAIR_AVAILABLE = True
except ImportError:
    NORFAIR_AVAILABLE = False

from config import settings

logger = structlog.get_logger()


@dataclass
class TrackedObject:
    track_id: int
    class_name: str
    bbox: List[int]
    confidence: float
    age: int = 0
    violations: List[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class ObjectTracker:
    
    def __init__(
        self,
        max_distance: int = 100,
        hit_counter_max: int = 15
    ):
        self.enabled = settings.ENABLE_TRACKING and NORFAIR_AVAILABLE
        self.max_distance = max_distance
        self.hit_counter_max = hit_counter_max
        self.tracker = None
        self.track_history: Dict[int, TrackedObject] = {}
        
        if self.enabled:
            self._init_tracker()
            logger.info("tracker_initialized", backend="norfair")
        else:
            logger.warning("tracker_disabled", reason="norfair not available" if not NORFAIR_AVAILABLE else "disabled in config")
    
    def _init_tracker(self):
        self.tracker = NorfairTracker(
            distance_function=self._euclidean_distance,
            distance_threshold=self.max_distance,
            hit_counter_max=self.hit_counter_max,
            initialization_delay=3
        )
    
    def _euclidean_distance(self, detection, tracked_object):
        det_center = detection.points.mean(axis=0)
        track_center = tracked_object.estimate.mean(axis=0)
        return np.linalg.norm(det_center - track_center)
    
    def _to_norfair_detections(self, detections: List[Dict]) -> List:
        norfair_dets = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            points = np.array([[x1, y1], [x2, y2]])
            scores = np.array([det['confidence'], det['confidence']])
            norfair_det = Detection(
                points=points,
                scores=scores,
                data=det
            )
            norfair_dets.append(norfair_det)
        return norfair_dets
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        if not self.enabled or not detections:
            return detections
        
        norfair_dets = self._to_norfair_detections(detections)
        tracked_objects = self.tracker.update(detections=norfair_dets)
        
        tracked_detections = []
        for obj in tracked_objects:
            if obj.last_detection is None:
                continue
            
            det = obj.last_detection.data.copy()
            det['track_id'] = obj.id
            
            if obj.id not in self.track_history:
                self.track_history[obj.id] = TrackedObject(
                    track_id=obj.id,
                    class_name=det['class_name'],
                    bbox=det['bbox'],
                    confidence=det['confidence']
                )
            else:
                self.track_history[obj.id].bbox = det['bbox']
                self.track_history[obj.id].confidence = det['confidence']
                self.track_history[obj.id].age += 1
            
            tracked_detections.append(det)
        
        self._cleanup_old_tracks([obj.id for obj in tracked_objects])
        
        return tracked_detections
    
    def _cleanup_old_tracks(self, active_ids: List[int]):
        to_remove = []
        for track_id in self.track_history:
            if track_id not in active_ids:
                self.track_history[track_id].age += 1
                if self.track_history[track_id].age > self.hit_counter_max * 2:
                    to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.track_history[track_id]
    
    def get_track_info(self, track_id: int) -> Optional[TrackedObject]:
        return self.track_history.get(track_id)
    
    def add_violation(self, track_id: int, violation: str):
        if track_id in self.track_history:
            if violation not in self.track_history[track_id].violations:
                self.track_history[track_id].violations.append(violation)
    
    def reset(self):
        if self.enabled:
            self._init_tracker()
        self.track_history.clear()
