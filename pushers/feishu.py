"""飞书机器人推送"""

import httpx
from crawlers.base import NewsItem


class FeishuPusher:
    def __init__(self, webhook: str):
        self.webhook = webhook

    async def push(self, items: list[NewsItem], title: str = "📰 今日新闻推送"):
        if not items or not self.webhook:
            return

        # 构建飞书卡片消息，使用 lark_md 格式
        content_lines = []
        for i, it in enumerate(items, 1):
            line = f"{i}. **[{it.source}]** [{it.title}]({it.url})"
            if it.summary:
                short = it.summary[:100].replace("\n", " ")
                line += f"\\n> {short}"
            content_lines.append(line)

        body = "\n".join(content_lines)

        # 飞书消息有长度限制，超长截断
        if len(body) > 30000:
            body = body[:30000] + "\n...（内容过长已截断）"

        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title,
                    }
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": body,
                    }
                ],
            },
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(self.webhook, json=payload)
            if resp.status_code != 200:
                print(f"[Feishu] 推送失败: {resp.text}")
            else:
                resp_data = resp.json()
                if resp_data.get("code") != 0:
                    print(f"[Feishu] 推送失败: {resp.text}")
