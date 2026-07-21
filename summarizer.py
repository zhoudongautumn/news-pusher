"""LLM 摘要 — 完整段落 + 外文翻译 + 品质要求"""

from openai import OpenAI
from crawlers.base import NewsItem


class Summarizer:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = ""):
        kwargs = {"api_key": api_key}
        if base_url: kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    async def summarize(self, items: list[NewsItem]) -> list[NewsItem]:
        if not items: return items
        for cat in [
            "国内科技", "国内综合", "国际科技", "国际经济", "国际军事", "国际综合", "中国经济",
            "中国军事",
        ]:
            ci = [it for it in items if it.category == cat]
            if not ci: continue
            await self._go(ci, cat)
        return items

    async def _go(self, items: list[NewsItem], cat: str):
        parts = []
        for i, it in enumerate(items):
            d = it.summary[:600] if it.summary else "(无)"
            parts.append(f"[{i+1}] 标题: {it.title}\n    原文: {d}")
        block = "\n\n".join(parts)

        prompt = (
            f"你是资深中文新闻编辑。下面{len(items)}条「{cat}」新闻，部分为外文。\n\n"
            f"== 硬性要求 ==\n"
            f"1. 全部中文输出，禁止英文单词。外文新闻先翻译成中文。\n"
            f"2. 每条返回一行，格式: 序号. 中文标题——中文概述\n"
            f"3. 概述必须包含: 事件背景 → 核心事实 → 各方表态/市场反应 → 后续影响\n"
            f"4. 每条概述至少100字，最后一个句子必须是完整的句号结尾。禁止半句截断。\n"
            f"5. 语言专业流畅，像财新/路透风格，不要「据悉」「据报道」等套话。\n\n"
            f"{block}\n\n"
            f"== 严格用中文，逐条输出 =="
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
                    for sep in ["——", "：", ": ", ". "]:
                        if sep in line:
                            line = line.split(sep, 1)[-1]
                            break
                    items[i].summary = line.strip()[:1200]
        except Exception as e:
            print(f"[LLM/{cat}] 失败: {e}")
