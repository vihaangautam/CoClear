import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, ChevronRight, FileCheck } from 'lucide-react';
import { fetchApi } from '../api';
import './Pages.css';

interface Tenancy {
  id: string; status: string; rent_amount: string; deposit_amount: string;
  move_in_date: string | null; notice_given_date: string | null; vacating_date: string | null;
  tenant: { id: string; name: string; phone: string } | null;
  bed: { id: string; label: string } | null;
}

const statusStyles: Record<string, { bg: string; color: string }> = {
  active:        { bg: 'var(--accent-green-bg)', color: 'var(--accent-green)' },
  notice_period: { bg: 'var(--accent-orange-bg)', color: 'var(--accent-orange)' },
  inquiry:       { bg: 'var(--accent-blue-bg)', color: 'var(--accent-blue)' },
  confirmed:     { bg: 'var(--accent-blue-bg)', color: 'var(--accent-blue)' },
  vacated:       { bg: '#f3f4f6', color: 'var(--text-muted)' },
  cancelled:     { bg: 'var(--accent-red-bg)', color: 'var(--accent-red)' },
};

export default function Tenancies() {
  const [tenancies, setTenancies] = useState<Tenancy[]>([]);
  useEffect(() => { fetchApi<Tenancy[]>('/tenancies').then(setTenancies); }, []);

  const fmt = (v: string) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(parseFloat(v));

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Tenancies</h1>
          <p className="page-subtitle">{tenancies.length} total records across all properties</p>
        </div>
      </header>

      <div className="table-card card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Tenant</th>
              <th>Bed</th>
              <th>Status</th>
              <th>Rent</th>
              <th>Deposit</th>
              <th>Move-in</th>
              <th>Reports</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {tenancies.map((t) => {
              const s = statusStyles[t.status] || statusStyles.active;
              return (
                <tr key={t.id}>
                  <td>
                    <div className="cell-with-icon">
                      <div className="cell-icon"><Users size={16} /></div>
                      <div>
                        <span className="cell-primary">{t.tenant?.name ?? 'N/A'}</span>
                        <span className="cell-sub">{t.tenant?.phone ?? ''}</span>
                      </div>
                    </div>
                  </td>
                  <td><span className="mono-text">{t.bed?.label ?? '—'}</span></td>
                  <td>
                    <span className="status-badge" style={{ background: s.bg, color: s.color }}>
                      {t.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>{fmt(t.rent_amount)}</td>
                  <td>{fmt(t.deposit_amount)}</td>
                  <td className="mono-text">{t.move_in_date ? new Date(t.move_in_date).toLocaleDateString('en-IN') : '—'}</td>
                  <td>
                    <Link to={`/tenancies/${t.id}/condition-reports`} className="row-action" title="Condition Reports">
                      <FileCheck size={18} />
                    </Link>
                  </td>
                  <td><button className="row-action"><ChevronRight size={16} /></button></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
