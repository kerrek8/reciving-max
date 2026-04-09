import asyncio
import logging

from fastapi import FastAPI, Request, HTTPException

from app.worker import queue, worker
from app.config import WEBHOOK_SECRET

logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.on_event("startup")
async def startup():
    asyncio.create_task(worker())


@app.middleware("http")
async def limit_body(request: Request, call_next):
    if request.url.path == "/webhook":
        client_ip = request.client.host
        allowed_ips = {"89.169.144.17", "158.160.195.0", "158.160.47.204", "207.154.255.195"}
        if client_ip not in allowed_ips:
            raise HTTPException(status_code=403, detail="Unauthorized")
        auth = request.headers.get("Authorization")
        if auth != WEBHOOK_SECRET:
            logging.warning("Unauthorized request")
            raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.body()

    if len(body) > 1024 * 1024:  # 1MB
        raise HTTPException(status_code=413, detail="Payload too large")

    return await call_next(request)


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    logging.info("Webhook received")

    await queue.put(payload)

    return {"status": "ok"}

@app.get("/ping")
async def ping(request: Request):
    return {"ping": "pong"}