import io
import json
import logging
import os
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

MODEL_PATH = os.environ.get("MODEL_PATH", "/app/models/best.pt")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

model: YOLO | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    try:
        model = YOLO(MODEL_PATH)
        logger.info("YOLO model loaded from %s", MODEL_PATH)
    except Exception as exc:
        logger.error("Failed to load model: %s", exc)
    yield


app = FastAPI(title="Scorpion Detector API", version="1.0.0", lifespan=lifespan)

origins = [o.strip() for o in CORS_ORIGINS.split(",")] if CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=CORS_ORIGINS != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_inference(image_bytes: bytes) -> list[dict]:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc

    frame = np.array(image)
    results = model(frame)
    detections = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            detections.append(
                {
                    "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)],
                    "confidence": round(conf, 4),
                    "class_id": cls_id,
                    "class_name": model.names[cls_id],
                }
            )
    return detections


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/")
def root():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(status_code=415, detail=f"Unsupported media type: {file.content_type}")

    data = await file.read()
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        detections = _run_inference(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"detections": detections}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if model is None:
        await websocket.accept()
        await websocket.send_text(json.dumps({"error": "Model not loaded"}))
        await websocket.close()
        return

    await websocket.accept()
    logger.info("WebSocket connection opened")

    try:
        while True:
            data = await websocket.receive_bytes()
            if not data:
                continue
            try:
                detections = _run_inference(data)
                await websocket.send_text(json.dumps({"detections": detections}))
            except ValueError as exc:
                await websocket.send_text(json.dumps({"error": str(exc)}))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as exc:
        logger.error("WebSocket error: %s", exc)
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=False)
