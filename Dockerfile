# Dehallucinator API image (DH-181, NFR-5).
#
#   docker build -t dehallucinator .
#   docker run --rm -p 8000:8000 dehallucinator
#   curl http://localhost:8000/health        -> {"status":"ok"}
#
# The demo UI runs from the same image:
#   docker run --rm -p 8501:8501 dehallucinator \
#       streamlit run ui/app.py --server.address=0.0.0.0 --server.port=8501

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Dependencies first, so code changes do not reinstall them. The CPU-only PyTorch index
# keeps the image several GB smaller than the default CUDA build.
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Bake the NLI model into the image so the first /check does not wait for a download.
COPY src/dehallucinator/config.py /tmp/config.py
RUN python -c "import runpy; from transformers import AutoModelForSequenceClassification, AutoTokenizer; name = runpy.run_path('/tmp/config.py')['NLI_MODEL']; AutoTokenizer.from_pretrained(name); AutoModelForSequenceClassification.from_pretrained(name)" \
    && rm /tmp/config.py

COPY src/ src/
COPY ui/ ui/
COPY data/ data/

# Run as an unprivileged user. .cache holds the model files; data/ must be writable because
# the retriever keeps its Wikipedia cache in data/wiki_cache.sqlite3.
RUN useradd --create-home --uid 10001 app \
    && mkdir -p /app/.cache \
    && chown -R app:app /app/.cache /app/data
USER app

EXPOSE 8000 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "dehallucinator.api:app", "--host", "0.0.0.0", "--port", "8000"]
