"""RSS 爬虫 — 支持标准 RSS/Atom 源"""

import asyncio
import feedparser
from datetime import datetime
from typing import Optional

from .base import BaseCrawler, NewsItem


class RSSCrawler(BaseCrawler):
    name = "rss"

    def __init__(self, feed_urls: list[str], max_items: int = 10):
        self.feed_urls = feed_urls
        self.max_items = max_items

    async def fetch(self) -> list[NewsItem]:
        items: list[NewsItem] = []
        for url in self.feed_urls:
            try:
                feed = await asyncio.to_thread(feedparser.parse, url)
                source_name = feed.feed.get("title", url)
                for entry in feed.entries[:self.max_items]:
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    summary = (entry.get("summary", "") or "")[:200]
                    items.append(NewsItem(
                        title=entry.get("title", "(无标题)"),
                        url=entry.get("link", ""),
                        summary=summary,
                        source=f"RSS/{source_name}",
                        published=published,
                    ))
            except Exception as e:
                print(f"[RSS] 抓取失败 {url}: {e}")
        return items

