"""飞书推送 — 早晚双版 + 清爽排版"""

import httpx
from datetime import datetime
import pytz
from crawlers.base import NewsItem

LAYOUT = [
    ("国内", ["国内经济", "国内科技", "国内军事", "国内综合"]),
    ("国际", ["国际经济", "国际科技", "国际军事", "国际综合"]),
]

ICONS = {
    "经济": "💰", "科技": "🔬", "军事": "🛡️", "综合": "📋",
    "国内": "🇨🇳", "国际": "🌍",
}


class FeishuPusher:
    def __init__(self, w: str): self.w = w

    async def push(self, items: list[NewsItem], title: str = ""):
        if not items or not self.w: return

        # 根据当前北京时间判断早晚
        now = datetime.now(pytz.timezone("Asia/Shanghai"))
        hour = now.hour
        is_morning = hour < 12
        header = "☀️ **每日晨报**" if is_morning else "🌤 **每日午报**"
        date_str = now.strftime("%Y年%m月%d日 %A")
        tagline = "清晨速览全球大事，开启新的一天" if is_morning else "午后更新要闻，掌握全天动态"

        lines = [f"{header}  |  {date_str}", tagline, ""]
        idx = 0

        for region, cats in LAYOUT:
            r_items = [it for it in items if it.category in cats]
            if not r_items: continue
            region_icon = ICONS.get(region, "")
            lines.append(f"\n━━━ {region_icon} {region} ━━━")

            for cat in cats:
                ci = [it for it in r_items if it.category == cat]
                if not ci: continue
                sub = cat[2:]
                icon = ICONS.get(sub, "")
                lines.append(f"\n  {icon} {sub}")
                for it in ci:
                    idx += 1
                    # 标题
                    lines.append(f"  **{idx}. {it.title}**")
                    # 摘要
                    if it.summary:
                        lines.append(f"  {it.summary[:500]}")
                    # 链接
                    if it.url:
                        lines.append(f"  🔗 {it.url}")
                    lines.append("")

        body = "\n".join(lines)
        if len(body) > 18000:
            body = body[:18000] + "\n...（截断）"

        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": f"{header} | {date_str}"},
                    "template": "blue" if is_morning else "orange",
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": body}},
                ],
            },
        }

        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(self.w, json=payload)
            if r.status_code == 200:
                d = r.json()
                if d.get("code", -1) == 0:
                    print("[Feishu] OK")
                else:
                    print(f"[Feishu] err code={d.get('code')} msg={d.get('msg')}")
                    # 降级为纯文本重试
                    await self._fallback_text(items, title)
            else:
                print(f"[Feishu] HTTP {r.status_code}, 降级重试")
                await self._fallback_text(items, title)

    async def _fallback_text(self, items: list[NewsItem], title: str = ""):
        """纯文本降级推送"""
        now = datetime.now(pytz.timezone("Asia/Shanghai"))
        hour = now.hour
        is_morning = hour < 12
        header = "☀️ 每日晨报" if is_morning else "🌤 每日午报"
        date_str = now.strftime("%Y-%m-%d %A")

        lines = [f"{header}  |  {date_str}", ""]
        idx = 0
        for region, cats in LAYOUT:
            r_items = [it for it in items if it.category in cats]
            if not r_items: continue
            lines.append(f"\n━━━ {ICONS.get(region, '')} {region} ━━━")
            for cat in cats:
                ci = [it for it in r_items if it.category == cat]
                if not ci: continue
                sub = cat[2:]
                lines.append(f"\n  {ICONS.get(sub, '')} {sub}")
                for it in ci:
                    idx += 1
                    lines.append(f"  {idx}. {it.title}")
                    if it.summary:
                        lines.append(f"     {it.summary[:500]}")
                    if it.url:
                        lines.append(f"     🔗 {it.url}")
                    lines.append("")

        body = "\n".join(lines)
        if len(body) > 18000: body = body[:18000] + "\n...（截断）"
        payload = {"msg_type": "text", "content": {"text": body}}
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(self.w, json=payload)
            if r.status_code == 200:
                d = r.json()
                if d.get("code", -1) == 0:
                    print("[Feishu] OK (text)")
                else:
                    print(f"[Feishu] text err {d}")
            else:
                print(f"[Feishu] text HTTP {r.status_code}")
