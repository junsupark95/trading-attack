FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# PYTHONPATH를 설정하여 'app' 패키지를 정상적으로 찾을 수 있게 함
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
