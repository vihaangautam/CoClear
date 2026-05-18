import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchApi, postApi } from '../../api';
import { Plus, AlertCircle, CheckCircle2, Clock, X } from 'lucide-react';
import './TenantComplaints.css';

interface Ticket {
  id: string;
  tenancy_id: string;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  updated_at: string;
}

export default function TenantComplaints() {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({ title: '', description: '', priority: 'medium' });

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
    loadTickets();
  }, [tenancyId]);

  const loadTickets = async () => {
    setLoading(true);
    try {
      const data = await fetchApi<Ticket[]>(`/tenant/tenancies/${tenancyId}/tickets`);
      setTickets(data);
    } catch {
      setTickets([]);
    }
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicket.title || !newTicket.description) return;
    try {
      const created = await postApi<Ticket>(`/tenancies/${tenancyId}/tickets`, {
        title: newTicket.title,
        description: newTicket.description,
        priority: newTicket.priority,
      });
      setTickets([created, ...tickets]);
      setIsModalOpen(false);
      setNewTicket({ title: '', description: '', priority: 'medium' });
    } catch (e: any) {
      alert(`Error: ${e.message}`);
    }
  };

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'resolved': return { icon: <CheckCircle2 size={16} />, label: 'Fixed', color: 'var(--accent-green)', bg: 'var(--accent-green-bg)' };
      case 'in_progress': return { icon: <Clock size={16} />, label: 'Working on it', color: 'var(--accent-orange)', bg: 'var(--accent-orange-bg)' };
      default: return { icon: <AlertCircle size={16} />, label: 'Raised', color: 'var(--accent-red)', bg: 'var(--accent-red-bg)' };
    }
  };

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / 3600000);
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  };

  return (
    <div className="tenant-complaints">
      <div className="complaints-header">
        <div>
          <h2>Complaints</h2>
          <p className="complaints-sub">Let your PG owner know about any issues</p>
        </div>
        <button className="new-complaint-btn" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} />
          <span>New</span>
        </button>
      </div>

      {loading ? (
        <div className="complaints-loading">Loading...</div>
      ) : tickets.length === 0 ? (
        <div className="complaints-empty">
          <CheckCircle2 size={48} className="empty-check" />
          <h3>No complaints</h3>
          <p>Everything looks good! Tap "New" if something needs fixing.</p>
        </div>
      ) : (
        <div className="complaints-list">
          {tickets.map(ticket => {
            const statusInfo = getStatusInfo(ticket.status);
            return (
              <div key={ticket.id} className="complaint-card">
                <div className="complaint-top">
                  <h4 className="complaint-title">{ticket.title}</h4>
                  <span className="complaint-time">{timeAgo(ticket.created_at)}</span>
                </div>
                <p className="complaint-desc">{ticket.description}</p>
                <div className="complaint-footer">
                  <span className="complaint-status" style={{ color: statusInfo.color, background: statusInfo.bg }}>
                    {statusInfo.icon}
                    {statusInfo.label}
                  </span>
                  <span className="complaint-priority">{ticket.priority}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* New Complaint Modal */}
      {isModalOpen && (
        <div className="complaint-modal-backdrop">
          <div className="complaint-modal">
            <div className="complaint-modal-header">
              <h3>What's the problem?</h3>
              <button className="modal-close" onClick={() => setIsModalOpen(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="complaint-form">
              <div className="complaint-field">
                <label>Issue (short)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., AC not cooling, wifi down"
                  value={newTicket.title}
                  onChange={(e) => setNewTicket({ ...newTicket, title: e.target.value })}
                  autoFocus
                />
              </div>

              <div className="complaint-field">
                <label>Details</label>
                <textarea
                  required
                  rows={3}
                  placeholder="When did this start? Anything you've already tried?"
                  value={newTicket.description}
                  onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                />
              </div>

              <div className="complaint-field">
                <label>How urgent?</label>
                <div className="priority-pills">
                  {['low', 'medium', 'high', 'urgent'].map(p => (
                    <button
                      key={p}
                      type="button"
                      className={`priority-pill ${newTicket.priority === p ? 'active' : ''} ${p}`}
                      onClick={() => setNewTicket({ ...newTicket, priority: p })}
                    >
                      {p === 'low' ? '😊 Low' : p === 'medium' ? '⚠️ Medium' : p === 'high' ? '🔥 High' : '🚨 Urgent'}
                    </button>
                  ))}
                </div>
              </div>

              <button type="submit" className="submit-complaint-btn">
                Submit Complaint
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
