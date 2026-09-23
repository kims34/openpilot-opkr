FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY monitor.py .
COPY production.py .
ENV PORT=8080
CMD ["sh", "-c", "uvicorn production:app --host 0.0.0.0 --port ${PORT:-8080}"]
