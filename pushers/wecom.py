"""企业微信机器人推送 — 按板块分组"""

import httpx
from crawlers.base import NewsItem


class WeComPusher:
    def __init__(self, webhook: str):
        self.webhook = webhook

    async def push(self, items: list[NewsItem], title: str = "📰 今日新闻推送"):
        if not items or not self.webhook:
            return

        categories = ["科技", "金融", "综合"]
        content = f"**{title}**\n\n"
        global_idx = 0

        for cat in categories:
            cat_items = [it for it in items if it.category == cat]
            if not cat_items:
                continue
            content += f"**━━━ 📌 {cat} ━━━**\n"
            for it in cat_items:
                global_idx += 1
                content += f"{global_idx}. **{it.title}**\n"
                if it.summary:
                    content += f"   > 📝 {it.summary[:100]}\n"
                if it.url:
                    content += f"   > 🔗 [{it.url}]({it.url})\n"
            content += "\n"

        # 企业微信 Markdown 消息限制 4096 字节
        if len(content.encode()) > 4096:
            content = content.encode()[:4090].decode("utf-8", errors="ignore") + "\n...(已截断)"

        payload = {
            "msgtype": "markdown",
            "markdown": {"content": content},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(self.webhook, json=payload)
            if resp.status_code != 200:
                print(f"[WeCom] 推送失败: {resp.text}")
            else:
                print(f"[WeCom] 推送成功")
