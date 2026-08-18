FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install C++ dependencies for both MediaPipe and OpenCV
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        libegl1 \
        libgles2 \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home --shell /usr/sbin/nologin sportai \
    && mkdir -p /app/app/uploads \
    && chown -R sportai:sportai /app

USER sportai

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-10000}\""]