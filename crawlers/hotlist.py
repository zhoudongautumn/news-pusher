"""热搜爬虫 — 知乎 / 微博 / 百度热搜"""

import httpx
import re
from urllib.parse import quote
from datetime import datetime

from .base import BaseCrawler, NewsItem


class HotlistCrawler(BaseCrawler):
    name = "hotlist"

    def __init__(self, sources: list[str], max_items: int = 10):
        self.sources = sources
        self.max_items = max_items
        self._handlers = {
            "zhihu": self._zhihu,
            "weibo": self._weibo,
            "baidu": self._baidu,
        }

    async def fetch(self) -> list[NewsItem]:
        items: list[NewsItem] = []
        async with httpx.AsyncClient(timeout=15) as client:
            for src in self.sources:
                handler = self._handlers.get(src)
                if not handler:
                    continue
                try:
                    result = await handler(client)
                    items.extend(result)
                except Exception as e:
                    print(f"[Hotlist/{src}] 抓取失败: {e}")
        return items

    async def _zhihu(self, client: httpx.AsyncClient) -> list[NewsItem]:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = await client.get(url, headers=headers)
        data = resp.json()
        items = []
        for entry in data.get("data", [])[:self.max_items]:
            target = entry.get("target", {})
            items.append(NewsItem(
                title=target.get("title", ""),
                url=target.get("url", ""),
                summary=f"热度 #{(entry.get('detail_text', ''))}",
                source="知乎热榜",
            ))
        return items

    async def _weibo(self, client: httpx.AsyncClient) -> list[NewsItem]:
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://weibo.com/",
        }
        resp = await client.get(url, headers=headers)
        data = resp.json()
        items = []
        for entry in data.get("data", {}).get("realtime", [])[:self.max_items]:
            word = entry.get("word", "")
            items.append(NewsItem(
                title=word,
                url=f"https://s.weibo.com/weibo?q={quote(word)}",
                summary=f"热度: {entry.get('raw_hot', 'N/A')}",
                source="微博热搜",
            ))
        return items

    async def _baidu(self, client: httpx.AsyncClient) -> list[NewsItem]:
        url = "https://top.baidu.com/board?tab=realtime"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = await client.get(url, headers=headers)
        html = resp.text
        items = []
        words = re.findall(r'"word":"([^"]+)"', html)
        queries = re.findall(r'"query":"([^"]+)"', html)
        for i, word in enumerate(words[:self.max_items]):
            q = queries[i] if i < len(queries) else word
            items.append(NewsItem(
                title=word,
                url=f"https://www.baidu.com/s?wd={quote(q)}",
                source="百度热搜",
            ))
        return items
