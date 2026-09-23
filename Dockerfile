FROM python:3.11-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code (credentials strictly excluded via .dockerignore)
COPY app/ app/
COPY data/ data/
COPY scripts/ scripts/
COPY evaluation/ evaluation/

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV DATA_BACKEND=LOCAL_DATA
ENV DATA_DIR=data

EXPOSE 8000

# Render dynamic port binding with 8000 fallback
CMD ["sh", "-c", "uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
