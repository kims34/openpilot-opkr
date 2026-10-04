FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN python -m pip install --upgrade pip && pip install pandas==2.3.3 requests==2.32.3 pyarrow==21.0.0
COPY research_v1_marcap.py ./
COPY verify_pit_volume.py ./
COPY list_pit_layout.py ./
CMD ["python","research_v1_marcap.py","--start","2018-01-02","--end","2026-09-28","--out","/pit/marcap_kospi_pit","--raw","/pit/marcap_raw"]
