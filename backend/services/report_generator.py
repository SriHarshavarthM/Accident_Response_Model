"""
Report Generator Service
Generates structured incident reports for police stations
"""
from datetime import datetime
from typing import Optional
import json
import os
from config import get_settings

settings = get_settings()


def generate_incident_report(
    incident,
    camera,
    police_station=None,
    additional_notes: Optional[str] = None
) -> dict:
    """
    Generate a structured incident report (JSON format).
    This is a PRELIMINARY INCIDENT INTIMATION, not an official FIR.
    """
    
    report = {
        "document_type": "PRELIMINARY_INCIDENT_INTIMATION",
        "disclaimer": "This is an AI-generated preliminary report for information purposes only. It does NOT constitute an official First Information Report (FIR). Official action requires human verification.",
        
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "generated_by": "Accident Incident Responder System",
            "version": "1.0"
        },
        
        "incident_details": {
            "incident_id": incident.incident_id,
            "timestamp": incident.timestamp.isoformat() if incident.timestamp else None,
            "created_at": incident.created_at.isoformat() if incident.created_at else None,
            "incident_type": incident.incident_type.value if incident.incident_type else None,
            "severity": incident.severity.value if incident.severity else None,
            "confidence_score": incident.confidence_score,
            "status": incident.status.value if incident.status else None
        },
        
        "location": {
            "camera_id": camera.camera_id if camera else None,
            "address": camera.location_address if camera else None,
            "zone": camera.zone if camera else None,
            "coordinates": {
                "latitude": camera.latitude if camera else None,
                "longitude": camera.longitude if camera else None
            }
        },
        
        "accident_details": {
            "vehicles_involved": incident.vehicles_involved,
            "pedestrian_involved": incident.pedestrian_involved,
            "ai_description": incident.description or "AI-detected incident requiring human verification."
        },
        
        "evidence": {
            "video_clip": incident.video_clip_path,
            "snapshots": incident.snapshots or [],
            "bounding_boxes": incident.bounding_boxes or []
        },
        
        "verification": {
            "verified": incident.verified_by is not None,
            "verified_by": incident.verified_by,
            "verified_at": incident.verified_at.isoformat() if incident.verified_at else None
        },
        
        "additional_information": {
            "notes": additional_notes,
            "human_verification_required": True,
            "action_required": "Please verify incident and take appropriate action as per protocol."
        }
    }
    
    if police_station:
        report["recipient"] = {
            "station_id": police_station.station_id,
            "station_name": police_station.name,
            "jurisdiction": police_station.jurisdiction,
            "contact": police_station.contact_phone,
            "email": police_station.email
        }
    
    return report


def generate_pdf_report(incident, camera, police_station=None, additional_notes=None) -> str:
    """
    Generate PDF version of the incident report.
    Returns the file path to the generated PDF.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    
    filename = f"incident_report_{incident.incident_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(settings.REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        spaceAfter=12
    )
    story.append(Paragraph("PRELIMINARY INCIDENT INTIMATION REPORT", title_style))
    story.append(Spacer(1, 0.25*inch))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.red,
        spaceAfter=12
    )
    story.append(Paragraph(
        "<b>DISCLAIMER:</b> This is an AI-generated preliminary report for information purposes only. "
        "It does NOT constitute an official First Information Report (FIR).",
        disclaimer_style
    ))
    story.append(Spacer(1, 0.25*inch))
    
    # Incident Details Table
    incident_data = [
        ["Incident ID", incident.incident_id],
        ["Date/Time", str(incident.timestamp)],
        ["Type", incident.incident_type.value if incident.incident_type else "N/A"],
        ["Severity", incident.severity.value if incident.severity else "N/A"],
        ["Confidence", f"{incident.confidence_score * 100:.1f}%"],
        ["Vehicles Involved", str(incident.vehicles_involved)],
        ["Pedestrian Involved", "Yes" if incident.pedestrian_involved else "No"],
    ]
    
    t = Table(incident_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(Paragraph("<b>Incident Details</b>", styles['Heading2']))
    story.append(t)
    story.append(Spacer(1, 0.25*inch))
    
    # Location
    if camera:
        location_data = [
            ["Camera ID", camera.camera_id],
            ["Address", camera.location_address or "N/A"],
            ["Zone", camera.zone or "N/A"],
            ["Coordinates", f"{camera.latitude}, {camera.longitude}"],
        ]
        t = Table(location_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(Paragraph("<b>Location</b>", styles['Heading2']))
        story.append(t)
        story.append(Spacer(1, 0.25*inch))
    
    # Description
    if incident.description:
        story.append(Paragraph("<b>AI-Generated Description</b>", styles['Heading2']))
        story.append(Paragraph(incident.description, styles['Normal']))
        story.append(Spacer(1, 0.25*inch))
    
    # Additional Notes
    if additional_notes:
        story.append(Paragraph("<b>Additional Notes</b>", styles['Heading2']))
        story.append(Paragraph(additional_notes, styles['Normal']))
        story.append(Spacer(1, 0.25*inch))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey
    )
    story.append(Paragraph(
        f"Report generated by Accident Incident Responder System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        footer_style
    ))
    
    doc.build(story)
    
    return filepath
