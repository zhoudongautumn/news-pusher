from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class NewsItem:
    """统一的新闻条目"""
    title: str
    url: str
    summary: str = ""
    source: str = ""
    published: Optional[datetime] = None
    extra: dict = field(default_factory=dict)

    def formatted(self, idx: int = 0) -> str:
        prefix = f"{idx}. " if idx else ""
        date_str = ""
        if self.published:
            date_str = self.published.strftime(" (%m-%d %H:%M)")
        s = f"{prefix}**{self.title}**{date_str}\n  {self.summary[:120]}…" if len(self.summary) > 120 else f"{prefix}**{self.title}**{date_str}\n  {self.summary}"
        if self.url:
            s += f"\n  🔗 {self.url}"
        return s


class BaseCrawler:
    """爬虫基类"""
    name = "base"

    async def fetch(self) -> list[NewsItem]:
        raise NotImplementedError
