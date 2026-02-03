import { useState, useEffect } from 'react';
import {
    BarChart3,
    TrendingUp,
    AlertTriangle,
    Clock,
    CheckCircle,
    XCircle
} from 'lucide-react';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend
} from 'recharts';
import './Analytics.css';

// Demo analytics data
const DEMO_DAILY_DATA = [
    { date: 'Mon', incidents: 8, verified: 6, falseAlarms: 2 },
    { date: 'Tue', incidents: 12, verified: 10, falseAlarms: 2 },
    { date: 'Wed', incidents: 6, verified: 5, falseAlarms: 1 },
    { date: 'Thu', incidents: 15, verified: 12, falseAlarms: 3 },
    { date: 'Fri', incidents: 10, verified: 9, falseAlarms: 1 },
    { date: 'Sat', incidents: 18, verified: 15, falseAlarms: 3 },
    { date: 'Sun', incidents: 14, verified: 11, falseAlarms: 3 },
];

const DEMO_SEVERITY_DATA = [
    { name: 'Critical', value: 15, color: '#ff006e' },
    { name: 'High', value: 32, color: '#ff5c33' },
    { name: 'Medium', value: 45, color: '#ffbe0b' },
    { name: 'Low', value: 28, color: '#06d6a0' },
];

const DEMO_ZONE_DATA = [
    { zone: 'Highway North', incidents: 25 },
    { zone: 'City Center', incidents: 18 },
    { zone: 'Industrial', incidents: 12 },
    { zone: 'Residential', incidents: 8 },
    { zone: 'Highway South', incidents: 22 },
];

const DEMO_RESPONSE_TIME = [
    { hour: '00:00', avgTime: 4.2 },
    { hour: '04:00', avgTime: 3.8 },
    { hour: '08:00', avgTime: 6.5 },
    { hour: '12:00', avgTime: 5.2 },
    { hour: '16:00', avgTime: 7.1 },
    { hour: '20:00', avgTime: 5.8 },
];

function Analytics() {
    const [timeRange, setTimeRange] = useState('week');
    const [stats, setStats] = useState({
        totalIncidents: 120,
        verifiedRate: 85.3,
        avgResponseTime: 5.2,
        falsePositiveRate: 12.5
    });

    return (
        <div className="analytics">
            <div className="page-header">
                <div className="page-title">
                    <BarChart3 size={28} />
                    <h1>Analytics Dashboard</h1>
                </div>
                <div className="page-actions">
                    <select
                        className="time-select"
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                    >
                        <option value="day">Today</option>
                        <option value="week">This Week</option>
                        <option value="month">This Month</option>
                        <option value="year">This Year</option>
                    </select>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon primary">
                        <AlertTriangle size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.totalIncidents}</h3>
                        <p>Total Incidents</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon success">
                        <CheckCircle size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.verifiedRate}%</h3>
                        <p>Verification Rate</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon warning">
                        <Clock size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.avgResponseTime}m</h3>
                        <p>Avg Response Time</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon danger">
                        <XCircle size={24} />
                    </div>
                    <div className="stat-info">
                        <h3>{stats.falsePositiveRate}%</h3>
                        <p>False Positive Rate</p>
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="charts-grid">
                {/* Daily Incidents Chart */}
                <div className="card chart-card">
                    <h3>📈 Daily Incidents</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={DEMO_DAILY_DATA}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="date" stroke="#a0a0b0" />
                                <YAxis stroke="#a0a0b0" />
                                <Tooltip
                                    contentStyle={{
                                        background: '#16213e',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="incidents"
                                    stroke="#4361ee"
                                    strokeWidth={3}
                                    dot={{ fill: '#4361ee' }}
                                    name="Total"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="verified"
                                    stroke="#06d6a0"
                                    strokeWidth={2}
                                    dot={{ fill: '#06d6a0' }}
                                    name="Verified"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="falseAlarms"
                                    stroke="#ff006e"
                                    strokeWidth={2}
                                    dot={{ fill: '#ff006e' }}
                                    name="False Alarms"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Severity Distribution */}
                <div className="card chart-card">
                    <h3>🎯 Severity Distribution</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={DEMO_SEVERITY_DATA}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                    label={({ name, value }) => `${name}: ${value}`}
                                >
                                    {DEMO_SEVERITY_DATA.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        background: '#16213e',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Incidents by Zone */}
                <div className="card chart-card">
                    <h3>📍 Incidents by Zone</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={DEMO_ZONE_DATA} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis type="number" stroke="#a0a0b0" />
                                <YAxis dataKey="zone" type="category" stroke="#a0a0b0" width={100} />
                                <Tooltip
                                    contentStyle={{
                                        background: '#16213e',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Bar
                                    dataKey="incidents"
                                    fill="url(#barGradient)"
                                    radius={[0, 4, 4, 0]}
                                />
                                <defs>
                                    <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                                        <stop offset="0%" stopColor="#4361ee" />
                                        <stop offset="100%" stopColor="#7209b7" />
                                    </linearGradient>
                                </defs>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Response Time by Hour */}
                <div className="card chart-card">
                    <h3>⏱️ Avg Response Time by Hour</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={DEMO_RESPONSE_TIME}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="hour" stroke="#a0a0b0" />
                                <YAxis stroke="#a0a0b0" unit="m" />
                                <Tooltip
                                    contentStyle={{
                                        background: '#16213e',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                    formatter={(value) => [`${value} min`, 'Response Time']}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="avgTime"
                                    stroke="#ffbe0b"
                                    strokeWidth={3}
                                    dot={{ fill: '#ffbe0b' }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Analytics;
