"""飞书推送 — 国内/国际双区"""

import httpx
from crawlers.base import NewsItem

LAYOUT = [
    ("🇨🇳 国内", ["国内经济", "国内科技", "国内军事", "国内综合"]),
    ("🌍 国际", ["国际经济", "国际科技", "国际军事", "国际综合"]),
]
SUB_LABEL = {"经济": "💰 经济财经", "科技": "🔬 科技前沿", "军事": "🛡️ 军事防务", "综合": "📋 综合要闻"}

class FeishuPusher:
    def __init__(self, w: str): self.w = w
    async def push(self, items: list[NewsItem], title: str = ""):
        if not items or not self.w: return
        lines = [title, ""]; idx = 0
        for region, cats in LAYOUT:
            region_items = [it for it in items if it.category in cats]
            if not region_items: continue
            lines.append(f"\n{'='*20}  {region}  {'='*20}")
            for cat in cats:
                ci = [it for it in region_items if it.category == cat]
                if not ci: continue
                sub = cat[2:]  # "国内经济" → "经济"
                lines.append(f"\n  {SUB_LABEL.get(sub, sub)}")
                for it in ci:
                    idx += 1
                    s = f"  {idx}. {it.title}"
                    if it.summary: s += f"\n     {it.summary[:400]}"
                    if it.url: s += f"\n     🔗 {it.url}"
                    lines.append(s)
        body = "\n".join(lines)
        if len(body) > 18000: body = body[:18000] + "\n...(截断)"
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(self.w, json={"msg_type":"text","content":{"text":body}})
            if r.status_code == 200:
                d = r.json()
                if d.get("code",-1)==0: print("[Feishu] OK")
                else: print(f"[Feishu] err {d}")
            else: print(f"[Feishu] HTTP {r.status_code}")
