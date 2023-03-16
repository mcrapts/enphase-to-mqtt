from fastapi import Cookie, FastAPI, Request, Response, status

app = FastAPI()


FAKE_WEB_SESSION_VALUE_SUCCESS = "fake-web-session-value-success"
FAKE_WEB_SESSION_VALUE_FAILED = "fake-web-session-value-failed"
FAKE_LOCAL_SESSION_VALUE = "fake-local-session-value"
FAKE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiIxMjIyNDgwMDc1NTYiLCJpc3MiOiJFbnRyZXoiLCJlbnBoYXNlVXNlciI6Im93bmVyIiwiZXhwIjoxNzEwNDQyODIwLCJpYXQiOjE2Nzg5MDY4MjAsImp0aSI6IjEzMDQ4ODA5LWMyMTEtNGI0ZS05Y2Q3LTNkOTIwYjIyMDYyMSIsInVzZXJuYW1lIjoidXNlckBlbWFpbC5jb20ifQ.8xtMYUjVA0A9kXpJcdlovL2zzcezXNN33rmLUab6izw"


@app.post("/web/auth_url_success")
def web_auth_success(response: Response):
    response.set_cookie(key="_enlighten_4_session", value=FAKE_WEB_SESSION_VALUE_SUCCESS)
    response.status_code = status.HTTP_302_FOUND
    return response


@app.post("/web/auth_url_failed")
def web_auth_failed(response: Response):
    response.set_cookie(key="_enlighten_4_session", value=FAKE_WEB_SESSION_VALUE_FAILED)
    response.status_code = status.HTTP_302_FOUND
    return response


@app.get("/web/token_url")
def get_token(request: Request):
    if request.cookies.get("_enlighten_4_session") == FAKE_WEB_SESSION_VALUE_SUCCESS:
        return {
            "generation_time": 1678899325,
            "token": FAKE_TOKEN,
            "expires_at": 1710435325,
        }
    else:
        return Response(status_code=status.HTTP_302_FOUND)


@app.get("/local/auth_url")
def local_auth(request: Request, response: Response):
    if request.headers.get("authorization", "") == f"Bearer {FAKE_TOKEN}":
        response.set_cookie(key="local_session_id", value=FAKE_LOCAL_SESSION_VALUE)
        return True


@app.get("/local/data/production")
def get_data_production(request: Request):
    if request.cookies.get("local_session_id") == FAKE_LOCAL_SESSION_VALUE:
        return {
            "wattHoursToday": 16383,
            "wattHoursSevenDays": 1388,
            "wattHoursLifetime": 17768,
            "wattsNow": 338,
        }


@app.get("/local/data/inverters")
def get_data_inverters(request: Request):
    if request.cookies.get("local_session_id") == FAKE_LOCAL_SESSION_VALUE:
        return [
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
        ]
