import { useNavigate } from 'react-router-dom';
import { Clock, MapPin, Car, AlertTriangle } from 'lucide-react';
import './IncidentCard.css';

function IncidentCard({ incident }) {
    const navigate = useNavigate();

    const getSeverityClass = (severity) => {
        return `badge-${severity.toLowerCase()}`;
    };

    const getStatusColor = (status) => {
        return `status-${status.toLowerCase()}`;
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = (now - date) / 1000 / 60; // minutes

        if (diff < 1) return 'Just now';
        if (diff < 60) return `${Math.floor(diff)} min ago`;
        if (diff < 1440) return `${Math.floor(diff / 60)} hr ago`;
        return date.toLocaleDateString();
    };

    const isCritical = incident.severity === 'CRITICAL';

    return (
        <div
            className={`incident-card ${isCritical ? 'critical-flash' : ''}`}
            onClick={() => navigate(`/incident/${incident.id}`)}
        >
            <div className="incident-header">
                <span className={`badge ${getSeverityClass(incident.severity)}`}>
                    <AlertTriangle size={12} />
                    {incident.severity}
                </span>
                <span className={`status ${getStatusColor(incident.status)}`}>
                    {incident.status}
                </span>
            </div>

            <div className="incident-body">
                <h4 className="incident-type">
                    {incident.incident_type?.replace(/_/g, ' ')}
                </h4>
                <p className="incident-id">{incident.incident_id}</p>
            </div>

            <div className="incident-meta">
                <div className="meta-item">
                    <Clock size={14} />
                    <span>{formatTime(incident.timestamp)}</span>
                </div>
                <div className="meta-item">
                    <Car size={14} />
                    <span>{incident.vehicles_involved} vehicle(s)</span>
                </div>
            </div>

            <div className="incident-footer">
                <div className="confidence-bar">
                    <div
                        className="confidence-fill"
                        style={{ width: `${incident.confidence_score * 100}%` }}
                    ></div>
                </div>
                <span className="confidence-text">
                    {(incident.confidence_score * 100).toFixed(0)}% confidence
                </span>
            </div>
        </div>
    );
}

export default IncidentCard;
