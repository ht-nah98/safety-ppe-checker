# Safety PPE Checker — CLAUDE.md

Developer guide for AI assistants working in this codebase.

---

## 1. Project Overview

AI-powered PPE compliance checking for **electrical workers**. Upload a worker photo → YOLOv8 detects 5 PPE items → PASS/FAIL result returned.

**PASS rule:** ALL 5 items must be detected above their confidence threshold. One missing item = FAIL.

**5 PPE classes** (exact names, used as keys throughout codebase):
- `helmet`
- `reflective_vest`
- `gloves`
- `safety_boots`
- `safety_glasses`

**Tech stack:** FastAPI + SQLAlchemy (SQLite) + YOLOv8 (Ultralytics) + OpenCV → React + Vite + Tailwind

---

## 2. Development Commands

```bash
# Backend (from repo root)
cd backend && uvicorn main:app --reload

# Frontend (Sprint 2 — not yet built)
cd frontend && npm run dev

# Docker (full stack)
docker-compose up --build

# Seed demo data (MUST run from repo root, not backend/)
python scripts/seed_demo_data.py

# Model training (from repo root, after dataset is prepared)
yolo detect train data=data/dataset.yaml model=yolov8n.pt epochs=100

# Model evaluation
yolo detect val data=data/dataset.yaml model=models_weights/best.pt
```

API docs auto-generated at `http://localhost:8000/docs` (Swagger) and `/redoc`.

---

## 3. Architecture Overview

```
Frontend (React/Vite :5173)
    │
    ▼ HTTP (VITE_API_URL)
Backend (FastAPI :8000)
    ├── routers/
    │   ├── check_ppe.py      → POST /api/v1/check-ppe
    │   ├── inspections.py    → GET  /api/v1/inspections/**
    │   └── stats.py          → GET  /api/v1/stats
    ├── services/
    │   ├── cv_engine.py      → YOLOv8 inference (singleton)
    │   └── inspection_service.py → all DB operations
    ├── models/inspection.py  → SQLAlchemy ORM
    ├── schemas/              → Pydantic request/response models
    ├── config.py             → single source of truth
    └── database.py           → SQLAlchemy engine + session
```

**Key patterns:**
- **Singleton CVEngine** — loaded once on first request via `get_engine()` in `check_ppe.py`. Warmup runs a dummy inference so model weights are in memory.
- **Service layer** — routers call service functions; service functions are synchronous; route handlers are `async def`.
- **`config.py` as single source of truth** — all thresholds, paths, class maps, CORS origins live here. Never hardcode these elsewhere.
- **`results_json` as Text column** — stores a JSON string, not a Python dict. Always `json.dumps()` on write, `json.loads()` on read.

---

## 4. File Organization

```
safety-ppe-checker/
├── CLAUDE.md                    # ← this file
├── README.md
├── docker-compose.yml           # mounts ./backend/static, ./data, ./models_weights
├── .gitignore
│
├── backend/
│   ├── main.py                  # FastAPI app, lifespan, CORS, router registration
│   ├── config.py                # ALL thresholds, class maps, paths — read this first
│   ├── database.py              # SQLAlchemy engine, Base, get_db, create_tables
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models/
│   │   └── inspection.py        # ORM: inspections table
│   ├── schemas/
│   │   ├── inspection.py        # Pydantic: InspectionResponse, InspectionDetail, etc.
│   │   └── stats.py             # Pydantic: StatsResponse
│   ├── routers/
│   │   ├── check_ppe.py         # POST /check-ppe + CVEngine singleton
│   │   ├── inspections.py       # GET history, /export, /{id}
│   │   └── stats.py             # GET aggregated stats
│   ├── services/
│   │   ├── cv_engine.py         # YOLOv8 inference pipeline
│   │   └── inspection_service.py # save, get, stats, CSV export
│   ├── models_weights/          # .pt files (gitignored); .gitkeep present
│   └── static/
│       ├── results/             # annotated output images (gitignored)
│       └── originals/           # uploaded originals (gitignored)
│
├── frontend/                    # Sprint 2 — React/Vite (not yet built)
│
├── data/
│   ├── dataset.yaml             # YOLOv8 training config — class names MUST match config.py
│   ├── demo/                    # sample images for testing
│   ├── raw/                     # gitignored
│   └── processed/               # gitignored (train/val/test splits)
│
├── scripts/
│   └── seed_demo_data.py        # generates 30 fake inspection records
│
└── docs/
    ├── 02_technical_specs/architecture.md
    ├── 02_technical_specs/cv-engine/TP-CV-001.md
    ├── 02_technical_specs/dashboard/TP-DSH-001.md
    ├── 02_technical_specs/web-interface/TP-WEB-001.md
    ├── 03_plans/MASTER-PLAN.md
    ├── 04_testing/test-strategy.md
    ├── 06_research/DATA-STRATEGY.md
    └── 06_research/INSIGHTS-AND-TIPS.md
```

---

## 5. Key Files to Understand First

Read these in order before making any significant change:

1. **`backend/config.py`** — thresholds, class maps, file paths, CORS origins. Everything else imports from here.
2. **`backend/services/cv_engine.py`** — full AI pipeline: decode → resize → YOLO inference → map classes → threshold gate → annotate → return dict.
3. **`backend/routers/check_ppe.py`** — main endpoint, singleton pattern, validation logic.
4. **`backend/services/inspection_service.py`** — all DB operations: save, paginate, stats aggregation, CSV export.
5. **`data/dataset.yaml`** — 5 class names for training. Must stay in sync with `REQUIRED_PPE_CLASSES` in `config.py`.

---

## 6. Critical Rules

**NEVER do the following without explicit instruction:**

| Rule | Why |
|---|---|
| Do NOT modify `PPE_CLASS_MAP` in `config.py` | Maps raw dataset labels → project class names; changing it breaks inference on all existing datasets |
| Do NOT modify `REQUIRED_PPE_CLASSES` | Used as dict keys throughout; changing order or names corrupts DB records |
| Do NOT raise `CONFIDENCE_THRESHOLDS` for `gloves` (0.40) or `safety_glasses` (0.40) | Set intentionally low — small items far from camera; higher threshold causes false negatives |
| Do NOT re-instantiate `CVEngine` per request | Singleton is intentional; warmup takes several seconds and would make every request slow |
| Do NOT hardcode PPE class names, file paths, or thresholds anywhere | Always import from `config.py` |
| Do NOT use `print()` in backend code | Use `logging.getLogger(__name__)` |
| Do NOT move `/inspections/export` route after `/{inspection_id}` | FastAPI matches routes in registration order — "export" would be treated as an inspection ID |

---

## 7. Code Style & Conventions

**Python (backend):**
- Type hints on all function signatures
- `async def` for all route handlers; service functions are **synchronous**
- Pydantic v2 syntax (no `.dict()` — use `.model_dump()`)
- Import order: stdlib → third-party → local (separated by blank lines)
- Logging: `logger = logging.getLogger(__name__)` at module level

**Frontend (Sprint 2 — pending):**
- Functional components only (no class components)
- All API calls via `src/api/ppe.js` — never call `fetch()` directly in components
- Backend URL via `VITE_API_URL` env var only
- Tailwind CSS only — no inline styles, no separate CSS files

---

## 8. Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./ppe_checker.db` (in backend/) | SQLAlchemy connection string |
| `MODEL_PATH` | `./models_weights/best.pt` | Path to custom-trained YOLO weights |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL for frontend (Docker: set in compose) |

**Model fallback chain** (defined in `cv_engine.py`):
1. `$MODEL_PATH` (custom `best.pt`)
2. `models_weights/yolov8n.pt` (pretrained fallback)
3. `"yolov8n.pt"` (Ultralytics auto-download on first use)

---

## 9. Gotchas & Non-Obvious Details

- **Two-stage confidence filtering:** `INFERENCE_CONF = 0.25` in `config.py` is a YOLO pre-filter that discards very weak detections before Python sees them. Per-class `CONFIDENCE_THRESHOLDS` (0.40–0.50) are a second gate applied in Python inside `cv_engine.py`. Both must pass for a detection to count.

- **Single-worker assumption:** `cv_engine.py` keeps only the **highest-confidence detection per class**. If two workers appear in one photo, only one person's gear is counted. This is by design for the demo scenario.

- **`results_json` is always a string:** The `Inspection.results_json` column is `Text`, not JSON. Always serialize with `json.dumps()` before saving and deserialize with `json.loads()` after reading. Never assign a `dict` directly to this field.

- **Stats aggregation is Python-side:** `get_stats()` in `inspection_service.py` loads all failed inspection rows and parses their JSON in Python to count per-class violations. There is no SQL aggregation. This is fine at demo scale (~hundreds of records).

- **Seed script path:** `seed_demo_data.py` adds `../backend` to `sys.path`, so it **must be run from the repo root** (not from inside `backend/`). The correct invocation is `python scripts/seed_demo_data.py`.

- **Seed script is not fully idempotent:** If any inspection records exist in the DB, the script exits without inserting. To re-seed, delete `backend/ppe_checker.db` first.

- **CSV export uses UTF-8-BOM:** The export endpoint encodes the CSV with `utf-8-sig` (BOM). This is intentional for Vietnamese Windows users where Excel requires BOM to auto-detect UTF-8.

- **Docker volume paths:** `docker-compose.yml` mounts `./backend/static` → `/app/static`. Changing `STATIC_DIR` in `config.py` without updating `docker-compose.yml` will break static file serving in Docker.

- **`dataset.yaml` class names:** Training labels in `data/dataset.yaml` use project-standard names (e.g., `reflective_vest`, not `vest`). `PPE_CLASS_MAP` in `config.py` translates raw dataset names (e.g., `"vest"`, `"Safety-vest"`) to these standard names. If you add a new dataset, add its label mappings to `PPE_CLASS_MAP` — do not change `REQUIRED_PPE_CLASSES`.

---

## 10. Gitignored Items

These exist locally but are not in the repo:

- `models_weights/*.pt` — model weight files (large binaries)
- `data/raw/`, `data/processed/` — training datasets
- `backend/ppe_checker.db` — SQLite database
- `backend/static/results/`, `backend/static/originals/` — generated images
- `frontend/node_modules/`, `frontend/dist/`
- `runs/` — Ultralytics training output
- `.env`, `.env.local`, `.env.production`

---

## 11. Testing Strategy

**Manual API testing** — Swagger UI at `http://localhost:8000/docs` or curl:

| Test scenario | Expected result |
|---|---|
| Upload image with all 5 PPE visible | `overall_pass: true`, all items `detected: true` |
| Upload image missing one PPE item | `overall_pass: false`, one item `detected: false` |
| Upload non-image file (e.g., PDF) | HTTP 400, "Invalid file format" |
| Upload image > 10MB | HTTP 413, "File too large" |
| GET `/api/v1/stats` after seeding | Returns counts, pass rate, violations by class |
| GET `/api/v1/inspections/export` | Downloads CSV with BOM, all records |

**CV model evaluation:** `yolo detect val data=data/dataset.yaml model=models_weights/best.pt`

**Dashboard testing:** Run seed script → verify stats endpoint returns realistic distribution (~65% pass).

---

## 12. Project Timeline

| Phase | Dates | Status |
|---|---|---|
| Week 1 — Planning & docs | Before Mar 22 | Complete |
| Sprint 1 — Backend + CV engine | Mar 22–28, 2026 | In progress |
| Sprint 2 — React frontend | Mar 29 – Apr 4, 2026 | Pending |
| Sprint 3 — Polish, testing, demo prep | Apr 5–12, 2026 | Pending |
| **Demo** | **2026-04-12** | — |

---

## 13. Reference Documentation

| File | Purpose |
|---|---|
| `docs/02_technical_specs/architecture.md` | System architecture, component diagram |
| `docs/02_technical_specs/cv-engine/TP-CV-001.md` | CV engine technical spec (inference pipeline, thresholds) |
| `docs/02_technical_specs/dashboard/TP-DSH-001.md` | Dashboard/history API spec |
| `docs/02_technical_specs/web-interface/TP-WEB-001.md` | Frontend technical spec (Sprint 2) |
| `docs/03_plans/MASTER-PLAN.md` | Sprint plan, task breakdown, timeline |
| `docs/04_testing/test-strategy.md` | Test approach, tools, acceptance criteria |
| `docs/06_research/DATA-STRATEGY.md` | Dataset sources, labeling guide, `PPE_CLASS_MAP` origins |
| `docs/06_research/INSIGHTS-AND-TIPS.md` | Research notes, YOLOv8 tips, lessons learned |
| `project-context.md` | High-level project context and goals |
| `backlog.md` | Remaining tasks and known issues |
| `glossary.md` | Term definitions (Vietnamese/English PPE names, etc.) |
