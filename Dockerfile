FROM python:3.15.0-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 QT_AUDIO_BACKEND=pulseaudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libegl1 libgl1 libopengl0 libglib2.0-0 libdbus-1-3 libxkbcommon0 \
    libgssapi-krb5-2 libfontconfig1 libfreetype6 libwayland-client0 libwayland-cursor0 \
    libwayland-egl1 libpulse0 libasound2t64 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
COPY . .
RUN pip install --no-cache-dir --no-deps . && pip freeze > /app/requirements.resolved.txt
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd -g ${APP_GID} signal && useradd -m -u ${APP_UID} -g signal signal \
    && mkdir -p /data /tmp/runtime-signal && chown signal:signal /data /tmp/runtime-signal \
    && chmod 700 /tmp/runtime-signal
USER signal
ENV HOME=/home/signal XDG_RUNTIME_DIR=/tmp/runtime-signal SIGNAL_LAB_DATA_DIR=/data
CMD ["python", "-m", "solar_forge_signal_lab"]
