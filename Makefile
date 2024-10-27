mock-server:
	docker-compose up -d --build mock-server

dev: 
	uv run python -m enphase_to_mqtt.app

format:
	uv run ruff format

test: mock-server
	uv run pytest -s
