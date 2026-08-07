FROM registry.access.redhat.com/ubi9/python-311:latest

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=1001:1001 . .

ENV PORT=8000
ENV CLIENT_VALIDATION=Prod

EXPOSE 8000

USER 1001

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
