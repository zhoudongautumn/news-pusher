"""LLM 摘要 — 外文翻译 + 深度专业概述"""

from openai import OpenAI
from crawlers.base import NewsItem


SYSTEM_PROMPT = (
    "你是一位资深国际新闻主编，精通中英文。"
    "你的任务是把外文新闻翻译成地道中文，并写出专业、有深度的内容概述。"
    "输出必须全部使用中文，不允许出现任何英文单词或句子。"
    "概述要求：讲清事件背景、核心事实、各方立场、市场/社会影响。"
    "不要只复述标题，不要出现「据悉」「据报道」等套话开头。"
)


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
        for cat in ["世界要闻", "科技前沿", "金融财经", "综合"]:
            cat_items = [it for it in items if it.category == cat]
            if not cat_items:
                continue
            await self._summarize_category(cat_items, cat)
        return items

    async def _summarize_category(self, items: list[NewsItem], category: str):
        texts = "\n\n".join(
            f"新闻{i+1}\n标题: {it.title}\n原文摘要: {it.summary[:500]}"
            for i, it in enumerate(items)
        )
        user_msg = (
            f"以下是 {len(items)} 条「{category}」新闻，部分为英文。请逐条处理：\n\n"
            f"{texts}\n\n"
            f"请为每条新闻返回一行，格式: 「序号. 中文标题：中文概述」\n"
            f"概述要完整深入，包含背景、要点和影响，不限字数。英文标题和摘要必须翻译成中文。"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.5,
                max_tokens=8192,
            )
            content = resp.choices[0].message.content.strip()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if i < len(items):
                    clean = line.split(". ", 1)[-1] if ". " in line else line
                    items[i].summary = clean[:1000]
        except Exception as e:
            print(f"[Summarizer/{category}] LLM 失败: {e}")
