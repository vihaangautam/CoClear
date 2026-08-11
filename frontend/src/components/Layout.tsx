import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Building2, Users, Settings, HelpCircle, Wrench, LogOut, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/properties', label: 'Properties', icon: Building2 },
  { to: '/tenancies', label: 'Tenancies', icon: Users },
  { to: '/tickets', label: 'Tickets', icon: Wrench },
];

export default function Layout() {
  const { operator, logout } = useAuth();

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1 className="brand-name">PGPal</h1>
          <span className="brand-tag">Verified Management</span>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item"><Settings size={18} /><span>Settings</span></button>
          <button className="nav-item"><HelpCircle size={18} /><span>Support</span></button>
          <div className="user-card">
            <div className="user-avatar">
              {operator?.name?.charAt(0) || 'U'}
            </div>
            <div className="user-info">
              <span className="user-name">{operator?.name || 'Operator'}</span>
              <span className="user-id">Owner</span>
            </div>
            <button className="logout-btn" onClick={logout} title="Logout">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}