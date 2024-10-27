FROM python:3.13.0-slim

COPY --from=ghcr.io/astral-sh/uv:0.4.27 /uv /uvx /bin/
COPY pyproject.toml uv.lock  ./
RUN uv sync --frozen

COPY enphase_to_mqtt enphase_to_mqtt

CMD ["uv", "run", "python", "-m", "enphase_to_mqtt.app"]
