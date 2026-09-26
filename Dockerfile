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
COPY production_investing.py .
COPY production_v14.py .
COPY production_v17.py .
COPY briefing.py .
COPY history_routes.py .
COPY laggards.py .
COPY next_day_probability.py .
COPY next_day_probability_v31.py .
COPY one_month_probability.py .
COPY one_month_distribution.py .
COPY one_month_calibrated.py .
COPY kospi_monthly.py .
COPY probability_shadow.py .
COPY probability_milestone.py .
COPY probability_model.py .
COPY probability_model_v31_runtime.py .
COPY sitecustomize.py .
ENV PYTHONPATH=/app
ENV PORT=8080
CMD ["sh", "-c", "python -m uvicorn production_v17:app --host 0.0.0.0 --port ${PORT:-8080}"]
