# How to build
# docker build --no-cache -f back/Dockerfile -t water-backend .
# How to up
# docker run --rm -p 8000:8000 --env-file .env -v "${PWD}\back\credentials:/app/credentials:ro" water-backend

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_EXTRA_INDEX_URL=https://pypi.org/simple \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache \
    pip install uv && \
    uv pip install --system --upgrade pip && \
    uv pip install --system -r requirements.txt

COPY . .

RUN mkdir -p /app/credentials /app/output /app/img/classified

EXPOSE 8000

CMD ["python", "-X", "utf8", "-m", "uvicorn", "app:app", "--host=0.0.0.0", "--port=8000"]
