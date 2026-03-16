import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Upload, Camera, Play, CheckCircle2, AlertCircle, Terminal as TerminalIcon, Clock, PlusCircle } from 'lucide-react';
import { checkPPE } from '../api/ppe';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { PPEChecklist } from '../components/PPEChecklist';
import { VerdictHeader } from '../components/VerdictHeader';
import './InspectPage.css';

const ALLOWED_TYPES = ['image/jpeg', 'image/png'];
const MAX_SIZE = 10 * 1024 * 1024;

const InspectPage = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const fileInputRef = useRef(null);
  const webcamRef = useRef(null);
  const logEndRef = useRef(null);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const addLog = (message, type = 'info', delay = 0) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        setLogs((prev) => [...prev, { 
          id: Date.now() + Math.random(), 
          message, 
          type, 
          timestamp: new Date().toLocaleTimeString([], { hour12: false, minute: '2-digit', second: '2-digit' }) 
        }]);
        resolve();
      }, delay);
    });
  };

  const handleFileSelect = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    if (!ALLOWED_TYPES.includes(selected.type)) {
      setError('Chỉ hỗ trợ ảnh JPEG hoặc PNG');
      return;
    }
    if (selected.size > MAX_SIZE) {
      setError('Ảnh quá lớn — tối đa 10MB');
      return;
    }
    setError(null);
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
    setLogs([]);
  };

  const captureCamera = () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
      setResult(null);
      setLogs([]);
    }
  };

  const base64ToFile = (base64, filename) => {
    const arr = base64.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) u8arr[n] = bstr.charCodeAt(n);
    return new File([u8arr], filename, { type: mime });
  };

  const runAnalysis = async () => {
    let imageToUpload = null;
    if (activeTab === 'upload' && file) {
      imageToUpload = file;
    } else if (activeTab === 'webcam' && capturedImage) {
      imageToUpload = base64ToFile(capturedImage, 'capture.jpg');
    }

    if (!imageToUpload) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setLogs([]);
    setIsAnimating(true);

    try {
      await addLog('🚀 Khởi tạo quá trình phân tích...', 'info');
      await addLog(`📂 Đang tải ảnh (${(imageToUpload.size / 1024 / 1024).toFixed(2)} MB)...`, 'info', 400);

      const response = await checkPPE(imageToUpload);
      
      // Deep dive into debug logs from backend
      if (response.debug_info) {
        await addLog('✅ Đã nhận phản hồi từ AI Server', 'success', 300);
        await addLog(`🖼️ Kích thước ảnh: ${response.debug_info.original_size[0]}x${response.debug_info.original_size[1]}px`, 'info', 200);
        await addLog('🔄 Đang xử lý tiền xử lý ảnh...', 'info', 300);
        await addLog('🤖 Chạy mô hình YOLOv8 Inference...', 'info', 500);
        await addLog(`📦 Phát hiện ${response.debug_info.raw_detections_count} đối tượng thô`, 'info', 400);
        
        // Mapping logs
        for (const log of (response.debug_info.mapping_logs || [])) {
           const type = log.includes('✅') ? 'success' : (log.includes('⚠️') ? 'warning' : 'info');
           await addLog(log, type, 100);
        }
      }

      setResult(response);
      await addLog(`🏁 Kết quả: ${response.overall_pass ? 'ĐẠT (PASS)' : 'KHÔNG ĐẠT (FAIL)'}`, response.overall_pass ? 'success' : 'error', 300);
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi kết nối server');
      await addLog('❌ Lỗi quá trình phân tích', 'error');
    } finally {
      setLoading(false);
      setIsAnimating(false);
    }
  };

  return (
    <div className="inspect-container">
      <div className="inspect-panel input-panel">
        <div className="panel-header">
          <div className="tab-switcher">
            <button 
              className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              <Upload size={18} /> Upload file
            </button>
            <button 
              className={`tab-btn ${activeTab === 'webcam' ? 'active' : ''}`}
              onClick={() => setActiveTab('webcam')}
            >
              <Camera size={18} /> Webcam
            </button>
          </div>
        </div>

        <div className="panel-content">
          {activeTab === 'upload' ? (
            <div 
              className="dropzone"
              onClick={() => fileInputRef.current.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                onChange={handleFileSelect}
                accept="image/*"
              />
              {preview ? (
                <div className="preview-container">
                  <img src={preview} alt="Preview" />
                  <div className="preview-overlay">Thay đổi ảnh</div>
                </div>
              ) : (
                <div className="dropzone-empty">
                  <div className="icon-circle"><Upload size={32} /></div>
                  <p>Kéo thả hoặc click để chọn ảnh</p>
                  <span>JPEG, PNG lên đến 10MB</span>
                </div>
              )}
            </div>
          ) : (
            <div className="webcam-container">
              {capturedImage ? (
                <div className="preview-container">
                  <img src={capturedImage} alt="Captured" />
                  <button className="retake-btn" onClick={() => setCapturedImage(null)}>Chụp lại</button>
                </div>
              ) : (
                <div className="webcam-wrapper">
                   <Webcam
                    ref={webcamRef}
                    mirrored={true}
                    screenshotFormat="image/jpeg"
                    className="webcam-view"
                  />
                  <button className="capture-btn" onClick={captureCamera}>
                    <div className="inner-circle"></div>
                  </button>
                </div>
              )}
            </div>
          )}

          {error && <ErrorMessage error={error} onRetry={() => setError(null)} />}

          <button 
            className="analyze-btn" 
            disabled={(!file && !capturedImage) || loading}
            onClick={runAnalysis}
          >
            {loading ? <LoadingSpinner size="sm" /> : <><PlusCircle size={20} /> Bắt đầu phân tích</>}
          </button>
        </div>
      </div>

      <div className="inspect-panel log-panel">
        <div className="panel-header">
          <div className="panel-title">
            <TerminalIcon size={18} /> Nhật ký phân tích
          </div>
          {isAnimating && <div className="pulse-indicator"></div>}
        </div>
        
        <div className="log-content">
          {logs.length === 0 && !loading && (
            <div className="log-empty">
              <Clock size={40} opacity={0.2} />
              <p>Chưa có dữ liệu. Hãy tải ảnh và nhấn "Bắt đầu phân tích".</p>
            </div>
          )}
          
          <div className="log-list">
            {logs.map((log) => (
              <div key={log.id} className={`log-entry ${log.type}`}>
                <span className="log-time">[{log.timestamp}]</span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>

          {result && (
            <div className="analysis-result-overlay">
              <VerdictHeader pass={result.overall_pass} />
              <div className="result-details">
                <PPEChecklist items={result.items} />
              </div>
              <div className="result-actions">
                <button 
                  className="btn-view-detail" 
                  onClick={() => window.open(`/history/${result.inspection_id}`, '_blank')}
                >
                  Xem ảnh chi tiết
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InspectPage;
