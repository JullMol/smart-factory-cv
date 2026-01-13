import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MODEL_PATH: str = "../models/best.pt"
    MODEL_FALLBACK_PATH: str = "../models/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    NMS_THRESHOLD: float = 0.45
    
    USE_TENSORRT: bool = False
    USE_FP16: bool = True
    DEVICE: str = "cuda"
    
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50051
    REST_HOST: str = "0.0.0.0"
    REST_PORT: int = 8000
    
    ENABLE_TRACKING: bool = True
    TRACKER_MAX_DISTANCE: int = 100
    TRACKER_HIT_COUNTER_MAX: int = 15
    
    ENABLE_ZONES: bool = True
    ZONES_CONFIG_PATH: str = "../config/zones.yaml"
    
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


CLASS_NAMES = [
    'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 
    'NO-Safety Vest', 'Person', 'Safety Cone', 
    'Safety Vest', 'machinery', 'vehicle'
]

PPE_CLASSES = {'Hardhat', 'Mask', 'Safety Vest'}
VIOLATION_CLASSES = {'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest'}
PERSON_CLASS = 'Person'
