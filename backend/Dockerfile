FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# MediaPipe Tasks' Linux binary links directly to libEGL.so.1 and
# libGLESv2.so.2. No X11/desktop packages are needed for server-side frames.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends libegl1 libgles2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY models ./models

RUN useradd --create-home --shell /usr/sbin/nologin sportai \
    && mkdir -p /app/app/uploads \
    && chown -R sportai:sportai /app

USER sportai

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-10000}\""]
