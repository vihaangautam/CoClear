import { useEffect, useState } from 'react';
import { TrendingUp, Building2, AlertTriangle, Search, Bell, HelpCircle } from 'lucide-react';
import { fetchApi } from '../api';
import './Dashboard.css';

interface Stats {
  total_properties: number;
  total_beds: number;
  active_tenancies: number;
  occupancy_percent: number;
  total_revenue_mtd: string;
  tenancies_in_notice: number;
}

interface OccBed {
  bed_id: string;
  label: string;
  room_number: string;
  status: string | null;
  tenant_name: string | null;
}

interface PropOcc {
  property_id: string;
  property_name: string;
  address: string;
  occupancy_percent: number;
  beds: OccBed[];
}

const statusColor: Record<string, string> = {
  active: 'var(--accent-green)',
  notice_period: 'var(--accent-orange)',
  inquiry: 'var(--accent-blue)',
  confirmed: 'var(--accent-blue)',
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [occupancy, setOccupancy] = useState<PropOcc[]>([]);

  useEffect(() => {
    fetchApi<Stats>('/dashboard/stats').then(setStats);
    fetchApi<PropOcc[]>('/dashboard/occupancy').then(setOccupancy);
  }, []);

  const revenue = stats ? parseFloat(stats.total_revenue_mtd) : 0;
  const revenueFormatted = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(revenue);

  return (
    <div className="dashboard">
      <header className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Welcome back, Ramesh. Here's your portfolio overview.</p>
        </div>
        <div className="header-actions">
          <div className="search-box">
            <Search size={16} />
            <input type="text" placeholder="Search records, IDs..." />
          </div>
          <button className="icon-btn"><Bell size={18} /></button>
          <button className="icon-btn"><HelpCircle size={18} /></button>
        </div>
      </header>

      {/* ─── Stat Cards ─── */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Rent This Month</span>
            <Building2 size={16} className="stat-icon" />
          </div>
          <div className="stat-value">{stats ? revenueFormatted : '...'}</div>
          <div className="stat-trend positive"><TrendingUp size={14} /> +5.2% vs last month</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Beds Filled</span>
            <Building2 size={16} className="stat-icon" />
          </div>
          <div className="stat-value">{stats?.occupancy_percent ?? '...'}%</div>
          <div className="stat-detail">{stats?.active_tenancies ?? 0} / {stats?.total_beds ?? 0} Active Beds</div>
        </div>

        <div className="stat-card warning">
          <div className="stat-header">
            <span className="stat-label">Leaving Soon</span>
            <AlertTriangle size={16} className="stat-icon warning" />
          </div>
          <div className="stat-value accent-orange">{stats?.tenancies_in_notice ?? 0}</div>
          <div className="stat-detail">People leaving</div>
        </div>
      </div>

      {/* ─── Occupancy Grid ─── */}
      <div className="card occupancy-card">
        <div className="card-header">
          <h2 className="card-title">Who's in which bed</h2>
          <div className="legend">
            <span className="legend-item"><span className="dot green" />Active</span>
            <span className="legend-item"><span className="dot orange" />Notice</span>
            <span className="legend-item"><span className="dot blue" />Inquiry</span>
            <span className="legend-item"><span className="dot grey" />Vacant</span>
          </div>
        </div>

        {occupancy.map((prop) => (
          <div key={prop.property_id} className="property-row">
            <div className="property-label">
              <span className="property-name">{prop.property_name}</span>
              <span className="property-dot">&#x2022;</span>
              <span className="property-addr">{prop.address}</span>
              <span className="occ-badge">{prop.occupancy_percent}% Occ</span>
            </div>
            <div className="bed-grid">
              {prop.beds.map((bed) => (
                <div
                  key={bed.bed_id}
                  className="bed-cell"
                  style={{ background: bed.status ? statusColor[bed.status] || 'var(--accent-grey)' : 'var(--bg-hover)', color: bed.status ? '#fff' : 'var(--text-muted)' }}
                  title={bed.tenant_name ? `${bed.tenant_name} (${bed.status})` : 'Vacant'}
                >
                  {bed.label}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
