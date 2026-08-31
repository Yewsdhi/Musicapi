from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.cache import cache
from app.youtube import search_youtube, get_details
from app.lyrics import get_lyrics

app = FastAPI(
    title="Fast Music API",
    version="3.0.0",
    description="FastAPI backend for a Telegram music bot.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: str | None) -> None:
    # Authentication is enabled automatically when API_KEYS is configured.
    if settings.api_keys and x_api_key not in settings.api_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )


@app.get("/")
async def root():
    return {
        "status": True,
        "service": "Fast Music API",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health():
    return {"status": True, "service": "online"}


@app.get("/api/search")
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(5, ge=1, le=20),
    x_api_key: str | None = Header(default=None),
):
    require_api_key(x_api_key)

    cache_key = f"search:{q.strip().lower()}:{limit}"
    cached = await cache.get(cache_key)

    if cached is not None:
        return {
            "status": True,
            "cached": True,
            "query": q,
            "results": cached,
        }

    try:
        results = await search_youtube(q.strip(), limit)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Search provider error: {type(exc).__name__}",
        )

    await cache.set(cache_key, results, settings.cache_ttl)

    return {
        "status": True,
        "cached": False,
        "query": q,
        "results": results,
    }


@app.get("/api/details")
async def details(
    url: str = Query(..., min_length=1, max_length=2000),
    x_api_key: str | None = Header(default=None),
):
    require_api_key(x_api_key)

    cache_key = f"details:{url}"
    cached = await cache.get(cache_key)

    if cached is not None:
        return {"status": True, "cached": True, "result": cached}

    try:
        result = await get_details(url)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read video metadata: {type(exc).__name__}",
        )

    await cache.set(cache_key, result, settings.cache_ttl)

    return {
        "status": True,
        "cached": False,
        "result": result,
    }


@app.get("/api/lyrics")
async def lyrics(
    q: str = Query(..., min_length=1, max_length=200),
    x_api_key: str | None = Header(default=None),
):
    require_api_key(x_api_key)

    result = await get_lyrics(q.strip())

    return {
        "status": True,
        "query": q,
        "lyrics": result,
    }
