FROM python:3.9-slim AS python

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["./venv/bin/uvicorn"]
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
