import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Building2, Users, Settings, HelpCircle } from 'lucide-react';
import './Layout.css';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/properties', label: 'Properties', icon: Building2 },
  { to: '/tenancies', label: 'Tenancies', icon: Users },
];

export default function Layout() {
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
            <div className="user-avatar">RK</div>
            <div className="user-info">
              <span className="user-name">Ramesh Kumar</span>
              <span className="user-id">OP-0001</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
