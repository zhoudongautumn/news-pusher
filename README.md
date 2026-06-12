# 📰 定时新闻推送系统

自建爬虫 + GitHub Actions 定时任务，每天自动抓取新闻并推送到指定渠道。

## 项目结构

```
news-pusher/
├── main.py                    # 主入口
├── config.py                  # 配置文件
├── requirements.txt           # Python 依赖
├── crawlers/
│   ├── base.py                # 新闻条目数据模型 & 爬虫基类
│   ├── rss.py                 # RSS 爬虫
│   └── hotlist.py             # 热搜爬虫 (知乎/微博/百度)
├── pushers/
│   ├── wecom.py               # 企业微信机器人推送
│   ├── telegram.py            # Telegram Bot 推送
│   └── email.py               # SMTP 邮件推送
├── summarizer.py              # LLM 摘要 (可选)
└── .github/workflows/push.yml # GitHub Actions 定时任务
```

## 快速开始

### 1. 克隆并安装依赖

```bash
cd news-pusher
pip install -r requirements.txt
```

### 2. 配置数据源和推送渠道

编辑 `config.py`，设置你要用的源和推送方式，或者通过环境变量注入。

### 3. 本地测试运行

```bash
python main.py
```

### 4. 配置 GitHub Actions 定时推送

1. 把代码推送到 GitHub 仓库
2. 在仓库 **Settings → Secrets and variables → Actions** 中添加需要的 Secrets
3. 推送渠道对应的 Secrets 参考下表

| Secret 名称 | 说明 | 必填 |
|------------|------|------|
| WECOM_WEBHOOK | 企业微信机器人 Webhook URL | 选填 |
| TG_BOT_TOKEN | Telegram Bot Token | 选填 |
| TG_CHAT_ID | Telegram 聊天 ID | 选填 |
| SMTP_HOST | SMTP 服务器地址 | 选填 |
| SMTP_PORT | SMTP 端口 | 选填 |
| SMTP_USER | SMTP 用户名 | 选填 |
| SMTP_PASS | SMTP 密码/应用密码 | 选填 |
| MAIL_TO | 接收邮箱 | 选填 |
| LLM_API_KEY | LLM API Key (摘要功能) | 选填 |
| NEWSAPI_KEY | NewsAPI Key | 选填 |

### 5. 手动触发

在 GitHub Actions 页面点击 **Run workflow** 即可手动推送一次。

## 数据源说明

- **RSS**: 默认内置 HackerNews、TheHackersNews、知乎、少数派等源，可在 `config.py` 中增删
- **热搜**: 知乎热榜、微博热搜、百度热搜
- **NewsAPI**: 需要自行申请 API Key (https://newsapi.org)

## 推送渠道

- ✅ 企业微信机器人 — 群聊中添加机器人即可
- ✅ Telegram Bot — 创建 Bot 并获取 Chat ID
- ✅ 邮件 — 支持任意 SMTP 服务 (Gmail/QQ/163 等)
- 更多渠道欢迎 PR

## 自定义

- 在 `crawlers/` 中添加新的爬虫类，继承 `BaseCrawler` 即可
- 在 `pushers/` 中添加新的推送类，实现 `push(items, title)` 方法即可
- 在 `config.py` 中注册开关和配置项
