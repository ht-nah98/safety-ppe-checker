import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Menu, Bell, Search, Circle } from 'lucide-react';
import { getHealth } from '../api/ppe';
import './TopBar.css';

const TopBar = ({ toggleSidebar }) => {
  const location = useLocation();
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const health = await getHealth();
        setIsOnline(health.status === 'ok');
      } catch (err) {
        setIsOnline(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/inspect')) return 'Kiểm tra PPE';
    if (path.startsWith('/history')) return 'Lịch sử kiểm tra';
    if (path === '/stats') return 'Thống kê & Phân tích';
    if (path === '/system') return 'Thông tin hệ thống';
    return 'PPE Checker';
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="menu-btn" onClick={toggleSidebar}>
          <Menu size={20} />
        </button>
        <div className="breadcrumb">
          <Link to="/">Home</Link>
          <span className="separator">/</span>
          <span className="current-page">{getPageTitle()}</span>
        </div>
      </div>
      
      <div className="topbar-right">
        <div className="status-badge">
          <span className={`status-dot ${isOnline ? 'online' : 'offline'}`}></span>
          <span className="status-text">{isOnline ? 'Backend Online' : 'Backend Offline'}</span>
        </div>
        
        <div className="actions">
          <button className="action-btn">
            <Search size={20} />
          </button>
          <button className="action-btn">
            <Bell size={20} />
            <span className="notification-dot"></span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
