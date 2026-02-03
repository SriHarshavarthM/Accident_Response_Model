import { useState, useEffect } from 'react';
import { AlertTriangle, Clock, Truck, FileText, Upload, RefreshCw } from 'lucide-react';
import IncidentCard from '../components/IncidentCard';
import MapView from '../components/MapView';
import api from '../services/api';
import wsService from '../services/websocket';
import './Dashboard.css';

// Demo data for when backend is not available
const DEMO_INCIDENTS = [
    {
        id: 1,
        incident_id: 'INC-2026-A1B2C3',
        incident_type: 'VEHICLE_COLLISION',
        severity: 'CRITICAL',
        confidence_score: 0.94,
        status: 'DETECTED',
        vehicles_involved: 2,
        pedestrian_involved: false,
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        camera_id: 1,
        description: 'High-speed collision detected at intersection'
    },
    {
        id: 2,
        incident_id: 'INC-2026-D4E5F6',
        incident_type: 'MULTI_VEHICLE',
        severity: 'HIGH',
        confidence_score: 0.88,
        status: 'VERIFIED',
        vehicles_involved: 3,
        pedestrian_involved: false,
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        camera_id: 2,
        description: 'Multiple vehicles involved in pile-up'
    },
    {
        id: 3,
        incident_id: 'INC-2026-G7H8I9',
        incident_type: 'PEDESTRIAN_IMPACT',
        severity: 'HIGH',
        confidence_score: 0.91,
        status: 'REPORTED',
        vehicles_involved: 1,
        pedestrian_involved: true,
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        camera_id: 3,
        description: 'Pedestrian hit by vehicle at crosswalk'
    },
    {
        id: 4,
        incident_id: 'INC-2026-J0K1L2',
        incident_type: 'ROLLOVER',
        severity: 'MEDIUM',
        confidence_score: 0.82,
        status: 'DETECTED',
        vehicles_involved: 1,
        pedestrian_involved: false,
        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        camera_id: 1,
        description: 'Vehicle rollover on highway'
    }
];

function Dashboard() {
    const [incidents, setIncidents] = useState([]);
    const [stats, setStats] = useState({
        active_incidents: 0,
        today_incidents: 0,
        pending_verification: 0,
        dispatched_ambulances: 0,
        police_reports_sent: 0
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchData();

        // Listen for new incidents
        wsService.on('new_incident', handleNewIncident);
        wsService.on('status_update', handleStatusUpdate);

        return () => {
            wsService.off('new_incident', handleNewIncident);
            wsService.off('status_update', handleStatusUpdate);
        };
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [incidentsData, statsData] = await Promise.all([
                api.getActiveIncidents(),
                api.getDashboardStats()
            ]);
            setIncidents(incidentsData);
            setStats(statsData);
            setError(null);
        } catch (err) {
            console.log('Using demo data - backend not available');
            // Keep using demo data
        } finally {
            setLoading(false);
        }
    };

    const handleNewIncident = (data) => {
        setIncidents(prev => [data, ...prev]);
        setStats(prev => ({
            ...prev,
            active_incidents: prev.active_incidents + 1,
            today_incidents: prev.today_incidents + 1,
            pending_verification: prev.pending_verification + 1
        }));
    };

    const handleStatusUpdate = ({ incident_id, status }) => {
        setIncidents(prev =>
            prev.map(inc =>
                inc.incident_id === incident_id ? { ...inc, status } : inc
            )
        );
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                const result = await api.uploadVideo(1, file);
                alert(`Video uploaded successfully! File ID: ${result.file_id}`);
            } catch (err) {
                alert('Failed to upload video. Please check if backend is running.');
            }
        }
    };

    return (
        <div className="dashboard">
            <div className="page-header">
                <div className="page-title">
                    <AlertTriangle size={28} />
                    <h1>Control Room</h1>
                </div>
                <div className="page-actions">
                    <label className="btn btn-primary upload-btn">
                        <Upload size={18} />
                        Upload Video
                        <input
                            type="file"
                            accept=".mp4,.avi,.mov,.mkv"
                            onChange={handleFileUpload}
                            hidden
                        />
                    </label>
                    <button className="btn btn-outline" onClick={fetchData}>
                        <RefreshCw size={18} className={loading ? 'spin' : ''} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon danger">
                        <AlertTriangle size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.active_incidents}</h3>
                        <p>Active Incidents</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon warning">
                        <Clock size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.pending_verification}</h3>
                        <p>Pending Verification</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon primary">
                        <Truck size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.dispatched_ambulances}</h3>
                        <p>Ambulances Dispatched</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon success">
                        <FileText size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.police_reports_sent}</h3>
                        <p>Reports Sent</p>
                    </div>
                </div>
            </div>

            {/* Main Dashboard Grid */}
            <div className="dashboard-grid">
                {/* Incident Feed */}
                <div className="card">
                    <div className="card-header">
                        <h3>📹 Live Incident Feed</h3>
                        <span className="incident-count">{incidents.length} active</span>
                    </div>

                    <div className="incident-list">
                        {loading ? (
                            <div className="loading">
                                <div className="loading-spinner"></div>
                            </div>
                        ) : incidents.length === 0 ? (
                            <div className="empty-state">
                                <AlertTriangle size={48} />
                                <p>No active incidents</p>
                            </div>
                        ) : (
                            incidents.map(incident => (
                                <IncidentCard key={incident.id} incident={incident} />
                            ))
                        )}
                    </div>
                </div>

                {/* Map View */}
                <div className="card">
                    <div className="card-header">
                        <h3>🗺️ Incident Map</h3>
                    </div>
                    <MapView incidents={incidents} />
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
