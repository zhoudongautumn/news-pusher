"""飞书推送 — 四大板块"""

import httpx
from crawlers.base import NewsItem

CATS = ["世界要闻", "科技前沿", "金融财经", "综合"]

class FeishuPusher:
    def __init__(self, webhook: str):
        self.webhook = webhook

    async def push(self, items: list[NewsItem], title: str = ""):
        if not items or not self.webhook:
            return
        lines = [title, ""]
        idx = 0
        for cat in CATS:
            ci = [it for it in items if it.category == cat]
            if not ci:
                continue
            lines.append(f"━━━ 🌍 {cat} ━━━")
            for it in ci:
                idx += 1
                s = f"{idx}. {it.title}"
                if it.summary:
                    s += f"\n    {it.summary[:500]}"
                if it.url:
                    s += f"\n    🔗 {it.url}"
                lines.append(s)
            lines.append("")
        body = "\n".join(lines)
        if len(body) > 18000:
            body = body[:18000] + "\n...(截断)"
        payload = {"msg_type": "text", "content": {"text": body}}
        async with httpx.AsyncClient(timeout=10) as cli:
            r = await cli.post(self.webhook, json=payload)
            if r.status_code != 200:
                print(f"[Feishu] HTTP {r.status_code}: {r.text}")
            else:
                d = r.json()
                if d.get("code", -1) != 0:
                    print(f"[Feishu] err code={d.get('code')} msg={d.get('msg')}")
                else:
                    print("[Feishu] OK")
