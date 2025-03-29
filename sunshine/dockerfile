FROM python:3.12-slim

ENV APP_BASE=/opt
WORKDIR ${APP_BASE}

COPY requirements.txt ${APP_BASE}/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY src/ ${APP_BASE}/
CMD ["python", "-m", main]
