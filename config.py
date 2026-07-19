import os

TIMEZONE = "Asia/Shanghai"
PER_SOURCE = 10
PER_SUBCAT = 8

ALL_CATS = [
    "国内科技", "国内经济", "国内军事", "国内综合",
    "国际科技", "国际经济", "国际军事", "国际综合",
]

REGIONS = {
    "国内": ["国内科技", "国内经济", "国内军事", "国内综合"],
    "国际": ["国际科技", "国际经济", "国际军事", "国际综合"],
}

RSS_FEEDS = [
    # === 国内科技 ===
    ("https://www.ithome.com/rss/", "国内科技"),
    ("https://www.36kr.com/feed", "国内科技"),
    ("https://www.scmp.com/rss/36/feed", "国内科技"),
    # === 国内经济 ===
    ("http://www.chinadaily.com.cn/rss/china_rss.xml", "国内经济"),
    ("https://www.scmp.com/rss/4/feed", "国内经济"),
    # === 国内军事 ===
    ("https://thediplomat.com/feed/", "国内军事"),
    # === 国内综合 ===
    ("https://feedx.net/rss/people.xml", "国内综合"),
    ("https://feedx.net/rss/sina.xml", "国内综合"),
    ("https://www.cgtn.com/subscribe/rss/section/world.xml", "国内综合"),
    ("http://www.xinhuanet.com/english/rss/worldrss.xml", "国内综合"
    ("https://www.scmp.com/rss/3/feed", "国内综合"),
    # === 国际综合 ===
    ("http://feeds.bbci.co.uk/news/world/rss.xml", "国际综合"),
    ("https://feeds.npr.org/1004/rss.xml", "国际综合"),
    ("https://www.theguardian.com/world/rss", "国际综合"),
    ("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "国际综合"),
    # === 国际科技 ===
    ("https://feeds.arstechnica.com/arstechnica/index", "国际科技"),
    ("https://www.technologyreview.com/feed/", "国际科技"),
    ("https://www.theverge.com/rss/index.xml", "国际科技"),
    ("https://www.wired.com/feed/rss", "国际科技"),
    ("https://hnrss.org/frontpage", "国际科技"),
    # === 国际经济 ===
    ("https://finance.yahoo.com/news/rssindex", "国际经济"),
    ("https://feeds.marketwatch.com/marketwatch/topstories/", "国际经济"),
    ("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "国际经济"),
    # === 国际军事 ===
    ("https://www.defensenews.com/arc/outboundfeeds/vdr-cat/?outputType=xml", "国际军事"),
]

ENABLE_HOTLIST = True
HOTLIST_SOURCES = [
    ("cls", "国内经济"),
    ("eastmoney", "国内经济"),
    ("sina_finance", "国内经济"),
    ("zhihu", "国内综合"),
    ("baidu", "国内综合"),
]

ENABLE_RSS = True

ENABLE_SUMMARY = True
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

ENABLE_EMAIL = False
ENABLE_FEISHU = True
ENABLE_WECOM = False
ENABLE_TELEGRAM = False

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "465")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
MAIL_TO = os.getenv("MAIL_TO", "")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")