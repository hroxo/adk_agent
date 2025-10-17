import asyncio
import os
from functools import lru_cache
from pathlib import Path

from firebase_functions import https_fn
from firebase_functions.options import set_global_options

# Carrega .env apenas em desenvolvimento (caso exista)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / "adk" / "totem_fashion" / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except Exception:
    pass

# Limita instâncias paralelas
set_global_options(max_instances=10)

DEFAULT_MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-pro")

def _build_scope(req: https_fn.Request) -> dict:
    headers = [(k.lower().encode(), v.encode()) for k, v in req.headers.items()]
    qs = (
        req.query_string
        if isinstance(req.query_string, (bytes, bytearray))
        else (req.query_string or "").encode()
    )
    return {
        "type": "http",
        "http_version": "1.1",
        "method": req.method,
        "path": req.path,
        "raw_path": req.path.encode(),
        "query_string": qs,
        "headers": headers,
        "scheme": "https",
        "server": ("functions", 443),
        "client": ("", 0),
    }

async def _run_asgi(app, scope, body: bytes) -> tuple[int, list[tuple[bytes, bytes]], bytes]:
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}
    status, headers, chunks = 200, [], bytearray()
    async def send(message):
        nonlocal status, headers, chunks
        if message["type"] == "http.response.start":
            status = message.get("status", 200)
            headers = message.get("headers", [])
        elif message["type"] == "http.response.body":
            chunks.extend(message.get("body", b""))
    await app(scope, receive, send)
    return status, headers, bytes(chunks)

# Lazy singletons para evitar timeouts no import
@lru_cache(maxsize=1)
def get_fastapi_app():
    from adk.totem_fashion.api.app import app as fastapi_app
    return fastapi_app

@lru_cache(maxsize=1)
def get_adk_app():
    from adk.totem_fashion.adk_fashion_agent import create_stylist_agent  # noqa: WPS433
    from google.adk.agent_engines import AdkApp  # IMPORTA O AdkApp do google.adk
    agent = create_stylist_agent()
    return AdkApp(agent=agent)

@https_fn.on_request()
def totem_api(req: https_fn.Request) -> https_fn.Response:
    scope = _build_scope(req)
    body = req.get_data() or b""
    fastapi_app = get_fastapi_app()
    status, headers, payload = asyncio.run(_run_asgi(fastapi_app, scope, body))
    hdrs = {k.decode(): v.decode() for k, v in headers}
    return https_fn.Response(response=payload, status=status, headers=hdrs)

@https_fn.on_request()
def adk_webhook(req: https_fn.Request) -> https_fn.Response:
    scope = _build_scope(req)
    body = req.get_data() or b""
    adk_app = get_adk_app()
    status, headers, payload = asyncio.run(_run_asgi(adk_app, scope, body))
    hdrs = {k.decode(): v.decode() for k, v in headers}
    return https_fn.Response(response=payload, status=status, headers=hdrs)

