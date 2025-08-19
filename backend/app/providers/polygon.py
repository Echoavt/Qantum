from __future__ import annotations
import httpx
from datetime import datetime, timezone
from typing import List, Dict
from ..config import settings

BASE = "https://api.polygon.io"

async def minute_bars(symbol: str, start: datetime, end: datetime) -> List[Dict]:
    if not settings.polygon_api_key:
        return []
    url = f"{BASE}/v2/aggs/ticker/{symbol}/range/1/minute/{start.date()}/{end.date()}"
    params = {"adjusted": "true", "sort": "asc", "apiKey": settings.polygon_api_key, "limit": 50000}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json().get("results", [])
    out = []
    for d in data:
        ts = datetime.fromtimestamp(d["t"]/1000, tz=timezone.utc)
        out.append({"ts": ts, "open": d["o"], "high": d["h"], "low": d["l"], "close": d["c"], "volume": d.get("v", 0)})
    return out
