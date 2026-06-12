"""RSS 爬虫 — 提取完整描述供需 LLM 翻译概述"""

import asyncio
import feedparser
import html as _html
import re
from datetime import datetime

from .base import BaseCrawler, NewsItem


def _clean(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = _html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


class RSSCrawler(BaseCrawler):
    name = "rss"

    def __init__(self, feed_urls: list[str], max_items: int = 10):
        self.feed_urls = feed_urls
        self.max_items = max_items

    async def fetch(self) -> list[NewsItem]:
        items = []
        for url in self.feed_urls:
            try:
                feed = await asyncio.to_thread(feedparser.parse, url)
                source_name = feed.feed.get("title", url)
                for entry in feed.entries[:self.max_items]:
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    raw = ""
                    if hasattr(entry, "content") and entry.content:
                        raw = entry.content[0].get("value", "")
                    if not raw:
                        raw = entry.get("description", "")
                    if not raw:
                        raw = entry.get("summary", "")
                    raw = _clean(raw)[:800]
                    items.append(NewsItem(
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        summary=raw,
                        source=f"RSS/{source_name}",
                        published=published,
                    ))
            except Exception as e:
                print(f"[RSS] fail {url}: {e}")
        return items
