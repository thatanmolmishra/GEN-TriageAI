import SeverityBadge from './SeverityBadge';

/**
 * SeverityPanel – Full result card shown after patient intake.
 */
export default function SeverityPanel({ result, onNewIntake }) {
  if (!result) return null;

  const waitLabel =
    result.severity === 'Critical' ? 'IMMEDIATE — NOW' :
    result.severity === 'Urgent'   ? `~${result.estimated_wait_minutes} minutes` :
                                     `~${result.estimated_wait_minutes} minutes`;

  const waitIcon =
    result.severity === 'Critical' ? '🚨' :
    result.severity === 'Urgent'   ? '⏱️' : '⏳';

  return (
    <div className="result-card">
      {/* Header */}
      <div className={`result-header ${result.severity}`}>
        <div className="result-top-row">
          <div className="result-severity-block">
            <div className="result-patient-name">{result.name}</div>
            <SeverityBadge severity={result.severity} />
          </div>
          <div className="result-confidence">
            <span className="result-confidence-label">AI Confidence</span>
            <span className="result-confidence-pct"
              style={{ color: `var(--${result.severity.toLowerCase()})` }}>
              {Math.round(result.confidence * 100)}%
            </span>
          </div>
        </div>

        {/* Wait time */}
        <div className="result-wait-info">
          <div className="result-wait-icon">{waitIcon}</div>
          <div className="result-wait-text">
            <div className="result-wait-title">Estimated Wait</div>
            <div className="result-wait-value">{waitLabel}</div>
          </div>
          <SeverityBadge severity={result.severity} />
        </div>
      </div>

      {/* Body */}
      <div className="result-body">
        {/* Message */}
        <p style={{ fontWeight: 600, fontSize: '0.95rem' }}>{result.message}</p>

        {/* Reasoning */}
        <div>
          <div className="modal-section-title">Clinical Reasoning</div>
          <div className="result-reasoning">{result.reasoning}</div>
        </div>

        {/* Recommended Actions */}
        <div>
          <div className="modal-section-title">Recommended Actions</div>
          <div className="result-actions-list">
            {result.recommended_actions.map((action, i) => (
              <div key={i} className={`result-action-item ${result.severity}`}>
                {action}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="result-footer">
        <button className="btn btn-ghost" onClick={onNewIntake} style={{ flex: 1 }}>
          ← New Patient
        </button>
        <button
          className="btn btn-primary"
          onClick={() => window.location.href = '/dashboard'}
          style={{ flex: 1 }}
        >
          View Dashboard →
        </button>
      </div>
    </div>
  );
}
