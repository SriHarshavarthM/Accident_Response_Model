import { useState, useEffect } from 'react';
import { Camera, Plus, MapPin, Wifi, WifiOff, Edit, Trash2 } from 'lucide-react';
import api from '../services/api';
import './Cameras.css';

// Demo cameras
const DEMO_CAMERAS = [
    {
        id: 1,
        camera_id: 'CAM-001',
        name: 'Highway Cam 1',
        location_address: 'NH-48, Km 45, Gurugram, Haryana',
        latitude: 28.4595,
        longitude: 77.0266,
        zone: 'Highway North',
        is_active: true
    },
    {
        id: 2,
        camera_id: 'CAM-002',
        name: 'City Center Junction',
        location_address: 'MG Road, Sector 14, Gurugram',
        latitude: 28.4715,
        longitude: 77.0842,
        zone: 'City Center',
        is_active: true
    },
    {
        id: 3,
        camera_id: 'CAM-003',
        name: 'Industrial Area Gate',
        location_address: 'IMT Manesar, Gurugram',
        latitude: 28.3523,
        longitude: 76.9378,
        zone: 'Industrial',
        is_active: true
    },
    {
        id: 4,
        camera_id: 'CAM-004',
        name: 'School Zone Cam',
        location_address: 'DLF Phase 4, Gurugram',
        latitude: 28.4713,
        longitude: 77.0955,
        zone: 'Residential',
        is_active: false
    },
];

function Cameras() {
    const [cameras, setCameras] = useState(DEMO_CAMERAS);
    const [showAddModal, setShowAddModal] = useState(false);
    const [newCamera, setNewCamera] = useState({
        camera_id: '',
        name: '',
        location_address: '',
        latitude: '',
        longitude: '',
        zone: '',
        rtsp_url: ''
    });

    useEffect(() => {
        fetchCameras();
    }, []);

    const fetchCameras = async () => {
        try {
            const data = await api.getCameras();
            setCameras(data);
        } catch (err) {
            console.log('Using demo data - backend not available');
        }
    };

    const handleAddCamera = async (e) => {
        e.preventDefault();

        try {
            const result = await api.createCamera({
                ...newCamera,
                latitude: parseFloat(newCamera.latitude),
                longitude: parseFloat(newCamera.longitude)
            });
            setCameras([...cameras, result]);
            setShowAddModal(false);
            setNewCamera({
                camera_id: '',
                name: '',
                location_address: '',
                latitude: '',
                longitude: '',
                zone: '',
                rtsp_url: ''
            });
        } catch (err) {
            // Demo mode - add locally
            const demoCamera = {
                id: cameras.length + 1,
                ...newCamera,
                latitude: parseFloat(newCamera.latitude) || 0,
                longitude: parseFloat(newCamera.longitude) || 0,
                is_active: true
            };
            setCameras([...cameras, demoCamera]);
            setShowAddModal(false);
            alert('Camera added (demo mode)');
        }
    };

    return (
        <div className="cameras-page">
            <div className="page-header">
                <div className="page-title">
                    <Camera size={28} />
                    <h1>Camera Management</h1>
                </div>
                <div className="page-actions">
                    <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                        <Plus size={18} />
                        Add Camera
                    </button>
                </div>
            </div>

            {/* Camera Grid */}
            <div className="camera-grid">
                {cameras.map(camera => (
                    <div key={camera.id} className={`camera-card ${!camera.is_active ? 'inactive' : ''}`}>
                        <div className="camera-header">
                            <div className="camera-status">
                                {camera.is_active ? (
                                    <Wifi size={16} className="online" />
                                ) : (
                                    <WifiOff size={16} className="offline" />
                                )}
                                <span>{camera.is_active ? 'Online' : 'Offline'}</span>
                            </div>
                            <div className="camera-actions">
                                <button className="btn btn-icon btn-small">
                                    <Edit size={14} />
                                </button>
                            </div>
                        </div>

                        <div className="camera-preview">
                            <Camera size={48} />
                            <span>Live Feed</span>
                        </div>

                        <div className="camera-info">
                            <h4>{camera.name}</h4>
                            <p className="camera-id">{camera.camera_id}</p>

                            <div className="camera-details">
                                <div className="detail">
                                    <MapPin size={14} />
                                    <span>{camera.location_address}</span>
                                </div>
                                <div className="detail">
                                    <span className="label">Zone:</span>
                                    <span className="value">{camera.zone}</span>
                                </div>
                                <div className="detail">
                                    <span className="label">Coords:</span>
                                    <span className="value">{camera.latitude?.toFixed(4)}, {camera.longitude?.toFixed(4)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Add Camera Modal */}
            {showAddModal && (
                <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Add New Camera</h3>
                        </div>

                        <form onSubmit={handleAddCamera}>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label>Camera ID</label>
                                    <input
                                        type="text"
                                        value={newCamera.camera_id}
                                        onChange={e => setNewCamera({ ...newCamera, camera_id: e.target.value })}
                                        placeholder="CAM-XXX"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Name</label>
                                    <input
                                        type="text"
                                        value={newCamera.name}
                                        onChange={e => setNewCamera({ ...newCamera, name: e.target.value })}
                                        placeholder="Camera Name"
                                        required
                                    />
                                </div>

                                <div className="form-group full-width">
                                    <label>Location Address</label>
                                    <input
                                        type="text"
                                        value={newCamera.location_address}
                                        onChange={e => setNewCamera({ ...newCamera, location_address: e.target.value })}
                                        placeholder="Full address"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Latitude</label>
                                    <input
                                        type="number"
                                        step="any"
                                        value={newCamera.latitude}
                                        onChange={e => setNewCamera({ ...newCamera, latitude: e.target.value })}
                                        placeholder="28.4595"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Longitude</label>
                                    <input
                                        type="number"
                                        step="any"
                                        value={newCamera.longitude}
                                        onChange={e => setNewCamera({ ...newCamera, longitude: e.target.value })}
                                        placeholder="77.0266"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Zone</label>
                                    <input
                                        type="text"
                                        value={newCamera.zone}
                                        onChange={e => setNewCamera({ ...newCamera, zone: e.target.value })}
                                        placeholder="Highway North"
                                    />
                                </div>

                                <div className="form-group">
                                    <label>RTSP URL (optional)</label>
                                    <input
                                        type="text"
                                        value={newCamera.rtsp_url}
                                        onChange={e => setNewCamera({ ...newCamera, rtsp_url: e.target.value })}
                                        placeholder="rtsp://..."
                                    />
                                </div>
                            </div>

                            <div className="modal-footer">
                                <button type="button" className="btn btn-outline" onClick={() => setShowAddModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    Add Camera
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Cameras;
