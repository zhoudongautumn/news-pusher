"""飞书推送 - 纯文本稳定版"""

import httpx
from datetime import datetime
import pytz
from crawlers.base import NewsItem

LAYOUT = [
    ("国内", ["国内科技", "国内军事", "国内综合"]),
    ("国际", ["国际科技", "国际经济", "国际军事", "国际综合", "中国经济"]),
]

ICONS = {
    "经济": "💰", "科技": "🔬", "军事": "🛡️", "综合": "📋",
    "国内": "🇨🇳", "国际": "🌍",
    "中国经济": "🇨🇳",
}

ICON_LABEL = {"中国经济": "💰 中国经济(英文源)"}


class FeishuPusher:
    def __init__(self, w: str): self.w = w

    async def push(self, items, title: str = ""):
        if not items or not self.w:
            return
        now = datetime.now(pytz.timezone("Asia/Shanghai"))
        emoji = "☀️" if now.hour < 12 else "🌤"
        subtitle = "晨报" if now.hour < 12 else "午报"

        lines = [f"{emoji} 每日{subtitle} | {now.strftime('%Y-%m-%d %A')}", ""]
        idx = 0

        for region, cats in LAYOUT:
            r_items = [it for it in items if it.category in cats]
            if not r_items:
                continue
            lines.append(f"━━━ {ICONS.get(region, '')} {region} ━━━")
            for cat in cats:
                ci = [it for it in r_items if it.category == cat]
                if not ci:
                    continue
                sub = cat[2:] if cat not in ICON_LABEL else ICON_LABEL[cat]
                label = ICON_LABEL.get(cat, f"  {ICONS.get(sub, '')} {sub}")
                lines.append(label if cat in ICON_LABEL else f"  {ICONS.get(sub, '')} {sub}")
                for it in ci:
                    idx += 1
                    lines.append(f"  {idx}. {it.title}")
                    if it.summary:
                        lines.append(f"     {it.summary[:500]}")
                    if it.url:
                        lines.append(f"     🔗 {it.url}")
                    lines.append("")

        body = "\n".join(lines)
        if len(body) > 18000:
            body = body[:18000] + "\n...(截断)"

        payload = {"msg_type": "text", "content": {"text": body}}
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(self.w, json=payload)
            if r.status_code == 200:
                d = r.json()
                if d.get("code", -1) == 0:
                    print("[Feishu] OK")
                else:
                    print(f"[Feishu] err {d}")
            else:
                print(f"[Feishu] HTTP {r.status_code}")