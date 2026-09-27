# Playwright's own image ships a matching Chromium + all OS deps, which
# avoids hand-maintaining apt package lists for headless Chromium on Debian.
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1
# Cloud Run injects PORT; uvicorn reads it at container start via the shell form below.
ENV PORT=8080
EXPOSE 8080

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
