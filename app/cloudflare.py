from datetime import datetime

import httpx
from pydantic import BaseModel

from app.config import Settings

BASE_URL = "https://api.cloudflare.com/client/v4"


class DnsRecord(BaseModel):
    id: str
    type: str
    name: str
    content: str
    ttl: int
    created_on: datetime
    modified_on: datetime


class DnsRecordListResponse(BaseModel):
    result: list[DnsRecord]
    success: bool


class DnsRecordResponse(BaseModel):
    result: DnsRecord
    success: bool


class CloudflareClient:
    def __init__(self, settings: Settings) -> None:
        self._zone_id = settings.cloudflare_zone_id
        self._record_name = settings.dns_record_name
        self._ttl = 60
        self._max_records = settings.dns_max_records
        self._http = httpx.AsyncClient(
            base_url=f"{BASE_URL}/zones/{self._zone_id}",
            headers={"Authorization": f"Bearer {settings.cloudflare_api_token}"},
            timeout=30,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def list_txt_records(self) -> list[DnsRecord]:
        resp = await self._http.get(
            "/dns_records",
            params={"name": self._record_name, "type": "TXT"},
        )
        resp.raise_for_status()
        parsed = DnsRecordListResponse.model_validate(resp.json())
        return sorted(parsed.result, key=lambda r: r.created_on, reverse=True)

    async def create_txt_record(self, content: str) -> DnsRecord:
        resp = await self._http.post(
            "/dns_records",
            json={
                "type": "TXT",
                "name": self._record_name,
                "content": content,
                "ttl": self._ttl,
            },
        )
        resp.raise_for_status()
        return DnsRecordResponse.model_validate(resp.json()).result

    async def delete_record(self, record_id: str) -> None:
        resp = await self._http.delete(f"/dns_records/{record_id}")
        resp.raise_for_status()

    async def add_dvc(self, dvc: str) -> DnsRecord:
        result = await self.create_txt_record(dvc)
        records = await self.list_txt_records()
        for record in records[self._max_records:]:
            await self.delete_record(record.id)
        return result
