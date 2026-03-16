import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Clock, Calendar, Shield, ExternalLink, Download } from 'lucide-react';
import { getInspectionById } from '../api/ppe';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { VerdictHeader } from '../components/VerdictHeader';
import { PPEChecklist } from '../components/PPEChecklist';
import { DebugPanel } from '../components/DebugPanel';
import './ResultDetailPage.css';

const ResultDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        setLoading(true);
        const data = await getInspectionById(id);
        setResult(data);
      } catch (err) {
        setError('Không thể tìm thấy kết quả kiểm tra này.');
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [id]);

  if (loading) return <LoadingSpinner message="Đang tải chi tiết..." />;
  if (error) return <ErrorMessage error={error} onRetry={() => navigate('/history')} />;
  if (!result) return null;

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="result-detail-container">
      <div className="result-header">
        <Link to="/history" className="back-link">
          <ArrowLeft size={18} /> Quay lại lịch sử
        </Link>
        <div className="header-actions">
          <button className="btn-secondary" onClick={() => window.print()}>
            <Download size={18} /> In kết quả
          </button>
        </div>
      </div>

      <div className="result-title-section">
        <div className="title-left">
          <h1>Chi tiết kiểm tra #{id.substring(0, 8)}</h1>
          <div className="meta-info">
            <span className="meta-item"><Calendar size={14} /> {formatDate(result.created_at)}</span>
            <span className="meta-item"><Shield size={14} /> Model: YOLOv8n</span>
          </div>
        </div>
        <VerdictHeader overallPass={result.overall_pass} />
      </div>

      <div className="result-grid">
        <div className="image-column">
          <div className="card">
            <div className="card-header">
              <h3><ExternalLink size={18} /> Ảnh đã phân tích</h3>
            </div>
            <div className="image-view">
              <img 
                src={import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/static/results/${result.result_image}` : `http://localhost:8000/static/results/${result.result_image}`} 
                alt="Annotated Result" 
              />
            </div>
          </div>
        </div>

        <div className="info-column">
          <div className="card">
            <div className="card-header">
              <h3><Shield size={18} /> Danh mục trang bị</h3>
            </div>
            <div className="card-content">
              <PPEChecklist items={result.items} />
            </div>
          </div>

          <DebugPanel debugInfo={result.debug_info} items={result.items} />
        </div>
      </div>
    </div>
  );
};

export default ResultDetailPage;
