"""LLM 摘要 — 强锁中文输出 + 专业概述"""

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
        for cat in ["世界要闻", "科技前沿", "金融财经", "综合"]:
            cat_items = [it for it in items if it.category == cat]
            if not cat_items:
                continue
            await self._summarize_category(cat_items, cat)
        return items

    async def _summarize_category(self, items: list[NewsItem], category: str):
        parts = []
        for i, it in enumerate(items):
            desc = it.summary[:600] if it.summary else "(无描述)"
            parts.append(f"第{i+1}条 | 标题: {it.title} | 原文描述: {desc}")
        news_text = "\n\n".join(parts)

        prompt = (
            f"== 任务开始 ==\n"
            f"你是中文新闻主编。下面有 {len(items)} 条「{category}」新闻。\n"
            f"其中一些是英文或外文，你必须先翻译成流暢的中文，再撰写概述。\n\n"
            f"要求：\n"
            f"- 输出语言：只能用中文，禁止出现任何英文单词或字母\n"
            f"- 每条返回一行：序号. 中文标题——概述内容\n"
            f"- 概述要包含：事件背景、核心事实、各方反应、影响分析\n"
            f"- 不限字数，要完整深入\n"
            f"- 不得使用「据悉」「据报道」等套话\n\n"
            f"{news_text}\n\n"
            f"== 请严格按照上述要求，用纯中文逐条输出 =="
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=8192,
            )
            content = resp.choices[0].message.content.strip()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if i < len(items):
                    for sep in ["——", "：", ": ", ". "]:
                        if sep in line:
                            line = line.split(sep, 1)[-1]
                            break
                    items[i].summary = line.strip()[:1200]
        except Exception as e:
            print(f"[Summarizer/{category}] 失败: {e}")
