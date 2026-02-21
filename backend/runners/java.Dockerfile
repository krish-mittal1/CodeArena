FROM eclipse-temurin:21-jdk-jammy
RUN useradd -m -u 1000 runner
USER runner
WORKDIR /sandbox
