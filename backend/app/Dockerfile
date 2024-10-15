FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

COPY . /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y netcat-openbsd libpq-dev gcc && \
    pip install --upgrade pip && \
    pip install -r /app/tools/requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/app/tools/entrypoint.sh"]

CMD [ "uvicorn", "app.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app", "--reload-include", "*.html", "--reload-include", "*.css", "--reload-include", "*.js" ]
