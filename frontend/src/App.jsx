import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import IntakePage from './pages/IntakePage';
import DashboardPage from './pages/DashboardPage';
import { useWebSocket } from './hooks/useWebSocket';
import { useCallback, useState } from 'react';

function Navbar({ wsStatus }) {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <div className="navbar-logo-icon">🏥</div>
        <span className="navbar-logo-text">TriageAI</span>
        <span className="navbar-logo-badge">LIVE</span>
      </div>

      <div className="navbar-nav">
        <NavLink
          to="/intake"
          id="nav-intake"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          📝 Intake
        </NavLink>
        <NavLink
          to="/dashboard"
          id="nav-dashboard"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          📊 Dashboard
        </NavLink>
      </div>

      <div className="navbar-status">
        <div className={`status-dot ${wsStatus}`} />
        <span>
          {wsStatus === 'connected' ? 'Live' :
           wsStatus === 'connecting' ? 'Connecting…' : 'Disconnected'}
        </span>
      </div>
    </nav>
  );
}

export default function App() {
  const [wsStatus, setWsStatus] = useState('connecting');

  // Lightweight ws status tracking (Dashboard manages the real connection)
  // This is just for Navbar display
  const handleMsg = useCallback(() => {}, []);

  return (
    <BrowserRouter>
      <Navbar wsStatus={wsStatus} />
      <Routes>
        <Route path="/" element={<Navigate to="/intake" replace />} />
        <Route path="/intake" element={<IntakePage />} />
        <Route
          path="/dashboard"
          element={<DashboardPage onWsStatus={setWsStatus} />}
        />
      </Routes>
    </BrowserRouter>
  );
}
