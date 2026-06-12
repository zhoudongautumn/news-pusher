"""LLM 摘要模块 — AI 内容概述 + 外文翻译"""

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
        if not items:
            return items
        for cat in ["科技", "金融", "综合"]:
            cat_items = [it for it in items if it.category == cat]
            if not cat_items:
                continue
            await self._summarize_category(cat_items, cat)
        return items

    async def _summarize_category(self, items: list[NewsItem], category: str):
        texts = "\n".join(
            f"{i+1}. {it.title}（来源: {it.source}）"
            for i, it in enumerate(items)
        )
        prompt = (
            f"你是一位资深新闻编辑。以下是一组「{category}」板块的新闻标题。\n\n"
            f"要求：\n"
            f"1. 如果标题是英文或其他外语，必须先翻译成流畅的中文\n"
            f"2. 根据你的知识，为每条新闻撰写一段完整的中文概述，包含：事件背景、核心内容、影响或意义\n"
            f"3. 语言自然流畅，像专业新闻简报，不要机械罗列\n"
            f"4. 没有字数限制，但要完整涵盖要点\n"
            f"5. 按序号一行返回，格式为「序号. 中文标题：概述内容」\n\n"
            f"{texts}"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=8192,
            )
            content = resp.choices[0].message.content.strip()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if i < len(items):
                    clean = line.split(". ", 1)[-1] if ". " in line else line
                    items[i].summary = clean[:600]
        except Exception as e:
            print(f"[Summarizer/{category}] LLM 调用失败: {e}")
