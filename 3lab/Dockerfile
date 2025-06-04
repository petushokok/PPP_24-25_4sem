FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY main.py ./
COPY celery_worker.sh ./

RUN sed -i 's/\r$//' celery_worker.sh && \
    chmod +x celery_worker.sh

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
