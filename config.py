import os

TIMEZONE = "Asia/Shanghai"
MAX_NEWS_PER_SOURCE = 10

ENABLE_RSS = True
ENABLE_HOTLIST = False
ENABLE_NEWSAPI = False

RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://www.v2ex.com/index.xml",
    "https://openai.com/blog/rss.xml",
    "https://deepmind.google/blog/rss/",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://sspai.com/feed",
    "https://www.ithome.com/rss/",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://edition.cnn.com/services/rss/",
    "https://feeds.npr.org/1004/rss.xml",
    "https://www.theguardian.com/us-news/rss",
    "https://www.bloomberg.com/feed/site/news",
    "https://www.ftchinese.com/rss/feed",
    "https://wallstreetcn.com/rss",
    "https://www.reutersagency.com/feed/",
    "http://www.xinhuanet.com/rss/",
]

ENABLE_EMAIL = False
ENABLE_FEISHU = True
ENABLE_TELEGRAM = False

FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
MAIL_TO = os.getenv("MAIL_TO", "")

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")
