"""
Camera Management Router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Camera
from schemas import CameraCreate, CameraResponse

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("/", response_model=List[CameraResponse])
def get_cameras(
    zone: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all cameras with optional filters"""
    query = db.query(Camera)
    
    if active_only:
        query = query.filter(Camera.is_active == True)
    if zone:
        query = query.filter(Camera.zone == zone)
    
    return query.all()


@router.get("/zones")
def get_zones(db: Session = Depends(get_db)):
    """Get list of all zones"""
    zones = db.query(Camera.zone).distinct().all()
    return [z[0] for z in zones if z[0]]


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """Get camera by ID"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/", response_model=CameraResponse)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    """Register a new camera"""
    # Check for duplicate camera_id
    existing = db.query(Camera).filter(Camera.camera_id == camera.camera_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Camera ID already exists")
    
    db_camera = Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    
    return db_camera


@router.patch("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    name: Optional[str] = None,
    location_address: Optional[str] = None,
    zone: Optional[str] = None,
    rtsp_url: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update camera details"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if name is not None:
        camera.name = name
    if location_address is not None:
        camera.location_address = location_address
    if zone is not None:
        camera.zone = zone
    if rtsp_url is not None:
        camera.rtsp_url = rtsp_url
    if is_active is not None:
        camera.is_active = is_active
    
    db.commit()
    db.refresh(camera)
    
    return camera


@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    """Deactivate a camera"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera.is_active = False
    db.commit()
    
    return {"message": "Camera deactivated successfully"}
