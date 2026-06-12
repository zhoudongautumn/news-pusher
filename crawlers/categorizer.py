"""新闻板块分类器 — 源映射 + URL 匹配 + 关键词"""

from crawlers.base import NewsItem

CATEGORY_KEYWORDS = {
    "科技": [
        "AI", "人工智能", "大模型", "ChatGPT", "GPT", "OpenAI", "DeepSeek",
        "芯片", "半导体", "GPU", "CPU", "NPU", "算力",
        "手机", "iPhone", "华为", "小米", "OPPO", "vivo",
        "科技", "技术", "软件", "硬件", "编程", "代码", "开源",
        "互联网", "算法", "数据", "云计算", "云服务", "SaaS",
        "机器人", "自动驾驶", "无人驾驶", "火箭", "卫星", "SpaceX",
        "苹果", "Apple", "Google", "谷歌", "微软", "Microsoft", "Meta",
        "英伟达", "NVIDIA", "特斯拉", "Tesla", "字节", "腾讯", "阿里",
        "5G", "6G", "VR", "AR", "元宇宙", "区块链", "Web3",
        "新能源", "电池", "电动车", "智能", "数字化",
    ],
    "金融": [
        "股票", "股市", "A股", "港股", "美股", "大盘", "指数",
        "基金", "ETF", "债券", "期货", "期权",
        "银行", "央行", "利率", "加息", "降息", "降准", "LPR",
        "人民币", "美元", "汇率", "外汇",
        "通胀", "CPI", "PPI", "GDP", "经济", "宏观",
        "投资", "理财", "保险", "贷款", "房贷", "按揭",
        "上市", "IPO", "财报", "营收", "利润", "市值",
        "比特币", "加密货币", "ETH", "BTC", "币圈",
        "房地产", "房价", "楼市", "调控",
        "贸易", "关税", "制裁", "供应链",
    ],
}


def classify(items: list[NewsItem], source_map: dict, url_map: dict = None) -> list[NewsItem]:
    """为新闻条目分配板块
    
    source_map: {source_name: category}  按 feed 标题匹配
    url_map:    {keyword: category}      按 URL 关键词兜底匹配
    """
    url_map = url_map or {}
    for item in items:
        # 1) 按来源名称映射
        if item.source in source_map:
            item.category = source_map[item.source]
            continue
        # 2) 按 URL 关键词兜底
        url_lower = item.url.lower()
        matched = False
        for kw, cat in url_map.items():
            if kw.lower() in url_lower:
                item.category = cat
                matched = True
                break
        if matched:
            continue
        # 3) 标题+摘要关键词匹配
        text = item.title + " " + item.summary
        item.category = _keyword_classify(text)
    return items


def _keyword_classify(text: str) -> str:
    scores = {"科技": 0, "金融": 0}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                scores[cat] += 1
    if scores["科技"] > scores["金融"]:
        return "科技"
    elif scores["金融"] > scores["科技"]:
        return "金融"
    return "综合"


def select_top(items: list[NewsItem], per_category: int = 10) -> list[NewsItem]:
    """从每个板块各选 top N"""
    result = []
    for cat in ["科技", "金融", "综合"]:
        cat_items = [it for it in items if it.category == cat]
        result.extend(cat_items[:per_category])
        print(f"  [{cat}] 共 {len(cat_items)} 条，精选 {min(len(cat_items), per_category)} 条")
    return result
