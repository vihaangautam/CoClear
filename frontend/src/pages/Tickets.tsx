import { useEffect, useState } from 'react';
import { fetchApi, postApi, patchApi } from '../api';
import { 
  Plus, Search, AlertCircle, CheckCircle2, Clock, 
  HelpCircle, ChevronRight, X, User, Home, ArrowUpDown, Filter
} from 'lucide-react';
import './Tickets.css';

interface Tenant {
  id: string;
  name: string;
  phone: string;
}

interface Bed {
  id: string;
  label: string;
}

interface Tenancy {
  id: string;
  status: string;
  tenant: Tenant | null;
  bed: Bed | null;
}

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

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [tenancies, setTenancies] = useState<Tenancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter and Search States
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({
    tenancy_id: '',
    title: '',
    description: '',
    priority: 'medium'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const ticketsData = await fetchApi<Ticket[]>('/tickets');
      const tenanciesData = await fetchApi<Tenancy[]>('/tenancies');
      setTickets(ticketsData);
      setTenancies(tenanciesData.filter(t => t.status === 'active'));
    } catch (e: any) {
      setError(e.message || 'Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicket.tenancy_id || !newTicket.title || !newTicket.description) {
      alert('Please fill out all required fields.');
      return;
    }

    try {
      const created = await postApi<Ticket>(
        `/tenancies/${newTicket.tenancy_id}/tickets`,
        {
          title: newTicket.title,
          description: newTicket.description,
          priority: newTicket.priority
        }
      );
      setTickets([created, ...tickets]);
      setIsModalOpen(false);
      setNewTicket({ tenancy_id: '', title: '', description: '', priority: 'medium' });
    } catch (e: any) {
      alert(`Error creating ticket: ${e.message}`);
    }
  };

  const handleUpdateStatus = async (ticketId: string, newStatus: 'open' | 'in_progress' | 'resolved') => {
    try {
      const updated = await patchApi<Ticket>(`/tickets/${ticketId}`, { status: newStatus });
      setTickets(tickets.map(t => t.id === ticketId ? updated : t));
    } catch (e: any) {
      alert(`Error updating ticket status: ${e.message}`);
    }
  };

  const handleUpdatePriority = async (ticketId: string, newPriority: 'low' | 'medium' | 'high' | 'urgent') => {
    try {
      const updated = await patchApi<Ticket>(`/tickets/${ticketId}`, { priority: newPriority });
      setTickets(tickets.map(t => t.id === ticketId ? updated : t));
    } catch (e: any) {
      alert(`Error updating ticket priority: ${e.message}`);
    }
  };

  // Find tenancy details for a ticket
  const getTenancyDetails = (tenancyId: string) => {
    const fullTenancies = tenancies.length > 0 ? tenancies : [];
    const tenancy = fullTenancies.find(t => t.id === tenancyId);
    return {
      tenantName: tenancy?.tenant?.name || 'Unknown Tenant',
      bedLabel: tenancy?.bed?.label || 'No Bed Assigned'
    };
  };

  // Filter logic
  const filteredTickets = tickets.filter(ticket => {
    const tenancyDetails = getTenancyDetails(ticket.tenancy_id);
    const matchesSearch = 
      ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tenancyDetails.tenantName.toLowerCase().includes(searchQuery.toLowerCase());
      
    const matchesStatus = statusFilter === 'all' || ticket.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || ticket.priority === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  const getPriorityStyle = (priority: string) => {
    switch (priority) {
      case 'urgent': return { bg: '#fee2e2', color: '#991b1b', label: 'Urgent' };
      case 'high': return { bg: '#ffedd5', color: '#c2410c', label: 'High' };
      case 'medium': return { bg: '#e0f2fe', color: '#0369a1', label: 'Medium' };
      default: return { bg: '#f3f4f6', color: '#374151', label: 'Low' };
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'resolved': return <CheckCircle2 size={16} className="status-resolved-icon" />;
      case 'in_progress': return <Clock size={16} className="status-progress-icon" />;
      default: return <AlertCircle size={16} className="status-open-icon" />;
    }
  };

  return (
    <div className="page tickets-page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Support Tickets</h1>
          <p className="page-subtitle">Track, manage, and resolve tenant complaints</p>
        </div>
        <button className="primary-button add-ticket-btn" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} />
          <span>New Ticket</span>
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* Control panel for searching and filtering */}
      <div className="card controls-card">
        <div className="search-bar">
          <Search size={18} className="search-icon" />
          <input 
            type="text" 
            placeholder="Search by title, description, or tenant..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filters-group">
          <div className="filter-item">
            <Filter size={14} className="filter-icon" />
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="all">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <div className="filter-item">
            <ArrowUpDown size={14} className="filter-icon" />
            <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
              <option value="all">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">Loading support tickets...</div>
      ) : filteredTickets.length === 0 ? (
        <div className="empty-state card">
          <HelpCircle size={48} className="empty-icon" />
          <h3>No tickets found</h3>
          <p>Try refining your search queries or create a new request above.</p>
        </div>
      ) : (
        <div className="tickets-grid">
          {filteredTickets.map(ticket => {
            const priorityStyle = getPriorityStyle(ticket.priority);
            const { tenantName, bedLabel } = getTenancyDetails(ticket.tenancy_id);

            return (
              <div key={ticket.id} className={`ticket-card card status-${ticket.status}`}>
                <div className="ticket-card-header">
                  <span className="priority-badge" style={{ backgroundColor: priorityStyle.bg, color: priorityStyle.color }}>
                    {priorityStyle.label}
                  </span>
                  <div className="status-indicator">
                    {getStatusIcon(ticket.status)}
                    <span className="status-label">{ticket.status.replace('_', ' ')}</span>
                  </div>
                </div>

                <h3 className="ticket-title">{ticket.title}</h3>
                <p className="ticket-desc">{ticket.description}</p>

                <div className="ticket-meta">
                  <div className="meta-row">
                    <User size={14} />
                    <span>{tenantName}</span>
                  </div>
                  <div className="meta-row">
                    <Home size={14} />
                    <span>{bedLabel}</span>
                  </div>
                </div>

                <div className="ticket-actions">
                  <div className="action-select">
                    <label>Status</label>
                    <select 
                      value={ticket.status} 
                      onChange={(e) => handleUpdateStatus(ticket.id, e.target.value as any)}
                    >
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                    </select>
                  </div>

                  <div className="action-select">
                    <label>Priority</label>
                    <select 
                      value={ticket.priority} 
                      onChange={(e) => handleUpdatePriority(ticket.id, e.target.value as any)}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Ticket Modal */}
      {isModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-content card">
            <div className="modal-header">
              <h3>Raise Maintenance Request</h3>
              <button className="close-btn" onClick={() => setIsModalOpen(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateTicket} className="modal-form">
              <div className="form-group">
                <label>Active Tenant / Bed <span className="required">*</span></label>
                <select 
                  required
                  value={newTicket.tenancy_id} 
                  onChange={(e) => setNewTicket({ ...newTicket, tenancy_id: e.target.value })}
                >
                  <option value="">Select Tenant</option>
                  {tenancies.map(t => (
                    <option key={t.id} value={t.id}>
                      {t.tenant?.name || 'Unknown'} - {t.bed?.label || 'No bed'}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Issue Title <span className="required">*</span></label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g., Water geyser not working"
                  value={newTicket.title}
                  onChange={(e) => setNewTicket({ ...newTicket, title: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Detailed Description <span className="required">*</span></label>
                <textarea 
                  required
                  rows={4}
                  placeholder="Describe the issue in detail..."
                  value={newTicket.description}
                  onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Priority</label>
                <select 
                  value={newTicket.priority} 
                  onChange={(e) => setNewTicket({ ...newTicket, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div className="modal-actions">
                <button type="button" className="secondary-button" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary-button">
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
