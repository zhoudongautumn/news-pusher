"""新闻推送 — 国内+国际 × 经济/科技/军事/综合"""

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
from pushers.wecom import WeComPusher


async def main():
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    print("=" * 50)
    print(f"📰 新闻早报 — {now.strftime('%Y-%m-%d %A')}")
    print("=" * 50)

    # 1. 抓取
    print("🌐 抓取...")
    tasks = []
    if config.ENABLE_RSS:
        tasks.append(RSSCrawler(config.RSS_FEEDS, config.PER_SOURCE).fetch())
    if config.ENABLE_HOTLIST:
        tasks.append(HotlistCrawler(config.HOTLIST_SOURCES, config.PER_SOURCE).fetch())
    if not tasks:
        print("无数据源"); return
    results = await asyncio.gather(*tasks)
    items = []
    for r in results: items.extend(r)
    print(f"   共 {len(items)} 条")

    if not items:
        print("⚠️ 无新闻"); return

    # 2. 去重
    seen = set(); uni = []
    for it in items:
        k = (it.title, it.url)
        if k not in seen: seen.add(k); uni.append(it)
    items = uni
    print(f"   去重后 {len(items)} 条")

    # 3. 兜底分类
    items = classify(items)
    for cat in config.ALL_CATS:
        c = sum(1 for it in items if it.category == cat)
        if c: print(f"   [{cat}] {c} 条")

    # 4. 精选
    print(f"✨ 精选每子类 Top {config.PER_SUBCAT}...")
    items = select_top(items, config.PER_SUBCAT)
    print(f"   精选后 {len(items)} 条")

    # 5. AI 概述
    if config.ENABLE_SUMMARY and config.LLM_API_KEY:
        print("🤖 AI 概述（翻译+深度总结）...")
        items = await Summarizer(
            config.LLM_API_KEY, config.LLM_MODEL, config.LLM_BASE_URL
        ).summarize(items)
        print("   完成")
    elif config.ENABLE_SUMMARY:
        print("⚠️ 未配 LLM_API_KEY，跳过 AI")

    # 6. 推送
    title = f"📰 新闻早报 — {now.strftime('%Y-%m-%d %A')}"
    print("📤 推送...")
    tasks2 = []
    if config.FEISHU_WEBHOOK:
        tasks2.append(FeishuPusher(config.FEISHU_WEBHOOK).push(items, title))
    if config.WECOM_WEBHOOK:
        tasks2.append(WeComPusher(config.WECOM_WEBHOOK).push(items, title))
    if tasks2: await asyncio.gather(*tasks2)
    print("✅ 完成")


if __name__ == "__main__":
    asyncio.run(main())
