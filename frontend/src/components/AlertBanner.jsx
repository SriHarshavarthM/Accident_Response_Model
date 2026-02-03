import { X, AlertTriangle } from 'lucide-react';
import './AlertBanner.css';

function AlertBanner({ alert, onDismiss }) {
    if (!alert) return null;

    return (
        <div className="alert-banner critical-flash">
            <div className="alert-content">
                <AlertTriangle size={24} />
                <div className="alert-text">
                    <strong>🚨 CRITICAL INCIDENT DETECTED</strong>
                    <span>
                        {alert.incident_type} at {alert.location || 'Unknown Location'} -
                        Confidence: {(alert.confidence * 100).toFixed(0)}%
                    </span>
                </div>
            </div>

            <div className="alert-actions">
                <button className="btn btn-danger" onClick={() => window.location.href = `/incident/${alert.id}`}>
                    View Incident
                </button>
                <button className="btn btn-outline" onClick={onDismiss}>
                    <X size={16} />
                </button>
            </div>
        </div>
    );
}

export default AlertBanner;
