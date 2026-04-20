# FasalDoc API 🌾

**AI-powered plant disease detection backend for Indian farmers.**  
Detects 38 plant diseases from leaf photos, delivers localized treatment advice in English, Hindi (हिंदी), and Punjabi (ਪੰਜਾਬੀ), and sends weather-based disease risk alerts via FCM push notifications.

---

## Architecture Overview

```
Mobile App (React Native)
        │
        ▼
FastAPI (4 Uvicorn workers)
   ├── POST /detect  ──► EfficientNetB4 ML Model ──► S3 (image storage)
   ├── GET  /alerts  ──► OpenWeatherMap API ──► Redis cache (1hr TTL)
   ├── GET  /treatment/{id}  ──► PostgreSQL ──► Redis cache (24hr TTL)
   ├── POST /sync    ──► Idempotent batch upsert
   └── POST /auth/*  ──► JWT (phone-number auth)
        │
Celery Beat (every 6h)
   └── Weather check ──► FCM broadcast to at-risk regions
        │
PostgreSQL  Redis  AWS S3  Firebase FCM  Prometheus/Grafana
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.111 + Uvicorn (uvloop) |
| ML Model | EfficientNetB4 (TensorFlow 2.16) / TFLite INT8 fallback |
| Database | PostgreSQL 16 + SQLAlchemy async + Alembic |
| Cache | Redis 7 (weather TTL 1h, treatments TTL 24h) |
| Storage | AWS S3 (ap-south-1, Mumbai) |
| Auth | JWT (HS256) + bcrypt, phone-number based |
| Notifications | Firebase Cloud Messaging (FCM) |
| Task Queue | Celery + Redis broker, Beat scheduler |
| Monitoring | Prometheus + Grafana + structlog (JSON) |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- AWS S3 bucket in `ap-south-1`
- OpenWeatherMap API key (free tier works)
- Firebase project with FCM enabled (optional for notifications)

### 1. Clone and configure

```bash
git clone https://github.com/yourorg/fasaldoc-backend
cd fasaldoc-backend
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start all services

```bash
cd docker
docker compose up -d
```

Services started:
- `api` on port 8000
- `worker` (Celery worker)
- `beat` (Celery scheduler, runs every 6h)
- `postgres` on port 5432
- `redis` on port 6379
- `prometheus` on port 9090
- `grafana` on port 3000

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Add your ML model

Place your trained model in the `models/` directory:
```
models/
├── plant_disease_efficientnet.keras   # Keras model (primary)
└── plant_disease.tflite               # TFLite INT8 (fallback)
```

See [Training](#training-the-model) to train from scratch.

### 5. Verify health

```bash
curl http://localhost:8000/health
```

Expected:
```json
{"status": "ok", "database": "ok", "redis": "ok", "model": "keras"}
```

---

## API Reference

Full interactive docs at: `http://localhost:8000/docs`

### Authentication

All endpoints (except `/auth/*`) require:
```
Authorization: Bearer <jwt_token>
```

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone": "9876543210",        // Indian mobile (10 digits, starts 6-9)
  "name": "Harjinder Singh",
  "region": "Punjab",
  "language": "pa",             // "en" | "hi" | "pa"
  "primary_crops": ["wheat", "rice"],
  "password": "securepass123"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{"phone": "9876543210", "password": "securepass123"}
```

---

### Disease Detection

```http
POST /api/v1/detect?language=hi
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <leaf_image.jpg>   (JPEG/PNG/WebP, max 10MB)
```

**Response:**
```json
{
  "scan_id": "uuid",
  "disease_name": "अगेती झुलसा",
  "crop_name": "टमाटर",
  "confidence": 87.3,
  "stage": "Stage 2",
  "treatment_id": "uuid",
  "description": "अगेती झुलसा एक फफूंद रोग है...",
  "image_url": "https://fasaldoc-images.s3.ap-south-1.amazonaws.com/scans/...",
  "scan_date": "2024-06-15T10:30:00"
}
```

---

### Treatment Plan

```http
GET /api/v1/treatment/tomato_early_blight?language=hi
Authorization: Bearer <token>
```

---

### Weather-Based Alerts

```http
GET /api/v1/alerts?region=Punjab&language=hi
Authorization: Bearer <token>
```

---

### Scan History

```http
GET /api/v1/history?page=1&page_size=20&crop=tomato
GET /api/v1/history/{scan_id}
PATCH /api/v1/history/{scan_id}    {"status": "treated"}
```

---

### Offline Sync

```http
POST /api/v1/sync
Authorization: Bearer <token>
Content-Type: application/json

{
  "records": [
    {
      "id": "uuid",
      "disease_name": "Early Blight",
      "crop_name": "Tomato",
      "confidence": 82.5,
      "stage": "Stage 2",
      "image_uri": "file:///local/path.jpg",
      "scan_date": "2024-06-15T08:00:00",
      "status": "active",
      "treatment_id": "tomato_early_blight",
      "disease_class_index": 32
    }
  ]
}
```

---

## Error Response Format

All errors return:
```json
{
  "error": "SHORT_CODE",
  "message": "Human readable description",
  "detail": {}
}
```

| Code | HTTP | Meaning |
|---|---|---|
| `INVALID_FILE_TYPE` | 400 | Not JPEG/PNG/WebP |
| `FILE_TOO_LARGE` | 413 | Exceeds 10 MB |
| `LOW_CONFIDENCE` | 422 | Model confidence < 50% |
| `UNAUTHORIZED` | 401 | Missing/expired JWT |
| `FORBIDDEN` | 403 | Access to another user's data |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `RATE_LIMITED` | 429 | Too many requests |
| `INFERENCE_ERROR` | 500 | ML model failure |
| `MODEL_NOT_LOADED` | 503 | Model still loading |

---

## Training the Model

### 1. Download PlantVillage dataset
```bash
# From Kaggle: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
# Place in data/plantvillage/
```

### 2. Train
```bash
cd ml_training
python train.py \
  --data-dir ../data/plantvillage \
  --output-dir ../models \
  --phase1-epochs 5 \
  --phase2-epochs 20
```

### 3. Evaluate
```bash
python evaluate.py \
  --model ../models/plant_disease_efficientnet.keras \
  --data-dir ../data/plantvillage \
  --output-dir ../eval_results
```

### 4. Export to TFLite (INT8)
```bash
python export.py \
  --model ../models/plant_disease_efficientnet.keras \
  --output ../models/plant_disease.tflite \
  --images "../data/plantvillage/*/*.jpg" \
  --samples 100
```

### Performance Targets

| Metric | Target | 
|---|---|
| Top-1 Accuracy (PlantVillage val) | > 94% |
| TFLite model size | < 15 MB |
| API p95 latency (cloud) | < 800 ms |
| TFLite p95 latency (Snapdragon 680) | < 150 ms |

---

## Running Tests

```bash
pip install pytest pytest-asyncio aiosqlite httpx
pytest tests/ -v
```

---

## Monitoring

- **Prometheus metrics**: `http://localhost:9090`
- **Grafana dashboards**: `http://localhost:3000` (admin / see `.env`)
- **API metrics endpoint**: `http://localhost:8000/metrics`

### Key metrics exposed:
- `http_request_duration_seconds` — latency by endpoint
- `http_requests_total` — request count by status
- Model inference tracked via structlog (JSON → your log aggregator)

---

## Supported Diseases (38 Classes)

Crops covered: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, **Rice** ⭐, Soybean, Squash, Strawberry, Tomato, **Wheat** ⭐

⭐ = Added specifically for Indian farmers (not in original PlantVillage)

---

## Deployment Notes

- Deploy to **AWS EC2** (`c6g.xlarge` or `c6i.large`) in `ap-south-1` (Mumbai) for lowest latency to Indian users
- Use **AWS RDS PostgreSQL** in the same region
- Use **ElastiCache Redis** (r6g.large) for production cache
- Set `DEBUG=false` in production — enables JSON logging
- Configure `RATE_LIMIT_PER_MINUTE=60` for general endpoints, `/detect` is internally capped to 10/min
- The `/detect` endpoint S3 upload and ML inference run concurrently where possible to meet the 2s p95 target

---

## License

MIT License — see LICENSE file.
