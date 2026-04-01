/**
 * StatsBar – Top summary bar: Total / Critical / Urgent / Minor / Alerts
 */
export default function StatsBar({ stats = {} }) {
  const { total = 0, critical = 0, urgent = 0, minor = 0, unacknowledged_alerts = 0 } = stats;

  return (
    <div className="stats-bar">
      <div className="stat-card total">
        <div className="stat-value">{total}</div>
        <div className="stat-label">Total Patients</div>
      </div>
      <div className="stat-card critical">
        <div className="stat-value">{critical}</div>
        <div className="stat-label">🔴 Critical</div>
      </div>
      <div className="stat-card urgent">
        <div className="stat-value">{urgent}</div>
        <div className="stat-label">🟠 Urgent</div>
      </div>
      <div className="stat-card minor">
        <div className="stat-value">{minor}</div>
        <div className="stat-label">🟢 Minor</div>
      </div>
      <div className="stat-card alerts">
        <div className="stat-value">{unacknowledged_alerts}</div>
        <div className="stat-label">⚠ Unread Alerts</div>
      </div>
    </div>
  );
}
