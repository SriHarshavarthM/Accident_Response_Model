import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    AlertTriangle,
    BarChart3,
    Camera,
    Truck,
    FileText,
    MapPin,
    Settings
} from 'lucide-react';
import './Sidebar.css';

function Sidebar({ isOpen }) {
    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/analytics', icon: BarChart3, label: 'Analytics' },
        { path: '/cameras', icon: Camera, label: 'Cameras' },
    ];

    return (
        <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
            <nav className="sidebar-nav">
                <div className="nav-section">
                    <span className="nav-section-title">Main</span>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        >
                            <item.icon size={20} />
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </div>

                <div className="nav-section">
                    <span className="nav-section-title">Quick Stats</span>
                    <div className="quick-stats">
                        <div className="quick-stat">
                            <span className="quick-stat-value critical">3</span>
                            <span className="quick-stat-label">Critical</span>
                        </div>
                        <div className="quick-stat">
                            <span className="quick-stat-value high">7</span>
                            <span className="quick-stat-label">High</span>
                        </div>
                        <div className="quick-stat">
                            <span className="quick-stat-value medium">12</span>
                            <span className="quick-stat-label">Medium</span>
                        </div>
                    </div>
                </div>

                <div className="nav-section">
                    <span className="nav-section-title">Services</span>
                    <div className="service-status">
                        <div className="service-item">
                            <Truck size={16} />
                            <span>Ambulance Ready</span>
                            <span className="status-dot online"></span>
                        </div>
                        <div className="service-item">
                            <FileText size={16} />
                            <span>Police API</span>
                            <span className="status-dot online"></span>
                        </div>
                        <div className="service-item">
                            <MapPin size={16} />
                            <span>GPS Active</span>
                            <span className="status-dot online"></span>
                        </div>
                    </div>
                </div>
            </nav>

            <div className="sidebar-footer">
                <NavLink to="/settings" className="nav-item">
                    <Settings size={20} />
                    <span>Settings</span>
                </NavLink>
            </div>
        </aside>
    );
}

export default Sidebar;
