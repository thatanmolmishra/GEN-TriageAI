import SeverityBadge from './SeverityBadge';

function formatWait(arrivedAt) {
  if (!arrivedAt) return '—';
  const diff = Math.floor((Date.now() - new Date(arrivedAt).getTime()) / 1000);
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
}

const STATUS_COLORS = {
  waiting: 'var(--text-muted)',
  in_treatment: 'var(--accent)',
  treated: 'var(--minor)',
  discharged: 'var(--text-muted)',
};

/**
 * ERQueue – Live priority-sorted table of ER patients.
 */
export default function ERQueue({ patients = [], onSelectPatient, lastUpdated }) {
  const critical = patients.filter((p) => p.severity === 'Critical');
  const others = patients.filter((p) => p.severity !== 'Critical');

  if (patients.length === 0) {
    return (
      <div>
        <div className="panel-header">
          <div className="panel-title">
            <span className="panel-title-icon">📋</span>
            ER Queue
          </div>
          {lastUpdated && (
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Live · {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className="queue-empty">
          <div className="queue-empty-icon">🏥</div>
          <div className="queue-empty-title">Queue is empty</div>
          <div className="queue-empty-sub">Submit a patient intake to populate the queue</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-icon">📋</span>
          ER Queue
          <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>
            ({patients.length})
          </span>
        </div>
        {lastUpdated && (
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            🔴 Live · {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>

      <div className="queue-container">
        {patients.map((patient, idx) => (
          <div
            key={patient.patient_id}
            className={`patient-row ${patient.severity || ''}`}
            onClick={() => onSelectPatient?.(patient)}
          >
            {/* Rank */}
            <div className="patient-rank">#{idx + 1}</div>

            {/* Info */}
            <div className="patient-info">
              <div className="patient-name">{patient.name}</div>
              <div className="patient-meta">
                <span className="patient-meta-item">👤 {patient.age}y</span>
                <span className="patient-meta-item">⚧ {patient.gender}</span>
                <span className="patient-meta-item"
                  style={{ color: STATUS_COLORS[patient.status] || 'var(--text-muted)' }}>
                  ● {patient.status?.replace('_', ' ')}
                </span>
              </div>
              <div className="patient-symptoms">{patient.symptoms}</div>
            </div>

            {/* Severity */}
            <SeverityBadge severity={patient.severity} />

            {/* Wait time */}
            <div className="patient-wait">
              <span className="wait-time">⏱ {formatWait(patient.arrived_at)}</span>
              {patient.is_alerted && (
                <span style={{ fontSize: '0.65rem', color: 'var(--critical)' }}>⚠ ALERTED</span>
              )}
            </div>

            {/* Confidence */}
            {patient.confidence != null && (
              <div className="confidence-bar">
                <div className="confidence-track">
                  <div
                    className={`confidence-fill ${patient.severity}`}
                    style={{ width: `${Math.round(patient.confidence * 100)}%` }}
                  />
                </div>
                <span className="confidence-label">
                  {Math.round(patient.confidence * 100)}%
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
