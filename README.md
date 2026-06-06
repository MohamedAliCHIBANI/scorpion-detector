# Scorpion Detector

**Real-time scorpion detection from a webcam feed — powered by YOLOv8 and FastAPI.**

Scorpion stings are a major public-health concern in North Africa and the Middle East,
causing thousands of hospitalisations each year.  This project demonstrates how a
lightweight YOLO model served over a WebSocket can provide instant, on-device detection
through an ordinary browser — no app installation required.

---

## Architecture

```
Browser (webcam → WebSocket frames)
       ↕  ws://localhost:8000/ws
FastAPI backend  →  YOLO inference  →  JSON detections
       ↕  POST /predict  (single image)
Static frontend  (nginx)
```

Full diagram: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Quick start (Docker)

> **Docker and Docker Compose are the only supported way to run this project.**

### 1 — Get the model weights

```bash
bash models/download_weights.sh
```

This downloads `best.pt` from the latest GitHub Release into `models/`.

### 2 — Start the stack

```bash
docker compose up --build
```

| Service  | URL |
|----------|-----|
| Frontend | <http://localhost:8080> |
| Backend  | <http://localhost:8000> |

Open `http://localhost:8080` in a browser, grant camera permission, and scorpion
detection begins immediately.

---

## API reference

### `GET /health`

```bash
curl http://localhost:8000/health
# {"status":"ok","model_loaded":true}
```

### `POST /predict` — single image upload

```bash
curl -X POST http://localhost:8000/predict \
     -F "file=@path/to/image.jpg"
```

**Response:**

```json
{
  "detections": [
    {
      "bbox": [142.5, 88.3, 310.7, 224.1],
      "confidence": 0.9123,
      "class_id": 0,
      "class_name": "scorpion"
    }
  ]
}
```

### `WS /ws` — live webcam stream

Send JPEG frames as binary; receive detection JSON after each frame.

---

## Environment variables (backend)

| Variable      | Default              | Description |
|---------------|----------------------|-------------|
| `MODEL_PATH`  | `/app/models/best.pt`| Path to YOLO weights |
| `HOST`        | `0.0.0.0`            | Bind address |
| `PORT`        | `8000`               | Bind port |
| `CORS_ORIGINS`| `*`                  | Comma-separated allowed origins, or `*` |

---

## Dataset

The training dataset is publicly available on Kaggle:

> **[Scorpion Detection Dataset](https://www.kaggle.com/datasets/chibanimohamedali/scorpion-detection-dataset)**

See [docs/DATASET.md](docs/DATASET.md) for full documentation (classes, label format,
image count, licence).

---

## Training

1. Download the dataset from Kaggle and unzip it.
2. Install dependencies: `pip install ultralytics`
3. Adjust `training/data.yaml` to point to the dataset root.
4. Run:

```bash
python training/train.py --data training/data.yaml --epochs 100
```

The best weights are saved to `runs/train/scorpion/weights/best.pt`.
Copy them to `models/best.pt` and create a GitHub Release to publish them.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Detection model | [YOLOv8](https://github.com/ultralytics/ultralytics) |
| Backend API | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn |
| Image decoding | Pillow, NumPy |
| Frontend | Vanilla HTML / CSS / JS |
| Static server | Nginx (Alpine) |
| Containerisation | Docker + Docker Compose |
| CI | GitHub Actions |

---

## Screenshots / Demo

<!-- Add screenshots here -->
> *Place a screenshot of the live detection UI in `docs/` and link it here.*

---

## Licence

MIT — see [LICENSE](LICENSE).

Dataset: CC BY 4.0 — see [docs/DATASET.md](docs/DATASET.md).
