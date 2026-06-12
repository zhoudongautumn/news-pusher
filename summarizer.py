"""LLM 摘要模块 — 用 AI 给新闻生成内容概述（翻译+长摘要）"""

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
        """按板块批量生成内容概述，原地修改 summary 字段"""
        if not items:
            return items

        for cat in ["科技", "金融", "综合"]:
            cat_items = [it for it in items if it.category == cat]
            if not cat_items:
                continue
            await self._summarize_category(cat_items, cat)
        return items

    async def _summarize_category(self, items: list[NewsItem], category: str):
        """为同一板块的新闻生成中文概述（外语自动翻译）"""
        texts = "\n".join(
            f"{i+1}. {it.title}（来源: {it.source}）"
            for i, it in enumerate(items)
        )
        prompt = (
            f"以下是一组「{category}」板块的新闻标题。请为每条新闻写一段约250字的中文内容概述，"
            f"说清楚新闻事件的前因后果和关键信息。如果原标题是英文或外文，请先翻译成中文再做概述。"
            f"按序号一行一条返回，格式为「序号. 概述内容」。\n\n"
            + texts
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
            content = resp.choices[0].message.content.strip()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if i < len(items):
                    clean = line.split(". ", 1)[-1] if ". " in line else line
                    items[i].summary = clean[:300]
        except Exception as e:
            print(f"[Summarizer/{category}] LLM 调用失败: {e}")
