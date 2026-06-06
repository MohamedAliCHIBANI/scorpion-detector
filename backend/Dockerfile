FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV MODEL_PATH=/app/models/best.pt
ENV HOST=0.0.0.0
ENV PORT=8000
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["python", "server.py"]
