import React, { useState, useEffect } from 'react';
import { Settings, Server, Cpu, Activity, Database, CheckCircle, XCircle } from 'lucide-react';
import { getHealth, getStats } from '../api/ppe';
import { LoadingSpinner } from '../components/LoadingSpinner';
import './SystemPage.css';

const SystemPage = () => {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [healthData, statsData] = await Promise.all([
          getHealth().catch(() => ({ status: 'error' })),
          getStats().catch(() => null)
        ]);
        setHealth(healthData);
        setStats(statsData);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const ppeClassMapping = [
    { key: 'helmet', label: 'Mũ bảo hộ', threshold: '50%' },
    { key: 'reflective_vest', label: 'Áo phản quang', threshold: '50%' },
    { key: 'gloves', label: 'Găng tay', threshold: '40%' },
    { key: 'safety_boots', label: 'Giày bảo hộ', threshold: '45%' },
    { key: 'safety_glasses', label: 'Kính bảo hộ', threshold: '40%' },
  ];

  if (loading) return <LoadingSpinner message="Đang kiểm tra hệ thống..." />;

  const isOnline = health?.status === 'ok';

  return (
    <div className="system-container">
      <div className="system-header">
        <h1>Thông tin hệ thống</h1>
        <p>Giám sát trạng thái hoạt động và cấu hình mô hình AI.</p>
      </div>

      <div className="system-grid">
        <div className="status-column">
          <div className="card status-card">
            <div className="card-header">
              <h3><Activity size={18} /> Trạng thái hoạt động</h3>
            </div>
            <div className="card-content">
              <div className={`health-badge ${isOnline ? 'online' : 'offline'}`}>
                {isOnline ? <CheckCircle size={24} /> : <XCircle size={24} />}
                <div className="health-text">
                  <span className="label">Backend Status</span>
                  <span className="value">{isOnline ? 'RUNNING' : 'UNREACHABLE'}</span>
                </div>
              </div>

              <div className="details-list">
                <div className="detail-item">
                  <span className="dot online"></span>
                  <span className="item-label">API v1</span>
                  <span className="item-value">v1.0.4</span>
                </div>
                <div className="detail-item">
                  <span className="dot online"></span>
                  <span className="item-label">Database</span>
                  <span className="item-value">SQLite Online</span>
                </div>
                <div className="detail-item">
                  <span className="dot online"></span>
                  <span className="item-label">Storage</span>
                  <span className="item-value">File System OK</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card db-card">
            <div className="card-header">
              <h3><Database size={18} /> Dữ liệu tích lũy</h3>
            </div>
            <div className="card-content">
              <div className="db-stats">
                <div className="stat-row">
                  <span>Tổng số lượt kiểm tra:</span>
                  <strong>{stats?.total || 0}</strong>
                </div>
                <div className="stat-row">
                  <span>Kích thước DB:</span>
                  <strong>~28 KB</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="config-column">
          <div className="card model-card">
            <div className="card-header">
              <h3><Cpu size={18} /> Cấu hình Mô hình AI</h3>
            </div>
            <div className="card-content">
              <div className="model-info">
                <div className="model-badge">
                  <Server size={32} />
                  <div>
                    <h4>YOLOv8n</h4>
                    <p>Weights: <code>yolov8n.pt</code></p>
                  </div>
                </div>
                
                <div className="thresholds-table">
                  <h4>Ngưỡng ranh giới (Thresholds)</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>Lớp đối tượng</th>
                        <th>Ngưỡng</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ppeClassMapping.map(item => (
                        <tr key={item.key}>
                          <td>{item.label}</td>
                          <td className="mono">{item.threshold}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemPage;
