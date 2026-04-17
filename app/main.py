import asyncio
import collections
import contextlib

from fastapi import FastAPI, Response
from pydantic import BaseModel

from app.cloudflare import CloudflareClient
from app.config import Settings


class DvcRequest(BaseModel):
    dvc: str


class DnsDvcRequest(BaseModel):
    dvc: str
    fqdn: str


class EmailRequest(BaseModel):
    email: str


def quote(content: str) -> str:
    return content if content.startswith('"') and content.endswith('"') else f'"{content}"'


settings = Settings()
http_codes: collections.deque[str] = collections.deque(maxlen=settings.http_queue_size)
cf_client = CloudflareClient(settings)
dns_lock = asyncio.Lock()


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await cf_client.close()


app = FastAPI(title="DVC Fixture", lifespan=lifespan)


@app.post("/dvc/http", status_code=204)
async def add_http_dvc(req: DvcRequest):
    http_codes.append(req.dvc)


@app.get(settings.well_known_path)
async def serve_well_known():
    content = "\n".join(http_codes)
    return Response(content=content, media_type="text/plain")


@app.delete("/dvc/http", status_code=204)
async def remove_http_dvc(req: DvcRequest):
    try:
        http_codes.remove(req.dvc)
    except ValueError:
        pass


@app.post("/dvc/dns", status_code=204)
async def add_dns_dvc(req: DnsDvcRequest):
    async with dns_lock:
        await cf_client.add_dvc(quote(req.dvc), req.fqdn)


@app.delete("/dvc/dns", status_code=204)
async def remove_dns_dvc(req: DnsDvcRequest):
    async with dns_lock:
        await cf_client.remove_dvc(quote(req.dvc), req.fqdn)


@app.post("/dvc/email", status_code=204)
async def add_contactemail(req: EmailRequest):
    async with dns_lock:
        await cf_client.add_contactemail(quote(req.email))


@app.delete("/dvc/email", status_code=204)
async def remove_contactemail(req: EmailRequest):
    async with dns_lock:
        await cf_client.remove_contactemail(quote(req.email))
