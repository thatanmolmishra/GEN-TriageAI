import { useState } from 'react';
import IntakeChat from '../components/IntakeChat';
import SeverityPanel from '../components/SeverityPanel';
import { submitIntake } from '../api/triageAPI';

export default function IntakePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const res = await submitIntake(data);
      setResult(res);
    } catch (e) {
      const msg = e.response?.data?.detail;
      setError(Array.isArray(msg) ? msg.join(' | ') : (msg || 'Something went wrong. Is the backend running?'));
    } finally {
      setLoading(false);
    }
  };

  const handleNewIntake = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="intake-page">
      {!result ? (
        <>
          {/* Hero */}
          <div className="intake-hero">
            <h1>AI Triage Assessment</h1>
            <p>
              Submit patient symptoms for instant AI-powered severity assessment
              powered by Google Gemini 1.5 Flash.
            </p>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              width: '100%', maxWidth: 680,
              background: 'var(--critical-dim)',
              border: '1px solid rgba(255,45,85,0.3)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-md) var(--space-lg)',
              color: 'var(--critical)',
              fontSize: '0.875rem',
              marginBottom: 'var(--space-md)',
            }}>
              ⚠️ {error}
            </div>
          )}

          {/* Form */}
          <div className="intake-card">
            <IntakeChat onSubmit={handleSubmit} loading={loading} />
          </div>

          {/* Info pills */}
          <div style={{
            display: 'flex', gap: 12, marginTop: 'var(--space-lg)',
            flexWrap: 'wrap', justifyContent: 'center',
          }}>
            {[
              { icon: '🔴', label: 'Critical → Immediate' },
              { icon: '🟠', label: 'Urgent → ≤30 mins' },
              { icon: '🟢', label: 'Minor → Standard queue' },
              { icon: '🤖', label: 'Powered by Gemini 1.5 Flash' },
            ].map((item) => (
              <div key={item.label} style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '6px 14px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.78rem', color: 'var(--text-secondary)',
              }}>
                {item.icon} {item.label}
              </div>
            ))}
          </div>
        </>
      ) : (
        <>
          <div className="intake-hero" style={{ marginBottom: 'var(--space-lg)' }}>
            <h1 style={{ fontSize: '1.75rem' }}>Assessment Complete</h1>
          </div>
          <SeverityPanel result={result} onNewIntake={handleNewIntake} />
        </>
      )}
    </div>
  );
}
