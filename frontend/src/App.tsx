import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Properties from './pages/Properties';
import Tenancies from './pages/Tenancies';
import ConditionReports from './pages/ConditionReports';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/properties" element={<Properties />} />
          <Route path="/tenancies" element={<Tenancies />} />
          <Route path="/tenancies/:id/condition-reports" element={<ConditionReports />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
