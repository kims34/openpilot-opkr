FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY monitor.py .
COPY production.py .
COPY production_fixed.py .
COPY production_naver.py .
COPY production_naver_live.py .
COPY production_naver_state.py .
COPY laggards.py .
COPY sitecustomize.py .
ENV PYTHONPATH=/app
ENV PORT=8080
CMD ["sh", "-c", "python -m uvicorn production_naver_state:app --host 0.0.0.0 --port ${PORT:-8080}"]
