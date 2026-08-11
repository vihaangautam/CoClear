import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import TenantLayout from './components/TenantLayout';
import OperatorLogin from './pages/OperatorLogin';
import Dashboard from './pages/Dashboard';
import Properties from './pages/Properties';
import Tenancies from './pages/Tenancies';
import ConditionReports from './pages/ConditionReports';
import Tickets from './pages/Tickets';
import TenantLogin from './pages/tenant/TenantLogin';
import TenantHome from './pages/tenant/TenantHome';
import TenantConditionReport from './pages/tenant/TenantConditionReport';
import TenantComplaints from './pages/tenant/TenantComplaints';
import './index.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* ── Operator Auth ── */}
          <Route path="/login" element={<OperatorLogin />} />

          {/* ── Operator Panel (Protected) ── */}
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/properties" element={<Properties />} />
              <Route path="/tenancies" element={<Tenancies />} />
              <Route path="/tenancies/:id/condition-reports" element={<ConditionReports />} />
              <Route path="/tickets" element={<Tickets />} />
            </Route>
          </Route>

          {/* ── Tenant Portal ── */}
          <Route path="/tenant" element={<TenantLogin />} />
          <Route element={<TenantLayout />}>
            <Route path="/tenant/home" element={<TenantHome />} />
            <Route path="/tenant/condition-report" element={<TenantConditionReport />} />
            <Route path="/tenant/complaints" element={<TenantComplaints />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;