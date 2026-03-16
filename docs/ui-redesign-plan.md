# Plan: UI Redesign — Shell Layout + Detect Page Split View

## Context

Sprint 2 frontend đã hoạt động nhưng có 2 vấn đề lớn về UX:
1. **Không có shell/layout chung** — mỗi trang là trang rời, không có sidebar/navbar → người dùng mất phương hướng
2. **Trang detect quá đơn giản** — upload ảnh xong "bụp" ra kết quả, không thấy gì đang xảy ra trong quá trình detect

Yêu cầu của user:
- Trang chủ (/) là **Dashboard tổng quan** — nơi chứa thống kê, menu điều hướng đến các tính năng
- **Sidebar navigation** với các tab: Kiểm tra PPE, Lịch sử, Thống kê, Hệ thống, v.v.
- **Trang detect chia 2 panel**: trái = upload/camera, phải = log quá trình real-time
- Sau đó (plan riêng): tích hợp PPE pretrained model

---

## New Application Structure

### Layout Shell
```
┌─────────────────────────────────────────────────────────┐
│  🦺 PPE Checker          [breadcrumb]      [status badge] │  ← TopBar
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Sidebar  │           Main Content Area                  │
│          │                                              │
│ • Trang  │                                              │
│   chủ    │                                              │
│ • Kiểm   │                                              │
│   tra    │                                              │
│ • Lịch   │                                              │
│   sử     │                                              │
│ • Thống  │                                              │
│   kê     │                                              │
│ • Hệ     │                                              │
│   thống  │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### Routes (updated)
| Route | Page | Note |
|---|---|---|
| `/` | DashboardPage (tổng quan) | Trang chủ mới — stats + quick actions |
| `/inspect` | InspectPage | Upload + Log panel (chia đôi) |
| `/inspect/camera` | InspectPage (camera mode) | Tương tự nhưng webcam |
| `/history` | HistoryPage | Danh sách lịch sử + filter |
| `/history/:id` | ResultDetailPage | Chi tiết 1 kết quả |
| `/stats` | StatsPage | Thống kê + biểu đồ chi tiết |
| `/system` | SystemPage | Model info, health, config |

---

## Implementation Plan

### Step 1 — Layout Shell (`src/layouts/AppLayout.jsx`)
- `AppLayout` wraps all pages: Sidebar + TopBar + `<Outlet />`
- **Sidebar:** logo + 5 nav items với icon + label, active highlight
- **TopBar:** breadcrumb (tên trang hiện tại), backend status indicator (green dot nếu /health OK)
- Sidebar collapsible trên mobile (hamburger)
- Dùng `<Outlet />` của react-router-dom v6

**New component files:**
- `src/layouts/AppLayout.jsx`
- `src/components/Sidebar.jsx`
- `src/components/TopBar.jsx`

### Step 2 — Update App.jsx routing
Wrap tất cả routes trong `<Route element={<AppLayout />}>`:
```jsx
<Route element={<AppLayout />}>
  <Route path="/"            element={<DashboardPage />} />
  <Route path="/inspect"     element={<InspectPage />} />
  <Route path="/history"     element={<HistoryPage />} />
  <Route path="/history/:id" element={<ResultDetailPage />} />
  <Route path="/stats"       element={<StatsPage />} />
  <Route path="/system"      element={<SystemPage />} />
</Route>
```
Redirect `/upload`, `/camera`, `/results/:id`, `/dashboard` → routes mới để không break bookmarks.

### Step 3 — New DashboardPage (`/`) — Trang chủ tổng quan
Thay thế HomePage + DashboardPage cũ:
- **4 stat cards** (total, pass, fail, pass_rate) — gọi `getStats()`
- **Quick action buttons:** "Kiểm tra ngay" → /inspect, "Xem lịch sử" → /history
- **ViolationChart** — biểu đồ vi phạm
- **Recent inspections table** — 5 bản ghi gần nhất (không cần pagination ở đây)
- Backend status card: model đang dùng, uptime

**Reuses:** `StatsCards`, `ViolationChart`, `InspectionTable` (limit=5, no pagination)

### Step 4 — InspectPage (`/inspect`) — Split panel view ⭐
Layout chia đôi ngang (50/50 hoặc 45/55):

**Panel trái — Input:**
- Tabs: "📁 Upload file" / "📷 Webcam"
- Upload: drag-drop zone + preview (reuse logic từ UploadPage)
- Camera: react-webcam (reuse logic từ CameraPage)
- Submit button

**Panel phải — Realtime Log:**
- Header: "📋 Nhật ký phân tích"
- **Log entries hiển thị tuần tự** với timestamp ms:
  ```
  [0ms]    ✅ Nhận ảnh — 1.2MB, 1280×960px
  [12ms]   🔄 Resize → 1280×853px
  [15ms]   🤖 Bắt đầu YOLO inference...
  [280ms]  📦 YOLO trả về 3 raw detections
  [281ms]  🔍 Mapping: "helmet" → helmet ✅ (conf: 0.87)
  [282ms]  🔍 Mapping: "person" → ignored
  [283ms]  🔍 Mapping: "vest" → reflective_vest ✅ (conf: 0.72)
  [284ms]  ⚠️  gloves: không detect được (conf: 0.0 < 0.40)
  [284ms]  ⚠️  safety_boots: không detect được
  [284ms]  ⚠️  safety_glasses: không detect được
  [285ms]  ❌ Kết quả: FAIL — thiếu 3 hạng mục
  ```
- Log được **populate từ `debug_info`** trong API response (đã có sẵn trong backend)
- Sau khi có kết quả: hiển thị VerdictHeader + PPEChecklist ngay trong panel phải

**Implementation note:** Log entries được build client-side từ response data (không cần streaming). Sau khi API trả về, animate từng dòng log với `setTimeout` delay nhỏ (~50ms/entry) để tạo cảm giác "real-time".

### Step 5 — HistoryPage (`/history`)
Giữ lại InspectionTable hiện tại + thêm:
- Filter: PASS/FAIL/ALL dropdown
- Search: filter theo ngày (date range input)
- Export CSV button
- Click row → navigate `/history/:id`

**Reuses:** `InspectionTable` (extended), `getInspections()`

### Step 6 — ResultDetailPage (`/history/:id`)
Gộp ResultsPage hiện tại + DebugPanel:
- Layout 2 cột: ảnh annotated (trái) + checklist + debug (phải)
- Breadcrumb: Lịch sử > [ID ngắn]

**Reuses:** `VerdictHeader`, `PPEChecklist`, `DebugPanel`

### Step 7 — StatsPage (`/stats`)
Mở rộng stats section:
- ViolationChart (bar chart vi phạm)
- Pass rate theo thời gian (line chart nếu có đủ data)
- Stat cards chi tiết hơn

**Reuses:** `ViolationChart`, `StatsCards`, `getStats()`

### Step 8 — SystemPage (`/system`)
Page thông tin hệ thống:
- Model hiện tại: tên file, loại (pretrained/custom)
- Backend health status (polling `/health`)
- Confidence thresholds (5 classes)
- PPE class mapping (PPE_CLASS_MAP hiển thị dạng bảng)
- DB stats (tổng số records)

**Data source:** `/api/v1/stats` + `/health` + hardcode config thresholds từ frontend

---

## Critical Files to Modify / Create

### New files
- `frontend/src/layouts/AppLayout.jsx` — shell wrapper
- `frontend/src/components/Sidebar.jsx` — navigation sidebar
- `frontend/src/components/TopBar.jsx` — top bar + status
- `frontend/src/pages/InspectPage.jsx` — split panel detect (replaces UploadPage + CameraPage)
- `frontend/src/pages/HistoryPage.jsx` — replaces DashboardPage list portion
- `frontend/src/pages/ResultDetailPage.jsx` — replaces ResultsPage
- `frontend/src/pages/StatsPage.jsx` — new stats page
- `frontend/src/pages/SystemPage.jsx` — new system info page

### Modified files
- `frontend/src/App.jsx` — new routing structure with AppLayout
- `frontend/src/pages/DashboardPage.jsx` — rewrite as homepage overview
- `frontend/src/api/ppe.js` — add `getHealth()` function

### Kept as-is (reused)
- `frontend/src/components/VerdictHeader.jsx`
- `frontend/src/components/PPEChecklist.jsx`
- `frontend/src/components/DebugPanel.jsx`
- `frontend/src/components/StatsCards.jsx`
- `frontend/src/components/ViolationChart.jsx`
- `frontend/src/components/InspectionTable.jsx`
- `frontend/src/components/LoadingSpinner.jsx`
- `frontend/src/components/ErrorMessage.jsx`

### Old pages to delete (logic migrated)
- `frontend/src/pages/HomePage.jsx` → replaced by new DashboardPage
- `frontend/src/pages/UploadPage.jsx` → logic moved to InspectPage
- `frontend/src/pages/CameraPage.jsx` → logic moved to InspectPage
- `frontend/src/pages/ResultsPage.jsx` → replaced by ResultDetailPage

---

## Key Design Decisions

**Log animation:** Build log array from `debug_info` AFTER API response, then reveal entries one by one with 60ms interval. This gives real-time feel without needing websockets.

**Sidebar active state:** Use `useLocation()` from react-router to match current path and highlight active nav item.

**Backend health polling:** SystemPage polls `/health` every 30s. TopBar shows green/red dot based on last known status.

**No new dependencies needed** — chart.js, react-webcam, axios, react-router-dom all already installed.

---

## Verification

1. `npm run dev` → app loads, sidebar visible, "/" shows DashboardPage với stats
2. Click "Kiểm tra ngay" → InspectPage với split panel
3. Upload ảnh → submit → log panel animates entries → kết quả xuất hiện
4. Sidebar → Lịch sử → HistoryPage với table
5. Click row → ResultDetailPage với DebugPanel
6. Sidebar → Thống kê → StatsPage với biểu đồ
7. Sidebar → Hệ thống → SystemPage với model info
8. `npm run build` → build thành công, không lỗi
