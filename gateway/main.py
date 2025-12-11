from fastapi import FastAPI, Request, HTTPException
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Gateway")

AUTH_SERVICE_URL = "http://127.0.0.1:8001"
APP_SERVICE_URL = "http://127.0.0.1:8000"
LOG_SERVICE_URL = "http://127.0.0.1:8002"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    if service == "auth":
        url = f"{AUTH_SERVICE_URL}/{path}"
    elif service == "app_service":
        url = f"{APP_SERVICE_URL}/{path}"
    elif service == "logs":
        url = f"{LOG_SERVICE_URL}/{path}"
    else:
        raise HTTPException(status_code=404, detail="Nieznany serwis")

    body = await request.body()
    headers = dict(request.headers)

    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            url,
            content=body,
            headers=headers,
            params=request.query_params
        )
    return response.json()
