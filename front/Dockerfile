# How to build
# docker build -f front/Dockerfile -t water-frontend .
# How to up
# docker run -p 8501:8501 water-frontend

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_EXTRA_INDEX_URL=https://pypi.org/simple \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY front/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY front/ ./front/

# Порт Streamlit
EXPOSE 8501

# Запуск Streamlit
CMD ["python", "-X", "utf8", "-m", "streamlit", "run", "front/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
