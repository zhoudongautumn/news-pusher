"""邮件推送 (SMTP)"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crawlers.base import NewsItem


class EmailPusher:
    def __init__(self, host: str, port: int, user: str, passwd: str, to: str):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.to = to

    async def push(self, items: list[NewsItem], title: str = "📰 今日新闻推送"):
        if not items or not self.to:
            return

        html = f"<h2>{title}</h2><hr>"
        for i, it in enumerate(items, 1):
            html += f"<p><b>{i}. [{it.source}] {it.title}</b><br>"
            if it.summary:
                html += f"  {it.summary[:200]}<br>"
            if it.url:
                html += f'  <a href="{it.url}">阅读原文</a></p>'

        msg = MIMEMultipart("alternative")
        msg["Subject"] = title
        msg["From"] = self.user
        msg["To"] = self.to
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.passwd)
                server.sendmail(self.user, [self.to], msg.as_string())
            print(f"[Email] 推送成功 → {self.to}")
        except Exception as e:
            print(f"[Email] 推送失败: {e}")
