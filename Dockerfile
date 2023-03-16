FROM python:3.11.2-slim

RUN pip install poetry==1.4.0
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false --local && \
    poetry install

COPY enphase_to_mqtt enphase_to_mqtt
CMD ["python", "-m", "enphase_to_mqtt.app"]
