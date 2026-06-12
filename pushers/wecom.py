"""企业微信推送 — 四大板块"""

import httpx
from crawlers.base import NewsItem

CATS = ["世界要闻", "科技前沿", "金融财经", "综合"]

class WeComPusher:
    def __init__(self, webhook: str):
        self.webhook = webhook

    async def push(self, items: list[NewsItem], title: str = ""):
        if not items or not self.webhook:
            return
        content = f"**{title}**\n\n"
        idx = 0
        for cat in CATS:
            ci = [it for it in items if it.category == cat]
            if not ci:
                continue
            content += f"**━━━ 🌍 {cat} ━━━**\n"
            for it in ci:
                idx += 1
                content += f"{idx}. **{it.title}**\n"
                if it.summary:
                    content += f"   > {it.summary[:400]}\n"
                if it.url:
                    content += f"   > 🔗 [{it.url}]({it.url})\n"
            content += "\n"
        if len(content.encode()) > 4000:
            content = content.encode()[:4000].decode("utf-8", errors="ignore") + "\n...(截断)"
        payload = {"msgtype": "markdown", "markdown": {"content": content}}
        async with httpx.AsyncClient(timeout=10) as cli:
            r = await cli.post(self.webhook, json=payload)
            if r.status_code != 200:
                print(f"[WeCom] err: {r.text}")
            else:
                print("[WeCom] OK")
