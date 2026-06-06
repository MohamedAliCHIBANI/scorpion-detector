/* ── Config ────────────────────────────────────────────────────
   Set BACKEND_WS_URL to your backend WebSocket address.
   When running via docker-compose this defaults to the same
   host on port 8000.  Override with a query-param ?wsUrl=...
   for quick local testing without rebuilding the image.
────────────────────────────────────────────────────────────── */
const params = new URLSearchParams(window.location.search);
const BACKEND_WS_URL =
    params.get("wsUrl") ||
    `${location.protocol === "https:" ? "wss" : "ws"}://${location.hostname}:8000/ws`;

/* Frame capture rate in milliseconds */
const CAPTURE_INTERVAL_MS = 200;
const JPEG_QUALITY = 0.72;

/* ── DOM refs ──────────────────────────────────────────────── */
const video        = document.getElementById("video");
const canvas       = document.getElementById("canvas");
const ctx          = canvas.getContext("2d");
const statusDot    = document.getElementById("statusDot");
const statusText   = document.getElementById("statusText");
const detectionEl  = document.getElementById("detectionCount");
const errorBanner  = document.getElementById("errorBanner");

/* ── State ─────────────────────────────────────────────────── */
let ws = null;
let captureTimer = null;

/* ── Helpers ───────────────────────────────────────────────── */
function setStatus(state, text) {
    statusDot.className = `status-dot ${state}`;
    statusText.textContent = text;
}

function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.setAttribute("aria-hidden", "false");
}

function hideError() {
    errorBanner.setAttribute("aria-hidden", "true");
}

function updateDetectionCount(n) {
    detectionEl.textContent = `${n} detection${n !== 1 ? "s" : ""}`;
    detectionEl.className = `detection-count${n > 0 ? " has-detections" : ""}`;
}

/* ── Drawing ───────────────────────────────────────────────── */
const BBOX_COLOR  = "#3b82f6";
const ALERT_COLOR = "#fbbf24";

function drawDetections(detections) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const color = detections.length > 0 ? ALERT_COLOR : BBOX_COLOR;
    ctx.strokeStyle = color;
    ctx.fillStyle   = color;
    ctx.lineWidth   = 2;
    ctx.font        = "bold 14px 'Segoe UI', system-ui, sans-serif";
    ctx.shadowColor = color;
    ctx.shadowBlur  = 6;

    detections.forEach(({ bbox, class_name, confidence }) => {
        const [x1, y1, x2, y2] = bbox;
        const w = x2 - x1;
        const h = y2 - y1;

        ctx.strokeRect(x1, y1, w, h);

        const label = `${class_name} ${(confidence * 100).toFixed(1)}%`;
        const labelY = y1 > 20 ? y1 - 6 : y1 + 18;
        ctx.fillText(label, x1 + 2, labelY);
    });

    ctx.shadowBlur = 0;
    updateDetectionCount(detections.length);
}

/* ── WebSocket ─────────────────────────────────────────────── */
function connectWebSocket() {
    setStatus("inactive", "Connecting…");

    ws = new WebSocket(BACKEND_WS_URL);
    ws.binaryType = "arraybuffer";

    ws.addEventListener("open", () => {
        setStatus("active", "Connected");
        hideError();
    });

    ws.addEventListener("message", (evt) => {
        try {
            const data = JSON.parse(evt.data);
            if (data.error) {
                showError(`Server: ${data.error}`);
                updateDetectionCount(0);
            } else {
                hideError();
                drawDetections(data.detections || []);
            }
        } catch {
            /* ignore malformed frames */
        }
    });

    ws.addEventListener("close", () => {
        setStatus("inactive", "Disconnected — retrying…");
        stopCapture();
        setTimeout(connectWebSocket, 3000);
    });

    ws.addEventListener("error", () => {
        setStatus("error", "Connection error");
        showError(`Cannot reach backend at ${BACKEND_WS_URL}. Is the server running?`);
    });
}

/* ── Frame capture ─────────────────────────────────────────── */
function startCapture() {
    captureTimer = setInterval(() => {
        if (
            video.readyState < video.HAVE_ENOUGH_DATA ||
            ws?.readyState !== WebSocket.OPEN
        ) return;

        canvas.toBlob(
            (blob) => {
                if (!blob) return;
                blob.arrayBuffer().then((buf) => {
                    if (ws?.readyState === WebSocket.OPEN) ws.send(buf);
                });
            },
            "image/jpeg",
            JPEG_QUALITY
        );
    }, CAPTURE_INTERVAL_MS);
}

function stopCapture() {
    clearInterval(captureTimer);
    captureTimer = null;
}

/* ── Camera ────────────────────────────────────────────────── */
async function initCamera() {
    if (!navigator.mediaDevices?.getUserMedia) {
        showError("Camera API not available. Use HTTPS or localhost.");
        setStatus("error", "No camera API");
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } },
            audio: false,
        });

        video.srcObject = stream;
        video.addEventListener("loadedmetadata", () => {
            canvas.width  = video.videoWidth;
            canvas.height = video.videoHeight;
            startCapture();
        });
    } catch (err) {
        const messages = {
            NotAllowedError:   "Camera access denied. Allow it in your browser settings.",
            NotFoundError:     "No camera found on this device.",
            NotSupportedError: "Camera not supported by this browser.",
            NotReadableError:  "Camera is in use by another application.",
        };
        const msg = messages[err.name] ?? `Camera error: ${err.message}`;
        showError(msg);
        setStatus("error", "Camera unavailable");
    }
}

/* ── Boot ──────────────────────────────────────────────────── */
window.addEventListener("load", () => {
    connectWebSocket();
    initCamera();
});
