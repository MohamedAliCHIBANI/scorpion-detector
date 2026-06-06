# Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Browser                              │
│                                                              │
│   webcam ──► canvas ──► JPEG bytes ──► WebSocket /ws        │
│                ▲                            │                │
│                └────── detections ◄─────────┘                │
└──────────────────────────────────────────────────────────────┘
                              │
                    WebSocket (port 8000)
                              │
┌──────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Python)                     │
│                                                              │
│   /health  GET   → {"status":"ok","model_loaded":true}       │
│   /predict POST  → upload an image, get JSON detections      │
│   /ws      WS    → binary frames in, JSON detections out     │
│                              │                               │
│                        YOLO (Ultralytics)                    │
│                              │                               │
│                       models/best.pt                        │
└──────────────────────────────────────────────────────────────┘

Training pipeline (offline):
    dataset (Kaggle) → training/train.py → runs/train/.../best.pt
                                                    │
                                            GitHub Release
                                                    │
                                          models/download_weights.sh
```

## Data flow (live detection)

1. The browser opens a WebSocket connection to `ws://<host>:8000/ws`.
2. Every 200 ms a JPEG frame is captured from the webcam and sent as binary.
3. The backend decodes the frame with Pillow, runs YOLO inference, and returns:
   ```json
   { "detections": [{ "bbox":[x1,y1,x2,y2], "confidence":0.87,
                       "class_id":0, "class_name":"scorpion" }] }
   ```
4. The frontend draws bounding boxes and labels on the canvas overlay.

## Data flow (HTTP inference)

POST a multipart image to `/predict`:
```
curl -X POST http://localhost:8000/predict \
     -F "file=@scorpion.jpg"
```
