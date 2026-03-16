import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import DashboardPage from './pages/DashboardPage';
import InspectPage from './pages/InspectPage';
import HistoryPage from './pages/HistoryPage';
import ResultDetailPage from './pages/ResultDetailPage';
import StatsPage from './pages/StatsPage';
import SystemPage from './pages/SystemPage';


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/"            element={<DashboardPage />} />
          <Route path="/inspect"     element={<InspectPage />} />
          <Route path="/history"     element={<HistoryPage />} />
          <Route path="/history/:id" element={<ResultDetailPage />} />
          <Route path="/stats"       element={<StatsPage />} />
          <Route path="/system"      element={<SystemPage />} />
          
          {/* Redirects for legacy routes */}
          <Route path="/upload"      element={<Navigate to="/inspect" replace />} />
          <Route path="/camera"      element={<Navigate to="/inspect" replace />} />
          <Route path="/dashboard"   element={<Navigate to="/" replace />} />
          <Route path="/results/:id" element={<Navigate to="/history/:id" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
