# Sample Videos Directory

Place your test videos here for processing.

## Supported Formats
- MP4
- AVI
- MOV
- MKV

## Usage

Process a video using the ML pipeline:

```bash
cd ../ml
python inference_pipeline.py --video ../samples/your_video.mp4 --camera-id 1
```

## Finding Sample Videos

For testing accident detection, you can use:

1. **Public Datasets**:
   - Drive360 (MIT)
   - TAD (Traffic Accident Dataset)
   - YouTube dashcam compilations

2. **Requirements**:
   - Clear road visibility
   - Contains vehicles
   - Resolution: 720p or higher preferred

## Note

The ML model uses YOLOv8 for vehicle detection with custom accident classification logic. For best results, use videos with:
- Stable camera (CCTV-style)
- Good lighting
- Multiple vehicles visible
