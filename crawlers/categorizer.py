"""新闻板块分类器 — 源映射 + URL + 关键词"""

from crawlers.base import NewsItem

CATEGORY_KEYWORDS = {
    "科技前沿": [
        "AI", "人工智能", "大模型", "ChatGPT", "GPT", "OpenAI", "DeepSeek",
        "芯片", "半导体", "GPU", "CPU", "NPU", "算力", "量子",
        "手机", "iPhone", "华为", "小米", "三星", "Pixel",
        "科技", "技术", "软件", "硬件", "编程", "代码", "开源",
        "互联网", "算法", "数据", "云计算", "SaaS",
        "机器人", "自动驾驶", "无人驾驶", "火箭", "卫星", "SpaceX", "NASA",
        "苹果", "Apple", "Google", "谷歌", "微软", "Microsoft", "Meta",
        "英伟达", "NVIDIA", "特斯拉", "Tesla", "字节", "腾讯", "阿里",
        "5G", "6G", "VR", "AR", "元宇宙", "区块链", "Web3",
        "新能源", "电池", "电动车", "智能",
    ],
    "金融财经": [
        "股票", "股市", "A股", "港股", "美股", "大盘", "指数", "标普", "道指", "纳指",
        "基金", "ETF", "债券", "期货", "期权",
        "银行", "央行", "美联储", "利率", "加息", "降息", "降准", "LPR",
        "人民币", "美元", "汇率", "外汇",
        "通胀", "CPI", "PPI", "GDP", "经济", "宏观", "衰退",
        "投资", "理财", "保险", "贷款", "房贷",
        "上市", "IPO", "财报", "营收", "利润", "市值",
        "比特币", "加密货币", "ETH", "BTC",
        "房地产", "房价", "楼市",
        "贸易", "关税", "制裁", "供应链",
    ],
}


def classify(items: list[NewsItem], source_map: dict, url_map: dict = None) -> list[NewsItem]:
    url_map = url_map or {}
    for item in items:
        if item.source in source_map:
            item.category = source_map[item.source]
            continue
        url_lower = item.url.lower()
        matched = False
        for kw, cat in url_map.items():
            if kw.lower() in url_lower:
                item.category = cat
                matched = True
                break
        if matched:
            continue
        text = item.title + " " + item.summary
        item.category = _keyword_classify(text)
    return items


def _keyword_classify(text: str) -> str:
    scores = {"科技前沿": 0, "金融财经": 0}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                scores[cat] += 1
    if scores["科技前沿"] > scores["金融财经"] and scores["科技前沿"] >= 2:
        return "科技前沿"
    elif scores["金融财经"] > scores["科技前沿"] and scores["金融财经"] >= 2:
        return "金融财经"
    return "世界要闻"


def select_top(items: list[NewsItem], per_category: int = 10) -> list[NewsItem]:
    result = []
    for cat in ["世界要闻", "科技前沿", "金融财经", "综合"]:
        cat_items = [it for it in items if it.category == cat]
        result.extend(cat_items[:per_category])
        print(f"  [{cat}] {len(cat_items)} 条, 精选 {min(len(cat_items), per_category)} 条")
    return result
