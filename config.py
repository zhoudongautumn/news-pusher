import os

CATEGORIES = ["世界要闻", "科技前沿", "金融财经", "综合"]

TIMEZONE = "Asia/Shanghai"
MAX_NEWS_PER_SOURCE = 10
MAX_NEWS_PER_CATEGORY = 10

RSS_CATEGORY_MAP = {
    "BBC News": "世界要闻",
    "NPR Topics: News": "世界要闻",
    "Reuters": "世界要闻",
    "The Guardian": "世界要闻",
    "Al Jazeera": "世界要闻",
    "路透": "世界要闻",
    "Ars Technica": "科技前沿",
    "MIT Technology Review": "科技前沿",
    "The Verge": "科技前沿",
    "IT之家": "科技前沿",
    "Hacker News": "科技前沿",
    "Reuters Business News": "金融财经",
    "MarketWatch.com - Top Stories": "金融财经",
    "CNBC": "金融财经",
    "Yahoo Finance": "金融财经",
    "Financial Times": "金融财经",
    "Wall Street Journal": "金融财经",
}

RSS_URL_CATEGORY_MAP = {
    "bbc": "世界要闻",
    "npr.org": "世界要闻",
    "reuters.com/world": "世界要闻",
    "theguardian.com": "世界要闻",
    "aljazeera": "世界要闻",
    "reuters.com/news": "世界要闻",
    "arstechnica": "科技前沿",
    "technologyreview.com": "科技前沿",
    "theverge.com": "科技前沿",
    "ithome": "科技前沿",
    "hnrss": "科技前沿",
    "openai.com": "科技前沿",
    "reuters.com/reuters/business": "金融财经",
    "marketwatch.com": "金融财经",
    "cnbc.com": "金融财经",
    "finance.yahoo.com": "金融财经",
    "ft.com": "金融财经",
    "wsj.com": "金融财经",
    "cls": "金融财经",
}

RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.npr.org/1004/rss.xml",
    "https://www.theguardian.com/world/rss",
    "http://cn.reuters.com/tools/rss/",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.technologyreview.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.ithome.com/rss/",
    "https://openai.com/blog/rss.xml",
    "https://hnrss.org/frontpage",
    "https://feeds.marketwatch.com/marketwatch/topstories/",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "https://finance.yahoo.com/news/rssindex",
    "https://rsshub.app/zhihu/hot",
]

ENABLE_HOTLIST = True
HOTLIST_SOURCES = ["cls", "zhihu"]

HOTLIST_CATEGORY_MAP = {
    "zhihu": "综合",
    "cls": "金融财经",
}

ENABLE_RSS = True
ENABLE_NEWSAPI = False

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
