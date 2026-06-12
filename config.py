import os
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# 全局配置 — 板块化版本
# ============================================================

TIMEZONE = "Asia/Shanghai"
MAX_NEWS_PER_SOURCE = 10
MAX_NEWS_PER_CATEGORY = 10  # 每个板块精选条数

# ============================================================
# 板块定义
# ============================================================
CATEGORIES = ["科技", "金融", "综合"]

# RSS 源 → 板块映射（按 feed 标题匹配）
RSS_CATEGORY_MAP = {
    # --- 科技 ---
    "Hacker News": "科技",
    "OpenAI Blog": "科技",
    "IT之家": "科技",
    "iThome": "科技",
    "少数派": "科技",
    "InfoQ": "科技",
    "阮一峰的网络日志": "科技",
    "Gea-Suan Lin's BLOG": "科技",
    # --- 金融 ---
    "财联社": "金融",
    "华尔街见闻": "金融",
    "Reuters Business News": "金融",
    "路透": "金融",
    # --- 综合（不写也行，默认就是综合）---
}

# URL 关键词 → 板块（兜底匹配）
RSS_URL_CATEGORY_MAP = {
    "cls": "金融",
    "wallstreetcn": "金融",
    "reuters.com/reuters/business": "金融",
    "ithome": "科技",
    "openai.com": "科技",
    "hnrss": "科技",
}

# ============================================================
# RSS 源列表
# ============================================================
RSS_FEEDS = [
    # ---- 科技 ----
    "https://www.ithome.com/rss/",                    # IT之家
    "https://openai.com/blog/rss.xml",                 # OpenAI Blog
    "https://hnrss.org/frontpage",                     # Hacker News
    # ---- 金融 ----
    "https://rsshub.app/cls/hot",                      # 财联社热点
    "https://rsshub.app/wallstreetcn/hot/",             # 华尔街见闻
    "http://feeds.reuters.com/reuters/businessNews",    # 路透商业
    # ---- 综合 ----
    "https://rsshub.app/zhihu/hot",                    # 知乎热榜
    "https://rsshub.app/weibo/search/hot",              # 微博热搜
    "https://www.newtimespace.com/",                    # 新时代
    "http://feeds.bbci.co.uk/news/world/rss.xml",      # BBC 国际
    "http://rss.cnn.com/rss/edition_world.rss",        # CNN 国际
    "https://www.nytimes.com/section/world/rss.xml",    # 纽约时报国际
    "http://cn.reuters.com/tools/rss/",                 # 路透中文
]

# ============================================================
# 热搜源
# ============================================================
ENABLE_HOTLIST = True
HOTLIST_SOURCES = ["zhihu", "weibo", "baidu"]

HOTLIST_CATEGORY_MAP = {
    "zhihu": "综合",
    "weibo": "综合",
    "baidu": "综合",
}

# ============================================================
# 数据源开关
# ============================================================
ENABLE_RSS = True
ENABLE_NEWSAPI = False

# ============================================================
# LLM 摘要
# ============================================================
ENABLE_SUMMARY = True
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

# ============================================================
# 推送渠道
# ============================================================
ENABLE_EMAIL = False
ENABLE_FEISHU = True
ENABLE_WECOM = True
ENABLE_TELEGRAM = False

# 邮件
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "465")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
MAIL_TO = os.getenv("MAIL_TO", "")

# 飞书
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

# 企业微信
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK", "")

# Telegram
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")
