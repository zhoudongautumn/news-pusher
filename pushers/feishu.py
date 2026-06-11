"""飞书机器人推送"""

import httpx
from crawlers.base import NewsItem


class FeishuPusher:
    def __init__(self, webhook: str):
        self.webhook = webhook

    async def push(self, items: list[NewsItem], title: str = "📰 今日新闻推送"):
        if not items or not self.webhook:
            return

        elements = []
        for i, it in enumerate(items, 1):
            text = f"**{i}. [{it.source}] {it.title}**"
            if it.summary:
                text += f"\n{it.summary[:100]}"
            if it.url:
                text += f"\n[🔗 阅读原文]({it.url})"
            elements.append({"tag": "markdown", "content": text})
            if i < len(items):
                elements.append({"tag": "hr"})

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": title}},
                "elements": elements,
            },
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(self.webhook, json=payload)
            if resp.status_code != 200:
                print(f"[飞书] 推送失败: {resp.text}")
