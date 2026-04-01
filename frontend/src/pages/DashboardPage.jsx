import { useCallback, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useQueue } from '../hooks/useQueue';
import StatsBar from '../components/StatsBar';
import AlertPanel from '../components/AlertPanel';
import ERQueue from '../components/ERQueue';
import PatientModal from '../components/PatientModal';
import { acknowledgeAlert, getPatient } from '../api/triageAPI';

export default function DashboardPage() {
  const { patients, stats, alerts, lastUpdated, applyUpdate, refreshFromAPI } = useQueue();
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [toasts, setToasts] = useState([]);

  // WebSocket message handler
  const handleMessage = useCallback((payload) => {
    applyUpdate(payload);

    // Show toast for new Critical alerts
    if (payload.type === 'alert' && payload.data?.new_alert) {
      const a = payload.data.new_alert;
      addToast({
        id: a.alert_id,
        type: 'critical',
        title: `🚨 Critical Alert: ${a.patient_name}`,
        msg: a.message?.slice(0, 80) + '...',
      });
    }
  }, [applyUpdate]);

  const { status } = useWebSocket(handleMessage);

  const addToast = (toast) => {
    setToasts((t) => [toast, ...t].slice(0, 3));
    setTimeout(() => {
      setToasts((t) => t.filter((x) => x.id !== toast.id));
    }, 6000);
  };

  const handleSelectPatient = async (patient) => {
    try {
      const full = await getPatient(patient.patient_id);
      setSelectedPatient(full);
    } catch {
      setSelectedPatient(patient);
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
      refreshFromAPI();
    } catch (e) {
      console.error(e);
    }
  };

  const handleAlertClick = (alert) => {
    // Find the patient in queue and open their modal
    const patient = patients.find((p) => p.patient_id === alert.patient_id);
    if (patient) handleSelectPatient(patient);
  };

  const wsStatusColor = {
    connected: 'var(--minor)',
    connecting: 'var(--urgent)',
    disconnected: 'var(--critical)',
  }[status];

  // Merge queue alerts with WebSocket alerts
  const allAlerts = alerts.length > 0 ? alerts : [];

  return (
    <div className="app-layout" style={{ height: '100vh', overflow: 'hidden' }}>
      {/* Stats Bar */}
      <StatsBar stats={{
        ...stats,
        unacknowledged_alerts: allAlerts.filter((a) => !a.acknowledged).length,
      }} />

      {/* Dashboard Grid */}
      <div className="dashboard-layout" style={{ flex: 1 }}>
        {/* Left: Alert Panel */}
        <div className="dashboard-left">
          <AlertPanel
            alerts={allAlerts}
            onSelectAlert={handleAlertClick}
            onAcknowledge={handleAcknowledgeAlert}
          />
        </div>

        {/* Right: ER Queue */}
        <div className="dashboard-main">
          <ERQueue
            patients={patients}
            onSelectPatient={handleSelectPatient}
            lastUpdated={lastUpdated}
          />
        </div>
      </div>

      {/* Patient Modal */}
      {selectedPatient && (
        <PatientModal
          patient={selectedPatient}
          onClose={() => setSelectedPatient(null)}
          onUpdated={refreshFromAPI}
        />
      )}

      {/* Toast Notifications */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast ${toast.type}`}>
            <div className="toast-icon">🚨</div>
            <div className="toast-text">
              <div className="toast-title">{toast.title}</div>
              <div className="toast-msg">{toast.msg}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
