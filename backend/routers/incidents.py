"""
Incident Management Router
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import os
import shutil

from database import get_db
from models import Incident, Camera, IncidentStatus, SeverityLevel
from schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, 
    IncidentDetailResponse, DashboardStats
)
from config import get_settings

router = APIRouter(prefix="/incidents", tags=["Incidents"])
settings = get_settings()


def generate_incident_id():
    """Generate unique incident ID"""
    now = datetime.now()
    return f"INC-{now.year}-{uuid.uuid4().hex[:6].upper()}"


@router.get("/", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[IncidentStatus] = None,
    severity: Optional[SeverityLevel] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all incidents with optional filters"""
    query = db.query(Incident).order_by(desc(Incident.created_at))
    
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    
    return query.offset(offset).limit(limit).all()


@router.get("/active", response_model=List[IncidentResponse])
def get_active_incidents(db: Session = Depends(get_db)):
    """Get all active (non-closed) incidents"""
    return db.query(Incident).filter(
        Incident.status.notin_([IncidentStatus.CLOSED, IncidentStatus.FALSE_ALARM])
    ).order_by(desc(Incident.created_at)).all()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    active = db.query(Incident).filter(
        Incident.status.notin_([IncidentStatus.CLOSED, IncidentStatus.FALSE_ALARM])
    ).count()
    
    today_count = db.query(Incident).filter(
        Incident.created_at >= today
    ).count()
    
    pending = db.query(Incident).filter(
        Incident.status == IncidentStatus.DETECTED
    ).count()
    
    dispatched = db.query(Incident).filter(
        Incident.status == IncidentStatus.DISPATCHED
    ).count()
    
    reported = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.REPORTED, IncidentStatus.DISPATCHED, IncidentStatus.CLOSED])
    ).count()
    
    return DashboardStats(
        active_incidents=active,
        today_incidents=today_count,
        pending_verification=pending,
        dispatched_ambulances=dispatched,
        police_reports_sent=reported
    )


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get incident by ID with full details"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=IncidentResponse)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    """Create new incident (typically called by ML engine)"""
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == incident.camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db_incident = Incident(
        incident_id=generate_incident_id(),
        camera_id=incident.camera_id,
        incident_type=incident.incident_type,
        severity=incident.severity,
        confidence_score=incident.confidence_score,
        vehicles_involved=incident.vehicles_involved,
        pedestrian_involved=incident.pedestrian_involved,
        description=incident.description,
        video_clip_path=incident.video_clip_path,
        snapshots=incident.snapshots,
        bounding_boxes=incident.bounding_boxes,
        status=IncidentStatus.DETECTED
    )
    
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    
    return db_incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int, 
    update: IncidentUpdate, 
    db: Session = Depends(get_db)
):
    """Update incident status or details"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    update_data = update.model_dump(exclude_unset=True)
    
    if update.status == IncidentStatus.VERIFIED and update.verified_by:
        update_data["verified_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(incident, key, value)
    
    db.commit()
    db.refresh(incident)
    
    return incident


@router.post("/{incident_id}/verify")
def verify_incident(
    incident_id: int,
    verified_by: str,
    db: Session = Depends(get_db)
):
    """Mark incident as verified by operator"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = IncidentStatus.VERIFIED
    incident.verified_by = verified_by
    incident.verified_at = datetime.now()
    
    db.commit()
    
    return {"message": "Incident verified successfully", "incident_id": incident.incident_id}


@router.post("/{incident_id}/false-alarm")
def mark_false_alarm(
    incident_id: int,
    marked_by: str,
    db: Session = Depends(get_db)
):
    """Mark incident as false alarm"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = IncidentStatus.FALSE_ALARM
    incident.verified_by = marked_by
    incident.verified_at = datetime.now()
    
    db.commit()
    
    return {"message": "Incident marked as false alarm", "incident_id": incident.incident_id}


@router.post("/{incident_id}/close")
def close_incident(
    incident_id: int,
    closed_by: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Close an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = IncidentStatus.CLOSED
    if notes:
        incident.description = (incident.description or "") + f"\n\nClosure notes: {notes}"
    
    db.commit()
    
    return {"message": "Incident closed", "incident_id": incident.incident_id}


@router.post("/upload-video")
async def upload_video(
    camera_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload video for ML processing and incident detection"""
    # Validate file type
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: MP4, AVI, MOV, MKV")
    
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")
    
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_id = uuid.uuid4().hex
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process video and detect incidents
    from services.video_processor import process_video_async
    import asyncio
    
    try:
        result = await process_video_async(file_path, camera_id, db)
        
        if result.get("detected"):
            return {
                "message": "🚨 INCIDENT DETECTED!",
                "file_id": file_id,
                "incident_created": True,
                "incident_id": result.get("incident_id"),
                "incident_db_id": result.get("incident_db_id"),
                "incident_type": result.get("incident_type"),
                "severity": result.get("severity"),
                "confidence_score": result.get("confidence_score"),
                "description": result.get("description"),
                "status": "incident_created"
            }
        else:
            return {
                "message": "Video analyzed - No incidents detected",
                "file_id": file_id,
                "incident_created": False,
                "analysis_summary": result.get("analysis_summary"),
                "status": "no_incident"
            }
    except Exception as e:
        # Log error but still return success for upload
        print(f"Error processing video: {e}")
        return {
            "message": "Video uploaded but processing failed",
            "file_id": file_id,
            "file_path": file_path,
            "camera_id": camera_id,
            "status": "processing_error",
            "error": str(e)
        }

