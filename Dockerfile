FROM python:3.12.9-alpine3.21 AS python

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

