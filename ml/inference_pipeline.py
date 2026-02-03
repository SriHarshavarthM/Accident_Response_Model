"""
Inference Pipeline
Complete pipeline: Video → Detection → Severity → API Submission
"""
import os
import json
import httpx
import asyncio
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from detector import AccidentDetector, AccidentDetection, IncidentType
from severity_scorer import SeverityScorer, SeverityFactors, SeverityLevel
from video_processor import VideoProcessor, FrameData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class IncidentReport:
    """Incident report ready for API submission"""
    camera_id: int
    incident_type: str
    severity: str
    confidence_score: float
    vehicles_involved: int
    pedestrian_involved: bool
    description: str
    video_clip_path: Optional[str]
    snapshots: List[str]
    bounding_boxes: List[Dict]
    timestamp: str


class InferencePipeline:
    """
    Complete ML inference pipeline.
    Processes video → detects accidents → scores severity → submits to API.
    """
    
    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/api/v1",
        model_path: str = "yolov8n.pt",
        sample_fps: int = 5,
        confidence_threshold: float = 0.85,
        consecutive_frames_required: int = 3
    ):
        """
        Initialize the pipeline.
        
        Args:
            api_base_url: Backend API base URL
            model_path: Path to YOLO model
            sample_fps: Frame sampling rate
            confidence_threshold: Minimum confidence for incident
            consecutive_frames_required: Number of consecutive detection frames to confirm incident
        """
        self.api_base_url = api_base_url
        self.confidence_threshold = confidence_threshold
        self.consecutive_frames_required = consecutive_frames_required
        
        # Initialize components
        self.detector = AccidentDetector(model_path=model_path, confidence_threshold=0.5)
        self.scorer = SeverityScorer()
        self.video_processor = VideoProcessor(sample_fps=sample_fps)
        
        # Tracking
        self.detection_buffer: List[AccidentDetection] = []
        self.incidents_reported: List[str] = []
    
    def process_video(
        self,
        video_path: str,
        camera_id: int,
        output_dir: str = "./output",
        submit_to_api: bool = True
    ) -> List[IncidentReport]:
        """
        Process a video file and detect incidents.
        
        Args:
            video_path: Path to video file
            camera_id: Camera ID for incident association
            output_dir: Directory for saving snapshots/clips
            submit_to_api: Whether to submit detected incidents to API
            
        Returns:
            List of IncidentReport objects
        """
        logger.info(f"Processing video: {video_path}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        snapshots_dir = os.path.join(output_dir, "snapshots")
        clips_dir = os.path.join(output_dir, "clips")
        os.makedirs(snapshots_dir, exist_ok=True)
        os.makedirs(clips_dir, exist_ok=True)
        
        # Load video
        video_info = self.video_processor.load_video(video_path)
        
        incidents: List[IncidentReport] = []
        self.detection_buffer = []
        
        try:
            for frame_data in self.video_processor.extract_frames():
                detection = self.detector.detect(frame_data.frame, frame_data.frame_id)
                
                # Check for incident
                if detection.detected and detection.confidence >= self.confidence_threshold:
                    self.detection_buffer.append(detection)
                    
                    # Confirm incident after consecutive detections
                    if len(self.detection_buffer) >= self.consecutive_frames_required:
                        # Calculate severity
                        factors = SeverityFactors(
                            vehicle_count=len(detection.vehicles),
                            pedestrian_involved=len(detection.pedestrians) > 0,
                            is_rollover=detection.incident_type == IncidentType.ROLLOVER,
                            is_multi_vehicle=detection.incident_type == IncidentType.MULTI_VEHICLE,
                            detection_confidence=detection.confidence
                        )
                        severity, score, _ = self.scorer.calculate_severity(factors)
                        
                        # Save snapshot
                        snapshot_path = os.path.join(
                            snapshots_dir,
                            f"incident_{frame_data.frame_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        )
                        annotated = self.detector.draw_detections(frame_data.frame, detection)
                        self.video_processor.save_snapshot(annotated, snapshot_path)
                        
                        # Extract video clip (5 seconds before and after)
                        clip_start = max(0, frame_data.timestamp - 5)
                        clip_end = min(video_info.duration_seconds, frame_data.timestamp + 5)
                        clip_path = os.path.join(
                            clips_dir,
                            f"clip_{frame_data.frame_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                        )
                        
                        # Note: Clip extraction requires video reload, skipping for performance
                        # self.video_processor.extract_clip(clip_start, clip_end, clip_path)
                        
                        # Create incident report
                        report = IncidentReport(
                            camera_id=camera_id,
                            incident_type=detection.incident_type.value,
                            severity=severity.value,
                            confidence_score=detection.confidence,
                            vehicles_involved=len(detection.vehicles),
                            pedestrian_involved=len(detection.pedestrians) > 0,
                            description=detection.description,
                            video_clip_path=None,  # clip_path if extracted
                            snapshots=[snapshot_path],
                            bounding_boxes=detection.bounding_boxes,
                            timestamp=datetime.now().isoformat()
                        )
                        
                        incidents.append(report)
                        logger.info(f"INCIDENT DETECTED: {detection.incident_type.value} - Severity: {severity.value}")
                        
                        # Submit to API
                        if submit_to_api:
                            asyncio.run(self._submit_incident(report))
                        
                        # Reset buffer to avoid duplicate reports
                        self.detection_buffer = []
                else:
                    # Reset buffer if detection chain broken
                    if self.detection_buffer:
                        self.detection_buffer = []
        
        finally:
            self.video_processor.close()
        
        logger.info(f"Processing complete. Detected {len(incidents)} incidents.")
        return incidents
    
    async def _submit_incident(self, report: IncidentReport) -> bool:
        """Submit incident to backend API"""
        try:
            async with httpx.AsyncClient() as client:
                # Convert report to API format
                payload = {
                    "camera_id": report.camera_id,
                    "incident_type": report.incident_type,
                    "severity": report.severity,
                    "confidence_score": report.confidence_score,
                    "vehicles_involved": report.vehicles_involved,
                    "pedestrian_involved": report.pedestrian_involved,
                    "description": report.description,
                    "video_clip_path": report.video_clip_path,
                    "snapshots": report.snapshots,
                    "bounding_boxes": report.bounding_boxes
                }
                
                response = await client.post(
                    f"{self.api_base_url}/incidents/",
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Incident submitted: {result.get('incident_id')}")
                    self.incidents_reported.append(result.get('incident_id'))
                    return True
                else:
                    logger.error(f"Failed to submit incident: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"API submission error: {e}")
            return False
    
    def process_frame_realtime(
        self,
        frame,
        camera_id: int,
        frame_id: int = 0
    ) -> Optional[IncidentReport]:
        """
        Process a single frame (for RTSP/live feed integration).
        
        Args:
            frame: BGR frame from camera
            camera_id: Camera ID
            frame_id: Frame number
            
        Returns:
            IncidentReport if incident detected, None otherwise
        """
        detection = self.detector.detect(frame, frame_id)
        
        if detection.detected and detection.confidence >= self.confidence_threshold:
            self.detection_buffer.append(detection)
            
            if len(self.detection_buffer) >= self.consecutive_frames_required:
                # Calculate severity
                factors = SeverityFactors(
                    vehicle_count=len(detection.vehicles),
                    pedestrian_involved=len(detection.pedestrians) > 0,
                    is_rollover=detection.incident_type == IncidentType.ROLLOVER,
                    is_multi_vehicle=detection.incident_type == IncidentType.MULTI_VEHICLE,
                    detection_confidence=detection.confidence
                )
                severity, _, _ = self.scorer.calculate_severity(factors)
                
                report = IncidentReport(
                    camera_id=camera_id,
                    incident_type=detection.incident_type.value,
                    severity=severity.value,
                    confidence_score=detection.confidence,
                    vehicles_involved=len(detection.vehicles),
                    pedestrian_involved=len(detection.pedestrians) > 0,
                    description=detection.description,
                    video_clip_path=None,
                    snapshots=[],
                    bounding_boxes=detection.bounding_boxes,
                    timestamp=datetime.now().isoformat()
                )
                
                self.detection_buffer = []
                return report
        else:
            self.detection_buffer = []
        
        return None


def run_demo():
    """Run demo with test video or sample frames"""
    print("=" * 60)
    print("Accident Incident Responder - ML Inference Pipeline Demo")
    print("=" * 60)
    
    pipeline = InferencePipeline(
        api_base_url="http://localhost:8000/api/v1",
        sample_fps=5,
        confidence_threshold=0.7,
        consecutive_frames_required=2
    )
    
    print("\nPipeline initialized successfully!")
    print(f"- Detector: YOLOv8")
    print(f"- Sample FPS: 5")
    print(f"- Confidence threshold: 0.7")
    print(f"- Consecutive frames required: 2")
    print("\nTo process a video, use:")
    print('  python inference_pipeline.py --video path/to/video.mp4 --camera-id 1')


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Accident Detection Pipeline")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--camera-id", type=int, default=1, help="Camera ID")
    parser.add_argument("--output-dir", type=str, default="./output", help="Output directory")
    parser.add_argument("--no-submit", action="store_true", help="Don't submit to API")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    
    args = parser.parse_args()
    
    if args.demo or not args.video:
        run_demo()
    else:
        pipeline = InferencePipeline()
        incidents = pipeline.process_video(
            video_path=args.video,
            camera_id=args.camera_id,
            output_dir=args.output_dir,
            submit_to_api=not args.no_submit
        )
        
        print(f"\n{'='*40}")
        print(f"Processing complete!")
        print(f"Incidents detected: {len(incidents)}")
        for i, inc in enumerate(incidents):
            print(f"  {i+1}. {inc.incident_type} - {inc.severity} ({inc.confidence_score:.2f})")
