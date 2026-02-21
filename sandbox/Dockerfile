FROM debian:bookworm-slim

# ── Install all language runtimes ─────────────────────────
# Python 3, g++ (C++17), Node.js, and OpenJDK (Java)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    g++ \
    nodejs \
    default-jdk-headless \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# ── Create sandbox user with explicit UID 1000 ───────────
# Must match: no --user override in docker run, consistent permissions
RUN useradd -m -u 1000 -s /bin/bash sandbox

# ── Working directory = bind mount target ─────────────────
WORKDIR /sandbox

# ── Default to non-root user ─────────────────────────────
USER sandbox

# ── No fixed entrypoint — sandbox.py overrides with sh -c ─
CMD ["bash"]
