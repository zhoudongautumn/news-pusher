"""热搜爬虫 — 知乎/财联社，带分类"""

import httpx, re
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler, NewsItem


class HotlistCrawler(BaseCrawler):
    name = "hotlist"

    def __init__(self, sources: list, per_source: int = 10):
        """sources: [(name, category), ...]"""
        self.sources = sources
        self.per_source = per_source
        self._h = {
            "zhihu": self._zhihu,
            "cls": self._cls,
        }

    async def fetch(self) -> list[NewsItem]:
        items = []
        async with httpx.AsyncClient(timeout=15) as cli:
            for name, cat in self.sources:
                h = self._h.get(name)
                if not h: continue
                try:
                    r = await h(cli)
                    for it in r:
                        it.category = cat
                    items.extend(r)
                except Exception as e:
                    print(f"[Hotlist/{name}] fail: {e}")
        return items

    async def _zhihu(self, cli):
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        items = []
        for e in data.get("data", [])[:self.per_source]:
            t = e.get("target", {})
            items.append(NewsItem(
                title=t.get("title", ""), url=t.get("url", ""),
                summary=f"热度 {e.get('detail_text','')}", source="知乎热榜",
            ))
        return items

    async def _cls(self, cli):
        url = "https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.cls.cn/"})
        data = r.json()
        items = []
        entries = data.get("data", {}).get("roll_data", []) or data.get("data", [])
        if not isinstance(entries, list): entries = []
        for e in entries[:self.per_source]:
            t = e.get("title", "") or e.get("brief", "")
            c = e.get("content", "") or e.get("brief", "")
            ct = e.get("ctime", 0)
            items.append(NewsItem(
                title=t, url=f"https://www.cls.cn/detail/{e.get('id','')}",
                summary=c[:300], source="财联社",
                published=datetime.fromtimestamp(ct) if ct else None,
            ))
        return items
