"""
Video Processor Service
Processes uploaded videos and creates incident detections
"""
import os
import random
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio

# Try to import CV2 for video processing
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available. Using simulation mode.")


class VideoProcessor:
    """
    Processes video files for accident detection.
    Uses YOLOv8 or simulation for testing.
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.confidence_threshold = 0.85
        self.fps_sample = 5
        
        # Incident types that can be detected
        self.incident_types = [
            "VEHICLE_COLLISION",
            "MULTI_VEHICLE",
            "ROLLOVER",
            "PEDESTRIAN_IMPACT"
        ]
        
        # Severity levels
        self.severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def analyze_video(self, video_path: str, camera_id: int) -> Dict[str, Any]:
        """
        Analyze video and detect potential accidents.
        Returns detection results.
        """
        if not os.path.exists(video_path):
            return {"error": "Video file not found", "detected": False}
        
        if CV2_AVAILABLE:
            return self._analyze_with_cv2(video_path, camera_id)
        else:
            return self._simulate_detection(video_path, camera_id)
    
    def _analyze_with_cv2(self, video_path: str, camera_id: int) -> Dict[str, Any]:
        """Analyze video using OpenCV (simulated ML detection)"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"error": "Could not open video", "detected": False}
            
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Sample frames for analysis
            frame_count = 0
            analyzed_frames = 0
            detections = []
            
            sample_interval = max(1, fps // self.fps_sample)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Sample every Nth frame
                if frame_count % sample_interval == 0:
                    analyzed_frames += 1
                    
                    # Simulate detection on this frame
                    # In production, this would call YOLOv8
                    detection = self._simulate_frame_detection(frame, frame_count, fps)
                    if detection:
                        detections.append(detection)
            
            cap.release()
            
            # Process detections
            if detections:
                # Take the highest confidence detection
                best_detection = max(detections, key=lambda x: x['confidence'])
                
                return {
                    "detected": True,
                    "incident_type": best_detection['type'],
                    "severity": best_detection['severity'],
                    "confidence_score": best_detection['confidence'],
                    "vehicles_involved": best_detection['vehicles'],
                    "pedestrian_involved": best_detection['pedestrian'],
                    "timestamp_in_video": best_detection['timestamp'],
                    "description": self._generate_description(best_detection),
                    "video_path": video_path,
                    "camera_id": camera_id,
                    "analysis_summary": {
                        "total_frames": total_frames,
                        "analyzed_frames": analyzed_frames,
                        "detections_found": len(detections),
                        "duration_seconds": duration
                    }
                }
            
            return {
                "detected": False,
                "message": "No incidents detected in video",
                "analysis_summary": {
                    "total_frames": total_frames,
                    "analyzed_frames": analyzed_frames,
                    "duration_seconds": duration
                }
            }
            
        except Exception as e:
            return {"error": str(e), "detected": False}
    
    def _simulate_frame_detection(self, frame, frame_num: int, fps: int) -> Optional[Dict]:
        """
        Simulate detection on a frame.
        In production, this would run YOLOv8 inference.
        """
        # For demo: detect "accident" around the middle of the video
        # with some randomness to make it realistic
        
        # Probability of detection increases in middle of video
        base_probability = 0.02  # 2% base chance per sampled frame
        
        if random.random() < base_probability:
            # Generate a detection
            incident_type = random.choice(self.incident_types)
            
            # Severity based on incident type
            if incident_type == "PEDESTRIAN_IMPACT":
                severity = random.choice(["HIGH", "CRITICAL"])
                pedestrian = True
            elif incident_type == "MULTI_VEHICLE":
                severity = random.choice(["HIGH", "CRITICAL"])
                pedestrian = False
            elif incident_type == "ROLLOVER":
                severity = random.choice(["MEDIUM", "HIGH"])
                pedestrian = False
            else:
                severity = random.choice(["MEDIUM", "HIGH", "CRITICAL"])
                pedestrian = False
            
            vehicles = 2 if incident_type == "VEHICLE_COLLISION" else (
                random.randint(3, 5) if incident_type == "MULTI_VEHICLE" else 1
            )
            
            return {
                "type": incident_type,
                "severity": severity,
                "confidence": round(random.uniform(0.85, 0.98), 2),
                "vehicles": vehicles,
                "pedestrian": pedestrian,
                "timestamp": frame_num / fps,
                "frame": frame_num
            }
        
        return None
    
    def _simulate_detection(self, video_path: str, camera_id: int) -> Dict[str, Any]:
        """
        Simulate detection without OpenCV.
        Always detects an incident for demo purposes.
        """
        # Randomly select incident type
        incident_type = random.choice(self.incident_types)
        
        # Determine severity and other properties
        if incident_type == "PEDESTRIAN_IMPACT":
            severity = "CRITICAL"
            vehicles = 1
            pedestrian = True
        elif incident_type == "MULTI_VEHICLE":
            severity = random.choice(["HIGH", "CRITICAL"])
            vehicles = random.randint(3, 5)
            pedestrian = False
        elif incident_type == "ROLLOVER":
            severity = "HIGH"
            vehicles = 1
            pedestrian = False
        else:  # VEHICLE_COLLISION
            severity = random.choice(["MEDIUM", "HIGH", "CRITICAL"])
            vehicles = 2
            pedestrian = random.random() < 0.1  # 10% chance
        
        confidence = round(random.uniform(0.87, 0.96), 2)
        
        detection = {
            "type": incident_type,
            "severity": severity,
            "confidence": confidence,
            "vehicles": vehicles,
            "pedestrian": pedestrian,
            "timestamp": random.uniform(1.0, 5.0)
        }
        
        return {
            "detected": True,
            "incident_type": incident_type,
            "severity": severity,
            "confidence_score": confidence,
            "vehicles_involved": vehicles,
            "pedestrian_involved": pedestrian,
            "timestamp_in_video": detection['timestamp'],
            "description": self._generate_description(detection),
            "video_path": video_path,
            "camera_id": camera_id,
            "analysis_summary": {
                "mode": "simulation",
                "message": "OpenCV not available, using simulated detection"
            }
        }
    
    def _generate_description(self, detection: Dict) -> str:
        """Generate AI-style description of the incident"""
        descriptions = {
            "VEHICLE_COLLISION": [
                "Vehicle collision detected with significant impact force.",
                "Two vehicles involved in frontal collision at intersection.",
                "Side-impact collision detected between vehicles."
            ],
            "MULTI_VEHICLE": [
                "Multi-vehicle pile-up detected. Chain reaction collision.",
                "Multiple vehicles involved in collision sequence.",
                "Large-scale accident involving {v} vehicles detected."
            ],
            "ROLLOVER": [
                "Vehicle rollover detected. Single vehicle incident.",
                "Vehicle overturned after losing control.",
                "Rollover accident detected on roadway."
            ],
            "PEDESTRIAN_IMPACT": [
                "CRITICAL: Pedestrian impact detected. Immediate response required.",
                "Vehicle-pedestrian collision detected at crossing.",
                "Pedestrian struck by vehicle. High severity incident."
            ]
        }
        
        desc = random.choice(descriptions.get(detection['type'], ["Incident detected."]))
        desc = desc.replace("{v}", str(detection.get('vehicles', 2)))
        
        return f"{desc} Confidence: {detection['confidence']*100:.0f}%. Severity level: {detection['severity']}."


# Background task for processing
async def process_video_async(video_path: str, camera_id: int, db_session) -> Dict[str, Any]:
    """
    Async wrapper for video processing.
    Returns detection results and creates incident if detected.
    """
    from models import Incident, IncidentType, SeverityLevel, IncidentStatus
    
    processor = VideoProcessor()
    result = processor.analyze_video(video_path, camera_id)
    
    if result.get("detected"):
        # Create incident in database
        incident_id = f"INC-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
        
        # Map string to enum
        incident_type_map = {
            "VEHICLE_COLLISION": IncidentType.VEHICLE_COLLISION,
            "MULTI_VEHICLE": IncidentType.MULTI_VEHICLE,
            "ROLLOVER": IncidentType.ROLLOVER,
            "PEDESTRIAN_IMPACT": IncidentType.PEDESTRIAN_IMPACT
        }
        
        severity_map = {
            "LOW": SeverityLevel.LOW,
            "MEDIUM": SeverityLevel.MEDIUM,
            "HIGH": SeverityLevel.HIGH,
            "CRITICAL": SeverityLevel.CRITICAL
        }
        
        new_incident = Incident(
            incident_id=incident_id,
            camera_id=camera_id,
            incident_type=incident_type_map.get(result['incident_type'], IncidentType.VEHICLE_COLLISION),
            severity=severity_map.get(result['severity'], SeverityLevel.MEDIUM),
            confidence_score=result['confidence_score'],
            vehicles_involved=result['vehicles_involved'],
            pedestrian_involved=result['pedestrian_involved'],
            description=result['description'],
            video_clip_path=video_path,
            status=IncidentStatus.DETECTED
        )
        
        db_session.add(new_incident)
        db_session.commit()
        db_session.refresh(new_incident)
        
        result['incident_created'] = True
        result['incident_db_id'] = new_incident.id
        result['incident_id'] = incident_id
    
    return result
