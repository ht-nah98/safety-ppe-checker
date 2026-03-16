import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, Calendar } from 'lucide-react';
import { getInspections, getExportUrl } from '../api/ppe';
import { InspectionTable } from '../components/InspectionTable';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import './HistoryPage.css';

const PAGE_SIZE = 15;

const HistoryPage = () => {
  const [inspections, setInspections] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('ALL'); // ALL, PASS, FAIL

  useEffect(() => {
    fetchInspections();
  }, [page, filter]);

  const fetchInspections = async () => {
    try {
      setLoading(true);
      // Backend doesn't support filter in params yet based on ppe.js, 
      // but we could extend it if needed. For now, we'll fetch all.
      const data = await getInspections(PAGE_SIZE, page * PAGE_SIZE);
      
      let filteredData = data.inspections;
      if (filter === 'PASS') {
        filteredData = filteredData.filter(i => i.overall_pass);
      } else if (filter === 'FAIL') {
        filteredData = filteredData.filter(i => !i.overall_pass);
      }

      setInspections(filteredData);
      setTotal(data.total);
    } catch (err) {
      setError('Không thể tải lịch sử kiểm tra.');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  if (loading && page === 0) return <LoadingSpinner message="Đang tải lịch sử..." />;

  return (
    <div className="history-container">
      <div className="history-header">
        <div className="header-left">
          <h1>Lịch sử kiểm tra</h1>
          <p>Danh sách tất cả các lượt kiểm tra PPE hệ thống đã thực hiện.</p>
        </div>
        <div className="header-right">
          <a href={getExportUrl()} download className="btn-export">
            <Download size={18} /> Xuất CSV
          </a>
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-box">
          <Search size={18} />
          <input type="text" placeholder="Tìm kiếm theo ID hoặc ngày..." />
        </div>
        
        <div className="filters">
          <div className="filter-group">
            <label><Filter size={16} /> Kết quả:</label>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="ALL">Tất cả</option>
              <option value="PASS">Chỉ PASS</option>
              <option value="FAIL">Chỉ FAIL</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label><Calendar size={16} /> Thời gian:</label>
            <input type="date" />
          </div>
        </div>
      </div>

      {error && <ErrorMessage error={error} onRetry={fetchInspections} />}

      <div className="table-wrapper">
        <InspectionTable 
          inspections={inspections} 
          total={total} 
          page={page} 
          onPageChange={handlePageChange} 
        />
      </div>
    </div>
  );
};

export default HistoryPage;
