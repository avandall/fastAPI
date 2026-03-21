#!/bin/bash

# 1. Kích hoạt môi trường ảo (đường dẫn tuyệt đối cho chắc chắn)
source /home/avandall1999/fastapi/venv/bin/activate

# 2. Tính toán số lượng Worker tự động (nproc * 2 + 1)
NUM_WORKERS=$(($(nproc) * 2 + 1))

echo "Đang khởi động FastAPI với $NUM_WORKERS workers..."

# 3. Chạy Gunicorn với Uvicorn Worker
# -w: số lượng worker
# -k: loại worker (phải có uvicorn.workers.UvicornWorker)
# -b: bind vào IP và Port (0.0.0.0 để Cloudflare Tunnel nhìn thấy)
exec gunicorn -w $NUM_WORKERS -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
