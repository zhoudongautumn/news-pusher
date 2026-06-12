"""新闻推送主入口 — 抓取 → 摘要 → 推送"""

import asyncio
import os
import sys
from datetime import datetime
import pytz

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from crawlers.rss import RSSCrawler
from crawlers.hotlist import HotlistCrawler
from crawlers.base import NewsItem
from pushers.feishu import FeishuPusher
from pushers.wecom import WeComPusher
from pushers.telegram import TelegramPusher
from pushers.email import EmailPusher
from summarizer import Summarizer


async def fetch_all() -> list[NewsItem]:
    """并发抓取所有启用的源"""
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
    """推送到所有启用的渠道"""
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    title = f"📰 新闻早报 — {now.strftime('%Y-%m-%d %A')}"

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

    # 1. 抓取
    print("🌐 正在抓取新闻...")
    items = await fetch_all()
    print(f"   共获取 {len(items)} 条新闻")

    if not items:
        print("⚠️  没有获取到新闻")
        return

    # 2. 去重 (按 title+url 去重)
    seen = set()
    unique_items = []
    for it in items:
        key = (it.title, it.url)
        if key not in seen:
            seen.add(key)
            unique_items.append(it)
    items = unique_items
    print(f"   去重后 {len(items)} 条")

    # 3. 可选 LLM 摘要
    if config.ENABLE_SUMMARY and config.LLM_API_KEY:
        print("🤖 正在生成 AI 摘要...")
        summarizer = Summarizer(config.LLM_API_KEY, config.LLM_MODEL, config.LLM_BASE_URL)
        items = await summarizer.summarize(items)
        print("   摘要生成完成")

    # 4. 控制台输出预览
    print("\n📋 今日新闻预览:")
    for i, it in enumerate(items, 1):
        print(f"  {i}. [{it.source}] {it.title}")
    print()

    # 5. 推送
    print("📤 正在推送...")
    await push_all(items)
    print("✅ 推送完成")


if __name__ == "__main__":
    asyncio.run(main())


