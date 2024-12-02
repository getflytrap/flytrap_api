FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y \
    libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-b", "0.0.0.0:8000", "flytrap:app", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-"]