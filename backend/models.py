"""
Database Models for Accident Incident Responder
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    VERIFIED = "VERIFIED"
    REPORTED = "REPORTED"
    DISPATCHED = "DISPATCHED"
    CLOSED = "CLOSED"
    FALSE_ALARM = "FALSE_ALARM"


class IncidentType(str, enum.Enum):
    VEHICLE_COLLISION = "VEHICLE_COLLISION"
    ROLLOVER = "ROLLOVER"
    MULTI_VEHICLE = "MULTI_VEHICLE"
    PEDESTRIAN_IMPACT = "PEDESTRIAN_IMPACT"
    FIRE_SMOKE = "FIRE_SMOKE"
    OTHER = "OTHER"


class DispatchStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    DISPATCHED = "DISPATCHED"
    ARRIVED = "ARRIVED"
    CLOSED = "CLOSED"


class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    location_address = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    zone = Column(String(100))
    rtsp_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    incidents = relationship("Incident", back_populates="camera")


class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    incident_type = Column(Enum(IncidentType))
    severity = Column(Enum(SeverityLevel))
    confidence_score = Column(Float)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.DETECTED)
    
    vehicles_involved = Column(Integer, default=0)
    pedestrian_involved = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    
    # Media
    video_clip_path = Column(String(500), nullable=True)
    snapshots = Column(JSON, default=list)  # List of snapshot paths
    bounding_boxes = Column(JSON, default=list)  # Detection bounding boxes
    
    # Metadata
    verified_by = Column(String(100), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    camera = relationship("Camera", back_populates="incidents")
    dispatch_logs = relationship("DispatchLog", back_populates="incident")


class PoliceStation(Base):
    __tablename__ = "police_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    address = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    jurisdiction = Column(String(200))
    
    contact_phone = Column(String(20))
    email = Column(String(100))
    api_endpoint = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AmbulanceProvider(Base):
    __tablename__ = "ambulance_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String(50), unique=True, index=True)
    name = Column(String(200))
    service_type = Column(String(100))  # 108, ERSS-112, Private
    
    contact_phone = Column(String(20))
    api_endpoint = Column(String(500), nullable=True)
    coverage_area = Column(String(500))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DispatchLog(Base):
    __tablename__ = "dispatch_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    
    service_type = Column(String(50))  # "POLICE" or "AMBULANCE"
    provider_id = Column(String(50))
    status = Column(Enum(DispatchStatus), default=DispatchStatus.REQUESTED)
    
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    
    requested_by = Column(String(100))
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    arrived_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    incident = relationship("Incident", back_populates="dispatch_logs")
