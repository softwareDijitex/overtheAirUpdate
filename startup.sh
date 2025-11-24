#!/bin/bash
# Azure App Service startup script for FastAPI
# Use PORT environment variable if set, otherwise default to 8000
PORT=${PORT:-8000}
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --access-logfile - --error-logfile -

