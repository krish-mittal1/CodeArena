FROM debian:bookworm-slim

# ── 1. Install Runtimes + Python Pip ──────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    g++ \
    nodejs \
    default-jdk-headless \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# ── 2. Set up Working Dir ────────────────────────────────
WORKDIR /app

# ── 3. Install Backend Dependencies ──────────────────────
# We do this before copying the whole project to save time
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# ── 4. Copy Project Files ────────────────────────────────
COPY . .

# ── 5. Setup User for Sandbox Security ───────────────────
RUN useradd -m -u 1000 -s /bin/bash sandbox

# ── 6. Default Command ──────────────────────────────────
# Using python3 -m uvicorn is the most stable way to start
CMD ["python3", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]