"""
Video Processor Module
Handles video ingestion with configurable frame sampling
"""
import cv2
import os
from typing import Generator, Tuple, Optional
from dataclasses import dataclass
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Video metadata"""
    path: str
    width: int
    height: int
    fps: float
    total_frames: int
    duration_seconds: float
    codec: str


@dataclass
class FrameData:
    """Processed frame with metadata"""
    frame: np.ndarray
    frame_id: int
    timestamp: float  # seconds from start
    original_fps: float


class VideoProcessor:
    """
    Video ingestion and frame extraction.
    Supports MP4, AVI, MOV, MKV formats.
    """
    
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    
    def __init__(self, sample_fps: int = 5):
        """
        Initialize processor.
        
        Args:
            sample_fps: Target frames per second to extract (default: 5)
        """
        self.sample_fps = sample_fps
        self.current_video: Optional[cv2.VideoCapture] = None
        self.video_info: Optional[VideoInfo] = None
    
    def load_video(self, video_path: str) -> VideoInfo:
        """
        Load a video file and get its metadata.
        
        Args:
            video_path: Path to video file
            
        Returns:
            VideoInfo with metadata
            
        Raises:
            ValueError: If file format not supported or file not found
        """
        # Check file exists
        if not os.path.exists(video_path):
            raise ValueError(f"Video file not found: {video_path}")
        
        # Check format
        ext = os.path.splitext(video_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {ext}. Supported: {self.SUPPORTED_FORMATS}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        # Get metadata
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        # Get codec
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        
        self.current_video = cap
        self.video_info = VideoInfo(
            path=video_path,
            width=width,
            height=height,
            fps=fps,
            total_frames=total_frames,
            duration_seconds=duration,
            codec=codec
        )
        
        logger.info(f"Loaded video: {video_path}")
        logger.info(f"Resolution: {width}x{height}, FPS: {fps:.2f}, Duration: {duration:.2f}s")
        
        return self.video_info
    
    def extract_frames(self, max_frames: Optional[int] = None) -> Generator[FrameData, None, None]:
        """
        Extract frames at the configured sample rate.
        
        Args:
            max_frames: Maximum number of frames to extract (None = all)
            
        Yields:
            FrameData for each sampled frame
        """
        if self.current_video is None or self.video_info is None:
            raise RuntimeError("No video loaded. Call load_video() first.")
        
        # Calculate frame skip based on sample rate
        original_fps = self.video_info.fps
        frame_skip = max(1, int(original_fps / self.sample_fps))
        
        logger.info(f"Extracting frames at {self.sample_fps} FPS (every {frame_skip} frames)")
        
        frame_count = 0
        extracted_count = 0
        
        while True:
            ret, frame = self.current_video.read()
            if not ret:
                break
            
            # Sample frames at target rate
            if frame_count % frame_skip == 0:
                timestamp = frame_count / original_fps
                
                yield FrameData(
                    frame=frame,
                    frame_id=frame_count,
                    timestamp=timestamp,
                    original_fps=original_fps
                )
                
                extracted_count += 1
                
                if max_frames and extracted_count >= max_frames:
                    break
            
            frame_count += 1
        
        logger.info(f"Extracted {extracted_count} frames from {frame_count} total")
    
    def extract_snapshot(self, timestamp_seconds: float) -> Optional[np.ndarray]:
        """
        Extract a single frame at specific timestamp.
        
        Args:
            timestamp_seconds: Time in seconds to extract frame
            
        Returns:
            Frame as numpy array or None if failed
        """
        if self.current_video is None or self.video_info is None:
            raise RuntimeError("No video loaded. Call load_video() first.")
        
        # Calculate frame number
        frame_number = int(timestamp_seconds * self.video_info.fps)
        
        # Seek to frame
        self.current_video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = self.current_video.read()
        if ret:
            return frame
        return None
    
    def save_snapshot(self, frame: np.ndarray, output_path: str) -> str:
        """
        Save a frame as an image file.
        
        Args:
            frame: Frame to save
            output_path: Output file path
            
        Returns:
            Saved file path
        """
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        cv2.imwrite(output_path, frame)
        logger.info(f"Saved snapshot: {output_path}")
        return output_path
    
    def extract_clip(
        self, 
        start_time: float, 
        end_time: float, 
        output_path: str
    ) -> str:
        """
        Extract a video clip between two timestamps.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output video file path
            
        Returns:
            Output file path
        """
        if self.current_video is None or self.video_info is None:
            raise RuntimeError("No video loaded. Call load_video() first.")
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # Setup writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path,
            fourcc,
            self.video_info.fps,
            (self.video_info.width, self.video_info.height)
        )
        
        # Calculate frame range
        start_frame = int(start_time * self.video_info.fps)
        end_frame = int(end_time * self.video_info.fps)
        
        # Seek to start
        self.current_video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        current_frame = start_frame
        while current_frame < end_frame:
            ret, frame = self.current_video.read()
            if not ret:
                break
            out.write(frame)
            current_frame += 1
        
        out.release()
        logger.info(f"Saved clip: {output_path} ({end_time - start_time:.2f}s)")
        
        return output_path
    
    def close(self):
        """Release video resources"""
        if self.current_video:
            self.current_video.release()
            self.current_video = None
            self.video_info = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def process_video_file(
    video_path: str,
    sample_fps: int = 5,
    max_frames: Optional[int] = None
) -> Generator[FrameData, None, None]:
    """
    Convenience function to process a video file.
    
    Args:
        video_path: Path to video file
        sample_fps: Target FPS for sampling
        max_frames: Maximum frames to extract
        
    Yields:
        FrameData for each sampled frame
    """
    with VideoProcessor(sample_fps=sample_fps) as processor:
        processor.load_video(video_path)
        yield from processor.extract_frames(max_frames=max_frames)


if __name__ == "__main__":
    # Test with a sample video
    print("Video Processor Module")
    print("=" * 40)
    
    # Create a test video (small, synthetic)
    test_video = "test_video.mp4"
    
    # If no test video exists, create a simple one
    if not os.path.exists(test_video):
        print("Creating test video...")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(test_video, fourcc, 30, (640, 480))
        
        for i in range(90):  # 3 seconds at 30 fps
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, f"Frame {i}", (200, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            out.write(frame)
        out.release()
        print(f"Created test video: {test_video}")
    
    # Test processing
    processor = VideoProcessor(sample_fps=5)
    try:
        info = processor.load_video(test_video)
        print(f"\nVideo Info: {info}")
        
        count = 0
        for frame_data in processor.extract_frames(max_frames=10):
            count += 1
            print(f"Frame {frame_data.frame_id} at {frame_data.timestamp:.2f}s")
        
        print(f"\nProcessed {count} frames")
    finally:
        processor.close()
