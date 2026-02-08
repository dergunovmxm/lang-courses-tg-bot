# -------- builder stage --------
FROM ubuntu:noble-20260113 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Переключаемся на более стабильное зеркало перед установкой
RUN sed -i 's|http://archive.ubuntu.com/ubuntu|http://us.archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources || true

# Retry логика с увеличенным числом попыток
RUN SUCCESS=false; \
    for i in 1 2 3 4 5; do \
        echo "=== Attempt $i of 5 ===" && \
        rm -rf /var/lib/apt/lists/* && \
        apt-get clean && \
        sleep 2 && \
        apt-get update && \
        apt-get install -y --allow-unauthenticated \
            build-essential \
            cmake \
            git \
            ca-certificates && \
        rm -rf /var/lib/apt/lists/* && \
        if git --version 2>/dev/null; then \
            echo "✓ Success! Git installed."; \
            SUCCESS=true; \
            break; \
        else \
            echo "✗ Failed, retrying in 15 seconds..."; \
            sleep 15; \
        fi; \
    done; \
    if [ "$SUCCESS" != "true" ]; then \
        echo "ERROR: Failed to install packages after 5 attempts"; \
        exit 1; \
    fi

# Build whisper.cpp
RUN git clone --depth 1 https://github.com/ggerganov/whisper.cpp.git /opt/whisper.cpp
WORKDIR /opt/whisper.cpp
RUN cmake -B build && cmake --build build --config Release

# -------- runtime stage --------
FROM ubuntu:noble-20260113

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Переключаемся на стабильное зеркало
RUN sed -i 's|http://archive.ubuntu.com/ubuntu|http://us.archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources || true

# Retry логика для runtime
RUN SUCCESS=false; \
    for i in 1 2 3 4 5; do \
        echo "=== Attempt $i of 5 ===" && \
        rm -rf /var/lib/apt/lists/* && \
        apt-get clean && \
        sleep 2 && \
        apt-get update && \
        apt-get install -y --allow-unauthenticated \
            ffmpeg \
            python3 \
            python3-pip \
            ca-certificates && \
        rm -rf /var/lib/apt/lists/* && \
        if python3 --version 2>/dev/null && pip3 --version 2>/dev/null; then \
            echo "✓ Success! Python installed."; \
            SUCCESS=true; \
            break; \
        else \
            echo "✗ Failed, retrying in 15 seconds..."; \
            sleep 15; \
        fi; \
    done; \
    if [ "$SUCCESS" != "true" ]; then \
        echo "ERROR: Failed to install packages after 5 attempts"; \
        exit 1; \
    fi

COPY --from=builder /opt/whisper.cpp/build/bin/whisper-cli /usr/local/bin/whisper-cli

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

ENV WHISPER_EXECUTABLE=/usr/local/bin/whisper-cli

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python3", "bot/main.py"]


