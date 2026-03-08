# How to build
# docker build -f front/Dockerfile -t water-frontend .
# How to up
# docker run -p 8501:8501 water-frontend

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY front/ ./front/

# Порт Streamlit
EXPOSE 8501

# Запуск Streamlit
CMD ["python", "-X", "utf8", "-m", "streamlit", "run", "front/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]