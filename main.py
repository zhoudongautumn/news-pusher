"""新闻推送主入口 — 抓取 → 推送"""

import asyncio
import os
import sys
from datetime import datetime
import pytz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from crawlers.rss import RSSCrawler
from crawlers.base import NewsItem
from pushers.feishu import FeishuPusher


async def fetch_all() -> list[NewsItem]:
    tasks = []
    if config.ENABLE_RSS:
        tasks.append(RSSCrawler(config.RSS_FEEDS, config.MAX_NEWS_PER_SOURCE).fetch())
    if not tasks:
        print("[Main] 未启用任何数据源")
        return []
    results = await asyncio.gather(*tasks)
    all_items = []
    for items in results:
        all_items.extend(items)
    return all_items


async def main():
    print("=" * 50)
    print(f"📰 新闻推送启动 — {datetime.now(pytz.timezone(config.TIMEZONE))}")
    print("=" * 50)

    print("🌐 正在抓取新闻...")
    items = await fetch_all()
    print(f"   共获取 {len(items)} 条新闻")
    if not items:
        print("⚠️  没有获取到新闻")
        return

    seen = set()
    unique_items = []
    for it in items:
        key = (it.title, it.url)
        if key not in seen:
            seen.add(key)
            unique_items.append(it)
    items = unique_items
    print(f"   去重后 {len(items)} 条")

    print("\n📋 今日新闻预览:")
    for i, it in enumerate(items, 1):
        print(f"  {i}. [{it.source}] {it.title}")
    print()

    print("📤 正在推送到飞书...")
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    title = f"📰 新闻早报 — {now.strftime('%Y-%m-%d %A')}"
    await FeishuPusher(config.FEISHU_WEBHOOK).push(items, title)
    print("✅ 推送完成")


if __name__ == "__main__":
    asyncio.run(main())
