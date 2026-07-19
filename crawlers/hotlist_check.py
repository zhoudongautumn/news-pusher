﻿"""热搜爬虫 — 六大国内源 + 丰富原文"""

import httpx, re, json
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler, NewsItem


class HotlistCrawler(BaseCrawler):
    name = "hotlist"

    def __init__(self, sources: list, per_source: int = 10):
        self.sources = sources
        self.per_source = per_source
        self._h = {
            "zhihu": self._zhihu, "cls": self._cls, "baidu": self._baidu,
            "sina": self._sina, "eastmoney": self._eastmoney, "thepaper": self._thepaper,
        }

    async def fetch(self) -> list[NewsItem]:
        items = []
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as cli:
            for name, cat in self.sources:
                h = self._h.get(name)
                if not h: continue
                try:
                    r = await h(cli)
                    for it in r: it.category = cat
                    items.extend(r)
                    print(f"  [Hotlist/{name}] {len(r)} 条")
                except Exception as e:
                    print(f"  [Hotlist/{name}] 失败: {e}")
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
                summary=f"知乎热度 {e.get('detail_text','')} | {t.get('excerpt','')}", source="知乎热榜",
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
                summary=c[:500], source="财联社",
                published=datetime.fromtimestamp(ct) if ct else None,
            ))
        return items

    async def _baidu(self, cli):
        url = "https://top.baidu.com/board?tab=realtime"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0"})
        html = r.text
        items = []
        words = re.findall(r'"word":"([^"]+)"', html)
        descs = re.findall(r'"desc":"([^"]*)"', html)
        queries = re.findall(r'"query":"([^"]+)"', html)
        for i, word in enumerate(words[:self.per_source]):
            q = queries[i] if i < len(queries) else word
            d = descs[i] if i < len(descs) else ""
            items.append(NewsItem(
                title=word, url=f"https://www.baidu.com/s?wd={quote(q)}",
                summary=f"百度热搜 | {d}", source="百度热搜",
            ))
        return items

    async def _sina(self, cli):
        url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=20"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://news.sina.com.cn/"})
        data = r.json()
        items = []
        for e in data.get("result", {}).get("data", [])[:self.per_source]:
            items.append(NewsItem(
                title=e.get("title", ""), url=e.get("url", ""),
                summary=e.get("intro", "")[:500], source="新浪新闻",
            ))
        return items

    async def _eastmoney(self, cli):
        url = "https://np-listapi.eastmoney.com/comm/web/getNewsList?client=web&biz=news_001&page=1&size=20"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.eastmoney.com/"})
        data = r.json()
        items = []
        news_list = data.get("result", [])
        for e in news_list[:self.per_source]:
            items.append(NewsItem(
                title=e.get("title", ""),
                url=f"https://finance.eastmoney.com/a/{e.get('code','')}.html",
                summary=e.get("digest", "")[:500], source="东方财富",
            ))
        return items

    async def _thepaper(self, cli):
        url = "https://www.thepaper.cn/contentapi/cont/list/contentList?pageidx=1&size=20"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.thepaper.cn/"})
        data = r.json()
        items = []
        for e in data.get("data", {}).get("list", [])[:self.per_source]:
            items.append(NewsItem(
                title=e.get("name", ""),
                url=f"https://www.thepaper.cn/newsDetail_forward_{e.get('contId','')}",
                summary=e.get("abstract", "")[:500], source="澎湃新闻",
            ))
        return items

