from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
import cv2
import uvicorn
from detector import SafetyDetector


app = FastAPI(
    title="Smart Factory AI Engine",
    description="YOLOv8 PPE Detection API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector: SafetyDetector = None


class DetectionResponse(BaseModel):
    detections: List[Dict]
    safety_check: Dict
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


@app.on_event("startup")
async def startup_event():
    global detector
    
    model_path = "../models/best.pt"
    
    try:
        detector = SafetyDetector(model_path, conf_threshold=0.5)
        print(f"Model loaded: {model_path}")
    except Exception as e:
        print(f"Failed to load model: {e}")
        detector = None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy" if detector is not None else "unhealthy",
        "model_loaded": detector is not None
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_image(file: UploadFile = File(...)):
    if detector is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        import time
        start = time.time()
        
        detections = detector.detect(frame)
        safety_check = detector.check_safety_violations(detections)
        
        processing_time = (time.time() - start) * 1000
        
        return {
            "detections": detections,
            "safety_check": safety_check,
            "processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect/base64")
async def detect_base64(data: Dict):
    if detector is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        import base64
        
        image_b64 = data.get("image", "")
        image_bytes = base64.b64decode(image_b64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        import time
        start = time.time()
        
        detections = detector.detect(frame)
        safety_check = detector.check_safety_violations(detections)
        
        processing_time = (time.time() - start) * 1000
        
        return {
            "detections": detections,
            "safety_check": safety_check,
            "processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
