import yaml
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import structlog

try:
    from shapely.geometry import Point, Polygon
    from shapely.prepared import prep
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

from config import settings, VIOLATION_CLASSES

logger = structlog.get_logger()


@dataclass
class Zone:
    id: str
    name: str
    severity: str
    polygon: List[Tuple[float, float]]
    required_ppe: List[str] = field(default_factory=list)
    enabled: bool = True
    _prepared_polygon: object = field(default=None, repr=False)
    
    def __post_init__(self):
        if SHAPELY_AVAILABLE and len(self.polygon) >= 3:
            poly = Polygon(self.polygon)
            self._prepared_polygon = prep(poly)


@dataclass
class ZoneViolation:
    zone_id: str
    zone_name: str
    severity: str
    person_track_id: int
    missing_ppe: List[str]
    timestamp: int
    bbox: List[int]


class ZoneManager:
    
    def __init__(self, config_path: Optional[str] = None):
        self.enabled = settings.ENABLE_ZONES and SHAPELY_AVAILABLE
        self.zones: Dict[str, Zone] = {}
        self.violation_history: Dict[str, List[ZoneViolation]] = {}
        
        if not SHAPELY_AVAILABLE:
            logger.warning("zones_disabled", reason="shapely not available")
            return
        
        config_path = config_path or settings.ZONES_CONFIG_PATH
        if Path(config_path).exists():
            self.load_config(config_path)
        else:
            logger.info("zones_no_config", path=config_path)
    
    def load_config(self, path: str):
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        for zone_data in config.get('zones', []):
            zone = Zone(
                id=zone_data['id'],
                name=zone_data['name'],
                severity=zone_data.get('severity', 'warning'),
                polygon=[(p['x'], p['y']) for p in zone_data['polygon']],
                required_ppe=zone_data.get('required_ppe', []),
                enabled=zone_data.get('enabled', True)
            )
            self.zones[zone.id] = zone
        
        logger.info("zones_loaded", count=len(self.zones))
    
    def add_zone(self, zone: Zone):
        self.zones[zone.id] = zone
        logger.info("zone_added", zone_id=zone.id, name=zone.name)
    
    def remove_zone(self, zone_id: str) -> bool:
        if zone_id in self.zones:
            del self.zones[zone_id]
            logger.info("zone_removed", zone_id=zone_id)
            return True
        return False
    
    def update_zone(self, zone_id: str, **kwargs) -> bool:
        if zone_id not in self.zones:
            return False
        
        zone = self.zones[zone_id]
        for key, value in kwargs.items():
            if hasattr(zone, key):
                setattr(zone, key, value)
        
        if 'polygon' in kwargs:
            poly = Polygon(zone.polygon)
            zone._prepared_polygon = prep(poly)
        
        return True
    
    def is_point_in_zone(self, x: float, y: float, zone: Zone) -> bool:
        if not zone.enabled or zone._prepared_polygon is None:
            return False
        point = Point(x, y)
        return zone._prepared_polygon.contains(point)
    
    def get_zone_for_point(self, x: float, y: float) -> Optional[Zone]:
        for zone in self.zones.values():
            if self.is_point_in_zone(x, y, zone):
                return zone
        return None
    
    def check_violations(
        self,
        detections: List[Dict],
        timestamp: int
    ) -> List[ZoneViolation]:
        if not self.enabled or not self.zones:
            return []
        
        violations = []
        
        persons = [d for d in detections if d['class_name'] == 'Person']
        ppe_detections = [d for d in detections if d['class_name'] not in ['Person', 'machinery', 'vehicle', 'Safety Cone']]
        
        for person in persons:
            px1, py1, px2, py2 = person['bbox']
            person_center_x = (px1 + px2) / 2
            person_center_y = (py1 + py2) / 2
            person_bottom_center_y = py2
            
            for zone in self.zones.values():
                if not self.is_point_in_zone(person_center_x, person_bottom_center_y, zone):
                    continue
                
                person_ppe = self._find_ppe_for_person(person, ppe_detections)
                
                missing_ppe = []
                for required in zone.required_ppe:
                    if required not in person_ppe:
                        missing_ppe.append(required)
                
                person_violations = [d['class_name'] for d in ppe_detections 
                                   if d['class_name'] in VIOLATION_CLASSES and
                                   self._boxes_overlap(person['bbox'], d['bbox'])]
                
                if missing_ppe or person_violations:
                    violation = ZoneViolation(
                        zone_id=zone.id,
                        zone_name=zone.name,
                        severity=zone.severity,
                        person_track_id=person.get('track_id', -1),
                        missing_ppe=missing_ppe + person_violations,
                        timestamp=timestamp,
                        bbox=person['bbox']
                    )
                    violations.append(violation)
                    
                    if zone.id not in self.violation_history:
                        self.violation_history[zone.id] = []
                    self.violation_history[zone.id].append(violation)
        
        return violations
    
    def _find_ppe_for_person(
        self,
        person: Dict,
        ppe_detections: List[Dict]
    ) -> List[str]:
        found_ppe = []
        px1, py1, px2, py2 = person['bbox']
        
        for ppe in ppe_detections:
            if ppe['class_name'].startswith('NO-'):
                continue
            
            if self._boxes_overlap(person['bbox'], ppe['bbox']):
                found_ppe.append(ppe['class_name'])
        
        return found_ppe
    
    def _boxes_overlap(self, box1: List[int], box2: List[int]) -> bool:
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        if x2_1 < x1_2 or x2_2 < x1_1:
            return False
        if y2_1 < y1_2 or y2_2 < y1_1:
            return False
        
        inter_x1 = max(x1_1, x1_2)
        inter_y1 = max(y1_1, y1_2)
        inter_x2 = min(x2_1, x2_2)
        inter_y2 = min(y2_1, y2_2)
        
        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        if box2_area == 0:
            return False
        
        return (inter_area / box2_area) > 0.3
    
    def get_all_zones(self) -> List[Dict]:
        return [
            {
                'id': z.id,
                'name': z.name,
                'severity': z.severity,
                'polygon': [{'x': p[0], 'y': p[1]} for p in z.polygon],
                'required_ppe': z.required_ppe,
                'enabled': z.enabled
            }
            for z in self.zones.values()
        ]
