import { useState } from 'react';
import SeverityBadge from './SeverityBadge';
import { getPatient, updatePatientStatus, removePatient } from '../api/triageAPI';

/**
 * PatientModal – Full detail modal for a selected patient.
 */
export default function PatientModal({ patient: initialPatient, onClose, onUpdated }) {
  const [patient, setPatient] = useState(initialPatient);
  const [loading, setLoading] = useState(false);

  if (!patient) return null;

  const handleStatusChange = async (newStatus) => {
    setLoading(true);
    try {
      await updatePatientStatus(patient.patient_id, newStatus);
      setPatient((p) => ({ ...p, status: newStatus }));
      onUpdated?.();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async () => {
    if (!confirm(`Remove ${patient.name} from the queue?`)) return;
    setLoading(true);
    try {
      await removePatient(patient.patient_id);
      onUpdated?.();
      onClose?.();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const arrivedAt = patient.arrived_at
    ? new Date(patient.arrived_at).toLocaleTimeString()
    : '—';

  const confidence = patient.confidence != null
    ? `${Math.round(patient.confidence * 100)}%`
    : '—';

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose?.()}>
      <div className="modal-panel">
        {/* Header */}
        <div className="modal-header">
          <div>
            <div className="modal-title">{patient.name}</div>
            <div style={{ marginTop: 6 }}>
              <SeverityBadge severity={patient.severity} />
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {/* Patient Info */}
          <div>
            <div className="modal-section-title">Patient Information</div>
            <div className="modal-info-grid">
              <div className="info-chip">
                <div className="info-chip-label">Age</div>
                <div className="info-chip-value">{patient.age} yrs</div>
              </div>
              <div className="info-chip">
                <div className="info-chip-label">Gender</div>
                <div className="info-chip-value">{patient.gender}</div>
              </div>
              <div className="info-chip">
                <div className="info-chip-label">Arrived</div>
                <div className="info-chip-value">{arrivedAt}</div>
              </div>
              <div className="info-chip">
                <div className="info-chip-label">AI Confidence</div>
                <div className="info-chip-value"
                  style={{ color: `var(--${patient.severity?.toLowerCase() || 'text-primary'})` }}>
                  {confidence}
                </div>
              </div>
              <div className="info-chip">
                <div className="info-chip-label">Status</div>
                <div className="info-chip-value" style={{ textTransform: 'capitalize' }}>
                  {patient.status?.replace('_', ' ')}
                </div>
              </div>
              <div className="info-chip">
                <div className="info-chip-label">Est. Wait</div>
                <div className="info-chip-value">
                  {patient.severity === 'Critical' ? 'NOW' : `${patient.estimated_wait_minutes}m`}
                </div>
              </div>
            </div>
          </div>

          {/* Chief Complaint */}
          <div>
            <div className="modal-section-title">Chief Complaint</div>
            <div className="modal-reasoning">{patient.symptoms}</div>
          </div>

          {/* Vitals */}
          {patient.vitals && (
            <div>
              <div className="modal-section-title">Vitals</div>
              <div className="modal-reasoning">{patient.vitals}</div>
            </div>
          )}

          {/* Reasoning */}
          {patient.reasoning && (
            <div>
              <div className="modal-section-title">Clinical Reasoning</div>
              <div className="modal-reasoning">{patient.reasoning}</div>
            </div>
          )}

          {/* Recommended Actions */}
          {patient.recommended_actions?.length > 0 && (
            <div>
              <div className="modal-section-title">Recommended Actions</div>
              <div className="modal-actions">
                {patient.recommended_actions.map((action, i) => (
                  <div key={i} className="action-item">{action}</div>
                ))}
              </div>
            </div>
          )}

          {/* Status Actions */}
          <div>
            <div className="modal-section-title">Update Status</div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['waiting', 'in_treatment', 'treated', 'discharged'].map((s) => (
                <button
                  key={s}
                  className={`btn ${patient.status === s ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: '0.78rem', padding: '6px 14px', textTransform: 'capitalize' }}
                  onClick={() => handleStatusChange(s)}
                  disabled={loading || patient.status === s}
                >
                  {s.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn btn-danger" onClick={handleRemove} disabled={loading}>
            🗑 Remove from Queue
          </button>
          <button className="btn btn-ghost" onClick={onClose} style={{ marginLeft: 'auto' }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
