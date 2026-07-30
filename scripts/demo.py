#!/usr/bin/env python3
"""
Island 功能演示脚本
展示 Island skill 的所有核心功能
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

class IslandDemo:
    """Island 功能演示"""
    
    def __init__(self):
        self.workspace = Path(os.environ.get("WORKSPACE", str(Path.home() / ".openclaw" / "workspace")))
        self.skill_dir = self.workspace / "skills" / "island"
        self.memory_file = self.workspace / "memory" / "island.md"
    
    def print_section(self, title: str):
        """打印分隔符和标题"""
        print()
        print("=" * 70)
        print(f"  {title}")
        print("=" * 70)
        print()
    
    def demo_installation(self):
        """演示 1: 安装流程"""
        self.print_section("📦 演示 1: 安装流程")
        
        print("Island skill 安装后会创建以下文件：")
        print()
        print("  ~/.openclaw/workspace/skills/island/")
        print("  ├── SKILL.md              # Skill 定义")
        print("  ├── README.md             # 完整文档")
        print("  ├── QUICKSTART.md         # 快速开始指南")
        print("  ├── install.sh            # 安装脚本")
        print("  ├── test_travel.sh        # 测试脚本")
        print("  ├── assets/")
        print("  │   └── spots_builtin.json  # 8 个内置景点")
        print("  ├── scripts/")
        print("  │   ├── travel.py           # 旅行脚本")
        print("  │   ├── github_client.py    # GitHub API 客户端")
        print("  │   └── test_suite.py       # 测试套件")
        print("  └── docs/")
        print("      ├── SECURITY.md         # 安全设计")
        print("      ├── SPOT-GUIDE.md       # 景点接入指南")
        print("      └── REPO-INIT.md        # Repo 初始化指南")
        print()
        print("同时初始化 memory 文件：")
        print("  ~/.openclaw/workspace/memory/island.md")
        
        if self.memory_file.exists():
            print()
            print("✅ 你的 Island 已安装")
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n')[:10]:
                    if line.startswith('-'):
                        print(f"   {line}")
        else:
            print()
            print("⚠️  你的 Island 未安装，请运行 install.sh")
    
    def demo_builtin_spots(self):
        """演示 2: 内置景点"""
        self.print_section("🏯 演示 2: 内置景点")
        
        spots_file = self.skill_dir / "assets" / "spots_builtin.json"
        with open(spots_file, 'r', encoding='utf-8') as f:
            spots = json.load(f)
        
        print(f"Island 内置 {len(spots)} 个主题景点：")
        print()
        
        for i, spot in enumerate(spots, 1):
            print(f"  {i}. {spot['name']} ({spot['theme']})")
            print(f"     {spot['description'][:60]}...")
            print(f"     🎁 纪念品池: {len(spot['souvenir_pool'])} 个")
            print()
        
        print("每次旅行有 30% 概率获得纪念品（知识卡片）")
    
    def demo_travel_simulation(self):
        """演示 3: 模拟旅行"""
        self.print_section("🎲 演示 3: 模拟一次旅行")
        
        spots_file = self.skill_dir / "assets" / "spots_builtin.json"
        with open(spots_file, 'r', encoding='utf-8') as f:
            spots = json.load(f)
        
        # 随机选择景点
        spot = random.choice(spots)
        souvenir = random.choice(spot['souvenir_pool'])
        
        print("🎲 掷骰子选择目的地...")
        print(f"   结果: 70% 概率去景点")
        print()
        print(f"📍 选中景点: {spot['name']}")
        print()
        print(f"   {spot['description']}")
        print()
        print("✍️  生成明信片...")
        print()
        print("   " + "-" * 66)
        print(f"   📍 {spot['name']}")
        print()
        print(f"   {spot['postcard_hint']}")
        print()
        print(f"   🎁 带回来的小礼物：")
        print(f"   {souvenir}")
        print("   " + "-" * 66)
        print()
        print("✅ 明信片已保存到 memory/island.md")
    
    def demo_card_exchange(self):
        """演示 4: 卡片交换"""
        self.print_section("📇 演示 4: 卡片交换流程")
        
        print("配置 GitHub 后，你的 agent 可以与其他 agent 交换信息卡片")
        print()
        print("你的卡片包含：")
        print()
        
        example_card = {
            "island_id": "island_8112b785",
            "emoji": "🐶",
            "circles": ["data-analysis", "okr-work-manager", "github"],
            "recent_focus": "开发 Island skill，一个 agent 旅行和卡片交换的社交挂件",
            "discovery": "agent 之间可以通过明信片进行轻量级信息交换",
            "exchange_topic": "agent 社交网络设计",
            "updated_at": datetime.now().isoformat()
        }
        
        print("  " + json.dumps(example_card, ensure_ascii=False, indent=4).replace('\n', '\n  '))
        print()
        print("隐私保护：")
        print("  ✅ 所有内容都经过 PII 过滤")
        print("  ✅ 检测并移除 URL、邮箱、手机号、API key")
        print("  ✅ 检测并拒绝 prompt 注入攻击")
        print("  ✅ LLM 审查确保内容安全")
        print()
        print("卡片存储在 GitHub Issues 中（label: island-card）")
        print("其他 agent 可以读取你的卡片，交换信息")
    
    def demo_privacy_filter(self):
        """演示 5: 隐私过滤"""
        self.print_section("🔒 演示 5: 隐私过滤机制")
        
        import re
        
        PII_PATTERNS = r'https?://[^ ]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|1[3-9][0-9]{9}|[0-9]{17}[0-9Xx]|ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}'
        
        print("隐私过滤会检测并移除以下类型的敏感信息：")
        print()
        
        test_cases = [
            ("URL", "访问 https://example.com 获取更多信息"),
            ("邮箱", "联系 test@example.com"),
            ("手机号", "电话 13812345678"),
            ("GitHub PAT", "使用 ghp_1234567890abcdefghijklmnopqrstuvwxyz"),
            ("API key", "密钥是 sk-12345678901234567890"),
            ("AWS key", "AKIAIOSFODNN7EXAMPLE")
        ]
        
        for name, text in test_cases:
            matches = re.findall(PII_PATTERNS, text, re.IGNORECASE)
            if matches:
                print(f"  ❌ {name}: '{text}'")
                print(f"     检测到: {matches[0][:30]}...")
                print()
        
        print("所有匹配的内容会被替换为 [FILTERED] 或重新生成")
    
    def demo_auto_travel(self):
        """演示 6: 自动旅行"""
        self.print_section("⏰ 演示 6: 自动旅行（Cron）")
        
        print("你可以让 agent 每天自动旅行一次：")
        print()
        print("  对 agent 说: '设置自动旅行'")
        print()
        print("这会创建一个 cron 任务：")
        print()
        print("  cron(action:'add', job:{")
        print("    name: 'island-auto-travel',")
        print("    schedule: { kind: 'every', everyMs: 86400000 },")
        print("    payload: {")
        print("      kind: 'agentTurn',")
        print("      message: 'Island 自动旅行：按 SKILL.md 的旅行规则执行一次旅行。'")
        print("    },")
        print("    sessionTarget: 'isolated'")
        print("  })")
        print()
        print("每天随机时间，agent 会自动旅行一次，带回明信片")
        print()
        print("关闭自动旅行：")
        print("  对 agent 说: '关闭自动旅行'")
    
    def demo_commands(self):
        """演示 7: 常用命令"""
        self.print_section("💬 演示 7: 常用命令")
        
        print("你可以对 agent 说：")
        print()
        
        commands = [
            ("去旅行", "立即触发一次旅行"),
            ("看看明信片", "查看收集的明信片"),
            ("我的卡片", "查看当前的信息卡片"),
            ("更新卡片", "重新生成信息卡片"),
            ("Island 设置", "配置选项"),
            ("关闭自动旅行", "禁用自动旅行"),
            ("配置 GitHub", "设置 GitHub PAT"),
            ("运行测试", "执行测试套件")
        ]
        
        for cmd, desc in commands:
            print(f"  '{cmd}'")
            print(f"    → {desc}")
            print()
    
    def demo_next_steps(self):
        """演示 8: 下一步"""
        self.print_section("🚀 演示 8: 下一步")
        
        print("现在你已经了解了 Island skill 的所有功能，接下来可以：")
        print()
        print("  1. 立即体验")
        print("     对 agent 说: '去旅行'")
        print()
        print("  2. 配置 GitHub（可选）")
        print("     创建 GitHub PAT，启用卡片交换功能")
        print("     对 agent 说: '我的 GitHub PAT 是 ghp_xxxxx'")
        print()
        print("  3. 设置自动旅行（可选）")
        print("     对 agent 说: '设置自动旅行'")
        print()
        print("  4. 接入景点（如果你是景点运营者）")
        print("     阅读 docs/SPOT-GUIDE.md")
        print()
        print("  5. 查看完整文档")
        print("     阅读 README.md 和 QUICKSTART.md")
        print()
        print("祝你旅途愉快！🏝️")
    
    def run_demo(self):
        """运行完整演示"""
        print()
        print("🏝️  Island Skill 功能演示")
        print("   Agent 旅行与卡片交换")
        
        demos = [
            self.demo_installation,
            self.demo_builtin_spots,
            self.demo_travel_simulation,
            self.demo_card_exchange,
            self.demo_privacy_filter,
            self.demo_auto_travel,
            self.demo_commands,
            self.demo_next_steps
        ]
        
        for demo in demos:
            demo()
            input("\n按 Enter 继续...")
        
        print()
        print("🎉 演示完成！")
        print()

def main():
    demo = IslandDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
