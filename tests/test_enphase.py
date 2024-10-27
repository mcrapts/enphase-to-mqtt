import pytest
from freezegun import freeze_time

from enphase_to_mqtt.app import (
    Endpoints,
    Token,
    mqtt_client,
    retrieve_data,
    retrieve_token,
    token,
)
from enphase_to_mqtt.mock import FAKE_TOKEN

MOCK_API_BASE_URL = "http://localhost:8000"


def test_token_is_valid():
    token = Token()
    token.value = FAKE_TOKEN
    assert token.is_valid == True


@freeze_time("2024-02-01")
def test_token_does_not_need_renewal():
    token = Token()
    token.value = FAKE_TOKEN
    assert token.needs_renewal == False


@freeze_time("2024-03-01")
def test_token_needs_renewal():
    token = Token()
    token.value = FAKE_TOKEN
    assert token.needs_renewal == True


@pytest.mark.asyncio
async def test_retrieve_token_auth_success(monkeypatch):
    monkeypatch.setattr(Endpoints, "WEB_AUTH_URL", f"{MOCK_API_BASE_URL}/web/auth_url_success")
    monkeypatch.setattr(Endpoints, "WEB_TOKEN_URL", f"{MOCK_API_BASE_URL}/web/token_url")
    token = await retrieve_token()
    assert token is not None
    assert token.value == FAKE_TOKEN


@pytest.mark.asyncio
async def test_retrieve_token_auth_failed(monkeypatch):
    monkeypatch.setattr(Endpoints, "WEB_AUTH_URL", f"{MOCK_API_BASE_URL}/web/auth_url_failed")
    monkeypatch.setattr(Endpoints, "WEB_TOKEN_URL", f"{MOCK_API_BASE_URL}/web/token_url")
    token = await retrieve_token()
    assert token is None


@pytest.mark.asyncio
@freeze_time("2024-02-01")
async def test_retrieve_data(monkeypatch):
    def mock_publish():
        return None

    monkeypatch.setattr(Endpoints, "LOCAL_AUTH_URL", f"{MOCK_API_BASE_URL}/local/auth_url")
    monkeypatch.setattr(
        Endpoints,
        "LOCAL_DATA_URL_PRODUCTION",
        f"{MOCK_API_BASE_URL}/local/data/production",
    )
    monkeypatch.setattr(
        Endpoints,
        "LOCAL_DATA_URL_INVERTERS",
        f"{MOCK_API_BASE_URL}/local/data/inverters",
    )
    monkeypatch.setattr(token, "value", FAKE_TOKEN)
    monkeypatch.setattr(mqtt_client, "publish", mock_publish)

    data = await retrieve_data()

    assert data == {
        "production": {
            "wattHoursToday": 16383,
            "wattHoursSevenDays": 1388,
            "wattHoursLifetime": 17768,
            "wattsNow": 338,
        },
        "inverters": [
            {
                "serialNumber": "123456107150",
                "lastReportDate": 1678895492,
                "devType": 1,
                "lastReportWatts": 49,
                "maxReportWatts": 329,
            },
            {
                "serialNumber": "123456107296",
                "lastReportDate": 1678895493,
                "devType": 1,
                "lastReportWatts": 45,
                "maxReportWatts": 329,
            },
            {
                "serialNumber": "123456107299",
                "lastReportDate": 1678895494,
                "devType": 1,
                "lastReportWatts": 44,
                "maxReportWatts": 325,
            },
            {
                "serialNumber": "123456094001",
                "lastReportDate": 1678895522,
                "devType": 1,
                "lastReportWatts": 42,
                "maxReportWatts": 325,
            },
            {
                "serialNumber": "123456107057",
                "lastReportDate": 1678895523,
                "devType": 1,
                "lastReportWatts": 43,
                "maxReportWatts": 328,
            },
            {
                "serialNumber": "123456094415",
                "lastReportDate": 1678895496,
                "devType": 1,
                "lastReportWatts": 41,
                "maxReportWatts": 329,
            },
            {
                "serialNumber": "123456093415",
                "lastReportDate": 1678895497,
                "devType": 1,
                "lastReportWatts": 34,
                "maxReportWatts": 329,
            },
            {
                "serialNumber": "123456067783",
                "lastReportDate": 1678895552,
                "devType": 1,
                "lastReportWatts": 40,
                "maxReportWatts": 330,
            },
        ],
    }
