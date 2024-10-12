FROM python:3.10-slim

WORKDIR /app

COPY requirements/requirements.txt /app/

RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
