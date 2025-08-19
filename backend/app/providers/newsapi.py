from __future__ import annotations
import httpx
from typing import List, Dict
from ..config import settings

BASE = "https://newsapi.org/v2/everything"

async def company_news(query: str, page_size: int = 20) -> List[Dict]:
    if not settings.newsapi_key:
        return []
    params = {"q": query, "language": "en", "pageSize": page_size, "sortBy": "publishedAt", "apiKey": settings.newsapi_key}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(BASE, params=params)
        r.raise_for_status()
        data = r.json().get("articles", [])
    return data
