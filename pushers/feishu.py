"""飞书机器人推送"""

import httpx
from crawlers.base import NewsItem


class FeishuPusher:
    def __init__(self, webhook: str):
        self.webhook = webhook

    async def push(self, items: list[NewsItem], title: str = "📰 今日新闻推送"):
        if not items or not self.webhook:
            return

        lines = [title, ""]
        for i, it in enumerate(items, 1):
            line = f"{i}. [{it.source}] {it.title}"
            if it.summary:
                short = it.summary[:80].replace("\n", " ")
                line += f"  |  {short}"
            lines.append(line)

        body = "\n".join(lines)

        if len(body) > 20000:
            body = body[:20000] + "\n...（内容过长已截断）"

        payload = {
            "msg_type": "text",
            "content": {
                "text": body,
            },
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(self.webhook, json=payload)
            if resp.status_code != 200:
                print(f"[Feishu] 推送失败: HTTP {resp.status_code} - {resp.text}")
            else:
                resp_data = resp.json()
                code = resp_data.get("code", -1)
                if code != 0:
                    print(f"[Feishu] 推送失败: code={code} msg={resp_data.get('msg')} full={resp.text}")
                else:
                    print(f"[Feishu] 推送成功")
