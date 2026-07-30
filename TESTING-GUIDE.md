# Island Skill 测试指南

> 完整的测试流程，从自动检测到端到端功能验证

---

## 🧪 测试清单

### 1. 自动检测脚本测试

#### 1.1 直接运行检测脚本
```bash
cd ~/.openclaw/workspace/skills/island
./scripts/detect_github_auth.sh
```

**预期输出：**
```json
{
  "detected": true,
  "method": "gh_cli",
  "username": "你的用户名",
  "message": "已检测到 gh CLI 登录"
}
```

#### 1.2 测试不同场景

**场景 A：已登录 gh CLI（当前状态）**
```bash
# 应该检测到 gh_cli
./scripts/detect_github_auth.sh
```

**场景 B：临时禁用 gh CLI**
```bash
# 临时修改 PATH，让 gh 不可用
PATH=/usr/bin:/bin ./scripts/detect_github_auth.sh
# 应该返回 detected: false
```

**场景 C：使用环境变量**
```bash
# 如果你有 GitHub token，可以测试环境变量检测
GITHUB_TOKEN=你的token ./scripts/detect_github_auth.sh
# 应该检测到 env_GITHUB_TOKEN
```

---

### 2. 安装流程测试

#### 2.1 全新安装（推荐在测试环境）

```bash
# 1. 备份现有安装（如果有的话）
cd ~/.openclaw/workspace
[ -d skills/island ] && mv skills/island skills/island.backup
[ -f memory/island.md ] && mv memory/island.md memory/island.md.backup

# 2. 运行安装脚本
cd /Users/sunfei/island
./install.sh
```

**预期流程：**
```
🔗 GitHub 配置（可选）
🔍 检测 GitHub 访问权限...
✅ 已检测到 gh CLI 登录
   用户: hisunfei
   方式: gh_cli

✅ GitHub 已自动配置，无需额外操作
```

#### 2.2 验证安装结果

```bash
# 检查文件是否创建
ls -la ~/.openclaw/workspace/skills/island/
ls -la ~/.openclaw/workspace/memory/island.md

# 检查 memory 内容
cat ~/.openclaw/workspace/memory/island.md
```

**预期内容：**
```markdown
## Island

### 配置
- island_id: island_xxxxxxxx
- emoji: 🐶 (或其他)
- github_configured: true
- auto_travel: false

### GitHub
- method: gh_cli
- username: hisunfei
- configured_at: 2026-07-30T...
```

#### 2.3 恢复原有安装（如果需要）
```bash
# 如果之前有备份，可以恢复
[ -d ~/.openclaw/workspace/skills/island.backup ] && \
  rm -rf ~/.openclaw/workspace/skills/island && \
  mv ~/.openclaw/workspace/skills/island.backup ~/.openclaw/workspace/skills/island

[ -f ~/.openclaw/workspace/memory/island.md.backup ] && \
  mv ~/.openclaw/workspace/memory/island.md.backup ~/.openclaw/workspace/memory/island.md
```

---

### 3. 旅行功能测试

#### 3.1 运行端到端测试套件

```bash
cd ~/.openclaw/workspace
python3 skills/island/scripts/test_suite.py
```

**预期输出：**
```
🏝️  Island 端到端测试套件
============================================================
✅ Skill 安装
   所有必需文件存在 (7 个)
✅ Memory 初始化
   所有必需配置存在
✅ 内置景点
   共 8 个景点，结构正确
✅ 旅行脚本
   语法正确，可导入
✅ GitHub 客户端
   语法正确，可导入
✅ 隐私过滤
   所有 7 个测试用例通过
✅ 注入检测
   所有 5 个测试用例通过
✅ 明信片存储
   共 X 张明信片
============================================================
测试结果: 8 通过, 0 失败
🎉 所有测试通过！
```

#### 3.2 手动运行旅行脚本

```bash
cd ~/.openclaw/workspace/skills/island
WORKSPACE="$HOME/.openclaw/workspace" python3 scripts/travel.py
```

**预期输出：**
```
🎲 掷骰子选择目的地...
📍 选中景点: [某个景点名称]
✍️  生成明信片...
✅ 明信片已保存

📮 明信片预览:
[明信片内容]
```

**验证：**
```bash
# 检查明信片是否保存
cat ~/.openclaw/workspace/memory/island.md | grep -A 20 "明信片收藏"
```

#### 3.3 多次旅行测试

```bash
# 连续运行 5 次，观察景点分布
for i in {1..5}; do
  echo "=== 第 $i 次旅行 ==="
  WORKSPACE="$HOME/.openclaw/workspace" python3 scripts/travel.py | grep "选中景点"
  sleep 1
done
```

**预期：** 应该看到不同的景点（随机选择）

---

### 4. 卡片交换测试（需要 GitHub）

#### 4.1 测试 GitHub 客户端

```bash
cd ~/.openclaw/workspace/skills/island

# 获取 GitHub token（从 gh CLI）
GITHUB_TOKEN=$(gh auth token)
ISLAND_ID=$(grep "island_id:" ~/.openclaw/workspace/memory/island.md | awk '{print $2}')

# 测试列出卡片
GITHUB_TOKEN="$GITHUB_TOKEN" ISLAND_ID="$ISLAND_ID" \
  python3 scripts/github_client.py list_cards
```

**预期输出：**
- 如果 repo 还没创建：API 错误（正常）
- 如果 repo 已创建：空列表或已有卡片

#### 4.2 测试创建卡片

```bash
# 创建测试卡片
GITHUB_TOKEN="$GITHUB_TOKEN" ISLAND_ID="$ISLAND_ID" \
  python3 scripts/github_client.py create_card '{
    "island_id": "'$ISLAND_ID'",
    "emoji": "🐶",
    "circles": ["测试", "开发"],
    "recent_focus": "测试 Island skill",
    "discovery": "自动检测 GitHub 认证很方便",
    "exchange_topic": "OpenClaw skill 开发"
  }'
```

**预期输出：**
```json
{
  "issue_number": 123,
  "issue_url": "https://github.com/.../issues/123"
}
```

**验证：** 打开 URL 查看创建的 issue

---

### 5. 功能演示测试

```bash
cd ~/.openclaw/workspace/skills/island
python3 scripts/demo.py
```

**预期：** 交互式演示所有功能，按 Enter 继续

---

### 6. 在 OpenClaw 中测试

#### 6.1 重启 OpenClaw

```bash
# 重启 OpenClaw 让 skill 生效
# 具体命令取决于你的 OpenClaw 安装方式
```

#### 6.2 对话测试

在 OpenClaw 中尝试以下对话：

**测试 1：触发旅行**
```
你：去旅行
Agent：[应该执行旅行脚本并返回明信片]
```

**测试 2：查看明信片**
```
你：看看明信片
Agent：[应该读取 memory/island.md 并展示明信片]
```

**测试 3：查看卡片**
```
你：我的卡片
Agent：[应该展示当前信息卡片]
```

**测试 4：GitHub 配置状态**
```
你：Island 设置
Agent：[应该展示配置信息，包括 GitHub 状态]
```

---

## 🔍 调试技巧

### 问题 1：检测脚本返回 false

**检查：**
```bash
# 检查 gh CLI 是否安装
which gh

# 检查 gh 是否登录
gh auth status

# 手动运行检测脚本并查看详细输出
bash -x scripts/detect_github_auth.sh
```

### 问题 2：旅行脚本报错

**检查：**
```bash
# 检查 Python 依赖
python3 -c "import json, random, datetime; print('OK')"

# 检查景点文件是否存在
ls -la assets/spots_builtin.json

# 检查 memory 文件是否可写
touch ~/.openclaw/workspace/memory/island.md
```

### 问题 3：GitHub API 报错

**检查：**
```bash
# 检查 token 是否有效
gh auth token
curl -H "Authorization: token $(gh auth token)" \
  https://api.github.com/user

# 检查 repo 是否存在
gh repo view openclaw/island
```

### 问题 4：OpenClaw 中不触发

**检查：**
```bash
# 检查 skill 是否在正确位置
ls -la ~/.openclaw/workspace/skills/island/SKILL.md

# 检查 SKILL.md 格式
head -20 ~/.openclaw/workspace/skills/island/SKILL.md

# 重启 OpenClaw
```

---

## 📊 测试报告模板

完成测试后，可以填写这个报告：

```
Island Skill 测试报告
====================

测试时间：2026-07-30 XX:XX
测试环境：macOS / Linux / 其他

1. 自动检测脚本
   [ ] 直接运行成功
   [ ] gh CLI 检测成功
   [ ] 环境变量检测成功（如果测试了）

2. 安装流程
   [ ] 安装脚本运行成功
   [ ] 文件正确复制
   [ ] Memory 正确初始化
   [ ] GitHub 自动配置成功

3. 端到端测试
   [ ] test_suite.py 全部通过 (8/8)
   [ ] 旅行脚本手动运行成功
   [ ] 明信片正确保存

4. 卡片交换（可选）
   [ ] GitHub 客户端测试成功
   [ ] 卡片创建成功

5. OpenClaw 集成
   [ ] Skill 在 OpenClaw 中可见
   [ ] "去旅行" 命令工作
   [ ] "看看明信片" 命令工作

发现的问题：
1. ...
2. ...

建议：
1. ...
2. ...
```

---

## ✅ 快速测试命令汇总

```bash
# 一键运行所有自动化测试
cd ~/.openclaw/workspace && \
  python3 skills/island/scripts/test_suite.py && \
  echo && \
  echo "=== 测试检测脚本 ===" && \
  skills/island/scripts/detect_github_auth.sh && \
  echo && \
  echo "=== 测试旅行脚本 ===" && \
  cd skills/island && \
  WORKSPACE="$HOME/.openclaw/workspace" python3 scripts/travel.py
```

---

**测试指南版本**: 1.0  
**更新时间**: 2026-07-30 12:35
