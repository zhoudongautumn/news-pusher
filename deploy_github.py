"""
新闻推送系统 — GitHub 部署助手
自动创建仓库 → 上传代码 → 配置 Secrets → 触发 Actions
用法: python deploy_github.py
"""

import os
import json
import base64
import getpass
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def api(method, path, data=None, token=""):
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "news-pusher-deploy",
    }
    body = json.dumps(data).encode() if data else None
    if body:
        headers["Content-Type"] = "application/json"

    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            text = resp.read().decode()
            return json.loads(text) if text else {}
    except HTTPError as e:
        text = e.read().decode()
        print(f"  ❌ API 错误 ({e.code}): {text[:200]}")
        return None
    except Exception as e:
        print(f"  ❌ 网络错误: {e}")
        return None


def get_files(base_dir):
    """遍历目录，返回 {path: content_bytes}"""
    files = {}
    base = os.path.abspath(base_dir)
    for root, dirs, fnames in os.walk(base):
        for fname in fnames:
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, base).replace("\\", "/")
            # 跳过 .git 目录
            if rel.startswith(".git") or rel.startswith("__pycache__"):
                continue
            with open(fpath, "rb") as f:
                files[rel] = f.read()
    return files


def encode_content(data: bytes) -> str:
    return base64.b64encode(data).decode()


def main():
    print("=" * 55)
    print("   📰 新闻推送系统 — GitHub 部署助手")
    print("=" * 55)

    # ---------- 1. Token ----------
    token = os.environ.get("GH_TOKEN") or getpass.getpass("🔑 输入 GitHub Personal Access Token: ").strip()
    if not token:
        print("❌ Token 不能为空")
        return

    # 验证 Token
    print("\n🔍 验证 Token...")
    user = api("GET", "/user", token=token)
    if not user or "login" not in user:
        print("❌ Token 无效，请检查权限（需要 repo + workflow）")
        return
    owner = user["login"]
    print(f"✅ 已认证: {owner}")

    # ---------- 2. 创建仓库 ----------
    print(f"\n🏗️  创建仓库 news-pusher...")
    repo_data = {
        "name": "news-pusher",
        "description": "📰 每日新闻推送系统 - 自建爬虫 + GitHub Actions 定时推送",
        "private": False,
        "auto_init": False,
    }
    repo = api("POST", "/user/repos", repo_data, token)
    if repo and "html_url" in repo:
        repo_url = repo["html_url"]
        default_branch = repo.get("default_branch", "main")
        print(f"✅ 仓库创建成功: {repo_url}")
    else:
        # 可能已存在
        repo = api("GET", f"/repos/{owner}/news-pusher", token=token)
        if repo and "html_url" in repo:
            repo_url = repo["html_url"]
            default_branch = repo.get("default_branch", "main")
            print(f"⚠️  仓库已存在: {repo_url}")
        else:
            print("❌ 创建仓库失败")
            return

    # ---------- 3. 获取当前分支 ----------
    print(f"\n📦 获取仓库信息...")
    branch = default_branch

    # 获取最新 commit（如果仓库是空的，先创建一个初始 commit）
    ref = api("GET", f"/repos/{owner}/news-pusher/git/ref/heads/{branch}", token=token)
    if ref and "object" in ref:
        latest_sha = ref["object"]["sha"]
        print(f"  当前最新 commit: {latest_sha[:8]}")
    else:
        # 空仓库，创建初始 commit
        print("  空仓库，创建初始 commit...")
        # 创建 blob（.gitkeep）
        blob = api("POST", f"/repos/{owner}/news-pusher/git/blobs", {"content": "", "encoding": "utf-8"}, token)
        if not blob:
            print("❌ 创建初始 blob 失败")
            return
        # 创建 tree
        tree = api("POST", f"/repos/{owner}/news-pusher/git/trees", {
            "tree": [{"path": ".gitkeep", "mode": "100644", "type": "blob", "sha": blob["sha"]}]
        }, token)
        if not tree:
            return
        # 创建 commit
        commit = api("POST", f"/repos/{owner}/news-pusher/git/commits", {
            "message": "🎉 init",
            "tree": tree["sha"],
        }, token)
        if not commit:
            return
        # 更新 ref
        api("PATCH", f"/repos/{owner}/news-pusher/git/refs/heads/{branch}", {
            "sha": commit["sha"], "force": True
        }, token)
        latest_sha = commit["sha"]
        print(f"✅ 初始 commit 创建: {latest_sha[:8]}")

    # ---------- 4. 上传文件 ----------
    print("\n📤 上传代码文件...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(script_dir, "news-pusher")
    if not os.path.isdir(project_dir):
        # 脚本可能在 news-pusher 目录内
        if os.path.isdir(os.path.join(script_dir, "main.py")):
            project_dir = script_dir
        else:
            print(f"❌ 找不到 news-pusher 项目目录（当前: {script_dir}）")
            print("   请把脚本放在 news-pusher/ 同目录下运行")
            return

    files = get_files(project_dir)
    print(f"   找到 {len(files)} 个文件")

    # 获取当前 tree 的 base
    latest_tree = api("GET", f"/repos/{owner}/news-pusher/git/trees/{latest_sha}", token=token)
    if not latest_tree:
        print("❌ 获取 tree 失败")
        return

    # 创建 blobs 并构建 tree items
    tree_items = []
    # 保留已有文件（除了 .gitkeep）
    if "tree" in latest_tree:
        for item in latest_tree["tree"]:
            if item["path"] != ".gitkeep":
                tree_items.append(item)

    for path, content in files.items():
        blob = api("POST", f"/repos/{owner}/news-pusher/git/blobs",
                   {"content": encode_content(content), "encoding": "base64"}, token)
        if not blob:
            print(f"  ⚠️  跳过 {path}")
            continue
        tree_items.append({
            "path": path,
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })

    # 创建新 tree
    new_tree = api("POST", f"/repos/{owner}/news-pusher/git/trees",
                   {"tree": tree_items, "base_tree": latest_tree.get("sha")}, token)
    if not new_tree:
        print("❌ 创建 tree 失败")
        return

    # 创建 commit
    commit = api("POST", f"/repos/{owner}/news-pusher/git/commits", {
        "message": "📰 每日新闻推送系统 - 初始代码",
        "tree": new_tree["sha"],
        "parents": [latest_sha],
    }, token)
    if not commit:
        return

    # 更新分支
    api("PATCH", f"/repos/{owner}/news-pusher/git/refs/heads/{branch}",
        {"sha": commit["sha"], "force": True}, token)
    print(f"✅ 代码上传完成 ({len(files)} 个文件)")
    print(f"   commit: {commit['sha'][:8]}")

    # ---------- 5. 配置 Secrets ----------
    print("\n" + "=" * 55)
    print("   🔐 配置推送渠道 Secrets")
    print("=" * 55)
    print("你需要至少配置一个推送渠道。以下是可选方式：")
    print()

    # 获取仓库公钥
    pubkey = api("GET", f"/repos/{owner}/news-pusher/actions/secrets/public-key", token=token)
    if not pubkey:
        print("⚠️  无法获取 Secrets 公钥，请稍后手动配置")
        print(f"   去这里配置: {repo_url}/settings/secrets/actions")
    else:
        print("✅ 已获取 Secrets 加密密钥")
        secrets_to_set = []

        # 询问推送渠道
        print("\n选择推送渠道 (输入编号，用逗号分隔，如 1,2):")
        print("  1. 企业微信机器人 (推荐，最简单)")
        print("  2. Telegram Bot")
        print("  3. SMTP 邮件")
        print("  0. 跳过，稍后手动配置")
        choice = input("> ").strip()

        if "1" in choice:
            webhook = input("  企业微信 Webhook URL: ").strip()
            if webhook:
                secrets_to_set.append(("WECOM_WEBHOOK", webhook))

        if "2" in choice:
            tg_token = input("  Telegram Bot Token: ").strip()
            chat_id = input("  Telegram Chat ID: ").strip()
            if tg_token:
                secrets_to_set.append(("TG_BOT_TOKEN", tg_token))
            if chat_id:
                secrets_to_set.append(("TG_CHAT_ID", chat_id))

        if "3" in choice:
            smtp_host = input("  SMTP 服务器 (如 smtp.gmail.com): ").strip()
            smtp_port = input("  SMTP 端口 (默认 587): ").strip() or "587"
            smtp_user = input("  SMTP 用户名: ").strip()
            smtp_pass = getpass.getpass("  SMTP 密码/应用密码: ").strip()
            mail_to = input("  接收邮箱: ").strip()
            if smtp_host:
                secrets_to_set.append(("SMTP_HOST", smtp_host))
                secrets_to_set.append(("SMTP_PORT", smtp_port))
            if smtp_user:
                secrets_to_set.append(("SMTP_USER", smtp_user))
            if smtp_pass:
                secrets_to_set.append(("SMTP_PASS", smtp_pass))
            if mail_to:
                secrets_to_set.append(("MAIL_TO", mail_to))

        if secrets_to_set:
            print(f"\n📤 正在设置 {len(secrets_to_set)} 个 Secret...")
            try:
                from nacl.bindings import crypto_box_seal
                has_nacl = True
            except ImportError:
                has_nacl = False
                # 尝试安装
                print("  ⚠️  需要 pynacl 库加密 Secrets")
                import subprocess
                subprocess.run(["pip", "install", "pynacl"], check=False)
                try:
                    from nacl.bindings import crypto_box_seal
                    has_nacl = True
                except ImportError:
                    has_nacl = False

            if has_nacl:
                import nacl.bindings
                import nacl.utils
                pubkey_bytes = base64.b64decode(pubkey["key"])
                pubkey_id = pubkey["key_id"]

                for name, value in secrets_to_set:
                    encrypted = nacl.bindings.crypto_box_seal(value.encode(), pubkey_bytes)
                    encrypted_b64 = base64.b64encode(encrypted).decode()
                    result = api("PUT", f"/repos/{owner}/news-pusher/actions/secrets/{name}", {
                        "encrypted_value": encrypted_b64,
                        "key_id": pubkey_id,
                    }, token)
                    if result is not None:
                        print(f"  ✅ {name} 已配置")
                    else:
                        print(f"  ❌ {name} 配置失败")
            else:
                print("  ⚠️  无法安装 pynacl，请手动配置 Secrets")
                print(f"    去: {repo_url}/settings/secrets/actions")
        else:
            print("  跳过 Secrets 配置")

    # ---------- 6. 触发 Actions ----------
    print(f"\n🎯 触发 Actions 工作流...")
    result = api("POST",
        f"/repos/{owner}/news-pusher/actions/workflows/push.yml/dispatches",
        {"ref": branch}, token)
    if result is not None:
        print("✅ 已触发！")
    else:
        print("⚠️  请手动触发: Actions → Run workflow")

    # ---------- 完成 ----------
    print("\n" + "=" * 55)
    print("   ✅ 部署完成！")
    print("=" * 55)
    print()
    print(f"📍 仓库地址:  {repo_url}")
    print(f"⏰ 每天早上 8:00 (UTC+8) 自动推送")
    print(f"📋 管理 Secrets: {repo_url}/settings/secrets/actions")
    print(f"⚡ 手动触发:   {repo_url}/actions")
    print()


if __name__ == "__main__":
    main()
