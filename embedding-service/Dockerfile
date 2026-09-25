FROM python:3.12-slim

# FastEmbed downloads ONNX weights into FASTEMBED_CACHE_PATH. The default
# model is baked into the image below so the service never downloads a
# model at runtime.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
    FASTEMBED_CACHE_PATH=/opt/fastembed

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Warm the ONNX cache at build time (~90 MB, one-off) so the container
# starts offline and fast.
RUN python -c "import os; from fastembed import TextEmbedding; TextEmbedding(model_name=os.environ['EMBEDDING_MODEL'], cache_dir=os.environ['FASTEMBED_CACHE_PATH']).embed(['warm up'])"

COPY app ./app
COPY tests ./tests

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
