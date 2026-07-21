"""LLM 摘要 - 完整翻译 + 深度概述"""

from openai import OpenAI
from crawlers.base import NewsItem


class Summarizer:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = ""):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    async def summarize(self, items):
        if not items:
            return items
        for cat in [
            "国内科技", "国内经济", "国内军事", "国内综合",
            "国际科技", "国际经济", "国际军事", "国际综合",
        ]:
            ci = [it for it in items if it.category == cat]
            if not ci:
                continue
            await self._go(ci, cat)
        return items

    async def _go(self, items, cat: str):
        parts = []
        for i, it in enumerate(items):
            d = it.summary[:600] if it.summary else "(无)"
            parts.append(f"[{i+1}] {it.title} | {d}")
        block = " || ".join(parts)

        prompt = (
            f"你是资深中文新闻编辑。处理以下{len(items)}条「{cat}」新闻（外文需翻译成中文）。\n"
            f"每条返回一行，格式: 序号. 中文标题——中文概述。\n"
            f"概述150-250字，完整段落句号结尾，禁止半截句子。\n"
            f"外文新闻先翻译成中文再概述。\n\n"
            f"{block}"
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4, max_tokens=8192,
            )
            lines = resp.choices[0].message.content.strip().split("\n")
            for i, line in enumerate(lines):
                if i < len(items):
                    for sep in ["——", "：", ": "]:
                        if sep in line:
                            line = line.split(sep, 1)[-1]
                            break
                    items[i].summary = line.strip()[:1200]
        except Exception as e:
            print(f"[LLM/{cat}] 失败: {e}")