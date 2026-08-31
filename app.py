import os
import secrets
import time
from functools import wraps

import yt_dlp
from flask import Flask, jsonify, request

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "").strip()
CACHE_TTL = max(0, int(os.environ.get("CACHE_TTL", "300")))
MAX_RESULTS = min(max(int(os.environ.get("MAX_RESULTS", "8")), 1), 20)
_cache = {}

def require_api_key(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not API_KEY:
            return jsonify({"status": False, "error": "API_KEY is not configured"}), 503
        supplied = request.headers.get("X-API-Key", "").strip()
        if not supplied or not secrets.compare_digest(supplied, API_KEY):
            return jsonify({"status": False, "error": "Invalid API key"}), 401
        return fn(*args, **kwargs)
    return wrapped

def cache_get(key):
    item = _cache.get(key)
    if item and (CACHE_TTL == 0 or time.time() - item["time"] < CACHE_TTL):
        return item["value"]
    _cache.pop(key, None)
    return None

def cache_put(key, value):
    if CACHE_TTL == 0:
        return
    _cache[key] = {"time": time.time(), "value": value}
    if len(_cache) > 500:
        oldest = min(_cache, key=lambda k: _cache[k]["time"])
        _cache.pop(oldest, None)

def youtube_options(flat=False):
    return {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "extract_flat": flat,
    }

def search_youtube(query, limit):
    key=f"search:{query}:{limit}"
    hit=cache_get(key)
    if hit is not None:
        return hit
    with yt_dlp.YoutubeDL(youtube_options(flat=True)) as ydl:
        data=ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
    results=[]
    for item in data.get("entries") or []:
        if not item:
            continue
        vid=item.get("id")
        results.append({
            "id": vid,
            "title": item.get("title"),
            "url": item.get("webpage_url") or (f"https://www.youtube.com/watch?v={vid}" if vid else None),
            "duration": item.get("duration"),
            "channel": item.get("channel") or item.get("uploader"),
            "thumbnail": item.get("thumbnail"),
        })
    cache_put(key, results)
    return results

def info_youtube(value):
    value=value.strip()
    url=value if value.startswith(("http://","https://")) else f"https://www.youtube.com/watch?v={value}"
    key=f"info:{url}"
    hit=cache_get(key)
    if hit is not None:
        return hit
    with yt_dlp.YoutubeDL(youtube_options(flat=False)) as ydl:
        item=ydl.extract_info(url, download=False)
    result={
        "id": item.get("id"),
        "title": item.get("title"),
        "url": item.get("webpage_url") or url,
        "duration": item.get("duration"),
        "channel": item.get("channel") or item.get("uploader"),
        "channel_id": item.get("channel_id"),
        "thumbnail": item.get("thumbnail"),
        "description": item.get("description"),
        "view_count": item.get("view_count"),
        "upload_date": item.get("upload_date"),
        "live": bool(item.get("is_live")),
    }
    cache_put(key, result)
    return result

@app.get("/")
def index():
    return jsonify({
        "status": True,
        "name": "Custom Music API",
        "version": "1.0.1",
        "service": "online",
        "endpoints": ["/", "/api/health", "/api/search", "/api/info"]
    })

@app.get("/api/health")
def health():
    return jsonify({"status": True, "service": "online"})

@app.get("/api/search")
@require_api_key
def search():
    q=request.args.get("q","").strip()
    if not q:
        return jsonify({"status":False,"error":"Missing q"}),400
    try:
        limit=min(max(int(request.args.get("limit",MAX_RESULTS)),1),20)
        results=search_youtube(q,limit)
        return jsonify({"status":True,"query":q,"count":len(results),"results":results})
    except Exception as e:
        app.logger.exception("search error")
        return jsonify({"status":False,"error":str(e)}),502

@app.get("/api/info")
@require_api_key
def info():
    value=(request.args.get("url") or request.args.get("id") or "").strip()
    if not value:
        return jsonify({"status":False,"error":"Missing url or id"}),400
    try:
        return jsonify({"status":True,"result":info_youtube(value)})
    except Exception as e:
        app.logger.exception("info error")
        return jsonify({"status":False,"error":str(e)}),502

if __name__=="__main__":
    port=int(os.environ.get("PORT","5000"))
    app.run(host="0.0.0.0",port=port)
