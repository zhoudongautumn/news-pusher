import os

TIMEZONE = "Asia/Shanghai"
PER_SOURCE = 10
PER_SUBCAT = 8

ALL_CATS = [
    "国内经济", "国内科技", "国内军事", "国内综合",
    "国际经济", "国际科技", "国际军事", "国际综合",
]

REGIONS = {
    "国内": ["国内经济", "国内科技", "国内军事", "国内综合"],
    "国际": ["国际经济", "国际科技", "国际军事", "国际综合"],
}

RSS_FEEDS = [
    # === 国内 ===
    ("https://www.ithome.com/rss/", "国内科技"),
    ("https://www.36kr.com/feed", "国内科技"),
    # === 国际 ===
    ("http://feeds.bbci.co.uk/news/world/rss.xml", "国际综合"),
    ("https://feeds.npr.org/1004/rss.xml", "国际综合"),
    ("https://www.theguardian.com/world/rss", "国际综合"),
    ("http://cn.reuters.com/tools/rss/", "国际综合"),
    ("https://feeds.marketwatch.com/marketwatch/topstories/", "国际经济"),
    ("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "国际经济"),
    ("https://finance.yahoo.com/news/rssindex", "国际经济"),
    ("https://feeds.arstechnica.com/arstechnica/index", "国际科技"),
    ("https://www.technologyreview.com/feed/", "国际科技"),
    ("https://www.theverge.com/rss/index.xml", "国际科技"),
    ("https://openai.com/blog/rss.xml", "国际科技"),
    ("https://hnrss.org/frontpage", "国际科技"),
    ("https://www.defensenews.com/arc/outboundfeeds/vdr-cat/?outputType=xml", "国际军事"),
]

ENABLE_HOTLIST = True
HOTLIST_SOURCES = [
    ("cls", "国内经济"),
    ("zhihu", "国内综合"),
]

ENABLE_RSS = True

ENABLE_SUMMARY = True
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

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
