FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /test

COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu "torch>=2.5" \
    && pip install --no-cache-dir -r requirements.txt

COPY test_indictrans2.py .

CMD ["python", "test_indictrans2.py"]