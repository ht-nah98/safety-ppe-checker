import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, History, BarChart2, PlusCircle, ArrowRight } from 'lucide-react';
import { getStats, getInspections } from '../api/ppe';
import { StatsCards } from '../components/StatsCards';
import { ViolationChart } from '../components/ViolationChart';
import { InspectionTable } from '../components/InspectionTable';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import './DashboardPage.css';

const DashboardPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentInspections, setRecentInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsData, inspectionsData] = await Promise.all([
          getStats(),
          getInspections(5, 0) // Only get 5 most recent
        ]);
        setStats(statsData);
        setRecentInspections(inspectionsData.inspections);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Không thể tải dữ liệu tổng quan. Vui lòng kiểm tra kết nối backend.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="Đang tải tổng quan..." />;
  if (error) return <ErrorMessage error={error} onRetry={() => window.location.reload()} />;

  return (
    <div className="dashboard-overview">
      <div className="welcome-banner">
        <div className="banner-content">
          <h1>Chào mừng trở lại! 👋</h1>
          <p>Hệ thống kiểm tra PPE đang hoạt động ổn định. Bạn muốn làm gì hôm nay?</p>
        </div>
        <div className="quick-actions-banner">
          <Link to="/inspect" className="btn-primary">
            <PlusCircle size={20} />
            Kiểm tra ngay
          </Link>
          <Link to="/history" className="btn-secondary">
            <History size={20} />
            Xem lịch sử
          </Link>
        </div>
      </div>

      <div className="overview-grid">
        <div className="stats-section">
          <h2 className="section-title">Thống kê tổng quan</h2>
          {stats && <StatsCards stats={stats} />}
        </div>
        
        <div className="chart-section">
          <div className="section-header">
            <h2 className="section-title">Phân tích vi phạm</h2>
            <Link to="/stats" className="view-more">
              Xem chi tiết <ArrowRight size={16} />
            </Link>
          </div>
          <div className="chart-container-inner">
            {stats && stats.total > 0 ? (
              <ViolationChart data={stats.violations_by_class} />
            ) : (
              <div className="empty-state">Chưa có dữ liệu vi phạm</div>
            )}
          </div>
        </div>
      </div>

      <div className="recent-inspections">
        <div className="section-header">
          <h2 className="section-title">Kiểm tra gần đây</h2>
          <Link to="/history" className="view-more">
            Tất cả lịch sử <ArrowRight size={16} />
          </Link>
        </div>
        {recentInspections.length > 0 ? (
          <InspectionTable 
            inspections={recentInspections} 
            total={recentInspections.length} 
            page={0} 
            onPageChange={() => {}} 
            hidePagination={true}
          />
        ) : (
          <div className="empty-state">Chưa có lượt kiểm tra nào được thực hiện.</div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
