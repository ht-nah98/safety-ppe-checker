# Technical Specification: TP-WEB-001
## Web Interface — React Frontend

> **Status**: Draft
> **Linked Epic**: [EPIC-WEB-001](../../01_product_requirements/web-interface/EPIC-WEB-001.md)
> **Linked Stories**: US-WEB-001, US-WEB-002, US-WEB-003, US-WEB-004, US-WEB-005
> **Source Files**: `frontend/src/`

---

## 1. Overview

Frontend là React SPA (Single Page Application) chạy trên port 3000. Có 4 trang chính: Home, Upload, Camera, Results, Dashboard. Tất cả API calls đến Backend (port 8000) qua `axios`. Không có state management library — dùng React `useState` + `useNavigate` đủ cho quy mô demo này.

---

## 2. API Specifications (Frontend Side)

### 2.1 API Module — `frontend/src/api/ppe.js`

```javascript
// frontend/src/api/ppe.js
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// POST /api/v1/check-ppe
export async function checkPPE(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  const res = await axios.post(`${API_BASE}/api/v1/check-ppe`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,
  });
  return res.data; // InspectionResponse
}

// GET /api/v1/inspections?limit=20&offset=0
export async function getInspections(limit = 20, offset = 0) {
  const res = await axios.get(`${API_BASE}/api/v1/inspections`, {
    params: { limit, offset },
  });
  return res.data; // { inspections: [], total: N }
}

// GET /api/v1/inspections/:id
export async function getInspectionById(id) {
  const res = await axios.get(`${API_BASE}/api/v1/inspections/${id}`);
  return res.data;
}

// GET /api/v1/stats
export async function getStats() {
  const res = await axios.get(`${API_BASE}/api/v1/stats`);
  return res.data;
}

// GET /api/v1/inspections/export (CSV download)
export function getExportUrl() {
  return `${API_BASE}/api/v1/inspections/export`;
}
```

---

## 3. Routing Structure

```javascript
// frontend/src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

<Routes>
  <Route path="/"               element={<HomePage />} />
  <Route path="/upload"         element={<UploadPage />} />
  <Route path="/camera"         element={<CameraPage />} />
  <Route path="/results/:id"    element={<ResultsPage />} />
  <Route path="/dashboard"      element={<DashboardPage />} />
</Routes>
```

---

## 4. Implementation Details — Từng trang

### 4.1 HomePage (`/`)

**Chức năng**: Entry point — chọn Upload hoặc Webcam

```jsx
// Chỉ 2 buttons lớn, căn giữa màn hình
<div className="flex flex-col gap-4 items-center">
  <button onClick={() => navigate('/upload')}>
    📁 Upload ảnh từ máy tính
  </button>
  <button onClick={() => navigate('/camera')}>
    📷 Chụp ảnh từ webcam
  </button>
</div>
```

---

### 4.2 UploadPage (`/upload`) — US-WEB-001

**State:**
```javascript
const [file, setFile]         = useState(null);    // File object
const [preview, setPreview]   = useState(null);    // Object URL for preview
const [loading, setLoading]   = useState(false);
const [error, setError]       = useState(null);
```

**Validation Logic (client-side):**
```javascript
const ALLOWED_TYPES = ['image/jpeg', 'image/png'];
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

function validateFile(file) {
  if (!ALLOWED_TYPES.includes(file.type))
    return 'Chỉ hỗ trợ ảnh JPEG hoặc PNG';
  if (file.size > MAX_SIZE)
    return 'Ảnh quá lớn — tối đa 10MB';
  return null;
}
```

**Submit Flow:**
```javascript
async function handleSubmit() {
  setLoading(true);
  try {
    const result = await checkPPE(file);          // API call
    navigate(`/results/${result.inspection_id}`, {
      state: { result }                            // Pass kết quả qua state
    });
  } catch (err) {
    setError('Lỗi kết nối — vui lòng thử lại');
  } finally {
    setLoading(false);
  }
}
```

**Drag-and-Drop:**
```javascript
// Dùng HTML5 drag events trên drop zone div
onDragOver={(e) => e.preventDefault()}
onDrop={(e) => {
  e.preventDefault();
  const droppedFile = e.dataTransfer.files[0];
  handleFileSelect(droppedFile);
}}
```

---

### 4.3 CameraPage (`/camera`) — US-WEB-002

**Thư viện**: `react-webcam`

```jsx
import Webcam from 'react-webcam';

// Ref để capture
const webcamRef = useRef(null);
const [capturedImage, setCapturedImage] = useState(null);

function capture() {
  const imageSrc = webcamRef.current.getScreenshot(); // base64 JPEG
  setCapturedImage(imageSrc);
}

// Convert base64 → File object để gọi API
function base64ToFile(base64, filename) {
  const arr = base64.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  const n = bstr.length;
  const u8arr = new Uint8Array(n);
  for (let i = 0; i < n; i++) u8arr[i] = bstr.charCodeAt(i);
  return new File([u8arr], filename, { type: mime });
}

// Cleanup: stop camera khi unmount
useEffect(() => {
  return () => {
    if (webcamRef.current?.stream) {
      webcamRef.current.stream.getTracks().forEach(t => t.stop());
    }
  };
}, []);
```

**Error handling:**
```javascript
// Webcam component onUserMediaError prop
<Webcam
  onUserMediaError={(err) => {
    if (err.name === 'NotAllowedError')
      setError('Cần cấp quyền camera — vui lòng kiểm tra cài đặt trình duyệt');
    else if (err.name === 'NotFoundError')
      setError('Không tìm thấy camera');
  }}
  mirrored={true}          // flip để tự nhiên hơn
  screenshotFormat="image/jpeg"
  screenshotQuality={0.85}
/>
```

---

### 4.4 ResultsPage (`/results/:id`) — US-WEB-003, US-WEB-004

**Lấy dữ liệu:**
```javascript
const { state } = useLocation();
// Ưu tiên dùng state (passed từ UploadPage/CameraPage)
// Fallback: GET /api/v1/inspections/:id nếu user reload trang
const [result, setResult] = useState(state?.result ?? null);

useEffect(() => {
  if (!result) {
    getInspectionById(id).then(setResult);
  }
}, [id]);
```

**PPEChecklist Component:**
```jsx
// frontend/src/components/PPEChecklist.jsx
const PPE_LABELS = {
  helmet:          { label: 'Mũ bảo hộ',     icon: '🪖' },
  reflective_vest: { label: 'Áo phản quang',  icon: '🦺' },
  gloves:          { label: 'Găng tay',        icon: '🧤' },
  safety_boots:    { label: 'Giày bảo hộ',    icon: '👟' },
  safety_glasses:  { label: 'Kính bảo hộ',    icon: '🥽' },
};

export function PPEChecklist({ items }) {
  const failCount = Object.values(items).filter(i => !i.detected).length;
  const failNames = Object.entries(items)
    .filter(([_, v]) => !v.detected)
    .map(([k]) => PPE_LABELS[k].label);

  return (
    <div>
      {Object.entries(items).map(([key, val]) => (
        <div key={key}
          className={val.detected ? 'text-green-600' : 'text-red-600 font-bold'}>
          {val.detected ? '✅' : '❌'}
          {PPE_LABELS[key].icon}
          {PPE_LABELS[key].label}
          <span className="ml-auto text-sm">
            {val.detected ? `${Math.round(val.confidence * 100)}%` : 'Không phát hiện'}
          </span>
        </div>
      ))}
      {failCount > 0 && (
        <div className="text-red-500 mt-2">
          ⚠️ Thiếu {failCount} hạng mục: {failNames.join(', ')}
        </div>
      )}
    </div>
  );
}
```

**VerdictHeader Component:**
```jsx
// frontend/src/components/VerdictHeader.jsx
export function VerdictHeader({ overallPass, timestamp }) {
  return (
    <div className={overallPass
      ? 'bg-green-100 border-green-500 text-green-800'
      : 'bg-red-100 border-red-500 text-red-800'
    }>
      <span className="text-2xl font-bold">
        {overallPass
          ? '✅ PASS — ĐỦ TRANG BỊ BẢO HỘ'
          : '❌ FAIL — THIẾU TRANG BỊ BẢO HỘ'
        }
      </span>
      <p className="text-sm mt-1">{timestamp}</p>  {/* US-WEB-005 */}
    </div>
  );
}
```

**Annotated Image:**
```jsx
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

<img
  src={`${API_BASE}${result.annotated_image_url}`}
  alt="PPE kiểm tra"
  className="max-w-full rounded shadow"
  onClick={() => window.open(`${API_BASE}${result.annotated_image_url}`, '_blank')}
  style={{ cursor: 'zoom-in' }}
/>
```

**Navigation Buttons:**
```jsx
<button onClick={() => navigate('/')}>Kiểm tra lại</button>
<button onClick={() => navigate('/dashboard')}>Xem lịch sử</button>
```

---

### 4.5 DashboardPage (`/dashboard`) — US-DSH-001, US-DSH-002

*(Chi tiết implementation trong TP-DSH-001)*

```jsx
// Chỉ nêu integration point ở đây
useEffect(() => {
  Promise.all([getStats(), getInspections(20, 0)])
    .then(([statsData, inspData]) => {
      setStats(statsData);
      setInspections(inspData.inspections);
      setTotal(inspData.total);
    });
}, []);
```

---

## 5. Loading & Error States

**Loading Component:**
```jsx
// Hiển thị khi đang gọi API
<div className="flex flex-col items-center py-16">
  <div className="animate-spin rounded-full h-16 w-16
                  border-b-4 border-blue-600" />
  <p className="mt-4 text-gray-600">AI đang phân tích... (~2-3 giây)</p>
</div>
```

**Error Component:**
```jsx
<div className="bg-red-50 border border-red-300 rounded p-4">
  <p className="text-red-700">⚠️ {error}</p>
  <button onClick={() => setError(null)}>Thử lại</button>
</div>
```

---

## 6. Security & Performance

| Concern | Solution |
|---------|----------|
| File validation | Client-side (type + size) trước khi gọi API |
| Camera cleanup | `useEffect` return function stop tracks |
| Large preview | `URL.createObjectURL()` + revoke khi unmount |
| API timeout | axios `timeout: 30000` (30 giây) |
| CORS | Backend config allow localhost:3000 |

```javascript
// Revoke object URL khi unmount (tránh memory leak)
useEffect(() => {
  return () => { if (preview) URL.revokeObjectURL(preview); };
}, [preview]);
```

---

## 7. Mapping to User Stories

| Component / Feature | User Story |
|--------------------|------------|
| UploadPage: file picker + drag-drop + validation | [US-WEB-001](../../01_product_requirements/web-interface/US-WEB-001.md) |
| CameraPage: webcam capture + error handling | [US-WEB-002](../../01_product_requirements/web-interface/US-WEB-002.md) |
| VerdictHeader: PASS/FAIL màu sắc + annotated image | [US-WEB-003](../../01_product_requirements/web-interface/US-WEB-003.md) |
| PPEChecklist: 5 items + status + summary | [US-WEB-004](../../01_product_requirements/web-interface/US-WEB-004.md) |
| Timestamp hiển thị trên Results page | [US-WEB-005](../../01_product_requirements/web-interface/US-WEB-005.md) |

---

> **Changelog**
> | Version | Date | Changes |
> |---------|------|---------|
> | v1.0 | 2026-03-15 | Initial tech spec |
