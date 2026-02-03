/**
 * API Service for Backend Communication
 */

const API_BASE = '/api/v1';

class ApiService {
    constructor() {
        this.baseUrl = API_BASE;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Incidents
    async getIncidents(status = null, severity = null) {
        let url = '/incidents/';
        const params = new URLSearchParams();
        if (status) params.append('status', status);
        if (severity) params.append('severity', severity);
        if (params.toString()) url += `?${params.toString()}`;
        return this.request(url);
    }

    async getActiveIncidents() {
        return this.request('/incidents/active');
    }

    async getIncident(id) {
        return this.request(`/incidents/${id}`);
    }

    async getDashboardStats() {
        return this.request('/incidents/stats');
    }

    async verifyIncident(incidentId, verifiedBy) {
        return this.request(`/incidents/${incidentId}/verify?verified_by=${verifiedBy}`, {
            method: 'POST',
        });
    }

    async markFalseAlarm(incidentId, markedBy) {
        return this.request(`/incidents/${incidentId}/false-alarm?marked_by=${markedBy}`, {
            method: 'POST',
        });
    }

    async closeIncident(incidentId, closedBy, notes = null) {
        let url = `/incidents/${incidentId}/close?closed_by=${closedBy}`;
        if (notes) url += `&notes=${encodeURIComponent(notes)}`;
        return this.request(url, { method: 'POST' });
    }

    async uploadVideo(cameraId, file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseUrl}/incidents/upload-video?camera_id=${cameraId}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }
        return await response.json();
    }

    // Cameras
    async getCameras() {
        return this.request('/cameras/');
    }

    async createCamera(cameraData) {
        return this.request('/cameras/', {
            method: 'POST',
            body: JSON.stringify(cameraData),
        });
    }

    // Dispatch
    async getPoliceStations() {
        return this.request('/dispatch/police-stations');
    }

    async getNearestPoliceStation(incidentId) {
        return this.request(`/dispatch/police-stations/nearest/${incidentId}`);
    }

    async sendPoliceReport(incidentId, policeStationId, notes = null) {
        return this.request('/dispatch/send-police-report', {
            method: 'POST',
            body: JSON.stringify({
                incident_id: incidentId,
                police_station_id: policeStationId,
                additional_notes: notes,
                send_method: 'email',
            }),
        });
    }

    async getAmbulanceProviders() {
        return this.request('/dispatch/ambulance-providers');
    }

    async dispatchAmbulance(incidentId, providerId, callbackNumber, operatorId) {
        return this.request('/dispatch/ambulance', {
            method: 'POST',
            body: JSON.stringify({
                incident_id: incidentId,
                provider_id: providerId,
                callback_number: callbackNumber,
                operator_id: operatorId,
                confirmed: true,
            }),
        });
    }

    async getDispatchLogs(incidentId) {
        return this.request(`/dispatch/logs/${incidentId}`);
    }

    async downloadReport(incidentId) {
        return this.request(`/dispatch/download-report/${incidentId}`);
    }
}

export const api = new ApiService();
export default api;
