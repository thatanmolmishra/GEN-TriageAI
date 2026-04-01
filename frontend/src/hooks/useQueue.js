import { useState, useCallback } from 'react';
import { getQueue } from '../api/triageAPI';

/**
 * Manages the ER queue state from WebSocket updates + REST polling fallback.
 */
export function useQueue() {
  const [patients, setPatients] = useState([]);
  const [stats, setStats] = useState({ total: 0, critical: 0, urgent: 0, minor: 0, unacknowledged_alerts: 0 });
  const [alerts, setAlerts] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);

  const applyUpdate = useCallback((payload) => {
    if (!payload?.type) return;

    if (payload.type === 'dashboard_update') {
      const { queue, alerts: alertsData } = payload.data;
      if (queue?.patients) setPatients(queue.patients);
      if (queue?.stats) setStats(queue.stats);
      if (alertsData) setAlerts(alertsData);
      setLastUpdated(new Date(payload.timestamp));
    } else if (payload.type === 'queue_update') {
      const { patients: pts, stats: s } = payload.data;
      if (pts) setPatients(pts);
      if (s) setStats(s);
      setLastUpdated(new Date(payload.timestamp));
    } else if (payload.type === 'alert') {
      const { alerts: alertsData } = payload.data;
      if (alertsData) setAlerts(alertsData);
    }
  }, []);

  const refreshFromAPI = useCallback(async () => {
    try {
      const data = await getQueue();
      setPatients(data.patients || []);
      setStats({
        total: data.total,
        critical: data.critical_count,
        urgent: data.urgent_count,
        minor: data.minor_count,
      });
      setLastUpdated(new Date());
    } catch (e) {
      console.error('[useQueue] REST fetch failed:', e);
    }
  }, []);

  return { patients, stats, alerts, lastUpdated, applyUpdate, refreshFromAPI };
}
