"""
Dispatch Router - Police Reporting and Ambulance Dispatch
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import math

from database import get_db
from models import (
    Incident, PoliceStation, AmbulanceProvider, DispatchLog, 
    IncidentStatus, DispatchStatus, Camera
)
from schemas import (
    PoliceStationCreate, PoliceStationResponse,
    AmbulanceProviderCreate, AmbulanceProviderResponse,
    PoliceReportRequest, AmbulanceDispatchRequest,
    DispatchLogResponse
)
from services.report_generator import generate_incident_report
from services.notification import send_police_report, dispatch_ambulance

router = APIRouter(prefix="/dispatch", tags=["Dispatch"])


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points (Haversine formula)"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


# ============ Police Stations ============

@router.get("/police-stations", response_model=List[PoliceStationResponse])
def get_police_stations(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all police stations"""
    query = db.query(PoliceStation)
    if active_only:
        query = query.filter(PoliceStation.is_active == True)
    return query.all()


@router.post("/police-stations", response_model=PoliceStationResponse)
def create_police_station(
    station: PoliceStationCreate,
    db: Session = Depends(get_db)
):
    """Register a police station"""
    db_station = PoliceStation(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station


@router.get("/police-stations/nearest/{incident_id}", response_model=PoliceStationResponse)
def get_nearest_police_station(incident_id: int, db: Session = Depends(get_db)):
    """Get nearest police station for an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    camera = db.query(Camera).filter(Camera.id == incident.camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    stations = db.query(PoliceStation).filter(PoliceStation.is_active == True).all()
    if not stations:
        raise HTTPException(status_code=404, detail="No police stations found")
    
    nearest = min(stations, key=lambda s: calculate_distance(
        camera.latitude, camera.longitude, s.latitude, s.longitude
    ))
    
    return nearest


# ============ Ambulance Providers ============

@router.get("/ambulance-providers", response_model=List[AmbulanceProviderResponse])
def get_ambulance_providers(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all ambulance providers"""
    query = db.query(AmbulanceProvider)
    if active_only:
        query = query.filter(AmbulanceProvider.is_active == True)
    return query.all()


@router.post("/ambulance-providers", response_model=AmbulanceProviderResponse)
def create_ambulance_provider(
    provider: AmbulanceProviderCreate,
    db: Session = Depends(get_db)
):
    """Register an ambulance provider"""
    db_provider = AmbulanceProvider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


# ============ Police Report ============

@router.post("/send-police-report")
async def send_report_to_police(
    request: PoliceReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send incident report to police station.
    This generates a preliminary incident intimation (NOT an FIR).
    """
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if incident.status == IncidentStatus.DETECTED:
        raise HTTPException(status_code=400, detail="Incident must be verified before reporting")
    
    station = db.query(PoliceStation).filter(PoliceStation.id == request.police_station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Police station not found")
    
    camera = db.query(Camera).filter(Camera.id == incident.camera_id).first()
    
    # Generate report
    report_data = generate_incident_report(incident, camera, station, request.additional_notes)
    
    # Create dispatch log
    dispatch_log = DispatchLog(
        incident_id=incident.id,
        service_type="POLICE",
        provider_id=station.station_id,
        status=DispatchStatus.REQUESTED,
        request_payload=report_data,
        requested_by="operator"  # Should come from auth
    )
    db.add(dispatch_log)
    
    # Update incident status
    incident.status = IncidentStatus.REPORTED
    db.commit()
    
    # Send report in background
    if request.send_method == "email":
        background_tasks.add_task(send_police_report, station.email, report_data)
    
    return {
        "message": "Police report generated and sent",
        "incident_id": incident.incident_id,
        "police_station": station.name,
        "report": report_data,
        "send_method": request.send_method
    }


@router.get("/download-report/{incident_id}")
def download_incident_report(incident_id: int, db: Session = Depends(get_db)):
    """Download incident report as JSON"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    camera = db.query(Camera).filter(Camera.id == incident.camera_id).first()
    
    report_data = generate_incident_report(incident, camera, None, None)
    
    return report_data


# ============ Ambulance Dispatch ============

@router.post("/ambulance")
async def dispatch_ambulance_service(
    request: AmbulanceDispatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Dispatch ambulance for an incident.
    REQUIRES operator confirmation (confirmed=True).
    """
    if not request.confirmed:
        raise HTTPException(
            status_code=400, 
            detail="Ambulance dispatch requires operator confirmation. Set confirmed=True after user confirms."
        )
    
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Get camera for location
    camera = db.query(Camera).filter(Camera.id == incident.camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera location not found")
    
    # Get provider
    provider = None
    if request.provider_id:
        provider = db.query(AmbulanceProvider).filter(
            AmbulanceProvider.id == request.provider_id
        ).first()
    else:
        # Get first active provider
        provider = db.query(AmbulanceProvider).filter(
            AmbulanceProvider.is_active == True
        ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="No ambulance provider available")
    
    # Prepare dispatch data
    dispatch_data = {
        "incident_id": incident.incident_id,
        "severity": incident.severity.value,
        "location": {
            "address": camera.location_address,
            "latitude": camera.latitude,
            "longitude": camera.longitude
        },
        "callback_number": request.callback_number,
        "snapshot_url": incident.snapshots[0] if incident.snapshots else None,
        "description": f"{incident.incident_type.value} - {incident.vehicles_involved} vehicle(s) involved"
    }
    
    # Create dispatch log
    dispatch_log = DispatchLog(
        incident_id=incident.id,
        service_type="AMBULANCE",
        provider_id=provider.provider_id,
        status=DispatchStatus.DISPATCHED,
        request_payload=dispatch_data,
        requested_by=request.operator_id,
        dispatched_at=datetime.now()
    )
    db.add(dispatch_log)
    
    # Update incident status
    incident.status = IncidentStatus.DISPATCHED
    db.commit()
    
    # Dispatch in background (API call or Twilio)
    background_tasks.add_task(dispatch_ambulance, provider, dispatch_data)
    
    return {
        "message": "Ambulance dispatched successfully",
        "incident_id": incident.incident_id,
        "provider": provider.name,
        "status": "DISPATCHED",
        "dispatch_data": dispatch_data
    }


# ============ Dispatch Logs ============

@router.get("/logs/{incident_id}", response_model=List[DispatchLogResponse])
def get_dispatch_logs(incident_id: int, db: Session = Depends(get_db)):
    """Get dispatch logs for an incident"""
    logs = db.query(DispatchLog).filter(DispatchLog.incident_id == incident_id).all()
    return logs


@router.patch("/logs/{log_id}/status")
def update_dispatch_status(
    log_id: int,
    status: DispatchStatus,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update dispatch log status"""
    log = db.query(DispatchLog).filter(DispatchLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dispatch log not found")
    
    log.status = status
    
    if status == DispatchStatus.ARRIVED:
        log.arrived_at = datetime.now()
    elif status == DispatchStatus.CLOSED:
        log.closed_at = datetime.now()
    
    if notes:
        log.notes = notes
    
    db.commit()
    
    return {"message": "Dispatch status updated", "status": status.value}
