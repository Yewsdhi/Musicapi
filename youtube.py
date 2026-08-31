import asyncio
import yt_dlp


def _search_sync(query: str, limit: int):
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        data = ydl.extract_info(
            f"ytsearch{limit}:{query}",
            download=False,
        )

    results = []

    for item in data.get("entries") or []:
        if not item:
            continue

        video_id = item.get("id")

        if not video_id:
            continue

        results.append(
            {
                "id": video_id,
                "title": item.get("title"),
                "url": item.get("webpage_url")
                or f"https://www.youtube.com/watch?v={video_id}",
                "duration": item.get("duration"),
                "thumbnail": item.get("thumbnail"),
                "channel": item.get("channel")
                or item.get("uploader"),
            }
        )

    return results


async def search_youtube(query: str, limit: int = 5):
    return await asyncio.to_thread(_search_sync, query, limit)


def _details_sync(url: str):
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "url": info.get("webpage_url") or url,
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "channel": info.get("channel")
        or info.get("uploader"),
        "uploader": info.get("uploader"),
        "view_count": info.get("view_count"),
        "upload_date": info.get("upload_date"),
    }


async def get_details(url: str):
    return await asyncio.to_thread(_details_sync, url)
