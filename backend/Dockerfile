FROM python:3.10-slim

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y netcat-openbsd libpq-dev gcc && \
    pip install --upgrade pip && \
    pip install -r /app/tools/requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/app/tools/entrypoint.sh"]

CMD [ "python", "-u", "manage.py", "runserver", "0.0.0.0:8000" ]