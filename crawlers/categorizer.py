"""分类器 — 源已预标记，兜底关键词"""

from crawlers.base import NewsItem

_KEYS = {
    "科技前沿": ["AI", "人工智能", "大模型", "ChatGPT", "GPT", "芯片", "半导体",
        "GPU", "手机", "iPhone", "华为", "科技", "软件", "硬件", "编程", "开源",
        "互联网", "算法", "云计算", "机器人", "自动驾驶", "SpaceX", "火箭", "卫星",
        "Apple", "Google", "微软", "NVIDIA", "英伟达", "特斯拉", "新能源", "电池"],
    "金融财经": ["股票", "股市", "A股", "港股", "美股", "大盘", "指数", "标普",
        "道指", "纳指", "基金", "ETF", "债券", "期货", "银行", "央行", "美联储",
        "利率", "加息", "降息", "人民币", "美元", "汇率", "通胀", "CPI", "GDP",
        "经济", "衰退", "投资", "理财", "IPO", "财报", "营收", "利润", "比特币",
        "加密货币", "房地产", "房价", "贸易", "关税"],
    "军事防务": ["军事", "军队", "战争", "导弹", "航母", "战机", "国防", "军演",
        "北约", "NATO", "五角大楼", "Pentagon", "武器", "装备", "核", "舰艇",
        "坦克", "防空", "海军", "陆军", "空军", "特种部队", "征兵", "冲突"],
}

_DOMESTIC_SOURCES = ["人民日报", "新华网", "人民网", "IT之家", "财联社", "知乎热榜", "新浪"]


def classify(items: list[NewsItem]) -> list[NewsItem]:
    for it in items:
        if it.category and it.category != "国内综合":
            continue
        text = it.title + " " + it.summary
        is_domestic = any(s in it.source for s in _DOMESTIC_SOURCES) or \
                      any(kw in text for kw in ["中国", "北京", "上海", "深圳", "A股"])
        sub = _keyword_sub(text)
        region = "国内" if is_domestic else "国际"
        it.category = f"{region}{sub}"
    return items


def _keyword_sub(text: str) -> str:
    scores = {}
    for cat, kws in _KEYS.items():
        scores[cat] = sum(1 for kw in kws if kw.lower() in text.lower())
    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return {"科技前沿": "科技", "金融财经": "经济", "军事防务": "军事"}[best]
    return "综合"


def select_top(items: list[NewsItem], per: int = 8) -> list[NewsItem]:
    result = []
    for cat in [
        "国内经济", "国内科技", "国内军事", "国内综合",
        "国际经济", "国际科技", "国际军事", "国际综合",
    ]:
        ci = [it for it in items if it.category == cat]
        result.extend(ci[:per])
        print(f"  [{cat}] {len(ci)} 条, 精选 {min(len(ci), per)} 条")
    return result
