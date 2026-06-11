import os
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# 全局配置 — 国内优化版
# ============================================================

TIMEZONE = "Asia/Shanghai"
MAX_NEWS_PER_SOURCE = 10

# --- 数据源 ---
ENABLE_RSS = True
ENABLE_HOTLIST = True
ENABLE_NEWSAPI = False

# --- RSS 源（国内可访问） ---
RSS_FEEDS = [
    # 国内科技/资讯
    "https://www.zhihu.com/rss",                   # 知乎
    "https://sspai.com/feed",                       # 少数派
    "https://www.infoq.cn/feed",                    # InfoQ
    "https://feeds.feedburner.com/ruanyifeng",      # 阮一峰的网络日志
    "https://blog.gslin.org/feed",                   # Gea-Suan Lin
    # 国际源（GitHub Actions runner 上可能可访问）
    "https://hnrss.org/frontpage",                   # Hacker News
]

# --- 热搜源（国内） ---
HOTLIST_SOURCES = ["zhihu", "weibo", "baidu"]

# --- LLM 摘要（国内建议关闭） ---
ENABLE_SUMMARY = False
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = "gpt-4o-mini"
LLM_BASE_URL = ""

# --- 推送渠道 ---
# 国内推荐：企业微信 > 邮件 > Telegram
ENABLE_EMAIL = False
ENABLE_WECOM = True
ENABLE_TELEGRAM = False

# 邮件 (推荐 QQ邮箱 / 163邮箱)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")      # QQ邮箱用授权码
MAIL_TO = os.getenv("MAIL_TO", "")

# 企业微信机器人 Webhook（国内首选）
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK", "")

# Telegram（国内需代理）
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")
