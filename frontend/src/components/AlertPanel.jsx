import { useEffect, useRef } from 'react';
import SeverityBadge from './SeverityBadge';

function formatTimeAgo(isoString) {
  if (!isoString) return '';
  const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

/**
 * AlertPanel – Left-side scrollable feed of critical alerts.
 */
export default function AlertPanel({ alerts = [], onSelectAlert, onAcknowledge }) {
  const panelRef = useRef(null);

  const unread = alerts.filter((a) => !a.acknowledged);
  const total = alerts.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-icon">🚨</span>
          Alerts
          {unread.length > 0 && (
            <span className="panel-badge">{unread.length}</span>
          )}
        </div>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          {total} total
        </span>
      </div>

      {/* Alert list */}
      <div className="alert-panel" ref={panelRef}>
        {alerts.length === 0 ? (
          <div className="alert-empty">
            <div className="alert-empty-icon">✅</div>
            <span>No active alerts</span>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.alert_id}
              className={`alert-card ${!alert.acknowledged ? 'unread' : ''}`}
              onClick={() => onSelectAlert?.(alert)}
            >
              <div className="alert-card-header">
                <span className="alert-patient-name">{alert.patient_name}</span>
                <span className="alert-time">
                  {formatTimeAgo(alert.triggered_at)}
                </span>
              </div>
              <div style={{ marginBottom: 6 }}>
                <SeverityBadge severity={alert.severity} />
              </div>
              <p className="alert-message">{alert.message}</p>
              {!alert.acknowledged && (
                <button
                  className="btn btn-ghost"
                  style={{ marginTop: 8, fontSize: '0.72rem', padding: '4px 10px' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    onAcknowledge?.(alert.alert_id);
                  }}
                >
                  Acknowledge
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
