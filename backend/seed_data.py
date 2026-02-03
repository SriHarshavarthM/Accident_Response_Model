"""
Seed Database with Demo Data
Run this script to populate the database with sample data for testing.
"""
import sys
sys.path.append('.')

from database import SessionLocal, init_db
from models import Camera, PoliceStation, AmbulanceProvider, Incident, IncidentType, SeverityLevel, IncidentStatus
from datetime import datetime, timedelta
import random


def seed_cameras(db):
    """Add demo cameras"""
    cameras = [
        {
            "camera_id": "CAM-001",
            "name": "Highway Cam 1",
            "location_address": "NH-48, Km 45, Gurugram, Haryana",
            "latitude": 28.4595,
            "longitude": 77.0266,
            "zone": "Highway North",
            "is_active": True
        },
        {
            "camera_id": "CAM-002",
            "name": "City Center Junction",
            "location_address": "MG Road, Sector 14, Gurugram",
            "latitude": 28.4715,
            "longitude": 77.0842,
            "zone": "City Center",
            "is_active": True
        },
        {
            "camera_id": "CAM-003",
            "name": "Industrial Area Gate",
            "location_address": "IMT Manesar, Gurugram",
            "latitude": 28.3523,
            "longitude": 76.9378,
            "zone": "Industrial",
            "is_active": True
        },
        {
            "camera_id": "CAM-004",
            "name": "Ring Road Flyover",
            "location_address": "Sohna Road, Gurugram",
            "latitude": 28.4120,
            "longitude": 77.0509,
            "zone": "Highway South",
            "is_active": True
        }
    ]
    
    for cam in cameras:
        existing = db.query(Camera).filter(Camera.camera_id == cam["camera_id"]).first()
        if not existing:
            db.add(Camera(**cam))
            print(f"Added camera: {cam['camera_id']}")
    
    db.commit()


def seed_police_stations(db):
    """Add demo police stations"""
    stations = [
        {
            "station_id": "PS-001",
            "name": "Sector 14 Police Station",
            "address": "Sector 14, Gurugram, Haryana 122001",
            "latitude": 28.4672,
            "longitude": 77.0808,
            "jurisdiction": "Sector 14, Sector 15, City Center",
            "contact_phone": "+91-124-2341001",
            "email": "ps.sector14.gurugram@haryana.gov.in"
        },
        {
            "station_id": "PS-002",
            "name": "IMT Manesar Police Station",
            "address": "IMT Manesar, Gurugram, Haryana 122050",
            "latitude": 28.3589,
            "longitude": 76.9412,
            "jurisdiction": "IMT Manesar, Industrial Area",
            "contact_phone": "+91-124-2341002",
            "email": "ps.imt.manesar@haryana.gov.in"
        },
        {
            "station_id": "PS-003",
            "name": "Highway Police Station",
            "address": "NH-48, Bilaspur Chowk, Gurugram",
            "latitude": 28.4521,
            "longitude": 77.0123,
            "jurisdiction": "NH-48, Highway North",
            "contact_phone": "+91-124-2341003",
            "email": "ps.highway.gurugram@haryana.gov.in"
        }
    ]
    
    for station in stations:
        existing = db.query(PoliceStation).filter(PoliceStation.station_id == station["station_id"]).first()
        if not existing:
            db.add(PoliceStation(**station))
            print(f"Added police station: {station['station_id']}")
    
    db.commit()


def seed_ambulance_providers(db):
    """Add demo ambulance providers"""
    providers = [
        {
            "provider_id": "AMB-108",
            "name": "108 Emergency Ambulance",
            "service_type": "Government",
            "contact_phone": "108",
            "coverage_area": "All Haryana",
            "is_active": True
        },
        {
            "provider_id": "AMB-ERSS",
            "name": "ERSS-112",
            "service_type": "Government (Unified)",
            "contact_phone": "112",
            "coverage_area": "All India",
            "is_active": True
        },
        {
            "provider_id": "AMB-APOLLO",
            "name": "Apollo Ambulance Service",
            "service_type": "Private Hospital",
            "contact_phone": "+91-124-6765000",
            "coverage_area": "Gurugram, Delhi NCR",
            "is_active": True
        }
    ]
    
    for prov in providers:
        existing = db.query(AmbulanceProvider).filter(AmbulanceProvider.provider_id == prov["provider_id"]).first()
        if not existing:
            db.add(AmbulanceProvider(**prov))
            print(f"Added ambulance provider: {prov['provider_id']}")
    
    db.commit()


def seed_sample_incidents(db):
    """Add sample incidents for testing"""
    cameras = db.query(Camera).all()
    if not cameras:
        print("No cameras found. Run camera seeding first.")
        return
    
    incidents_data = [
        {
            "incident_type": IncidentType.VEHICLE_COLLISION,
            "severity": SeverityLevel.CRITICAL,
            "confidence_score": 0.94,
            "status": IncidentStatus.DETECTED,
            "vehicles_involved": 2,
            "pedestrian_involved": False,
            "description": "High-speed collision detected at highway interchange. Two vehicles involved with significant damage."
        },
        {
            "incident_type": IncidentType.MULTI_VEHICLE,
            "severity": SeverityLevel.HIGH,
            "confidence_score": 0.88,
            "status": IncidentStatus.VERIFIED,
            "vehicles_involved": 3,
            "pedestrian_involved": False,
            "description": "Multi-vehicle pile-up detected. Chain reaction collision involving three vehicles."
        },
        {
            "incident_type": IncidentType.PEDESTRIAN_IMPACT,
            "severity": SeverityLevel.HIGH,
            "confidence_score": 0.91,
            "status": IncidentStatus.REPORTED,
            "vehicles_involved": 1,
            "pedestrian_involved": True,
            "description": "Pedestrian hit by vehicle at crosswalk. Single vehicle involved."
        },
        {
            "incident_type": IncidentType.ROLLOVER,
            "severity": SeverityLevel.MEDIUM,
            "confidence_score": 0.82,
            "status": IncidentStatus.DETECTED,
            "vehicles_involved": 1,
            "pedestrian_involved": False,
            "description": "Vehicle rollover detected on highway. Single vehicle, driver condition unknown."
        }
    ]
    
    for i, inc_data in enumerate(incidents_data):
        camera = random.choice(cameras)
        
        incident = Incident(
            incident_id=f"INC-2026-{random.randint(100000, 999999):06X}",
            camera_id=camera.id,
            timestamp=datetime.now() - timedelta(minutes=random.randint(5, 120)),
            **inc_data
        )
        db.add(incident)
        print(f"Added incident: {incident.incident_id}")
    
    db.commit()


def main():
    """Main seeding function"""
    print("=" * 50)
    print("Accident Incident Responder - Database Seeding")
    print("=" * 50)
    
    # Initialize database
    init_db()
    print("Database initialized.\n")
    
    db = SessionLocal()
    
    try:
        print("Seeding cameras...")
        seed_cameras(db)
        
        print("\nSeeding police stations...")
        seed_police_stations(db)
        
        print("\nSeeding ambulance providers...")
        seed_ambulance_providers(db)
        
        print("\nSeeding sample incidents...")
        seed_sample_incidents(db)
        
        print("\n" + "=" * 50)
        print("Seeding complete!")
        print("=" * 50)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
