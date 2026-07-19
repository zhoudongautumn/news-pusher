"""新闻推送 — 按区域分别推送"""

import asyncio, os, sys
from datetime import datetime
import pytz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from crawlers.rss import RSSCrawler
from crawlers.hotlist import HotlistCrawler
from crawlers.categorizer import classify, select_top
from summarizer import Summarizer
from crawlers.base import NewsItem
from pushers.feishu import FeishuPusher

REGION = os.getenv("REGION", "all")


async def main():
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    label = {"domestic": "国内", "international": "国际"}.get(REGION, "综合")
    print("=" * 50)
    print(f"📰 新闻推送 [{label}] — {now.strftime('%Y-%m-%d %A')}")
    print("=" * 50)

    all_feeds = config.RSS_FEEDS
    if REGION == "domestic":
        all_feeds = [(u, c) for u, c in all_feeds if c.startswith("国内")]
    elif REGION == "international":
        all_feeds = [(u, c) for u, c in all_feeds if c.startswith("国际")]

    hotlist_srcs = config.HOTLIST_SOURCES
    if REGION == "domestic":
        hotlist_srcs = [(n, c) for n, c in hotlist_srcs if c.startswith("国内")]
    elif REGION == "international":
        hotlist_srcs = [(n, c) for n, c in hotlist_srcs if c.startswith("国际")]

    print("🌐 抓取...")
    tasks = []
    if config.ENABLE_RSS:
        tasks.append(RSSCrawler(all_feeds, config.PER_SOURCE).fetch())
    if config.ENABLE_HOTLIST:
        tasks.append(HotlistCrawler(hotlist_srcs, config.PER_SOURCE).fetch())
    if not tasks:
        print("无数据源"); return
    results = await asyncio.gather(*tasks)
    items = []
    for r in results: items.extend(r)
    print(f"   共 {len(items)} 条")
    if not items: print("⚠️ 无新闻"); return

    seen = set(); uni = []
    for it in items:
        k = (it.title, it.url)
        if k not in seen: seen.add(k); uni.append(it)
    items = uni
    print(f"   去重后 {len(items)} 条")

    items = classify(items)
    target_cats = [c for c in config.ALL_CATS if (
        REGION == "all" or
        (REGION == "domestic" and c.startswith("国内")) or
        (REGION == "international" and c.startswith("国际"))
    )]
    for cat in target_cats:
        c = sum(1 for it in items if it.category == cat)
        if c: print(f"   [{cat}] {c} 条")

    print(f"✨ 精选 Top {config.PER_SUBCAT}...")
    items = select_top(items, config.PER_SUBCAT)
    print(f"   精选后 {len(items)} 条")

    if config.ENABLE_SUMMARY and config.LLM_API_KEY:
        print("🤖 AI 概述...")
        items = await Summarizer(
            config.LLM_API_KEY, config.LLM_MODEL, config.LLM_BASE_URL
        ).summarize(items)
        print("   完成")
    elif config.ENABLE_SUMMARY:
        print("⚠️ 未配 LLM_API_KEY")

    region_title = {"domestic": "国内", "international": "国际"}.get(REGION, "综合")
    title = f"📰 {region_title}新闻 — {now.strftime('%Y-%m-%d %A')}"
    print("📤 推送...")
    if config.FEISHU_WEBHOOK:
        await FeishuPusher(config.FEISHU_WEBHOOK).push(items, title)
    print("✅ 完成")


if __name__ == "__main__":
    asyncio.run(main())
