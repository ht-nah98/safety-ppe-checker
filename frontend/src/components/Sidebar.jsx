import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  BarChart2, 
  ShieldCheck, 
  History, 
  Settings, 
  LayoutDashboard,
  LogOut
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ isOpen }) => {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/inspect', label: 'Kiểm tra PPE', icon: <ShieldCheck size={20} /> },
    { path: '/history', label: 'Lịch sử', icon: <History size={20} /> },
    { path: '/stats', label: 'Thống kê', icon: <BarChart2 size={20} /> },
    { path: '/system', label: 'Hệ thống', icon: <Settings size={20} /> },
  ];

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <div className="logo">
          <ShieldCheck size={32} color="#3b82f6" />
          <span className="logo-text">PPE Checker</span>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="avatar">AD</div>
          <div className="details">
            <p className="name">Admin User</p>
            <p className="role">Administrator</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
