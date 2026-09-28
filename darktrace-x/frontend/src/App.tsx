import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ActorsPage } from './pages/ActorsPage';
import { ActorDetailPage } from './pages/ActorDetailPage';
import { PersonasPage } from './pages/PersonasPage';
import { IntelligencePage } from './pages/IntelligencePage';
import { GraphPage } from './pages/GraphPage';
import { TimelinePage } from './pages/TimelinePage';
import { InfrastructurePage } from './pages/InfrastructurePage';
import { EvidencePage } from './pages/EvidencePage';
import { AttributionPage } from './pages/AttributionPage';
import { SearchPage } from './pages/SearchPage';
import { ReportsPage } from './pages/ReportsPage';
import { AuditPage } from './pages/AuditPage';
import { SettingsPage } from './pages/SettingsPage';
import { InvestigationsPage } from './pages/InvestigationsPage';
import { CampaignsPage } from './pages/CampaignsPage';
import { AlertsPage } from './pages/AlertsPage';
import { AIPatternAnalysisPage } from './pages/AIPatternAnalysisPage';

// Protected Route Wrapper
const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const token = localStorage.getItem('darktrace_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

interface ErrorBoundaryState {
  hasError: boolean;
  error: any;
}

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('DARKTRACE-X Intercepted Exception:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#04060A] text-slate-100 flex items-center justify-center p-6 font-mono">
          <div className="max-w-lg w-full bg-slate-950 border border-rose-500/40 rounded-xl p-6 shadow-[0_0_40px_rgba(244,63,94,0.2)] space-y-4 text-center">
            <div>
              <h2 className="text-sm font-black text-rose-400 uppercase tracking-wider">
                TACTICAL UI RECOVERY INTERFACE
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                An unexpected component exception was intercepted. Threat telemetry and session data are secure.
              </p>
            </div>
            <div className="p-2.5 rounded bg-black/60 border border-slate-800 text-[11px] text-slate-300 text-left font-mono break-all max-h-24 overflow-y-auto">
              {String(this.state.error?.message || this.state.error || 'Unknown UI Error')}
            </div>
            <div className="flex gap-2 justify-center">
              <button
                onClick={() => { this.setState({ hasError: false, error: null }); window.location.href = '/dashboard'; }}
                className="px-4 py-2 rounded-lg bg-[#00D9FF] hover:bg-[#00c2e6] text-black font-extrabold text-xs"
              >
                RETURN TO WAR ROOM
              </button>
              <button
                onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload(); }}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs"
              >
                RELOAD SYSTEM
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Investigation Shell */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="investigations" element={<InvestigationsPage />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="actors" element={<ActorsPage />} />
          <Route path="actors/:id" element={<ActorDetailPage />} />
          <Route path="personas" element={<PersonasPage />} />
          <Route path="intelligence" element={<IntelligencePage />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="timeline" element={<TimelinePage />} />
          <Route path="infrastructure" element={<InfrastructurePage />} />
          <Route path="evidence" element={<EvidencePage />} />
          <Route path="evidence/:id" element={<EvidencePage />} />
          <Route path="attribution" element={<AttributionPage />} />
          <Route path="ai-analysis" element={<AIPatternAnalysisPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  </ErrorBoundary>
  );
};

export default App;
