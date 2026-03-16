import React, { useState, useEffect } from 'react';
import { BarChart2, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { getStats } from '../api/ppe';
import { StatsCards } from '../components/StatsCards';
import { ViolationChart } from '../components/ViolationChart';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import './StatsPage.css';

const StatsPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getStats();
        setStats(data);
      } catch (err) {
        setError('Không thể tải dữ liệu thống kê.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <LoadingSpinner message="Đang phân tích dữ liệu..." />;
  if (error) return <ErrorMessage error={error} onRetry={() => window.location.reload()} />;

  return (
    <div className="stats-container">
      <div className="stats-header">
        <h1>Thống kê & Phân tích</h1>
        <p>Phân tích chi tiết hiệu quả sử dụng trang bị bảo hộ lao động.</p>
      </div>

      <div className="stats-section">
        <h2 className="section-title"><TrendingUp size={20} /> Tổng quan hiệu suất</h2>
        {stats && <StatsCards stats={stats} />}
      </div>

      <div className="stats-grid">
        <div className="chart-card">
          <div className="card-header">
            <h3><AlertTriangle size={18} /> Phân tích vi phạm theo loại PPE</h3>
          </div>
          <div className="chart-container">
            {stats && stats.total > 0 ? (
              <ViolationChart data={stats.violations_by_class} />
            ) : (
              <div className="empty-state">Chưa có dữ liệu vi phạm</div>
            )}
          </div>
        </div>

        <div className="insights-card">
          <div className="card-header">
            <h3><CheckCircle size={18} /> Gợi ý cải thiện</h3>
          </div>
          <div className="insights-content">
            <div className="insight-item">
              <div className="insight-icon warning"><AlertTriangle size={20} /></div>
              <div className="insight-text">
                <h4>Trang bị thường xuyên thiếu</h4>
                <p>Găng tay và Kính bảo hộ là hai loại trang bị có tỷ lệ vi phạm cao nhất tháng này.</p>
              </div>
            </div>
            <div className="insight-item">
              <div className="insight-icon success"><CheckCircle size={20} /></div>
              <div className="insight-text">
                <h4>Xu hướng tuân thủ</h4>
                <p>Tỷ lệ PASS đã tăng 12% so với tuần trước nhờ các buổi training an toàn.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsPage;
