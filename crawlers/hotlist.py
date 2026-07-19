"""热搜爬虫 — 六大国内源"""

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
            "zhihu": self._zhihu,
            "cls": self._cls,
            "baidu": self._baidu,
            "sina": self._sina,
            "eastmoney": self._eastmoney,
            "thepaper": self._thepaper,
        }

    async def fetch(self) -> list[NewsItem]:
        items = []
        async with httpx.AsyncClient(timeout=15) as cli:
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

    # === 知乎热榜 ===
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

    # === 财联社电报 ===
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

    # === 百度热搜 ===
    async def _baidu(self, cli):
        url = "https://top.baidu.com/board?tab=realtime"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0"})
        html = r.text
        items = []
        words = re.findall(r'"word":"([^"]+)"', html)
        queries = re.findall(r'"query":"([^"]+)"', html)
        for i, word in enumerate(words[:self.per_source]):
            q = queries[i] if i < len(queries) else word
            items.append(NewsItem(
                title=word, url=f"https://www.baidu.com/s?wd={quote(q)}",
                source="百度热搜",
            ))
        return items

    # === 新浪新闻热点 ===
    async def _sina(self, cli):
        url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=20"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://news.sina.com.cn/"})
        data = r.json()
        items = []
        for e in data.get("result", {}).get("data", [])[:self.per_source]:
            items.append(NewsItem(
                title=e.get("title", ""), url=e.get("url", ""),
                summary=e.get("intro", "")[:200], source="新浪新闻",
            ))
        return items

    # === 东方财富快讯 ===
    async def _eastmoney(self, cli):
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f3,f12,f14&secids=1.000001,0.399001"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0"})
        # 东方财富新闻 API
        url2 = "https://np-listapi.eastmoney.com/comm/web/getNewsList?client=web&biz=news_001&page=1&size=20"
        r2 = await cli.get(url2, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.eastmoney.com/"})
        try:
            data = r2.json()
            items = []
            news_list = data.get("result", [])
            for e in news_list[:self.per_source]:
                items.append(NewsItem(
                    title=e.get("title", ""),
                    url=f"https://finance.eastmoney.com/a/{e.get('code','')}.html",
                    summary=e.get("digest", "")[:200], source="东方财富",
                ))
            return items
        except:
            return []

    # === 澎湃新闻 ===
    async def _thepaper(self, cli):
        url = "https://www.thepaper.cn/contentapi/cont/list/contentList?pageidx=1&size=20"
        r = await cli.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.thepaper.cn/"})
        data = r.json()
        items = []
        for e in data.get("data", {}).get("list", [])[:self.per_source]:
            items.append(NewsItem(
                title=e.get("name", ""),
                url=f"https://www.thepaper.cn/newsDetail_forward_{e.get('contId','')}",
                summary=e.get("abstract", "")[:200], source="澎湃新闻",
            ))
        return items
