FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /test

COPY requirements_onnx.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY test_onnx_harness.py .
COPY kannada_transliterate.py .

CMD ["python", "test_onnx_harness.py"]