#!/bin/bash
# GitHub 认证自动检测脚本
# 按优先级检测 GitHub 访问权限

set -e

# 输出 JSON 结果
output_json() {
    local detected=$1
    local method=$2
    local username=$3
    local message=$4
    
    cat << EOF
{
  "detected": $detected,
  "method": "$method",
  "username": "$username",
  "message": "$message"
}
EOF
}

# 优先级 1: 检查 gh CLI
check_gh_cli() {
    if command -v gh &> /dev/null; then
        # 检查 gh 是否已登录
        if gh auth status &> /dev/null; then
            username=$(gh api user -q .login 2>/dev/null || echo "unknown")
            output_json "true" "gh_cli" "$username" "已检测到 gh CLI 登录"
            exit 0
        fi
    fi
}

# 优先级 2: 检查环境变量
check_env_vars() {
    for var in GITHUB_TOKEN GH_TOKEN GITHUB_PAT; do
        if [ -n "${!var}" ]; then
            # 尝试验证 token 是否有效
            username=$(curl -s -H "Authorization: token ${!var}" \
                https://api.github.com/user 2>/dev/null | \
                grep -o '"login":"[^"]*"' | \
                cut -d'"' -f4 || echo "unknown")
            
            if [ "$username" != "unknown" ] && [ -n "$username" ]; then
                output_json "true" "env_$var" "$username" "已在环境变量中找到 $var"
                exit 0
            fi
        fi
    done
}

# 优先级 3: 检查配置文件
check_config_files() {
    # 检查 ~/.netrc
    if [ -f "$HOME/.netrc" ]; then
        if grep -q "github.com" "$HOME/.netrc" 2>/dev/null; then
            output_json "true" "netrc" "unknown" "已在 ~/.netrc 中找到 GitHub credentials"
            exit 0
        fi
    fi
    
    # 检查 gh CLI 配置文件
    if [ -f "$HOME/.config/gh/hosts.yml" ]; then
        if grep -q "github.com" "$HOME/.config/gh/hosts.yml" 2>/dev/null; then
            output_json "true" "gh_config" "unknown" "已在 gh CLI 配置中找到 GitHub 认证"
            exit 0
        fi
    fi
}

# 按优先级检测
check_gh_cli
check_env_vars
check_config_files

# 未检测到
output_json "false" "none" "none" "未检测到 GitHub 访问权限"
