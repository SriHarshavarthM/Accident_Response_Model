"""
Generate a sample test video for accident detection demo.
Creates a simple video with moving rectangles to simulate vehicles.
"""
import cv2
import numpy as np
import os

def create_sample_video(output_path="sample_collision.mp4", duration_seconds=10, fps=30):
    """
    Create a simple demo video simulating a road with vehicles.
    This is for testing the video upload and processing pipeline.
    """
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration_seconds * fps
    
    # Road parameters
    road_top = 300
    road_bottom = 500
    
    # Vehicle 1 (red car - moving right)
    car1_x = 100
    car1_speed = 8
    
    # Vehicle 2 (blue car - moving left)
    car2_x = 1100
    car2_speed = -6
    
    collision_frame = total_frames // 2
    collision_happened = False
    
    for frame_num in range(total_frames):
        # Create frame with road
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Sky (dark blue gradient)
        for y in range(road_top):
            intensity = int(40 + (y / road_top) * 30)
            frame[y, :] = [intensity + 20, intensity, intensity]
        
        # Road (gray)
        frame[road_top:road_bottom, :] = [80, 80, 80]
        
        # Road lines (white dashed)
        road_center = (road_top + road_bottom) // 2
        for x in range(0, width, 80):
            cv2.line(frame, (x, road_center), (x + 40, road_center), (255, 255, 255), 3)
        
        # Grass (green)
        frame[road_bottom:, :] = [34, 139, 34]
        
        # Move vehicles
        if frame_num < collision_frame:
            car1_x += car1_speed
            car2_x += car2_speed
        elif frame_num == collision_frame:
            collision_happened = True
            # Collision position
            collision_x = (car1_x + car2_x) // 2
            car1_x = collision_x - 50
            car2_x = collision_x + 50
        else:
            # After collision - vehicles stopped with slight movement
            if frame_num % 10 < 5:
                frame = cv2.addWeighted(frame, 0.9, np.zeros_like(frame), 0.1, 0)
        
        # Draw Vehicle 1 (Red)
        car1_rect = (car1_x, road_top + 40, car1_x + 100, road_top + 100)
        cv2.rectangle(frame, (car1_rect[0], car1_rect[1]), 
                     (car1_rect[2], car1_rect[3]), (0, 0, 255), -1)
        cv2.rectangle(frame, (car1_rect[0], car1_rect[1]), 
                     (car1_rect[2], car1_rect[3]), (0, 0, 180), 2)
        # Windows
        cv2.rectangle(frame, (car1_x + 10, road_top + 50), 
                     (car1_x + 40, road_top + 70), (200, 200, 200), -1)
        cv2.rectangle(frame, (car1_x + 60, road_top + 50), 
                     (car1_x + 90, road_top + 70), (200, 200, 200), -1)
        
        # Draw Vehicle 2 (Blue)
        car2_rect = (car2_x, road_top + 100, car2_x + 100, road_top + 160)
        cv2.rectangle(frame, (car2_rect[0], car2_rect[1]), 
                     (car2_rect[2], car2_rect[3]), (255, 100, 0), -1)
        cv2.rectangle(frame, (car2_rect[0], car2_rect[1]), 
                     (car2_rect[2], car2_rect[3]), (180, 80, 0), 2)
        # Windows
        cv2.rectangle(frame, (car2_x + 10, road_top + 110), 
                     (car2_x + 40, road_top + 130), (200, 200, 200), -1)
        cv2.rectangle(frame, (car2_x + 60, road_top + 110), 
                     (car2_x + 90, road_top + 130), (200, 200, 200), -1)
        
        # Collision effects
        if collision_happened:
            collision_x = (car1_x + car2_x) // 2 + 50
            collision_y = road_top + 100
            
            # Explosion effect (orange circles)
            if frame_num < collision_frame + 20:
                radius = (frame_num - collision_frame) * 5
                alpha = 1 - (frame_num - collision_frame) / 20
                overlay = frame.copy()
                cv2.circle(overlay, (collision_x, collision_y), radius, (0, 165, 255), -1)
                cv2.circle(overlay, (collision_x, collision_y), radius // 2, (0, 255, 255), -1)
                frame = cv2.addWeighted(overlay, alpha * 0.5, frame, 1 - alpha * 0.5, 0)
            
            # Debris particles
            np.random.seed(frame_num)
            for _ in range(10):
                dx = np.random.randint(-100, 100)
                dy = np.random.randint(-50, 50)
                size = np.random.randint(2, 6)
                cv2.circle(frame, (collision_x + dx, collision_y + dy), size, (100, 100, 100), -1)
        
        # Add timestamp overlay
        timestamp = f"CAM-001 | {frame_num // fps:02d}:{(frame_num % fps) * 2:02d}"
        cv2.putText(frame, timestamp, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 255, 255), 2)
        
        # Add "LIVE" indicator
        if frame_num % 30 < 20:
            cv2.circle(frame, (width - 80, 35), 8, (0, 0, 255), -1)
            cv2.putText(frame, "LIVE", (width - 65, 45), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (255, 255, 255), 2)
        
        # Add collision alert after it happens
        if collision_happened and frame_num < collision_frame + 90:
            alert_alpha = min(1.0, (frame_num - collision_frame) / 10)
            
            # Red flashing border
            if frame_num % 10 < 5:
                cv2.rectangle(frame, (0, 0), (width-1, height-1), (0, 0, 255), 10)
            
            # Alert text
            cv2.rectangle(frame, (width//2 - 200, 80), (width//2 + 200, 140), (0, 0, 180), -1)
            cv2.putText(frame, "⚠ COLLISION DETECTED", (width//2 - 180, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Sample video created: {output_path}")
    print(f"   Duration: {duration_seconds} seconds")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    return output_path


if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "sample_collision.mp4")
    create_sample_video(output_path)
