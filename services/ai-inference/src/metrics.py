from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import structlog

from config import settings

logger = structlog.get_logger()

inference_duration = Histogram(
    'ai_inference_duration_seconds',
    'Time spent on inference',
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0]
)

detections_total = Counter(
    'ai_detections_total',
    'Total detections by class',
    ['class_name']
)

violations_total = Counter(
    'ai_violations_total',
    'Total safety violations detected',
    ['violation_type', 'zone_id']
)

frames_processed = Counter(
    'ai_frames_processed_total',
    'Total frames processed'
)

model_confidence = Histogram(
    'ai_model_confidence',
    'Distribution of detection confidence scores',
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
)

active_tracks = Gauge(
    'ai_active_tracks',
    'Number of currently tracked objects'
)

people_in_zones = Gauge(
    'ai_people_in_zones',
    'Number of people currently in danger zones',
    ['zone_id']
)

compliance_rate = Gauge(
    'ai_compliance_rate_percent',
    'Current PPE compliance rate'
)


def start_metrics_server():
    if settings.METRICS_ENABLED:
        start_http_server(settings.METRICS_PORT)
        logger.info("metrics_server_started", port=settings.METRICS_PORT)


def record_inference(duration: float, detections: list, safety_check: dict):
    inference_duration.observe(duration)
    frames_processed.inc()
    
    for det in detections:
        detections_total.labels(class_name=det['class_name']).inc()
        model_confidence.observe(det['confidence'])
    
    compliance_rate.set(safety_check.get('compliance_rate', 100))


def record_violation(violation_type: str, zone_id: str = "global"):
    violations_total.labels(violation_type=violation_type, zone_id=zone_id).inc()


def record_tracks(count: int):
    active_tracks.set(count)


def record_zone_occupancy(zone_id: str, count: int):
    people_in_zones.labels(zone_id=zone_id).set(count)


class InferenceTimer:
    def __init__(self):
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        duration = time.perf_counter() - self.start_time
        inference_duration.observe(duration)
