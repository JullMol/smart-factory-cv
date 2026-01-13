FROM nvidia/cuda:12.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY models/ ./models/
COPY config/ ./config/

ENV MODEL_PATH=/app/models/best.onnx
ENV MODEL_FALLBACK_PATH=/app/models/best.pt
ENV GRPC_HOST=0.0.0.0
ENV GRPC_PORT=50051
ENV REST_HOST=0.0.0.0
ENV REST_PORT=8000
ENV METRICS_PORT=9090

EXPOSE 8000 50051 9090

WORKDIR /app/src

CMD ["python3", "main.py"]
