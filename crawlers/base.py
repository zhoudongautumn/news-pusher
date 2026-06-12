from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class NewsItem:
    title: str
    url: str
    summary: str = ""
    source: str = ""
    published: Optional[datetime] = None
    category: str = "国内综合"
    extra: dict = field(default_factory=dict)


class BaseCrawler:
    name = "base"
    async def fetch(self) -> list[NewsItem]:
        raise NotImplementedError
