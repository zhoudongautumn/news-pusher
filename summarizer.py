"""LLM 摘要模块 — 用 AI 给新闻生成一句话摘要"""

from openai import OpenAI
from crawlers.base import NewsItem


class Summarizer:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = ""):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    async def summarize(self, items: list[NewsItem]) -> list[NewsItem]:
        """批量生成摘要，原地修改 summary 字段"""
        if not items:
            return items

        texts = "\n".join(f"{i+1}. {it.title} — {it.summary}" for i, it in enumerate(items))
        prompt = (
            "以下是一组新闻条目（标题+已有简介）。请为每条新闻生成一句中文摘要（20字以内），"
            "按序号一行一个返回。\n\n" + texts
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            lines = resp.choices[0].message.content.strip().split("\n")
            for i, line in enumerate(lines):
                if i < len(items):
                    # 去掉序号前缀，如 "1. 摘要内容"
                    clean = line.split(". ", 1)[-1] if ". " in line else line
                    items[i].summary = clean[:120]
        except Exception as e:
            print(f"[Summarizer] LLM 调用失败: {e}")
        return items
