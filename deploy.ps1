<#
.SYNOPSIS
  新闻推送系统一键部署到 GitHub
.DESCRIPTION
  初始化 git → 创建 GitHub 仓库 → 推送代码 → 配置 Secrets → 触发 Actions
#>

$ErrorActionPreference = "Stop"
$RepoName = "news-pusher"
$ProjectDir = Split-Path -Parent $PSScriptRoot
$PushBranch = "main"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  📰 新闻推送系统 — 一键部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------- 检查依赖 ----------
Write-Host "🔍 检查环境依赖..." -ForegroundColor Yellow
$hasGit = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
$hasGh  = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)

if (-not $hasGit) {
    Write-Host "❌ 未安装 git。请先安装: https://git-scm.com/downloads" -ForegroundColor Red
    exit 1
}
if (-not $hasGh) {
    Write-Host "❌ 未安装 GitHub CLI。请先安装: winget install --id GitHub.cli" -ForegroundColor Red
    Write-Host "   或手动下载: https://cli.github.com/" -ForegroundColor Red
    exit 1
}

# ---------- 检查 gh 登录 ----------
Write-Host "🔍 检查 GitHub CLI 登录状态..." -ForegroundColor Yellow
$ghStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  未登录 GitHub。正在打开浏览器登录..." -ForegroundColor Yellow
    gh auth login --web -h github.com
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 登录失败" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ GitHub CLI 已登录" -ForegroundColor Green

# ---------- 获取用户信息 ----------
$ghUser = gh api user --jq ".login" 2>$null
Write-Host "👤 GitHub 用户: $ghUser" -ForegroundColor Cyan

# ---------- 初始化 git ----------
Write-Host ""
Write-Host "📦 初始化 Git 仓库..." -ForegroundColor Yellow
Set-Location $ProjectDir

if (Test-Path ".git") {
    Write-Host "  已存在 .git，跳过初始化" -ForegroundColor Gray
} else {
    git init
    git checkout -b $PushBranch
}

git add -A
git commit --allow-empty -m "🎉 init: 每日新闻推送系统"

# ---------- 创建 GitHub 仓库 ----------
Write-Host ""
Write-Host "🏗️  创建 GitHub 仓库 $RepoName ..." -ForegroundColor Yellow
$repoExists = gh repo view "$ghUser/$RepoName" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  仓库已存在，跳过创建" -ForegroundColor Gray
} else {
    gh repo create $RepoName --public --push --remote origin --source .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 创建仓库失败" -ForegroundColor Red
        exit 1
    }
}

# ---------- 推送代码 ----------
Write-Host ""
Write-Host "🚀 推送代码到 GitHub..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/$ghUser/$RepoName.git"
if (-not (git remote get-url origin 2>$null)) {
    git remote add origin $remoteUrl
}
git push -u origin $PushBranch

# ---------- 设置 Secrets（引导）----------
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🔐 配置推送渠道 Secrets" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "你需要至少配置一个推送渠道，新闻才能发出来。"
Write-Host "推荐先配「企业微信机器人」，5 分钟搞定。"
Write-Host ""

$choices = @(
    [System.Management.Automation.Host.ChoiceDescription]::new("&企业微信", "企业微信群机器人")
    [System.Management.Automation.Host.ChoiceDescription]::new("&Telegram", "Telegram Bot")
    [System.Management.Automation.Host.ChoiceDescription]::new("&邮件", "SMTP 邮件")
    [System.Management.Automation.Host.ChoiceDescription]::new("&跳过", "稍后手动配置")
)
$choice = $Host.UI.PromptForChoice("推送渠道", "请选择要配置的推送渠道：", $choices, 3)

switch ($choice) {
    0 {
        $webhook = Read-Host "🔗 输入企业微信机器人 Webhook URL"
        if ($webhook) {
            gh secret set WECOM_WEBHOOK --repo "$ghUser/$RepoName" --body "$webhook"
            Write-Host "✅ WECOM_WEBHOOK 已配置" -ForegroundColor Green
        }
    }
    1 {
        $token = Read-Host -AsSecureString "🤖 输入 Telegram Bot Token"
        $chatId = Read-Host "💬 输入 Chat ID"
        $tokenStr = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
        )
        if ($tokenStr) { gh secret set TG_BOT_TOKEN --repo "$ghUser/$RepoName" --body "$tokenStr" }
        if ($chatId) { gh secret set TG_CHAT_ID --repo "$ghUser/$RepoName" --body "$chatId" }
        Write-Host "✅ Telegram 配置完成" -ForegroundColor Green
    }
    2 {
        $smtpHost = Read-Host "📧 SMTP 服务器 (如 smtp.gmail.com)"
        $smtpPort = Read-Host "🔌 端口 (默认 587)"
        $smtpUser = Read-Host "👤 用户名"
        $smtpPass = Read-Host -AsSecureString "🔑 密码/应用密码"
        $mailTo   = Read-Host "📨 接收邮箱"
        $passStr = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($smtpPass)
        )
        if ($smtpHost) { gh secret set SMTP_HOST --repo "$ghUser/$RepoName" --body "$smtpHost" }
        if ($smtpPort) { gh secret set SMTP_PORT --repo "$ghUser/$RepoName" --body "$smtpPort" }
        if ($smtpUser) { gh secret set SMTP_USER --repo "$ghUser/$RepoName" --body "$smtpUser" }
        if ($passStr)  { gh secret set SMTP_PASS --repo "$ghUser/$RepoName" --body "$passStr" }
        if ($mailTo)   { gh secret set MAIL_TO --repo "$ghUser/$RepoName" --body "$mailTo" }
        Write-Host "✅ 邮件配置完成" -ForegroundColor Green
    }
}

# ---------- 手动触发 Actions ----------
Write-Host ""
Write-Host "🎯 手动触发一次工作流..." -ForegroundColor Yellow
gh workflow run push.yml --repo "$ghUser/$RepoName" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 已触发！去查看运行状态:" -ForegroundColor Green
    Write-Host "   https://github.com/$ghUser/$RepoName/actions" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  触发失败，请手动去 Actions 页面执行" -ForegroundColor Yellow
}

# ---------- 完成 ----------
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 仓库地址:" -ForegroundColor Cyan
Write-Host "   https://github.com/$ghUser/$RepoName" -ForegroundColor White
Write-Host ""
Write-Host "⏰ 定时推送: 每天早上 8:00 (UTC+8) 自动运行" -ForegroundColor Cyan
Write-Host "   也可手动触发: Actions → Run workflow" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 管理 Secrets:" -ForegroundColor Gray
Write-Host "   https://github.com/$ghUser/$RepoName/settings/secrets/actions" -ForegroundColor Gray
