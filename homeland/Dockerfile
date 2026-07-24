FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8088

CMD ["gunicorn", "--bind", "0.0.0.0:8088", "--workers", "2", "--threads", "2", "--timeout", "60", "--graceful-timeout", "30", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "--capture-output", "app:app"]
