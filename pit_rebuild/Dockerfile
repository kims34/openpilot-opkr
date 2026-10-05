FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN python -m pip install --upgrade pip && pip install pandas==2.3.3 requests==2.32.3 pyarrow==21.0.0 scikit-learn==1.7.2
COPY research_v1_marcap.py ./
COPY verify_pit_volume.py ./
COPY list_pit_layout.py ./
COPY verify_build_stats.py ./
COPY research_kospi_clean_v2.py ./
COPY research_kospi_abstention_v3.py ./
COPY research_v1_pit_legacy_adapter.py ./
COPY research_kospi_abstention_v3_position_regen.py ./
COPY verify_position_regen.py ./
COPY promote_position_candidate.py ./
COPY test_fingerprint_semantics.py ./
COPY validation_stage_gate.py ./
COPY prepare_sealed_holdout.py ./
COPY acquire_sealed_holdout.py ./
CMD ["python","verify_position_regen.py"]
