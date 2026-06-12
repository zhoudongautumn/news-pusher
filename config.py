import os
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# 全局配置 — 板块化版本
# ============================================================

TIMEZONE = "Asia/Shanghai"
MAX_NEWS_PER_SOURCE = 10
MAX_NEWS_PER_CATEGORY = 10

# ============================================================
# 板块定义
# ============================================================
CATEGORIES = ["科技", "金融", "综合"]

RSS_CATEGORY_MAP = {
    "Hacker News": "科技",
    "OpenAI Blog": "科技",
    "IT之家": "科技",
    "iThome": "科技",
    "Reuters Business News": "金融",
    "Yahoo Finance": "金融",
    "路透": "金融",
}

RSS_URL_CATEGORY_MAP = {
    "cls": "金融",
    "reuters.com/reuters/business": "金融",
    "finance.yahoo.com": "金融",
    "ithome": "科技",
    "openai.com": "科技",
    "hnrss": "科技",
}

# ============================================================
# RSS 源列表
# ============================================================
RSS_FEEDS = [
    # ---- 科技 ----
    "https://www.ithome.com/rss/",
    "https://openai.com/blog/rss.xml",
    "https://hnrss.org/frontpage",
    # ---- 金融 ----
    "http://feeds.reuters.com/reuters/businessNews",
    "https://finance.yahoo.com/news/rssindex",
    # ---- 综合 ----
    "https://rsshub.app/zhihu/hot",
    "https://rsshub.app/weibo/search/hot",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "http://rss.cnn.com/rss/edition_world.rss",
    "http://cn.reuters.com/tools/rss/",
]

# ============================================================
# 热搜源
# ============================================================
ENABLE_HOTLIST = True
HOTLIST_SOURCES = ["zhihu", "weibo", "baidu", "cls"]

HOTLIST_CATEGORY_MAP = {
    "zhihu": "综合",
    "weibo": "综合",
    "baidu": "综合",
    "cls": "金融",
}

# ============================================================
# 数据源开关
# ============================================================
ENABLE_RSS = True
ENABLE_NEWSAPI = False

# ============================================================
# LLM 摘要（DeepSeek）
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

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "465")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
MAIL_TO = os.getenv("MAIL_TO", "")

FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK", "")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")
