# 🦺 Safety PPE Checker

**Hệ thống tự động đánh giá tuân thủ trang phục bảo hộ (PPE) qua ảnh chụp**

> AI-powered PPE compliance checking for electrical workers using YOLOv8

---

## 📋 Tổng quan

Safety PPE Checker sử dụng Computer Vision (YOLOv8) để phân tích ảnh chụp toàn thân công nhân điện lực, tự động kiểm tra **5 hạng mục PPE bắt buộc** và trả về kết quả PASS/FAIL trong < 3 giây.

### 5 hạng mục PPE
| # | Hạng mục | Code Name |
|---|----------|-----------|
| 1 | 🪖 Mũ bảo hộ | `helmet` |
| 2 | 🦺 Áo phản quang | `reflective_vest` |
| 3 | 🧤 Găng tay | `gloves` |
| 4 | 👟 Giày bảo hộ | `safety_boots` |
| 5 | 🥽 Kính bảo hộ | `safety_glasses` |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+ / FastAPI |
| CV Engine | YOLOv8n (Ultralytics) |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Frontend | React 18 + Vite 5 + Tailwind CSS 3 |
| Charts | Chart.js / react-chartjs-2 |
| Deployment | Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone & Setup Backend
```bash
cd projects/safety-ppe-checker

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Setup Frontend
```bash
cd frontend
npm install
```

### 3. Run Development

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

---

## 🐳 Docker (Production)

```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## 📁 Project Structure

```
safety-ppe-checker/
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point
│   ├── config.py               # Settings & constants
│   ├── database.py             # SQLAlchemy setup
│   ├── models/                 # ORM models
│   ├── schemas/                # Pydantic schemas
│   ├── routers/                # API endpoints
│   ├── services/               # Business logic + CV Engine
│   ├── static/results/         # Annotated images output
│   └── requirements.txt
├── frontend/                   # React + Vite application
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── components/         # Reusable UI components
│   │   └── api/                # API client
│   └── package.json
├── data/                       # Training data (gitignored)
│   ├── raw/                    # Downloaded datasets
│   ├── processed/              # Merged & mapped data
│   └── demo/                   # Demo test images
├── models_weights/             # YOLOv8 .pt files (gitignored)
├── scripts/                    # Utility scripts
├── docker-compose.yml
└── README.md
```

---

## 📖 Documentation

| Document | Path |
|----------|------|
| PRD | [docs/01_product_requirements/prd/](./docs/01_product_requirements/prd/) |
| Architecture | [docs/02_technical_specs/architecture.md](./docs/02_technical_specs/architecture.md) |
| Master Plan | [docs/03_plans/MASTER-PLAN.md](./docs/03_plans/MASTER-PLAN.md) |
| Test Strategy | [docs/04_testing/test-strategy.md](./docs/04_testing/test-strategy.md) |
| Data Strategy | [docs/06_research/DATA-STRATEGY.md](./docs/06_research/DATA-STRATEGY.md) |

---

## 📅 Timeline

| Sprint | Dates | Focus |
|--------|-------|-------|
| Setup + Docs | 15–21/03/2026 | Documentation & project init |
| Sprint 1 | 22–28/03/2026 | Backend + CV Engine |
| Sprint 2 | 29/03–04/04/2026 | Frontend Web UI |
| Sprint 3 | 05–12/04/2026 | Dashboard + Demo prep |

---

## 📜 License

This project is for educational and demonstration purposes.
