"""LLM 摘要 — 8 子类 × 强锁中文"""

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
            "国内经济", "国内科技", "国内军事", "国内综合",
            "国际经济", "国际科技", "国际军事", "国际综合",
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
            f"你是中文新闻编辑。下面 {len(items)} 条是「{cat}」新闻，"
            f"部分为外文。\n\n"
            f"== 硬性要求 ==\n"
            f"1. 必须用中文输出，禁止出现英文单词或字母\n"
            f"2. 外文新闻先翻译成流暢中文\n"
            f"3. 每条返回一行: 序号. 中文标题——中文概述\n"
            f"4. 概述包含: 事件背景、核心事实、各方表态、影响\n"
            f"5. 不限字数，完整深入，语言自然\n\n"
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
                    items[i].summary = line.strip()[:1200]
        except Exception as e:
            print(f"[LLM/{cat}] 失败: {e}")
