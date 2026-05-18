import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchApi } from '../../api';
import { Bed, IndianRupee, CalendarDays, AlertCircle, FileCheck, MessageSquare } from 'lucide-react';
import './TenantHome.css';

interface TenancyInfo {
  id: string;
  status: string;
  rent_amount: string;
  deposit_amount: string;
  move_in_date: string | null;
  bed_label: string | null;
}

interface PaymentInfo {
  id: string;
  amount: string;
  payment_date: string;
  method: string | null;
  note: string | null;
}

export default function TenantHome() {
  const navigate = useNavigate();
  const tenantName = sessionStorage.getItem('tenant_name') || 'Tenant';
  const [tenancies, setTenancies] = useState<TenancyInfo[]>([]);
  const [payments, setPayments] = useState<PaymentInfo[]>([]);
  const [activeTenancy, setActiveTenancy] = useState<TenancyInfo | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem('tenant_tenancies');
    if (!stored) {
      navigate('/tenant');
      return;
    }
    const parsed: TenancyInfo[] = JSON.parse(stored);
    setTenancies(parsed);
    // Pick the first active tenancy (or the first one if none are active)
    const active = parsed.find(t => t.status === 'active') || parsed[0];
    setActiveTenancy(active);

    if (active) {
      fetchApi<PaymentInfo[]>(`/tenancies/${active.id}/payments`).then(setPayments).catch(() => {});
    }
  }, []);

  const fmt = (v: string) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(parseFloat(v));

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  if (!activeTenancy) {
    return (
      <div className="tenant-empty">
        <AlertCircle size={48} />
        <h3>No active room found</h3>
        <p>Please contact your PG owner if you think this is a mistake.</p>
      </div>
    );
  }

  return (
    <div className="tenant-home">
      <div className="greeting-section">
        <h1>{greeting()}, {tenantName.split(' ')[0]}!</h1>
        <p className="greeting-sub">Here's everything about your stay</p>
      </div>

      {/* Room Info Card */}
      <div className="info-card room-card">
        <div className="info-card-header">
          <Bed size={20} />
          <h3>Your Room</h3>
        </div>
        <div className="room-details">
          <div className="detail-row">
            <span className="detail-label">Bed</span>
            <span className="detail-value">{activeTenancy.bed_label || 'Not assigned'}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Status</span>
            <span className={`status-pill ${activeTenancy.status}`}>
              {activeTenancy.status === 'active' ? 'Living here' :
               activeTenancy.status === 'notice_period' ? 'Moving out soon' :
               activeTenancy.status.replace('_', ' ')}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Moved in</span>
            <span className="detail-value">
              {activeTenancy.move_in_date
                ? new Date(activeTenancy.move_in_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
                : 'Not recorded'}
            </span>
          </div>
        </div>
      </div>

      {/* Money Summary */}
      <div className="money-grid">
        <div className="info-card money-card">
          <div className="info-card-header">
            <IndianRupee size={18} />
            <h3>Monthly Rent</h3>
          </div>
          <div className="money-value">{fmt(activeTenancy.rent_amount)}</div>
        </div>
        <div className="info-card money-card">
          <div className="info-card-header">
            <IndianRupee size={18} />
            <h3>Your Deposit</h3>
          </div>
          <div className="money-value">{fmt(activeTenancy.deposit_amount)}</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-grid">
          <button className="action-card" onClick={() => navigate('/tenant/condition-report')}>
            <FileCheck size={24} />
            <span>Room Check</span>
            <span className="action-desc">View or sign your check-in / check-out report</span>
          </button>
          <button className="action-card" onClick={() => navigate('/tenant/complaints')}>
            <MessageSquare size={24} />
            <span>Raise Complaint</span>
            <span className="action-desc">AC broken? Wifi down? Let your owner know</span>
          </button>
        </div>
      </div>

      {/* Recent Payments */}
      {payments.length > 0 && (
        <div className="info-card payments-section">
          <div className="info-card-header">
            <CalendarDays size={20} />
            <h3>Recent Payments</h3>
          </div>
          <div className="payments-list">
            {payments.slice(0, 5).map(p => (
              <div key={p.id} className="payment-row">
                <div className="payment-info">
                  <span className="payment-amount">{fmt(p.amount)}</span>
                  <span className="payment-date">
                    {new Date(p.payment_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                  </span>
                </div>
                <span className="payment-method">{p.method || 'cash'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
