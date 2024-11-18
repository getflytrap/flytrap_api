FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./

RUN apt-get update && apt-get install -y \
    libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "eventlet", "-w", "flytrap:app", "--bind", "0.0.0.0:8000"]
