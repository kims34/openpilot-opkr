FROM python:3.12.14-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN python -m pip install --upgrade pip && pip install pandas==2.3.3 numpy==2.5.3 requests==2.32.3 pyarrow==21.0.0 scikit-learn==1.7.2
COPY research_v1_marcap.py ./
COPY rehydrate_frozen_long_history.py ./
COPY rehydrate_frozen_supervised_cache.py ./
COPY frozen_supervised_reference_36643183157.json ./
COPY frozen_supervised_v1 ./frozen_supervised_v1
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
COPY audit_retired_validation.py ./
COPY prepare_sealed_holdout.py ./
COPY acquire_sealed_holdout.py ./
COPY evaluate_sealed_holdout.py ./
COPY probe_pit_schema.py ./
CMD ["python","verify_position_regen.py"]
