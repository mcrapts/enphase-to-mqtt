import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class Config:
    ENPHASE_HOST: str = os.getenv("ENPHASE_HOST", "")
    ENPHASE_USERNAME: str = os.getenv("ENPHASE_USERNAME", "")
    ENPHASE_PASSWORD: str = os.getenv("ENPHASE_PASSWORD", "")
    SERIAL_NUMBER: str = os.getenv("SERIAL_NUMBER", "")
    LOG_LEVEL: str = ""


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.DEBUG if Config.LOG_LEVEL == "DEBUG" else logging.INFO,
)


def retrieve_token() -> str | None:
    auth_url = "https://enlighten.enphaseenergy.com/login/login"
    token_url = f"https://enlighten.enphaseenergy.com/entrez-auth-token?serial_num={Config.SERIAL_NUMBER}"

    try:
        with httpx.Client() as client:
            auth_response = client.post(
                auth_url,
                data={
                    "user[email]": Config.ENPHASE_USERNAME,
                    "user[password]": Config.ENPHASE_PASSWORD,
                },
            )
            token_response = client.get(token_url, cookies=auth_response.cookies)
            token: str = token_response.json().get("token")
            logging.info("Token successfully retrieved")
            return token
    except Exception as e:
        logging.error(e)


def retrieve_data(token: str):
    local_auth_url = f"https://{Config.ENPHASE_HOST}/auth/check_jwt"
    local_production_url = f"https://{Config.ENPHASE_HOST}/production.json"
    with httpx.Client(verify=False) as client:
        local_auth_response = client.get(
            local_auth_url, headers={"Authorization": f"Bearer {token}"}
        )
        local_production_response = client.get(
            local_production_url, cookies=local_auth_response.cookies
        )
        production = local_production_response.json()
        logging.info("Enphase production data successfully retrieved")
        print(production)


token = retrieve_token()
if token:
    retrieve_data(token)
