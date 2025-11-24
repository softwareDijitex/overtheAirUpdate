#!/bin/bash
echo "Starting Customer Management System Backend..."
echo "=============================================="
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
