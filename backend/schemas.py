"""
Pydantic Schemas for API Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    VERIFIED = "VERIFIED"
    REPORTED = "REPORTED"
    DISPATCHED = "DISPATCHED"
    CLOSED = "CLOSED"
    FALSE_ALARM = "FALSE_ALARM"


class IncidentType(str, Enum):
    VEHICLE_COLLISION = "VEHICLE_COLLISION"
    ROLLOVER = "ROLLOVER"
    MULTI_VEHICLE = "MULTI_VEHICLE"
    PEDESTRIAN_IMPACT = "PEDESTRIAN_IMPACT"
    FIRE_SMOKE = "FIRE_SMOKE"
    OTHER = "OTHER"


class DispatchStatus(str, Enum):
    REQUESTED = "REQUESTED"
    DISPATCHED = "DISPATCHED"
    ARRIVED = "ARRIVED"
    CLOSED = "CLOSED"


# Camera Schemas
class CameraBase(BaseModel):
    camera_id: str
    name: str
    location_address: str
    latitude: float
    longitude: float
    zone: Optional[str] = None
    rtsp_url: Optional[str] = None


class CameraCreate(CameraBase):
    pass


class CameraResponse(CameraBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Incident Schemas
class IncidentBase(BaseModel):
    incident_type: IncidentType
    severity: SeverityLevel
    confidence_score: float = Field(..., ge=0, le=1)
    vehicles_involved: int = 0
    pedestrian_involved: bool = False
    description: Optional[str] = None


class IncidentCreate(IncidentBase):
    camera_id: int
    video_clip_path: Optional[str] = None
    snapshots: List[str] = []
    bounding_boxes: List[dict] = []


class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    description: Optional[str] = None
    verified_by: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: int
    incident_id: str
    camera_id: int
    timestamp: datetime
    status: IncidentStatus
    video_clip_path: Optional[str] = None
    snapshots: List[str] = []
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class IncidentDetailResponse(IncidentResponse):
    camera: Optional[CameraResponse] = None
    dispatch_logs: List["DispatchLogResponse"] = []


# Police Station Schemas
class PoliceStationBase(BaseModel):
    station_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    jurisdiction: str
    contact_phone: str
    email: str
    api_endpoint: Optional[str] = None


class PoliceStationCreate(PoliceStationBase):
    pass


class PoliceStationResponse(PoliceStationBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Ambulance Provider Schemas
class AmbulanceProviderBase(BaseModel):
    provider_id: str
    name: str
    service_type: str
    contact_phone: str
    api_endpoint: Optional[str] = None
    coverage_area: str


class AmbulanceProviderCreate(AmbulanceProviderBase):
    pass


class AmbulanceProviderResponse(AmbulanceProviderBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dispatch Schemas
class DispatchRequest(BaseModel):
    incident_id: int
    service_type: str  # "POLICE" or "AMBULANCE"
    provider_id: Optional[str] = None
    requested_by: str
    notes: Optional[str] = None


class DispatchLogResponse(BaseModel):
    id: int
    incident_id: int
    service_type: str
    provider_id: str
    status: DispatchStatus
    requested_by: str
    requested_at: datetime
    dispatched_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# Report Schemas
class PoliceReportRequest(BaseModel):
    incident_id: int
    police_station_id: int
    additional_notes: Optional[str] = None
    send_method: str = "email"  # email, api, download


class AmbulanceDispatchRequest(BaseModel):
    incident_id: int
    provider_id: Optional[int] = None
    callback_number: str
    operator_id: str
    confirmed: bool = False


# Analytics Schemas
class IncidentStats(BaseModel):
    total_incidents: int
    by_severity: dict
    by_status: dict
    by_zone: dict
    false_positive_rate: float


class DashboardStats(BaseModel):
    active_incidents: int
    today_incidents: int
    pending_verification: int
    dispatched_ambulances: int
    police_reports_sent: int


# WebSocket Message
class WSMessage(BaseModel):
    type: str  # "new_incident", "status_update", "alert"
    data: dict


# Update forward references
IncidentDetailResponse.model_rebuild()
