import httpx

from app.config import settings


async def get_lyrics(query: str):
    # Optional authorized lyrics provider.
    # Configure LYRICS_URL in Heroku Config Vars.
    if not settings.lyrics_url:
        return None

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0)
        ) as client:
            response = await client.get(
                settings.lyrics_url,
                params={"q": query},
            )
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict):
                return data.get("lyrics")

    except Exception:
        return None

    return None
