import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import IncidentDetail from './pages/IncidentDetail';
import Analytics from './pages/Analytics';
import Cameras from './pages/Cameras';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import AlertBanner from './components/AlertBanner';
import wsService from './services/websocket';
import './App.css';

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [criticalAlert, setCriticalAlert] = useState(null);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        // Connect WebSocket
        wsService.connect();

        // Listen for new incidents
        wsService.on('new_incident', (data) => {
            if (data.severity === 'CRITICAL') {
                setCriticalAlert(data);
                // Play alert sound
                playAlertSound();
            }
        });

        wsService.on('connected', () => setConnected(true));
        wsService.on('disconnected', () => setConnected(false));

        return () => {
            wsService.disconnect();
        };
    }, []);

    const playAlertSound = () => {
        // Create a simple beep
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.value = 0.3;

        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.5);
    };

    return (
        <Router>
            <div className="app">
                <Header
                    onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                    connected={connected}
                />

                {criticalAlert && (
                    <AlertBanner
                        alert={criticalAlert}
                        onDismiss={() => setCriticalAlert(null)}
                    />
                )}

                <div className="app-body">
                    <Sidebar isOpen={sidebarOpen} />

                    <main className={`main-content ${sidebarOpen ? '' : 'sidebar-closed'}`}>
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/incident/:id" element={<IncidentDetail />} />
                            <Route path="/analytics" element={<Analytics />} />
                            <Route path="/cameras" element={<Cameras />} />
                        </Routes>
                    </main>
                </div>
            </div>
        </Router>
    );
}

export default App;
