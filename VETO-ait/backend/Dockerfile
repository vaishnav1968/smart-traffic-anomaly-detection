# VETO Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY configs /app/configs
COPY agent/workspace /app/agent/workspace
COPY conftest.py /app/conftest.py

ENV PYTHONPATH=/app
ENV VETO_ENV=production
ENV VETO_HOST=0.0.0.0
ENV VETO_PORT=8000

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
