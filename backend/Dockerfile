# Use UBI9 minimal as base, then add Python 3.11
# This is significantly smaller than ubi9/python-311:latest (~500MB → ~250MB)
FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

WORKDIR /app

# Install Python 3.11 and minimal runtime dependencies
RUN microdnf install -y \
    python3.11 \
    python3.11-pip \
    && microdnf clean all

# Upgrade pip and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Only copy application code — .dockerignore excludes tests, venv, cache
COPY --chown=1001:1001 . .

ENV PORT=8000
ENV CLIENT_VALIDATION=Prod

EXPOSE 8000

USER 1001

CMD ["sh", "-c", "uvicorn main:app --host 127.0.0.1 --port ${PORT}"]
