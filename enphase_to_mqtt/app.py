import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable

import httpx
import jwt
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()


class Config:
    ENPHASE_HOST: str = os.getenv("ENPHASE_HOST", "")
    ENPHASE_USERNAME: str = os.getenv("ENPHASE_USERNAME", "")
    ENPHASE_PASSWORD: str = os.getenv("ENPHASE_PASSWORD", "")
    SERIAL_NUMBER: str = os.getenv("SERIAL_NUMBER", "")
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "")
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", 1883))
    MQTT_TOPIC: str = os.getenv("MQTT_TOPIC", "")
    LOG_LEVEL: str = ""
    INTERVAL: int = int(os.getenv("INTERVAL", 60))


class Endpoints:
    WEB_AUTH_URL = "https://enlighten.enphaseenergy.com/login/login"
    WEB_TOKEN_URL = f"https://enlighten.enphaseenergy.com/entrez-auth-token?serial_num={Config.SERIAL_NUMBER}"
    LOCAL_AUTH_URL = f"https://{Config.ENPHASE_HOST}/auth/check_jwt"
    LOCAL_DATA_URL_PRODUCTION = f"https://{Config.ENPHASE_HOST}/api/v1/production"
    LOCAL_DATA_URL_INVERTERS = f"https://{Config.ENPHASE_HOST}/api/v1/production/inverters"


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.DEBUG if Config.LOG_LEVEL == "DEBUG" else logging.INFO,
)


mqtt_client = mqtt.Client()
try:
    if Config.MQTT_USERNAME:
        mqtt_client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
    mqtt_client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as err:
    logging.error("Unable to connect to MQTT broker")
    sys.exit()


class Token:
    def __init__(self):
        self.value: str = ""

    @property
    def is_valid(self):
        try:
            jwt.decode(self.value, options={"verify_signature": False})
            return True
        except Exception:
            return False

    @property
    def needs_renewal(self):
        try:
            payload: dict[str, Any] = jwt.decode(self.value, options={"verify_signature": False})
            exp: datetime = datetime.fromtimestamp(int(payload["exp"]))
            return datetime.now() > exp - timedelta(days=30)
        except Exception:
            return True


token = Token()


async def retrieve_token() -> Token | None:
    global token

    try:
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                Endpoints.WEB_AUTH_URL,
                data={
                    "user[email]": Config.ENPHASE_USERNAME,
                    "user[password]": Config.ENPHASE_PASSWORD,
                },
            )
            token_response = await client.get(Endpoints.WEB_TOKEN_URL, cookies=auth_response.cookies)
            token.value = token_response.json().get("token")
            logging.info("Token successfully retrieved")
            return token
    except Exception as err:
        logging.error(f"Unable to retrieve token: {str(err) or err.__class__.__name__}")


async def retrieve_data() -> dict | None:
    global token

    if not token.is_valid or token.needs_renewal:
        if not token.is_valid:
            logging.info("Token is invalid, fetching new token")
        else:
            logging.info("Token needs to be renewed, fetching new token")
        asyncio.create_task(retrieve_token())
    else:
        local_data_urls = {
            "production": Endpoints.LOCAL_DATA_URL_PRODUCTION,
            "inverters": Endpoints.LOCAL_DATA_URL_INVERTERS,
        }
        async with httpx.AsyncClient(verify=False) as client:
            local_auth_response = await client.get(
                Endpoints.LOCAL_AUTH_URL,
                headers={"Authorization": f"Bearer {token.value}"},
            )

            responses = await asyncio.gather(
                *[client.get(url, cookies=local_auth_response.cookies) for (source, url) in local_data_urls.items()]
            )
            production = {
                source: responses[index].json() for index, (source, url) in enumerate(local_data_urls.items())
            }
            logging.info("Enphase production data successfully retrieved")
            await publish_output(production)
            return production


async def publish_output(data):
    try:
        result = mqtt_client.publish(
            Config.MQTT_TOPIC,
            payload=json.dumps(data),
            retain=True,
        )
        if result.rc == 0:
            logging.info("Data published on MQTT")
        else:
            logging.error(f"Data not published (return code {result.rc})")
        return data
    except Exception as err:
        logging.error(f"Unable to publish data on MQTT: {err}")


async def read_enphase():
    async def timeout(awaitable: Callable, timeout: float) -> Awaitable | None:
        try:
            return await asyncio.wait_for(awaitable(), timeout=timeout)
        except Exception as err:
            logging.error(f"Unable to read data from Enphase: {str(err) or err.__class__.__name__}")

    while True:
        logging.info("Read Enphase production data")
        await asyncio.gather(
            asyncio.sleep(Config.INTERVAL),
            timeout(retrieve_data, timeout=10),
        )


if __name__ == "__main__":
    asyncio.run(read_enphase())
