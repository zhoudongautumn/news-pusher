import os

TIMEZONE = "Asia/Shanghai"
PER_SOURCE = 10
PER_SUBCAT = 8

# ============================================================
# 分类结构：8 个子类
# ============================================================
ALL_CATS = [
    "国内经济", "国内科技", "国内军事", "国内综合",
    "国际经济", "国际科技", "国际军事", "国际综合",
]

# 区域分组（推送用）
REGIONS = {
    "国内": ["国内经济", "国内科技", "国内军事", "国内综合"],
    "国际": ["国际经济", "国际科技", "国际军事", "国际综合"],
}

# ============================================================
# RSS 源：(url, category)
# ============================================================
RSS_FEEDS = [
    # === 国内 ===
    ("https://rsshub.app/people/xhs", "国内综合"),           # 人民日报
    ("https://rsshub.app/xinhua/news", "国内综合"),          # 新华社
    ("https://rsshub.app/cecn", "国内经济"),                 # 经济日报
    ("https://rsshub.app/cls/hot", "国内经济"),              # 财联社
    ("http://www.stdaily.com/rss/", "国内科技"),             # 科技日报
    ("https://www.ithome.com/rss/", "国内科技"),             # IT之家
    ("https://rsshub.app/huanqiu/mil", "国内军事"),          # 环球网军事
    ("https://rsshub.app/zhihu/hot", "国内综合"),            # 知乎热榜
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

# ============================================================
# 热搜：(name, category)
# ============================================================
ENABLE_HOTLIST = True
HOTLIST_SOURCES = [
    ("cls", "国内经济"),
    ("zhihu", "国内综合"),
]

# ============================================================
# 开关
# ============================================================
ENABLE_RSS = True

# LLM
ENABLE_SUMMARY = True
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

# 推送
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
