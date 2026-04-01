import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Patient Intake ─────────────────────────────────────────────────
export const submitIntake = (data) =>
  api.post('/api/intake', data).then((r) => r.data);

// ── Queue ──────────────────────────────────────────────────────────
export const getQueue = () =>
  api.get('/api/queue').then((r) => r.data);

// ── Alerts ────────────────────────────────────────────────────────
export const getAlerts = (unacknowledgedOnly = false) =>
  api.get('/api/alerts', { params: { unacknowledged_only: unacknowledgedOnly } })
    .then((r) => r.data);

export const acknowledgeAlert = (alertId) =>
  api.patch(`/api/alerts/${alertId}/acknowledge`).then((r) => r.data);

// ── Patients ──────────────────────────────────────────────────────
export const getPatient = (patientId) =>
  api.get(`/api/patients/${patientId}`).then((r) => r.data);

export const updatePatientStatus = (patientId, status) =>
  api.patch(`/api/patients/${patientId}/status`, { status }).then((r) => r.data);

export const removePatient = (patientId) =>
  api.delete(`/api/patients/${patientId}`).then((r) => r.data);

// ── Health ────────────────────────────────────────────────────────
export const checkHealth = () =>
  api.get('/health').then((r) => r.data);

export default api;
