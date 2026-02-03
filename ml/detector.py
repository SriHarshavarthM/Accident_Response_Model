"""
Accident Detection using YOLOv8
Detects: vehicles, collisions, pedestrians, rollovers
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IncidentType(str, Enum):
    VEHICLE_COLLISION = "VEHICLE_COLLISION"
    ROLLOVER = "ROLLOVER"
    MULTI_VEHICLE = "MULTI_VEHICLE"
    PEDESTRIAN_IMPACT = "PEDESTRIAN_IMPACT"
    FIRE_SMOKE = "FIRE_SMOKE"
    OTHER = "OTHER"


@dataclass
class DetectionResult:
    """Single detection result from YOLO"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]


@dataclass
class AccidentDetection:
    """Accident detection result"""
    detected: bool
    incident_type: IncidentType
    confidence: float
    vehicles: List[DetectionResult]
    pedestrians: List[DetectionResult]
    bounding_boxes: List[Dict]
    frame_id: int
    description: str


class AccidentDetector:
    """
    YOLOv8-based accident detector.
    Uses pre-trained model for vehicle/person detection,
    with custom logic for accident classification.
    """
    
    # COCO class IDs for relevant objects
    VEHICLE_CLASSES = {
        2: 'car',
        3: 'motorcycle', 
        5: 'bus',
        7: 'truck'
    }
    PERSON_CLASS = 0
    
    # Detection thresholds
    VEHICLE_THRESHOLD = 0.5
    COLLISION_IOU_THRESHOLD = 0.3
    ROLLOVER_ASPECT_RATIO = 0.7
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to YOLO model (default: yolov8n.pt - nano model)
            confidence_threshold: Minimum confidence for detections
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model"""
        try:
            logger.info(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(self, frame: np.ndarray, frame_id: int = 0) -> AccidentDetection:
        """
        Run detection on a single frame.
        
        Args:
            frame: BGR image from OpenCV
            frame_id: Frame number for tracking
            
        Returns:
            AccidentDetection with results
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Run YOLO inference
        results = self.model(frame, verbose=False)[0]
        
        # Parse detections
        vehicles = []
        pedestrians = []
        bounding_boxes = []
        
        for box in results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            
            if confidence < self.confidence_threshold:
                continue
            
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            
            detection = DetectionResult(
                class_id=class_id,
                class_name=results.names[class_id],
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                center=center
            )
            
            bbox_dict = {
                "class": results.names[class_id],
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            }
            bounding_boxes.append(bbox_dict)
            
            if class_id in self.VEHICLE_CLASSES:
                vehicles.append(detection)
            elif class_id == self.PERSON_CLASS:
                pedestrians.append(detection)
        
        # Classify incident type
        incident_type, confidence, description = self._classify_incident(
            vehicles, pedestrians, frame.shape
        )
        
        detected = incident_type != IncidentType.OTHER and confidence >= self.confidence_threshold
        
        return AccidentDetection(
            detected=detected,
            incident_type=incident_type,
            confidence=confidence,
            vehicles=vehicles,
            pedestrians=pedestrians,
            bounding_boxes=bounding_boxes,
            frame_id=frame_id,
            description=description
        )
    
    def _classify_incident(
        self, 
        vehicles: List[DetectionResult], 
        pedestrians: List[DetectionResult],
        frame_shape: Tuple
    ) -> Tuple[IncidentType, float, str]:
        """
        Classify the type of incident based on detections.
        
        Returns:
            Tuple of (incident_type, confidence, description)
        """
        if not vehicles:
            return IncidentType.OTHER, 0.0, "No vehicles detected"
        
        # Check for vehicle-pedestrian impact
        if pedestrians and vehicles:
            for ped in pedestrians:
                for vehicle in vehicles:
                    if self._check_proximity(ped.bbox, vehicle.bbox):
                        return (
                            IncidentType.PEDESTRIAN_IMPACT,
                            max(ped.confidence, vehicle.confidence),
                            f"Potential pedestrian-vehicle incident detected. {len(vehicles)} vehicle(s), {len(pedestrians)} pedestrian(s) in close proximity."
                        )
        
        # Check for multi-vehicle pile-up
        if len(vehicles) >= 3:
            overlapping = self._count_overlapping_vehicles(vehicles)
            if overlapping >= 2:
                avg_conf = sum(v.confidence for v in vehicles) / len(vehicles)
                return (
                    IncidentType.MULTI_VEHICLE,
                    avg_conf,
                    f"Multi-vehicle pile-up detected. {len(vehicles)} vehicles with {overlapping} overlapping."
                )
        
        # Check for collision between 2 vehicles
        if len(vehicles) >= 2:
            for i, v1 in enumerate(vehicles):
                for v2 in vehicles[i+1:]:
                    iou = self._calculate_iou(v1.bbox, v2.bbox)
                    if iou > self.COLLISION_IOU_THRESHOLD:
                        return (
                            IncidentType.VEHICLE_COLLISION,
                            max(v1.confidence, v2.confidence),
                            f"Vehicle collision detected. 2 vehicles overlapping with IoU {iou:.2f}."
                        )
        
        # Check for rollover (unusual aspect ratio)
        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle.bbox
            width = x2 - x1
            height = y2 - y1
            aspect_ratio = width / max(height, 1)
            
            # Very wide or very tall indicates possible rollover
            if aspect_ratio < self.ROLLOVER_ASPECT_RATIO or aspect_ratio > 1 / self.ROLLOVER_ASPECT_RATIO:
                return (
                    IncidentType.ROLLOVER,
                    vehicle.confidence,
                    f"Possible vehicle rollover detected. Unusual aspect ratio: {aspect_ratio:.2f}."
                )
        
        return IncidentType.OTHER, 0.0, f"Normal traffic: {len(vehicles)} vehicle(s) detected"
    
    def _check_proximity(self, bbox1: Tuple, bbox2: Tuple, threshold: int = 50) -> bool:
        """Check if two bounding boxes are in close proximity"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        center1 = ((x1_1 + x2_1) // 2, (y1_1 + y2_1) // 2)
        center2 = ((x1_2 + x2_2) // 2, (y1_2 + y2_2) // 2)
        
        distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        # Factor in box sizes
        avg_size = ((x2_1 - x1_1) + (x2_2 - x1_2)) / 2
        
        return distance < avg_size + threshold
    
    def _calculate_iou(self, bbox1: Tuple, bbox2: Tuple) -> float:
        """Calculate Intersection over Union between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / max(union, 1)
    
    def _count_overlapping_vehicles(self, vehicles: List[DetectionResult]) -> int:
        """Count number of overlapping vehicle pairs"""
        count = 0
        for i, v1 in enumerate(vehicles):
            for v2 in vehicles[i+1:]:
                if self._calculate_iou(v1.bbox, v2.bbox) > 0.1:
                    count += 1
        return count
    
    def draw_detections(self, frame: np.ndarray, detection: AccidentDetection) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame.
        
        Args:
            frame: Original frame
            detection: AccidentDetection result
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Draw vehicle boxes (green)
        for vehicle in detection.vehicles:
            x1, y1, x2, y2 = vehicle.bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{vehicle.class_name}: {vehicle.confidence:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw pedestrian boxes (blue)
        for ped in detection.pedestrians:
            x1, y1, x2, y2 = ped.bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label = f"Person: {ped.confidence:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Draw incident info
        if detection.detected:
            cv2.putText(annotated, f"INCIDENT: {detection.incident_type.value}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(annotated, f"Confidence: {detection.confidence:.2f}",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return annotated


if __name__ == "__main__":
    # Test the detector
    detector = AccidentDetector()
    
    # Create a test image
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    result = detector.detect(test_frame)
    print(f"Detection result: {result}")
