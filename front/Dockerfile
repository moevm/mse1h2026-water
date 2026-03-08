FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY front/ ./front/

# Порт Streamlit
EXPOSE 8501

# Запуск Streamlit
CMD ["python", "-X", "utf8", "-m", "streamlit", "run", "front/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]