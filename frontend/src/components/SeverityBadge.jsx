/**
 * SeverityBadge – Color-coded pill badge for Critical / Urgent / Minor
 */
export default function SeverityBadge({ severity, size = 'sm' }) {
  if (!severity) return null;

  const icons = { Critical: '🔴', Urgent: '🟠', Minor: '🟢' };

  return (
    <span className={`severity-badge ${severity}`}>
      <span className="badge-dot" />
      {severity}
    </span>
  );
}
