"""Telegram Bot 推送"""

import httpx
from crawlers.base import NewsItem


class TelegramPusher:
    def __init__(self, bot_token: str, chat_id: str):
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.chat_id = chat_id

    async def push(self, items: list[NewsItem], title: str = "📰 今日新闻"):
        if not items or not self.chat_id:
            return

        text = f"<b>{title}</b>\n\n"
        for i, it in enumerate(items, 1):
            text += f"{i}. <b>{it.title}</b> [{it.source}]\n"
            if it.summary:
                text += f"   {it.summary[:100]}\n"
            text += f"   <a href='{it.url}'>🔗 阅读原文</a>\n\n"

        # Telegram 消息限制 4096 字符
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text[:4096],
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
            if resp.status_code != 200:
                print(f"[Telegram] 推送失败: {resp.text}")
