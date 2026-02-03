"""
Notification Service
Handles email sending and API calls for police reports and ambulance dispatch
"""
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import json
import logging
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def send_police_report(email: str, report_data: dict):
    """
    Send police report via email.
    In demo mode, just logs the action.
    """
    logger.info(f"Sending police report to: {email}")
    
    if not settings.SMTP_HOST:
        # Demo mode - just log
        logger.info(f"[DEMO MODE] Police report would be sent to {email}")
        logger.info(f"Report data: {json.dumps(report_data, indent=2, default=str)}")
        return {"status": "demo", "message": "Email not configured - report logged"}
    
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = email
        msg['Subject'] = f"Incident Report - {report_data['incident_details']['incident_id']}"
        
        # Email body
        body = f"""
        PRELIMINARY INCIDENT INTIMATION
        
        Incident ID: {report_data['incident_details']['incident_id']}
        Type: {report_data['incident_details']['incident_type']}
        Severity: {report_data['incident_details']['severity']}
        Location: {report_data['location']['address']}
        
        This is an automated notification from the Accident Incident Responder System.
        Please verify and take appropriate action.
        
        Full report attached.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach JSON report
        attachment = MIMEApplication(json.dumps(report_data, indent=2, default=str).encode())
        attachment['Content-Disposition'] = f'attachment; filename="incident_report_{report_data["incident_details"]["incident_id"]}.json"'
        msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Police report sent successfully to {email}")
        return {"status": "sent", "email": email}
        
    except Exception as e:
        logger.error(f"Failed to send police report: {str(e)}")
        return {"status": "error", "message": str(e)}


async def dispatch_ambulance(provider, dispatch_data: dict):
    """
    Dispatch ambulance via API call or Twilio.
    In demo mode, just logs the action.
    """
    logger.info(f"Dispatching ambulance via {provider.name}")
    
    # Demo mode - just log
    if not provider.api_endpoint and not settings.TWILIO_ACCOUNT_SID:
        logger.info(f"[DEMO MODE] Ambulance dispatch to {provider.name}")
        logger.info(f"Dispatch data: {json.dumps(dispatch_data, indent=2, default=str)}")
        return {
            "status": "demo",
            "message": "Ambulance API not configured - dispatch logged",
            "provider": provider.name
        }
    
    # Try API endpoint if available
    if provider.api_endpoint:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    provider.api_endpoint,
                    json=dispatch_data,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Ambulance dispatched via API: {response.json()}")
                return {
                    "status": "dispatched",
                    "provider": provider.name,
                    "response": response.json()
                }
        except Exception as e:
            logger.error(f"API dispatch failed: {str(e)}")
            # Fall through to Twilio if available
    
    # Try Twilio if configured
    if settings.TWILIO_ACCOUNT_SID:
        try:
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message_body = f"""
            🚨 EMERGENCY AMBULANCE REQUEST
            
            Incident: {dispatch_data['incident_id']}
            Severity: {dispatch_data['severity']}
            Location: {dispatch_data['location']['address']}
            Coordinates: {dispatch_data['location']['latitude']}, {dispatch_data['location']['longitude']}
            
            Callback: {dispatch_data['callback_number']}
            """
            
            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=provider.contact_phone
            )
            
            logger.info(f"Ambulance notified via SMS: {message.sid}")
            return {
                "status": "notified",
                "provider": provider.name,
                "message_sid": message.sid
            }
            
        except Exception as e:
            logger.error(f"Twilio dispatch failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    return {"status": "no_method", "message": "No dispatch method configured"}


async def send_alert_notification(incident_data: dict, recipients: list):
    """
    Send real-time alert notifications (for future WebSocket/Push implementation)
    """
    logger.info(f"Alert notification for incident: {incident_data.get('incident_id')}")
    
    # This would integrate with:
    # - WebSocket for dashboard alerts
    # - Push notifications for mobile app
    # - SMS for critical alerts
    
    return {
        "status": "queued",
        "incident_id": incident_data.get('incident_id'),
        "recipients": len(recipients)
    }
