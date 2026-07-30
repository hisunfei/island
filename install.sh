#!/bin/bash
# Island Skill 安装脚本

set -e

WORKSPACE="$HOME/.openclaw/workspace"
SKILL_SOURCE="$(cd "$(dirname "$0")" && pwd)"
SKILL_TARGET="$WORKSPACE/skills/island"
MEMORY_FILE="$WORKSPACE/memory/island.md"

echo "🏝️  Island Skill 安装"
echo "===================="
echo

# 1. 检查是否已安装
if [ -d "$SKILL_TARGET" ] && [ -f "$MEMORY_FILE" ]; then
    echo "⚠️  Island 似乎已经安装"
    echo "   Skill 位置: $SKILL_TARGET"
    echo "   Memory 位置: $MEMORY_FILE"
    echo
    read -p "是否重新安装？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消安装"
        exit 0
    fi
fi

# 2. 复制 skill 文件
echo "📦 复制 skill 文件..."
mkdir -p "$SKILL_TARGET"
cp "$SKILL_SOURCE/SKILL.md" "$SKILL_TARGET/"
cp "$SKILL_SOURCE/README.md" "$SKILL_TARGET/"
mkdir -p "$SKILL_TARGET/assets"
cp "$SKILL_SOURCE/assets/spots_builtin.json" "$SKILL_TARGET/assets/"
echo "✅ Skill 文件已复制到 $SKILL_TARGET"
echo

# 3. 生成 island_id
ISLAND_ID="island_$(openssl rand -hex 4)"
echo "🆔 生成 Island ID: $ISLAND_ID"
echo

# 4. 选择 emoji
echo "🎨 选择你的 agent emoji:"
echo "  1) 🐶 狗"
echo "  2) 🐱 猫"
echo "  3) 🦊 狐狸"
echo "  4) 🐻 熊"
echo "  5) 🐼 熊猫"
echo "  6) 🐨 考拉"
echo "  7) 🦁 狮子"
echo "  8) 🐯 老虎"
echo "  9) 自定义"
echo
read -p "选择 (1-9, 默认 1): " EMOJI_CHOICE
EMOJI_CHOICE=${EMOJI_CHOICE:-1}

case $EMOJI_CHOICE in
    1) EMOJI="🐶" ;;
    2) EMOJI="🐱" ;;
    3) EMOJI="🦊" ;;
    4) EMOJI="🐻" ;;
    5) EMOJI="🐼" ;;
    6) EMOJI="🐨" ;;
    7) EMOJI="🦁" ;;
    8) EMOJI="🐯" ;;
    9) 
        read -p "输入自定义 emoji: " EMOJI
        ;;
    *) EMOJI="🐶" ;;
esac

echo "✅ 选择 emoji: $EMOJI"
echo

# 5. 创建 memory 文件
echo "📝 初始化 memory..."
mkdir -p "$WORKSPACE/memory"

cat > "$MEMORY_FILE" << EOF
## Island

### 配置
- island_id: $ISLAND_ID
- emoji: $EMOJI
- github_configured: false
- auto_travel: false
- installed_at: $(date -u +"%Y-%m-%dT%H:%M:%S+08:00")

### 明信片收藏

（暂无）

### 我的信息卡片（最新）

（暂无）
EOF

echo "✅ Memory 已初始化: $MEMORY_FILE"
echo

# 6. GitHub 配置（自动检测）
echo "🔗 GitHub 配置（可选）"
echo "   配置 GitHub 后可以："
echo "   - 与其他 agent 交换信息卡片"
echo "   - 访问更多认证景点"
echo

# 运行自动检测脚本
echo "🔍 检测 GitHub 访问权限..."
DETECT_RESULT=$(bash "$SKILL_SOURCE/scripts/detect_github_auth.sh" 2>/dev/null || echo '{"detected": false, "method": "none", "username": "none", "message": "检测脚本执行失败"}')

DETECTED=$(echo "$DETECT_RESULT" | grep -o '"detected": [a-z]*' | cut -d' ' -f2)
METHOD=$(echo "$DETECT_RESULT" | grep -o '"method": "[^"]*"' | cut -d'"' -f4)
USERNAME=$(echo "$DETECT_RESULT" | grep -o '"username": "[^"]*"' | cut -d'"' -f4)
MESSAGE=$(echo "$DETECT_RESULT" | grep -o '"message": "[^"]*"' | cut -d'"' -f4)

if [ "$DETECTED" = "true" ]; then
    echo "✅ $MESSAGE"
    echo "   用户: $USERNAME"
    echo "   方式: $METHOD"
    echo
    
    # 更新 memory 文件
    sed -i.bak "s/github_configured: false/github_configured: true/" "$MEMORY_FILE"
    cat >> "$MEMORY_FILE" << EOF

### GitHub
- method: $METHOD
- username: $USERNAME
- configured_at: $(date -u +"%Y-%m-%dT%H:%M:%S+08:00")
EOF
    
    echo "✅ GitHub 已自动配置，无需额外操作"
else
    echo "⚠️  未检测到 GitHub 访问权限"
    echo
    echo "   请选择配置方式："
    echo "   1) 使用 gh CLI 登录（推荐）"
    echo "   2) 手动提供 GitHub PAT"
    echo "   3) 跳过（只用内置景点）"
    echo
    read -p "选择 (1-3, 默认 3): " CONFIG_CHOICE
    CONFIG_CHOICE=${CONFIG_CHOICE:-3}
    echo
    
    case $CONFIG_CHOICE in
        1)
            echo "📦 启动 gh CLI 登录..."
            if command -v gh &> /dev/null; then
                gh auth login
                if gh auth status &> /dev/null; then
                    USERNAME=$(gh api user -q .login 2>/dev/null || echo "unknown")
                    sed -i.bak "s/github_configured: false/github_configured: true/" "$MEMORY_FILE"
                    cat >> "$MEMORY_FILE" << EOF

### GitHub
- method: gh_cli
- username: $USERNAME
- configured_at: $(date -u +"%Y-%m-%dT%H:%M:%S+08:00")
EOF
                    echo "✅ gh CLI 登录成功"
                else
                    echo "❌ 登录失败，跳过 GitHub 配置"
                fi
            else
                echo "❌ gh CLI 未安装"
                echo "   安装方法: brew install gh"
                echo "   跳过 GitHub 配置"
            fi
            ;;
        2)
            echo "   创建 GitHub Personal Access Token："
            echo "   1. 前往 https://github.com/settings/tokens"
            echo "   2. 点击 'Generate new token (classic)'"
            echo "   3. 不需要勾选任何权限（公开 repo 的 issue 不需要特殊权限）"
            echo "   4. 复制生成的 token（格式：ghp_xxxxx）"
            echo
            read -p "输入 GitHub PAT: " GITHUB_PAT
            
            if [[ $GITHUB_PAT == ghp_* ]]; then
                sed -i.bak "s/github_configured: false/github_configured: true/" "$MEMORY_FILE"
                cat >> "$MEMORY_FILE" << EOF

### GitHub
- method: manual_pat
- pat: $GITHUB_PAT
- configured_at: $(date -u +"%Y-%m-%dT%H:%M:%S+08:00")
EOF
                echo "✅ GitHub 已配置"
                echo "⚠️  注意：PAT 已存储在 memory 中，请注意安全"
            else
                echo "❌ PAT 格式不正确（应该以 ghp_ 开头）"
                echo "   跳过 GitHub 配置"
            fi
            ;;
        *)
            echo "⏭️  跳过 GitHub 配置（你可以之后再说 '配置 GitHub' 来设置）"
            ;;
    esac
fi
echo

# 7. 自动旅行
echo "⏰ 自动旅行（可选）"
echo "   设置后，agent 会每天自动旅行一次，带回明信片"
echo
read -p "是否设置自动旅行？(y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i.bak "s/auto_travel: false/auto_travel: true/" "$MEMORY_FILE"
    echo "✅ 自动旅行已启用"
    echo "💡 提示：你可以对 agent 说 '关闭自动旅行' 来禁用"
    echo "⚠️  注意：需要在 OpenClaw 中手动创建 cron 任务"
else
    echo "⏭️  跳过自动旅行（你可以之后再说 '设置自动旅行' 来启用）"
fi
echo

# 8. 完成
echo "🎉 安装完成！"
echo
echo "📋 安装摘要："
echo "   Island ID: $ISLAND_ID"
echo "   Emoji: $EMOJI"
echo "   Skill 位置: $SKILL_TARGET"
echo "   Memory 位置: $MEMORY_FILE"
echo
echo "🎮 使用方法："
echo "   - '去旅行' - 立即触发一次旅行"
echo "   - '看看明信片' - 查看收集的明信片"
echo "   - '我的卡片' - 查看当前的信息卡片"
echo "   - 'Island 设置' - 配置选项"
echo
echo "🏝️  祝你旅途愉快！"
