FROM node:20-slim
RUN useradd -m -u 1000 runner
USER runner
WORKDIR /sandbox
