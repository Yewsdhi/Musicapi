import os


def _read_keys() -> set[str]:
    raw = os.getenv("API_KEYS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


class Settings:
    api_keys = _read_keys()
    cache_ttl = max(10, int(os.getenv("CACHE_TTL", "300")))
    lyrics_url = os.getenv("LYRICS_URL", "").strip()


settings = Settings()
