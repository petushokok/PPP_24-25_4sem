#!/bin/sh
cd /app
celery -A app.tasks.celery worker --loglevel=info
