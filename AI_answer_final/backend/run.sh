#!/bin/bash
uvicorn backend_app.main:app --host 0.0.0.0 --port 8000 --reload