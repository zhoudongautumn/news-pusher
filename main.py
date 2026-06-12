"""新闻推送主入口 — 抓取 → 分类 → 精选 → 概述 → 推送"""

import asyncio
import os
import sys
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
        print("[Main] 未启用任何数据源")
        return []
    results = await asyncio.gather(*tasks)
    all_items: list[NewsItem] = []
    for items in results:
        all_items.extend(items)
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
    print(f"📰 新闻推送服务启动 — {datetime.now(pytz.timezone(config.TIMEZONE))}")
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

    print("🏷️  正在分类...")
    source_map = {}
    source_map.update(config.RSS_CATEGORY_MAP)
    source_map.update(config.HOTLIST_CATEGORY_MAP)
    items = classify(items, source_map, config.RSS_URL_CATEGORY_MAP)
    for cat in config.CATEGORIES:
        count = sum(1 for it in items if it.category == cat)
        print(f"   [{cat}] {count} 条")

    print(f"✨ 精选每个板块 Top {config.MAX_NEWS_PER_CATEGORY}...")
    items = select_top(items, config.MAX_NEWS_PER_CATEGORY)
    print(f"   精选后共 {len(items)} 条")

    if config.ENABLE_SUMMARY:
        if not config.LLM_API_KEY:
            print("⚠️  未配置 LLM_API_KEY，跳过 AI 概述！请在 GitHub Secrets 中添加")
        else:
            print("🤖 正在生成 AI 内容概述（约70字/条）...")
            summarizer = Summarizer(config.LLM_API_KEY, config.LLM_MODEL, config.LLM_BASE_URL)
            items = await summarizer.summarize(items)
            print("   概述生成完成")

    print("\n📋 今日新闻预览:")
    for cat in config.CATEGORIES:
        cat_items = [it for it in items if it.category == cat]
        if not cat_items:
            continue
        print(f"\n  【{cat}】")
        for i, it in enumerate(cat_items, 1):
            summary_preview = it.summary[:60] + "..." if len(it.summary) > 60 else it.summary
            print(f"    {i}. {it.title}")
            print(f"       {summary_preview}")
    print()

    print("📤 正在推送...")
    await push_all(items)
    print("✅ 推送完成")


if __name__ == "__main__":
    asyncio.run(main())
