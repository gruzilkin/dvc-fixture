import collections
import contextlib

from fastapi import FastAPI, Response
from pydantic import BaseModel

from app.cloudflare import CloudflareClient
from app.config import Settings
from app.dns_worker import DnsWorker


class DvcRequest(BaseModel):
    dvc: str


settings = Settings()
http_codes: collections.deque[str] = collections.deque(maxlen=settings.http_queue_size)
cf_client = CloudflareClient(settings)
dns_worker = DnsWorker(cf_client)


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    dns_worker.start()
    yield
    await dns_worker.stop()
    await cf_client.close()


app = FastAPI(title="DVC Fixture", lifespan=lifespan)


@app.post("/dvc/http", status_code=204)
async def add_http_dvc(req: DvcRequest):
    http_codes.append(req.dvc)


@app.get(settings.well_known_path)
async def serve_well_known():
    content = "\n".join(http_codes)
    return Response(content=content, media_type="text/plain")


@app.post("/dvc/dns", status_code=204)
async def add_dns_dvc(req: DvcRequest):
    await dns_worker.submit(req.dvc)
