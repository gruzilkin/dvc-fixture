import asyncio

from app.cloudflare import CloudflareClient, DnsRecord


class DnsWorker:
    def __init__(self, client: CloudflareClient) -> None:
        self._client = client
        self._queue: asyncio.Queue[tuple[str, asyncio.Future[DnsRecord]]] = asyncio.Queue()
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def submit(self, dvc: str) -> DnsRecord:
        future: asyncio.Future[DnsRecord] = asyncio.get_event_loop().create_future()
        await self._queue.put((dvc, future))
        return await future

    async def _run(self) -> None:
        while True:
            dvc, future = await self._queue.get()
            try:
                result = await self._client.add_dvc(dvc)
                future.set_result(result)
            except Exception as exc:
                future.set_exception(exc)
            finally:
                self._queue.task_done()
