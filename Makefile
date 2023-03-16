mock-server:
	docker-compose up -d --build mock-server

dev: 
	poetry run python -m enphase_to_mqtt.app

test: mock-server
	poetry run pytest
