import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchApi, postApi, putApi } from '../api';
import { Camera, CheckCircle, Lock, ArrowLeft, Loader2 } from 'lucide-react';
import './ConditionReports.css';

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

export default function ConditionReports() {
  const { id } = useParams<{ id: string }>();
  const [reportType, setReportType] = useState<'check_in' | 'check_out'>('check_in');
  const [report, setReport] = useState<ConditionReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadReport();
  }, [id, reportType]);

  const loadReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchApi<ConditionReport>(`/tenancies/${id}/condition-report/${reportType}`);
      setReport(data);
    } catch (e: any) {
      if (e.message.includes('404')) {
        setReport(null); // Report doesn't exist yet
      } else {
        setError(e.message);
      }
    }
    setLoading(false);
  };

  const createReport = async () => {
    try {
      const newReport = await postApi<ConditionReport>(`/tenancies/${id}/condition-report`, { report_type: reportType });
      setReport(newReport);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const updateItem = async (itemId: string, updates: Partial<ConditionItem>) => {
    if (!report || report.is_locked) return;
    try {
      // Optimistic update
      const updatedItems = report.items.map(it => it.id === itemId ? { ...it, ...updates } : it);
      setReport({ ...report, items: updatedItems });

      const currentItem = report.items.find(it => it.id === itemId);
      await putApi(`/condition-reports/${report.id}/items/${itemId}`, { ...currentItem, ...updates });
    } catch (e: any) {
      setError(`Failed to update item: ${e.message}`);
      loadReport(); // revert
    }
  };

  const handlePhotoUpload = async (itemId: string, file: File) => {
    if (!report || report.is_locked) return;
    try {
      // 1. Get presigned URL
      const { url, key } = await postApi<{ url: string; key: string }>('/upload/presigned-url', {
        filename: file.name,
        content_type: file.type
      });

      // 2. Upload to R2 directly
      const uploadRes = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
      });

      if (!uploadRes.ok) throw new Error('Failed to upload image to storage');

      // 3. Update the item with the new URL (in a real app, this would be a public URL, we'll just mock it as the key for now or a generic URL if bucket isn't public)
      const publicUrl = `https://pgpal-condition-reports.r2.cloudflarestorage.com/${key}`; // Replace with actual public URL pattern
      await updateItem(itemId, { photo_url: publicUrl });

    } catch (e: any) {
      setError(`Failed to upload photo: ${e.message}`);
    }
  };

  const signReport = async (role: 'operator' | 'tenant') => {
    if (!report) return;
    try {
      const updated = await postApi<ConditionReport>(`/condition-reports/${report.id}/sign?role=${role}`);
      setReport(updated);
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="page condition-reports-page">
      <header className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link to="/tenancies" className="back-link"><ArrowLeft size={20} /></Link>
          <div>
            <h1 className="page-title">Condition Reports</h1>
            <p className="page-subtitle">Tenancy {id?.slice(0, 8)}...</p>
          </div>
        </div>
        <div className="report-tabs">
          <button 
            className={`tab ${reportType === 'check_in' ? 'active' : ''}`}
            onClick={() => setReportType('check_in')}
          >
            Check-in
          </button>
          <button 
            className={`tab ${reportType === 'check_out' ? 'active' : ''}`}
            onClick={() => setReportType('check_out')}
          >
            Check-out
          </button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading-state"><Loader2 className="spinner" /></div>
      ) : !report ? (
        <div className="empty-state">
          <h3>No {reportType.replace('_', '-')} report found</h3>
          <p>Would you like to generate one now?</p>
          <button className="primary-button" onClick={createReport}>Generate Report</button>
        </div>
      ) : (
        <div className="report-container">
          <div className="report-status">
            {report.is_locked ? (
              <span className="badge locked"><Lock size={14} /> Locked (Signed by both)</span>
            ) : (
              <span className="badge draft">Draft (Awaiting Signatures)</span>
            )}
          </div>

          <div className="checklist">
            {report.items.map(item => (
              <div key={item.id} className="checklist-item">
                <div className="item-header">
                  <h4>{item.item_name}</h4>
                  <div className="condition-toggles">
                    {['good', 'fair', 'damaged', 'missing'].map(cond => (
                      <button
                        key={cond}
                        disabled={report.is_locked}
                        className={`cond-btn ${item.condition === cond ? 'selected' : ''} ${cond}`}
                        onClick={() => updateItem(item.id, { condition: cond as any })}
                      >
                        {cond}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="item-details">
                  <div className="photo-section">
                    {item.photo_url ? (
                      <div className="photo-preview">
                        <img src={item.photo_url} alt={item.item_name} />
                      </div>
                    ) : (
                      <label className={`photo-upload ${report.is_locked ? 'disabled' : ''}`}>
                        <Camera size={24} />
                        <span>Add Photo</span>
                        <input 
                          type="file" 
                          accept="image/*" 
                          disabled={report.is_locked}
                          onChange={(e) => e.target.files?.[0] && handlePhotoUpload(item.id, e.target.files[0])}
                        />
                      </label>
                    )}
                  </div>
                  <div className="notes-section">
                    <textarea 
                      placeholder="Add notes..." 
                      disabled={report.is_locked}
                      value={item.notes || ''}
                      onChange={(e) => updateItem(item.id, { notes: e.target.value })}
                    />
                    {reportType === 'check_out' && (
                      <input 
                        type="number" 
                        placeholder="Deduction ₹" 
                        disabled={report.is_locked}
                        value={item.deduction_amount || ''}
                        onChange={(e) => updateItem(item.id, { deduction_amount: e.target.value })}
                      />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="signatures">
            <button 
              className={`sign-btn ${report.signed_by_operator ? 'signed' : ''}`}
              onClick={() => signReport('operator')}
              disabled={report.signed_by_operator || report.is_locked}
            >
              {report.signed_by_operator ? <><CheckCircle size={18} /> Operator Signed</> : 'Sign as Operator'}
            </button>
            <button 
              className={`sign-btn ${report.signed_by_tenant ? 'signed' : ''}`}
              onClick={() => signReport('tenant')}
              disabled={report.signed_by_tenant || report.is_locked}
            >
              {report.signed_by_tenant ? <><CheckCircle size={18} /> Tenant Signed</> : 'Sign as Tenant'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
