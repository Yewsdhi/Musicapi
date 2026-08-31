import asyncio
import time


class MemoryCache:
    def __init__(self):
        self._data: dict[str, tuple[object, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str):
        async with self._lock:
            item = self._data.get(key)

            if item is None:
                return None

            value, expires_at = item

            if expires_at <= time.monotonic():
                self._data.pop(key, None)
                return None

            return value

    async def set(self, key: str, value, ttl: int):
        async with self._lock:
            self._data[key] = (
                value,
                time.monotonic() + max(1, ttl),
            )


cache = MemoryCache()
