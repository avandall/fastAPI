# 1. Dùng bản Python nhẹ (slim) để giảm dung lượng
FROM python:3.12-slim

# 2. Đặt thư mục làm việc trong container
WORKDIR /app

# 3. Chép file requirements vào và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Chép toàn bộ code dự án vào container
COPY . .

# 5. Mở cổng 8000
EXPOSE 8000

# 6. Lệnh khởi chạy (Dùng uvicorn trực tiếp hoặc gunicorn)
# Chạy Gunicorn với Uvicorn Worker bên trong Docker
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]

