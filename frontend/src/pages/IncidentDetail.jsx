import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ArrowLeft,
    CheckCircle,
    XCircle,
    FileText,
    Truck,
    AlertTriangle,
    Clock,
    MapPin,
    Car,
    User,
    Download
} from 'lucide-react';
import api from '../services/api';
import './IncidentDetail.css';

// Demo incident for when backend is not available
const DEMO_INCIDENT = {
    id: 1,
    incident_id: 'INC-2026-A1B2C3',
    incident_type: 'VEHICLE_COLLISION',
    severity: 'CRITICAL',
    confidence_score: 0.94,
    status: 'DETECTED',
    vehicles_involved: 2,
    pedestrian_involved: false,
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    camera_id: 1,
    description: 'High-speed collision detected at highway interchange. Two vehicles involved with significant damage. AI analysis suggests high-impact collision.',
    snapshots: [],
    video_clip_path: null,
    verified_by: null,
    verified_at: null,
    camera: {
        camera_id: 'CAM-001',
        name: 'Highway Cam 1',
        location_address: 'NH-48, Km 45, Gurugram, Haryana',
        zone: 'Highway North'
    }
};

function IncidentDetail() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [incident, setIncident] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showConfirmModal, setShowConfirmModal] = useState(null);
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        fetchIncident();
    }, [id]);

    const fetchIncident = async () => {
        setLoading(true);
        try {
            const data = await api.getIncident(id);
            setIncident(data);
        } catch (err) {
            console.log('Using demo data - backend not available');
            setIncident({ ...DEMO_INCIDENT, id: parseInt(id) });
        } finally {
            setLoading(false);
        }
    };

    const handleVerify = async () => {
        setProcessing(true);
        try {
            await api.verifyIncident(incident.id, 'Operator');
            setIncident(prev => ({ ...prev, status: 'VERIFIED', verified_by: 'Operator' }));
            setShowConfirmModal(null);
        } catch (err) {
            alert('Action simulated - Backend not available');
            setIncident(prev => ({ ...prev, status: 'VERIFIED', verified_by: 'Operator' }));
            setShowConfirmModal(null);
        }
        setProcessing(false);
    };

    const handleFalseAlarm = async () => {
        setProcessing(true);
        try {
            await api.markFalseAlarm(incident.id, 'Operator');
            setIncident(prev => ({ ...prev, status: 'FALSE_ALARM' }));
            setShowConfirmModal(null);
        } catch (err) {
            alert('Action simulated - Backend not available');
            setIncident(prev => ({ ...prev, status: 'FALSE_ALARM' }));
            setShowConfirmModal(null);
        }
        setProcessing(false);
    };

    const handleSendPoliceReport = async () => {
        setProcessing(true);
        try {
            const result = await api.sendPoliceReport(incident.id, 1, 'Sent via dashboard');
            alert(`Report sent successfully to ${result.police_station}`);
            setIncident(prev => ({ ...prev, status: 'REPORTED' }));
            setShowConfirmModal(null);
        } catch (err) {
            alert('Police report simulation - Backend not available\n\nReport would be sent to nearest police station.');
            setIncident(prev => ({ ...prev, status: 'REPORTED' }));
            setShowConfirmModal(null);
        }
        setProcessing(false);
    };

    const handleDispatchAmbulance = async () => {
        setProcessing(true);
        try {
            const result = await api.dispatchAmbulance(incident.id, null, '+91-9876543210', 'Operator');
            alert(`Ambulance dispatched: ${result.provider}`);
            setIncident(prev => ({ ...prev, status: 'DISPATCHED' }));
            setShowConfirmModal(null);
        } catch (err) {
            alert('Ambulance dispatch simulation - Backend not available\n\n🚑 Ambulance would be dispatched to location.');
            setIncident(prev => ({ ...prev, status: 'DISPATCHED' }));
            setShowConfirmModal(null);
        }
        setProcessing(false);
    };

    const handleDownloadReport = async () => {
        try {
            const report = await api.downloadReport(incident.id);
            const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `incident_report_${incident.incident_id}.json`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            // Create demo report
            const demoReport = {
                document_type: 'PRELIMINARY_INCIDENT_INTIMATION',
                incident_details: {
                    incident_id: incident.incident_id,
                    type: incident.incident_type,
                    severity: incident.severity,
                    confidence: incident.confidence_score
                }
            };
            const blob = new Blob([JSON.stringify(demoReport, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `incident_report_${incident.incident_id}.json`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading incident details...</p>
            </div>
        );
    }

    if (!incident) {
        return (
            <div className="error-container">
                <AlertTriangle size={48} />
                <h2>Incident not found</h2>
                <button className="btn btn-primary" onClick={() => navigate('/')}>
                    Back to Dashboard
                </button>
            </div>
        );
    }

    return (
        <div className="incident-detail">
            {/* Header */}
            <div className="detail-header">
                <button className="btn btn-outline back-btn" onClick={() => navigate('/')}>
                    <ArrowLeft size={18} />
                    Back
                </button>

                <div className="detail-title">
                    <span className={`badge badge-${incident.severity.toLowerCase()}`}>
                        {incident.severity}
                    </span>
                    <h1>{incident.incident_id}</h1>
                    <span className={`status-pill status-${incident.status.toLowerCase()}`}>
                        {incident.status}
                    </span>
                </div>
            </div>

            {/* Main Content */}
            <div className="detail-content">
                {/* Video / Snapshot Section */}
                <div className="card media-section">
                    <h3>📹 Incident Media</h3>
                    <div className="video-container">
                        {incident.video_clip_path ? (
                            <video controls>
                                <source src={incident.video_clip_path} type="video/mp4" />
                            </video>
                        ) : (
                            <div className="video-placeholder">
                                <AlertTriangle size={48} />
                                <p>No video clip available</p>
                                <small>Video will appear here when processed by ML engine</small>
                            </div>
                        )}
                    </div>

                    {incident.snapshots && incident.snapshots.length > 0 && (
                        <div className="snapshot-gallery">
                            {incident.snapshots.map((snap, idx) => (
                                <div key={idx} className="snapshot-item">
                                    <img src={snap} alt={`Snapshot ${idx + 1}`} />
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Details Section */}
                <div className="card details-section">
                    <h3>📋 Incident Details</h3>

                    <div className="detail-grid">
                        <div className="detail-item">
                            <div className="detail-label">Type</div>
                            <div className="detail-value">
                                {incident.incident_type?.replace(/_/g, ' ')}
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-label">Confidence</div>
                            <div className="detail-value">
                                {(incident.confidence_score * 100).toFixed(1)}%
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-label">
                                <Car size={14} /> Vehicles
                            </div>
                            <div className="detail-value">{incident.vehicles_involved}</div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-label">
                                <User size={14} /> Pedestrian
                            </div>
                            <div className="detail-value">
                                {incident.pedestrian_involved ? 'Yes' : 'No'}
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-label">
                                <Clock size={14} /> Time
                            </div>
                            <div className="detail-value">
                                {new Date(incident.timestamp).toLocaleString()}
                            </div>
                        </div>

                        <div className="detail-item">
                            <div className="detail-label">
                                <MapPin size={14} /> Location
                            </div>
                            <div className="detail-value">
                                {incident.camera?.location_address || 'Unknown'}
                            </div>
                        </div>
                    </div>

                    {incident.description && (
                        <div className="description-box">
                            <strong>AI Description:</strong>
                            <p>{incident.description}</p>
                        </div>
                    )}

                    {incident.verified_by && (
                        <div className="verification-info">
                            <CheckCircle size={16} />
                            Verified by {incident.verified_by} at {new Date(incident.verified_at).toLocaleString()}
                        </div>
                    )}
                </div>
            </div>

            {/* Action Buttons */}
            <div className="action-buttons">
                {incident.status === 'DETECTED' && (
                    <>
                        <button
                            className="btn btn-success"
                            onClick={() => setShowConfirmModal('verify')}
                        >
                            <CheckCircle size={18} />
                            Verify Incident
                        </button>
                        <button
                            className="btn btn-outline"
                            onClick={() => setShowConfirmModal('false_alarm')}
                        >
                            <XCircle size={18} />
                            Mark False Alarm
                        </button>
                    </>
                )}

                {['DETECTED', 'VERIFIED'].includes(incident.status) && (
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowConfirmModal('police')}
                    >
                        <FileText size={18} />
                        Send Police Report
                    </button>
                )}

                {['HIGH', 'CRITICAL'].includes(incident.severity) &&
                    !['DISPATCHED', 'CLOSED', 'FALSE_ALARM'].includes(incident.status) && (
                        <button
                            className="btn btn-danger"
                            onClick={() => setShowConfirmModal('ambulance')}
                        >
                            <Truck size={18} />
                            Call Ambulance
                        </button>
                    )}

                <button className="btn btn-outline" onClick={handleDownloadReport}>
                    <Download size={18} />
                    Download Report
                </button>
            </div>

            {/* Confirmation Modals */}
            {showConfirmModal && (
                <div className="modal-overlay" onClick={() => setShowConfirmModal(null)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        {showConfirmModal === 'verify' && (
                            <>
                                <div className="modal-header">
                                    <h3>Verify Incident</h3>
                                </div>
                                <div className="confirm-content">
                                    <div className="icon success">
                                        <CheckCircle size={48} />
                                    </div>
                                    <h3>Confirm Incident Verification</h3>
                                    <p>Are you sure this is a valid incident?</p>
                                </div>
                                <div className="modal-footer">
                                    <button className="btn btn-outline" onClick={() => setShowConfirmModal(null)}>
                                        Cancel
                                    </button>
                                    <button className="btn btn-success" onClick={handleVerify} disabled={processing}>
                                        {processing ? 'Processing...' : 'Verify'}
                                    </button>
                                </div>
                            </>
                        )}

                        {showConfirmModal === 'false_alarm' && (
                            <>
                                <div className="modal-header">
                                    <h3>Mark as False Alarm</h3>
                                </div>
                                <div className="confirm-content">
                                    <div className="icon warning">
                                        <XCircle size={48} />
                                    </div>
                                    <h3>Mark as False Alarm?</h3>
                                    <p>This will close the incident without action.</p>
                                </div>
                                <div className="modal-footer">
                                    <button className="btn btn-outline" onClick={() => setShowConfirmModal(null)}>
                                        Cancel
                                    </button>
                                    <button className="btn btn-warning" onClick={handleFalseAlarm} disabled={processing}>
                                        {processing ? 'Processing...' : 'Confirm'}
                                    </button>
                                </div>
                            </>
                        )}

                        {showConfirmModal === 'police' && (
                            <>
                                <div className="modal-header">
                                    <h3>Send Police Report</h3>
                                </div>
                                <div className="confirm-content">
                                    <div className="icon primary">
                                        <FileText size={48} />
                                    </div>
                                    <h3>Send Incident Report to Police?</h3>
                                    <p>A preliminary incident intimation will be sent to the nearest police station.</p>
                                    <p className="note">Note: This is NOT an official FIR.</p>
                                </div>
                                <div className="modal-footer">
                                    <button className="btn btn-outline" onClick={() => setShowConfirmModal(null)}>
                                        Cancel
                                    </button>
                                    <button className="btn btn-primary" onClick={handleSendPoliceReport} disabled={processing}>
                                        {processing ? 'Sending...' : 'Send Report'}
                                    </button>
                                </div>
                            </>
                        )}

                        {showConfirmModal === 'ambulance' && (
                            <>
                                <div className="modal-header">
                                    <h3>Dispatch Ambulance</h3>
                                </div>
                                <div className="confirm-content">
                                    <div className="icon danger">
                                        <Truck size={48} />
                                    </div>
                                    <h3>🚨 Critical Incident - Dispatch Ambulance?</h3>
                                    <p>An ambulance will be dispatched to the incident location immediately.</p>
                                    <div className="ambulance-details">
                                        <p><strong>Location:</strong> {incident.camera?.location_address || 'Unknown'}</p>
                                        <p><strong>Severity:</strong> {incident.severity}</p>
                                    </div>
                                </div>
                                <div className="modal-footer">
                                    <button className="btn btn-outline" onClick={() => setShowConfirmModal(null)}>
                                        Cancel
                                    </button>
                                    <button className="btn btn-danger" onClick={handleDispatchAmbulance} disabled={processing}>
                                        {processing ? 'Dispatching...' : '🚑 Dispatch Now'}
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default IncidentDetail;
