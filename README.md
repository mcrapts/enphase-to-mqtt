# Overview
This repository contains code to read data on a scheduled interval from Enphase Envoy gateways with firmware 7.x, and publish it on MQTT. 

The code will request a token using your Enphase credentials and use the token to read the data locally from your gateway. The token will be automatically refreshed if it expires within 30 days.

## Get started
1. Copy `.env.example` to `.env`
2. Enter the correct values in `.env`
3. Run `docker-compose up -d enphase-to-mqtt` 

## Development
1. Make sure you have [Poetry](https://python-poetry.org/) installed
2. Run the code locally using `make dev` or `poetry run python -m enphase_to_mqtt.app`
3. Start the mock API server using `docker-compose up -d mock-server`
3. Run tests using `poetry run pytest`
