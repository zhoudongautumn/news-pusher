"""新闻推送主入口 — 四大板块"""

import asyncio, os, sys
from datetime import datetime
import pytz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from crawlers.rss import RSSCrawler
from crawlers.hotlist import HotlistCrawler
from crawlers.categorizer import classify, select_top
from crawlers.base import NewsItem
from pushers.feishu import FeishuPusher
from pushers.wecom import WeComPusher
from pushers.telegram import TelegramPusher
from pushers.email import EmailPusher
from summarizer import Summarizer


async def fetch_all() -> list[NewsItem]:
    tasks = []
    if config.ENABLE_RSS:
        tasks.append(RSSCrawler(config.RSS_FEEDS, config.MAX_NEWS_PER_SOURCE).fetch())
    if config.ENABLE_HOTLIST:
        tasks.append(HotlistCrawler(config.HOTLIST_SOURCES, config.MAX_NEWS_PER_SOURCE).fetch())
    if not tasks:
        print("No sources")
        return []
    results = await asyncio.gather(*tasks)
    all_items = []
    for r in results:
        all_items.extend(r)
    return all_items


async def push_all(items: list[NewsItem]):
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    title = f"📰 每日新闻早报 — {now.strftime('%Y-%m-%d %A')}"
    tasks = []
    if config.ENABLE_FEISHU and config.FEISHU_WEBHOOK:
        tasks.append(FeishuPusher(config.FEISHU_WEBHOOK).push(items, title))
    if config.ENABLE_WECOM and config.WECOM_WEBHOOK:
        tasks.append(WeComPusher(config.WECOM_WEBHOOK).push(items, title))
    if config.ENABLE_TELEGRAM and config.TG_BOT_TOKEN and config.TG_CHAT_ID:
        tasks.append(TelegramPusher(config.TG_BOT_TOKEN, config.TG_CHAT_ID).push(items, title))
    if config.ENABLE_EMAIL and config.SMTP_USER and config.MAIL_TO:
        tasks.append(EmailPusher(
            config.SMTP_HOST, config.SMTP_PORT,
            config.SMTP_USER, config.SMTP_PASS, config.MAIL_TO,
        ).push(items, title))
    if tasks:
        await asyncio.gather(*tasks)


async def main():
    print("=" * 50)
    print(f"📰 新闻推送 — {datetime.now(pytz.timezone(config.TIMEZONE))}")
    print("=" * 50)

    print("🌐 抓取新闻...")
    items = await fetch_all()
    print(f"   共 {len(items)} 条")
    if not items:
        print("⚠️ 无新闻")
        return

    seen = set()
    unique = []
    for it in items:
        k = (it.title, it.url)
        if k not in seen:
            seen.add(k)
            unique.append(it)
    items = unique
    print(f"   去重后 {len(items)} 条")

    print("🏷️ 分类...")
    source_map = {}
    source_map.update(config.RSS_CATEGORY_MAP)
    source_map.update(config.HOTLIST_CATEGORY_MAP)
    items = classify(items, source_map, config.RSS_URL_CATEGORY_MAP)
    for cat in config.CATEGORIES:
        c = sum(1 for it in items if it.category == cat)
        print(f"   [{cat}] {c} 条")

    print(f"✨ 精选每板块 Top {config.MAX_NEWS_PER_CATEGORY}...")
    items = select_top(items, config.MAX_NEWS_PER_CATEGORY)
    print(f"   精选后共 {len(items)} 条")

    if config.ENABLE_SUMMARY:
        if not config.LLM_API_KEY:
            print("⚠️ 未配 LLM_API_KEY，跳过 AI 概述")
        else:
            print("🤖 AI 内容概述（翻译+深度总结）...")
            summarizer = Summarizer(config.LLM_API_KEY, config.LLM_MODEL, config.LLM_BASE_URL)
            items = await summarizer.summarize(items)
            print("   完成")

    print("\n📋 预览:")
    for cat in config.CATEGORIES:
        ci = [it for it in items if it.category == cat]
        if not ci:
            continue
        print(f"\n  【{cat}】")
        for i, it in enumerate(ci, 1):
            print(f"    {i}. {it.title}")
            print(f"       {it.summary[:120]}...")
    print()

    print("📤 推送...")
    await push_all(items)
    print("✅ 完成")


if __name__ == "__main__":
    asyncio.run(main())
