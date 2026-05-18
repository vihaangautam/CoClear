import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Home, FileCheck, MessageSquare, LogOut } from 'lucide-react';
import './TenantLayout.css';

const navItems = [
  { to: '/tenant/home', label: 'My Room', icon: Home },
  { to: '/tenant/condition-report', label: 'Room Check', icon: FileCheck },
  { to: '/tenant/complaints', label: 'Complaints', icon: MessageSquare },
];

export default function TenantLayout() {
  const navigate = useNavigate();
  const tenantName = sessionStorage.getItem('tenant_name') || 'Tenant';
  const initials = tenantName.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);

  const handleLogout = () => {
    sessionStorage.clear();
    navigate('/tenant');
  };

  return (
    <div className="tenant-layout">
      {/* Top header bar for mobile-first design */}
      <header className="tenant-header">
        <div className="tenant-brand">
          <span className="tenant-brand-name">PGPal</span>
          <span className="tenant-brand-tag">Tenant</span>
        </div>
        <div className="tenant-profile">
          <div className="tenant-avatar">{initials}</div>
          <button className="tenant-logout" onClick={handleLogout} title="Switch account">
            <LogOut size={18} />
          </button>
        </div>
      </header>

      {/* Main content area */}
      <main className="tenant-main">
        <Outlet />
      </main>

      {/* Bottom tab bar (mobile-native feel) */}
      <nav className="tenant-tabbar">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
