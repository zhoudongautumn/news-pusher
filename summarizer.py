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

    async def summarize(self, items: list[NewsItem]) -> list[NewsItem]:
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
            d = it.summary[:800] if it.summary else "(无)"
            parts.append(f"[{i+1}] 标题: {it.title}\n    原文: {d}")
        block = "\n\n".join(parts)

        prompt = (
            f"你是资深中文新闻编辑。请处理以下{len(items)}条「{cat}」新闻（部分为外文）。\n\n"
            f"== 必须遵守 ==\n"
            f"1. 全部用中文输出，外文新闻先翻译成地道中文。\n"
            f"2. 每条格式: 序号. 中文标题——中文概述\n"
            f"3. 概述结构: 事件背景(1句) → 核心内容(2-3句) → 影响/意义(1句)\n"
            f"4. 每条概述150-250字，完整段落，以句号结束，禁止半截句子。\n"
            f"5. 语言风格: 财新/第一财经风格，客观专业，不用「据悉」「据报道」套话。\n"
            f"6. 标题保留原标题关键信息，但翻译成中文。\n\n"
            f"{block}\n\n"
            f"== 严格用中文，逐条输出 =="
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=8192,
            )
            lines = resp.choices[0].message.content.strip().split("\n")
            for i, line in enumerate(lines):
                if i < len(items):
                    for sep in ["——", "：", ": ", ". "]:
                        if sep in line:
                            line = line.split(sep, 1)[-1]
                            break
                    items[i].summary = line.strip()[:1500]
        except Exception as e:
            print(f"[LLM/{cat}] 失败: {e}")