# Use minimal Python image — significantly smaller than full UBI9 python-311
FROM registry.access.redhat.com/ubi9/python-311-minimal:latest

WORKDIR /app

# Install only what's needed for Snowflake connector + FastAPI
# RUN microdnf install -y gcc python3-devel && microdnf clean all
# (Already included in python-311-minimal)

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Only copy application code — .dockerignore excludes tests, venv, cache
COPY --chown=1001:1001 . .

ENV PORT=8000
ENV CLIENT_VALIDATION=Prod

EXPOSE 8000

USER 1001

CMD ["sh", "-c", "uvicorn main:app --host 127.0.0.1 --port ${PORT}"]
