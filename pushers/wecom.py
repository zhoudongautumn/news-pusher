"""企业微信机器人推送"""

import httpx
from crawlers.base import NewsItem


class WeComPusher:
    def __init__(self, webhook: str):
        self.webhook = webhook

    async def push(self, items: list[NewsItem], title: str = "📰 今日新闻推送"):
        if not items or not self.webhook:
            return

        content = f"**{title}**\n\n"
        for i, it in enumerate(items, 1):
            content += f"{i}. **[{it.source}]** [{it.title}]({it.url})\n"
            if it.summary:
                content += f"   > {it.summary[:100]}\n"

        # 企业微信 Markdown 消息限制 4096 字节，超额分多条
        payload = {
            "msgtype": "markdown",
            "markdown": {"content": content},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(self.webhook, json=payload)
            if resp.status_code != 200:
                print(f"[WeCom] 推送失败: {resp.text}")
