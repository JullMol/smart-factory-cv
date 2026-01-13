import asyncio
import time
from concurrent import futures
from typing import Dict
import numpy as np
import cv2
import structlog
import grpc

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

import sys
sys.path.insert(0, 'proto')

from detector import Detector
from tracker import ObjectTracker
from zones import ZoneManager, Zone
from metrics import start_metrics_server, record_inference, record_tracks
from config import settings

try:
    from proto import detection_pb2, detection_pb2_grpc
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

import logging

log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" 
        else structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(log_level),
)

logger = structlog.get_logger()

detector: Detector = None
tracker: ObjectTracker = None
zone_manager: ZoneManager = None

app = FastAPI(
    title="Smart Factory AI Inference",
    description="Production-grade PPE Detection with ONNX/TensorRT",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DetectionResponse(BaseModel):
    detections: List[Dict]
    safety_check: Dict
    zone_violations: List[Dict]
    processing_time_ms: float


class ZoneRequest(BaseModel):
    id: str
    name: str
    severity: str = "warning"
    polygon: List[Dict]
    required_ppe: List[str] = []
    enabled: bool = True


@app.on_event("startup")
async def startup():
    global detector, tracker, zone_manager
    
    detector = Detector(
        model_path=settings.MODEL_PATH,
        conf_threshold=settings.CONFIDENCE_THRESHOLD,
        use_onnx=False
    )
    
    tracker = ObjectTracker(
        max_distance=settings.TRACKER_MAX_DISTANCE,
        hit_counter_max=settings.TRACKER_HIT_COUNTER_MAX
    )
    
    zone_manager = ZoneManager()
    
    if settings.METRICS_ENABLED:
        start_metrics_server()
    
    logger.info("ai_service_started", 
                model_backend=detector.backend,
                tracking=tracker.enabled,
                zones=len(zone_manager.zones))


@app.get("/health")
async def health():
    return {
        "status": "healthy" if detector else "unhealthy",
        "model_loaded": detector is not None,
        "model_type": detector.backend if detector else None,
        "device": settings.DEVICE
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect(file: UploadFile = File(...)):
    if not detector:
        raise HTTPException(503, "Model not loaded")
    
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(400, "Invalid image")
    
    return await process_frame(frame)


@app.post("/detect/base64")
async def detect_base64(data: Dict):
    if not detector:
        raise HTTPException(503, "Model not loaded")
    
    import base64
    image_bytes = base64.b64decode(data.get("image", ""))
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(400, "Invalid image data")
    
    return await process_frame(frame)


async def process_frame(frame: np.ndarray) -> Dict:
    start = time.perf_counter()
    
    detections = detector.detect(frame)
    
    if tracker.enabled:
        detections = tracker.update(detections)
        record_tracks(len(tracker.track_history))
    
    safety_check = detector.check_safety(detections)
    
    zone_violations = []
    if zone_manager.enabled:
        violations = zone_manager.check_violations(
            detections, 
            timestamp=int(time.time() * 1000)
        )
        zone_violations = [
            {
                'zone_id': v.zone_id,
                'zone_name': v.zone_name,
                'severity': v.severity,
                'person_track_id': v.person_track_id,
                'missing_ppe': v.missing_ppe,
                'timestamp': v.timestamp
            }
            for v in violations
        ]
    
    processing_time = (time.perf_counter() - start) * 1000
    
    record_inference(processing_time / 1000, detections, safety_check)
    
    return {
        "detections": detections,
        "safety_check": safety_check,
        "zone_violations": zone_violations,
        "processing_time_ms": round(processing_time, 2)
    }


@app.get("/zones")
async def get_zones():
    return zone_manager.get_all_zones()


@app.post("/zones")
async def create_zone(zone: ZoneRequest):
    new_zone = Zone(
        id=zone.id,
        name=zone.name,
        severity=zone.severity,
        polygon=[(p['x'], p['y']) for p in zone.polygon],
        required_ppe=zone.required_ppe,
        enabled=zone.enabled
    )
    zone_manager.add_zone(new_zone)
    return {"status": "created", "zone_id": zone.id}


@app.delete("/zones/{zone_id}")
async def delete_zone(zone_id: str):
    if zone_manager.remove_zone(zone_id):
        return {"status": "deleted"}
    raise HTTPException(404, "Zone not found")


if GRPC_AVAILABLE:
    class DetectionServicer(detection_pb2_grpc.DetectionServiceServicer):
        
        def Detect(self, request, context):
            nparr = np.frombuffer(request.image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return detection_pb2.DetectResponse()
            
            start = time.perf_counter()
            
            if request.confidence_threshold > 0:
                detector.conf_threshold = request.confidence_threshold
            
            detections = detector.detect(frame)
            
            if tracker.enabled:
                detections = tracker.update(detections)
            
            safety_check = detector.check_safety(detections)
            
            zone_violations = []
            if zone_manager.enabled:
                violations = zone_manager.check_violations(
                    detections, 
                    timestamp=int(time.time() * 1000)
                )
                zone_violations = violations
            
            processing_time = (time.perf_counter() - start) * 1000
            
            response = detection_pb2.DetectResponse(
                processing_time_ms=processing_time,
                timestamp=int(time.time() * 1000),
                camera_id=request.camera_id
            )
            
            for det in detections:
                bbox = detection_pb2.BoundingBox(
                    x1=det['bbox'][0], y1=det['bbox'][1],
                    x2=det['bbox'][2], y2=det['bbox'][3]
                )
                response.detections.append(detection_pb2.Detection(
                    class_id=det['class_id'],
                    class_name=det['class_name'],
                    confidence=det['confidence'],
                    bbox=bbox,
                    track_id=det.get('track_id', -1)
                ))
            
            response.safety_check.CopyFrom(detection_pb2.SafetyCheck(
                has_violations=safety_check['has_violations'],
                violations=safety_check['violations'],
                people_count=safety_check['people_count'],
                violation_count=safety_check['violation_count'],
                compliant_count=safety_check['compliant_count'],
                compliance_rate=safety_check['compliance_rate']
            ))
            
            for v in zone_violations:
                response.zone_violations.append(detection_pb2.ZoneViolation(
                    zone_id=v.zone_id,
                    zone_name=v.zone_name,
                    severity=v.severity,
                    person_track_id=v.person_track_id,
                    missing_ppe=v.missing_ppe,
                    timestamp=v.timestamp
                ))
            
            return response
        
        def HealthCheck(self, request, context):
            return detection_pb2.HealthResponse(
                status="healthy" if detector else "unhealthy",
                model_loaded=detector is not None,
                model_type=detector.backend if detector else "",
                device=settings.DEVICE
            )


def serve_grpc():
    if not GRPC_AVAILABLE:
        logger.warning("grpc_disabled", reason="proto stubs not generated")
        return
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    detection_pb2_grpc.add_DetectionServiceServicer_to_server(
        DetectionServicer(), server
    )
    server.add_insecure_port(f'{settings.GRPC_HOST}:{settings.GRPC_PORT}')
    server.start()
    logger.info("grpc_server_started", port=settings.GRPC_PORT)
    return server


async def main():
    global detector, tracker, zone_manager
    
    detector = Detector(
        model_path=settings.MODEL_PATH,
        conf_threshold=settings.CONFIDENCE_THRESHOLD,
        use_onnx=False
    )
    
    tracker = ObjectTracker()
    zone_manager = ZoneManager()
    
    if settings.METRICS_ENABLED:
        start_metrics_server()
    
    grpc_server = serve_grpc()
    
    config = uvicorn.Config(
        app,
        host=settings.REST_HOST,
        port=settings.REST_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    logger.info("all_servers_started",
                rest_port=settings.REST_PORT,
                grpc_port=settings.GRPC_PORT if GRPC_AVAILABLE else "disabled")
    
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
