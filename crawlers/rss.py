"""RSS 爬虫 — 48h 过滤 + 逐源日志"""

import asyncio, feedparser, html as _html, re
from datetime import datetime, timedelta, timezone
from .base import BaseCrawler, NewsItem


def _clean(text: str) -> str:
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = _html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


class RSSCrawler(BaseCrawler):
    name = "rss"

    def __init__(self, feeds: list, per_source: int = 10):
        self.feeds = feeds
        self.per_source = per_source

    async def fetch(self) -> list[NewsItem]:
        items = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
        for url, cat in self.feeds:
            try:
                feed = await asyncio.to_thread(feedparser.parse, url)
                src = feed.feed.get("title", url)
                count = 0
                total = len(feed.entries)
                for entry in feed.entries:
                    if count >= self.per_source: break
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    if published and published < cutoff: continue
                    raw = ""
                    if hasattr(entry, "content") and entry.content:
                        raw = entry.content[0].get("value", "")
                    if not raw: raw = entry.get("description", "")
                    if not raw: raw = entry.get("summary", "")
                    raw = _clean(raw)[:600]
                    items.append(NewsItem(
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        summary=raw, source=f"RSS/{src}",
                        published=published, category=cat,
                    ))
                    count += 1
                print(f"  [RSS] {src[:40]:40s} total={total:<3d} added={count}")
            except Exception as e:
                print(f"  [RSS] 失败 {url}: {e}")
        return items
