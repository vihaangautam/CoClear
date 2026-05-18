import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchApi, postApi, putApi } from '../../api';
import { Camera, CheckCircle, Lock, Loader2 } from 'lucide-react';
import './TenantConditionReport.css';

interface ConditionItem {
  id: string;
  item_name: string;
  condition: 'good' | 'fair' | 'damaged' | 'missing' | null;
  notes: string | null;
  photo_url: string | null;
  deduction_amount: string | null;
  disputed: boolean;
}

interface ConditionReport {
  id: string;
  tenancy_id: string;
  report_type: 'check_in' | 'check_out';
  signed_by_operator: boolean;
  signed_by_tenant: boolean;
  is_locked: boolean;
  items: ConditionItem[];
}

export default function TenantConditionReport() {
  const navigate = useNavigate();
  const [reportType, setReportType] = useState<'check_in' | 'check_out'>('check_in');
  const [report, setReport] = useState<ConditionReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const tenancyId = (() => {
    const stored = sessionStorage.getItem('tenant_tenancies');
    if (!stored) return null;
    const tenancies = JSON.parse(stored);
    const active = tenancies.find((t: any) => t.status === 'active') || tenancies[0];
    return active?.id || null;
  })();

  useEffect(() => {
    if (!tenancyId) {
      navigate('/tenant');
      return;
    }
    loadReport();
  }, [tenancyId, reportType]);

  const loadReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchApi<ConditionReport>(`/tenancies/${tenancyId}/condition-report/${reportType}`);
      setReport(data);
    } catch (e: any) {
      if (e.message.includes('404')) {
        setReport(null);
      } else {
        setError(e.message);
      }
    }
    setLoading(false);
  };

  const signReport = async () => {
    if (!report) return;
    try {
      const updated = await postApi<ConditionReport>(`/condition-reports/${report.id}/sign?role=tenant`);
      setReport(updated);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const conditionLabel = (c: string | null) => {
    if (!c) return '—';
    return c.charAt(0).toUpperCase() + c.slice(1);
  };

  const conditionColor = (c: string | null) => {
    switch (c) {
      case 'good': return 'var(--accent-green)';
      case 'fair': return 'var(--accent-orange)';
      case 'damaged': return 'var(--accent-red)';
      case 'missing': return '#374151';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div className="tenant-cr-page">
      <h2 className="cr-title">Room Check Report</h2>
      <p className="cr-subtitle">Review the condition of your room items and sign to confirm</p>

      <div className="cr-tabs">
        <button
          className={`cr-tab ${reportType === 'check_in' ? 'active' : ''}`}
          onClick={() => setReportType('check_in')}
        >
          Check-in
        </button>
        <button
          className={`cr-tab ${reportType === 'check_out' ? 'active' : ''}`}
          onClick={() => setReportType('check_out')}
        >
          Check-out
        </button>
      </div>

      {error && <div className="cr-error">{error}</div>}

      {loading ? (
        <div className="cr-loading"><Loader2 className="spinner" /> Loading...</div>
      ) : !report ? (
        <div className="cr-empty">
          <p>No {reportType.replace('_', '-')} report created yet.</p>
          <p className="cr-empty-sub">Your PG owner will create this before you move in or out.</p>
        </div>
      ) : (
        <div className="cr-report">
          {/* Status Badge */}
          <div className="cr-status">
            {report.is_locked ? (
              <span className="cr-badge locked"><Lock size={14} /> Signed & Locked</span>
            ) : report.signed_by_operator && !report.signed_by_tenant ? (
              <span className="cr-badge pending">Owner signed — your turn!</span>
            ) : (
              <span className="cr-badge draft">Waiting for signatures</span>
            )}
          </div>

          {/* Checklist Items */}
          <div className="cr-items">
            {report.items.map(item => (
              <div key={item.id} className="cr-item">
                <div className="cr-item-top">
                  <span className="cr-item-name">{item.item_name}</span>
                  <span className="cr-item-cond" style={{ color: conditionColor(item.condition) }}>
                    {conditionLabel(item.condition)}
                  </span>
                </div>
                {item.notes && <p className="cr-item-notes">{item.notes}</p>}
                {item.photo_url && (
                  <div className="cr-item-photo">
                    <img src={item.photo_url} alt={item.item_name} />
                  </div>
                )}
                {item.deduction_amount && parseFloat(item.deduction_amount) > 0 && (
                  <span className="cr-deduction">
                    Deduction: ₹{parseFloat(item.deduction_amount).toLocaleString('en-IN')}
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Signature Section */}
          <div className="cr-signatures">
            <div className={`cr-sig-card ${report.signed_by_operator ? 'signed' : ''}`}>
              <span>Owner</span>
              {report.signed_by_operator ? <CheckCircle size={20} /> : <span className="sig-pending">Pending</span>}
            </div>
            <div className={`cr-sig-card ${report.signed_by_tenant ? 'signed' : ''}`}>
              <span>You</span>
              {report.signed_by_tenant ? <CheckCircle size={20} /> : <span className="sig-pending">Pending</span>}
            </div>
          </div>

          {/* Sign Button */}
          {!report.signed_by_tenant && !report.is_locked && (
            <button className="cr-sign-btn" onClick={signReport}>
              <CheckCircle size={20} />
              I confirm this is accurate — Sign
            </button>
          )}

          {report.is_locked && (
            <p className="cr-locked-msg">
              ✅ This report is locked and cannot be changed. Both you and your PG owner have signed it.
              This is your proof.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
