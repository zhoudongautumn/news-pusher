"""企业微信推送 — 国内/国际双区"""

import httpx
from crawlers.base import NewsItem

LAYOUT = [
    ("🇨🇳 国内", ["国内经济", "国内科技", "国内军事", "国内综合"]),
    ("🌍 国际", ["国际经济", "国际科技", "国际军事", "国际综合"]),
]
SUB_LABEL = {"经济": "💰 经济财经", "科技": "🔬 科技前沿", "军事": "🛡️ 军事防务", "综合": "📋 综合要闻"}

class WeComPusher:
    def __init__(self, w: str): self.w = w
    async def push(self, items: list[NewsItem], title: str = ""):
        if not items or not self.w: return
        content = f"**{title}**\n"; idx = 0
        for region, cats in LAYOUT:
            ri = [it for it in items if it.category in cats]
            if not ri: continue
            content += f"\n**{'='*10} {region} {'='*10}**\n"
            for cat in cats:
                ci = [it for it in ri if it.category == cat]
                if not ci: continue
                sub = cat[2:]
                content += f"\n**{SUB_LABEL.get(sub, sub)}**\n"
                for it in ci:
                    idx += 1
                    content += f"{idx}. **{it.title}**\n"
                    if it.summary: content += f"   > {it.summary[:300]}\n"
                    if it.url: content += f"   > 🔗 [{it.url}]({it.url})\n"
        b = content.encode()
        if len(b) > 4000: content = b[:4000].decode("utf-8",errors="ignore")+"\n...(截断)"
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(self.w, json={"msgtype":"markdown","markdown":{"content":content}})
            if r.status_code == 200: print("[WeCom] OK")
            else: print(f"[WeCom] err {r.text}")
