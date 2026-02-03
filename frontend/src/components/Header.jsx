import { useState } from 'react';
import { Menu, Bell, Wifi, WifiOff, Settings, User } from 'lucide-react';
import './Header.css';

function Header({ onToggleSidebar, connected }) {
    const [showNotifications, setShowNotifications] = useState(false);

    return (
        <header className="header">
            <div className="header-left">
                <button className="btn btn-icon" onClick={onToggleSidebar}>
                    <Menu size={20} />
                </button>

                <div className="logo">
                    <span className="logo-icon">🚨</span>
                    <span className="logo-text">Accident Incident Responder</span>
                </div>
            </div>

            <div className="header-right">
                <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
                    {connected ? <Wifi size={16} /> : <WifiOff size={16} />}
                    <span>{connected ? 'Live' : 'Offline'}</span>
                </div>

                <button
                    className="btn btn-icon notification-btn"
                    onClick={() => setShowNotifications(!showNotifications)}
                >
                    <Bell size={20} />
                    <span className="notification-badge">3</span>
                </button>

                <button className="btn btn-icon">
                    <Settings size={20} />
                </button>

                <div className="user-menu">
                    <div className="user-avatar">
                        <User size={18} />
                    </div>
                    <span className="user-name">Operator</span>
                </div>
            </div>
        </header>
    );
}

export default Header;
