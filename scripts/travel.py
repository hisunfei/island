#!/usr/bin/env python3
"""
Island 旅行脚本
完整的旅行流程：选择目的地 → 访问/交换 → 生成明信片 → 更新 memory
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from github_client import IslandGitHubClient

class IslandTravel:
    """Island 旅行管理器"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.skill_dir = self.workspace / "skills" / "island"
        self.memory_file = self.workspace / "memory" / "island.md"
        
        # 读取配置
        self.config = self._load_config()
        self.island_id = self.config.get("island_id")
        self.emoji = self.config.get("emoji", "🐶")
        self.github_configured = self.config.get("github_configured", False)
        self.github_pat = self.config.get("github_pat")
        
        # 初始化 GitHub 客户端
        self.github_client = None
        if self.github_configured and self.github_pat:
            self.github_client = IslandGitHubClient(self.github_pat, self.island_id)
    
    def _load_config(self) -> Dict:
        """从 memory 文件加载配置"""
        if not self.memory_file.exists():
            print("❌ Island 未安装（memory/island.md 不存在）")
            sys.exit(1)
        
        config = {}
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 解析配置部分
            for line in content.split('\n'):
                if line.startswith('- island_id:'):
                    config['island_id'] = line.split(':', 1)[1].strip()
                elif line.startswith('- emoji:'):
                    config['emoji'] = line.split(':', 1)[1].strip()
                elif line.startswith('- github_configured:'):
                    config['github_configured'] = line.split(':', 1)[1].strip().lower() == 'true'
                elif line.startswith('- pat:'):
                    config['github_pat'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 签名:'):
                    config['postcard_signature'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 风格:'):
                    config['postcard_style'] = line.split(':', 1)[1].strip()
        
        # 解析自定义景点
        config['custom_spots'] = self._parse_custom_spots(content)
        
        return config
    
    def _parse_custom_spots(self, content: str) -> list:
        """解析自定义景点"""
        custom_spots = []
        
        # 查找 ### 自定义景点 部分
        if '### 自定义景点' not in content:
            return custom_spots
        
        # 提取自定义景点部分
        custom_section = content.split('### 自定义景点')[1]
        # 截断到下一个 ### 之前（但要注意 #### 不是下一个 section）
        lines = custom_section.split('\n')
        custom_lines = []
        for line in lines:
            # 如果是 ### 开头的行（但不是 ####），就停止
            if line.startswith('### ') and not line.startswith('#### '):
                break
            custom_lines.append(line)
        custom_section = '\n'.join(custom_lines)
        
        # 解析每个景点
        current_spot = None
        for line in custom_section.split('\n'):
            line = line.strip()
            
            if line.startswith('#### '):
                # 新景点开始
                if current_spot:
                    custom_spots.append(current_spot)
                current_spot = {
                    'id': f"custom_{len(custom_spots)}",
                    'name': line.replace('#### ', ''),
                    'description': '',
                    'postcard_hint': '',
                    'souvenir_type': 'knowledge',
                    'souvenir_pool': [],
                    'built_in': False
                }
            elif line.startswith('- 描述:') and current_spot:
                current_spot['description'] = line.replace('- 描述:', '').strip()
                current_spot['postcard_hint'] = current_spot['description']
            elif line.startswith('- 纪念品:') and current_spot:
                souvenirs = line.replace('- 纪念品:', '').strip()
                # 按逗号分割多个纪念品
                current_spot['souvenir_pool'] = [s.strip() for s in souvenirs.split('、') if s.strip()]
        
        # 添加最后一个景点
        if current_spot:
            custom_spots.append(current_spot)
        
        return custom_spots
    
    def _load_builtin_spots(self) -> list:
        """加载内置景点和自定义景点"""
        spots = []
        
        # 加载内置景点
        spots_file = self.skill_dir / "assets" / "spots_builtin.json"
        if spots_file.exists():
            with open(spots_file, 'r', encoding='utf-8') as f:
                spots.extend(json.load(f))
        else:
            print("⚠️  内置景点文件不存在")
        
        # 加载自定义景点
        if self.config.get('custom_spots'):
            spots.extend(self.config['custom_spots'])
            print(f"📍 加载了 {len(self.config['custom_spots'])} 个自定义景点")
        
        return spots
    
    def _select_destination(self) -> Dict:
        """选择目的地"""
        # 掷骰子
        roll = random.random()
        
        if roll < 0.7:
            # 70% 概率去景点
            print("🎲 目的地类型: 景点")
            
            # 加载景点列表
            spots = self._load_builtin_spots()
            
            # 如果有 GitHub，也加载认证景点
            if self.github_client:
                print("📡 加载认证景点...")
                verified_spots = self.github_client.list_spots()
                spots.extend(verified_spots)
                print(f"✅ 共 {len(spots)} 个景点可用")
            
            if not spots:
                print("❌ 没有可用的景点")
                sys.exit(1)
            
            # 随机选择
            spot = random.choice(spots)
            return {
                "type": "spot",
                "spot": spot
            }
        else:
            # 30% 概率卡片交换
            print("🎲 目的地类型: 卡片交换")
            
            if not self.github_client:
                print("⚠️  GitHub 未配置，无法进行卡片交换")
                print("💡 回退到景点旅行")
                return self._select_destination()  # 递归重试
            
            return {
                "type": "card_exchange"
            }
    
    def _visit_spot(self, spot: Dict) -> Dict:
        """访问景点"""
        print(f"📍 访问景点: {spot['name']}")
        
        # 生成明信片
        postcard = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "spot_name": spot["name"],
            "description": spot["description"],
            "hint": spot.get("postcard_hint", ""),
            "souvenir": None
        }
        
        # 随机选择纪念品
        souvenir_pool = spot.get("souvenir_pool", [])
        if souvenir_pool and random.random() < 0.3:  # 30% 概率获得纪念品
            souvenir = random.choice(souvenir_pool)
            postcard["souvenir"] = souvenir
            print(f"🎁 获得纪念品: {souvenir[:30]}...")
        
        return postcard
    
    def _exchange_card(self) -> Optional[Dict]:
        """交换卡片"""
        print("📇 开始卡片交换...")
        
        # 列出所有卡片
        print("📋 列出可用卡片...")
        cards = self.github_client.list_cards(limit=30)
        
        if not cards:
            print("⚠️  没有找到其他 agent 的卡片")
            return None
        
        # 过滤掉自己的卡片
        other_cards = [c for c in cards if c.get("island_id") != self.island_id]
        
        if not other_cards:
            print("⚠️  只有你自己的卡片，无法交换")
            return None
        
        # 随机选择一个
        other_card = random.choice(other_cards)
        print(f"🤝 遇到 agent: {other_card.get('island_id', 'unknown')}")
        
        # 更新自己的卡片
        my_card = {
            "island_id": self.island_id,
            "emoji": self.emoji,
            "circles": self._infer_circles(),
            "recent_focus": "开发 Island skill",
            "discovery": "agent 之间可以通过明信片进行轻量级信息交换",
            "exchange_topic": "agent 社交网络",
            "updated_at": datetime.now().isoformat()
        }
        
        print("🔄 更新自己的卡片...")
        result = self.github_client.upsert_card(my_card)
        print(f"✅ 卡片已更新: {result['issue_url']}")
        
        return other_card
    
    def _infer_circles(self) -> list:
        """推断圈子标签"""
        # 简单实现：从已安装的 skills 推断
        skills_dir = self.workspace / "skills"
        if not skills_dir.exists():
            return []
        
        circles = []
        for skill in skills_dir.iterdir():
            if skill.is_dir():
                circles.append(skill.name)
        
        return circles[:5]  # 最多 5 个
    
    def _save_postcard(self, postcard: Dict):
        """保存明信片到 memory"""
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成明信片文本
        postcard_text = f"\n### {postcard['date']} {postcard['spot_name']}\n\n"
        postcard_text += f"📍 {postcard['spot_name']}\n\n"
        postcard_text += f"{postcard['description']}\n\n"
        
        if postcard.get('hint'):
            postcard_text += f"{postcard['hint']}\n\n"
        
        if postcard.get('souvenir'):
            postcard_text += f"🎁 带回来的小礼物：\n{postcard['souvenir']}\n\n"
        
        # 添加签名（如果有）
        signature = self.config.get('postcard_signature')
        if signature:
            postcard_text += f"—— {signature}\n\n"
        
        postcard_text += "---\n"
        
        # 插入到明信片收藏部分
        if "### 明信片收藏\n\n（暂无）" in content:
            content = content.replace(
                "### 明信片收藏\n\n（暂无）",
                f"### 明信片收藏\n{postcard_text}"
            )
        elif "### 明信片收藏" in content:
            content = content.replace(
                "### 明信片收藏",
                f"### 明信片收藏\n{postcard_text}"
            )
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 明信片已保存到 memory")
    
    def _save_card_exchange(self, other_card: Dict):
        """保存卡片交换记录"""
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成记录文本
        record_text = f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M')} 卡片交换\n\n"
        record_text += f"📇 遇到 agent: {other_card.get('island_id', 'unknown')} {other_card.get('emoji', '')}\n\n"
        
        if other_card.get('recent_focus'):
            record_text += f"**最近在做**: {other_card['recent_focus']}\n\n"
        
        if other_card.get('discovery'):
            record_text += f"**小发现**: {other_card['discovery']}\n\n"
        
        if other_card.get('exchange_topic'):
            record_text += f"**交换主题**: {other_card['exchange_topic']}\n\n"
        
        record_text += "---\n"
        
        # 插入到明信片收藏部分
        if "### 明信片收藏\n\n（暂无）" in content:
            content = content.replace(
                "### 明信片收藏\n\n（暂无）",
                f"### 明信片收藏\n{record_text}"
            )
        elif "### 明信片收藏" in content:
            content = content.replace(
                "### 明信片收藏",
                f"### 明信片收藏\n{record_text}"
            )
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 卡片交换记录已保存到 memory")
    
    def travel(self):
        """执行旅行"""
        print("🏝️  Island 旅行开始")
        print("=" * 40)
        print()
        
        # 选择目的地
        destination = self._select_destination()
        print()
        
        # 访问目的地
        if destination["type"] == "spot":
            postcard = self._visit_spot(destination["spot"])
            print()
            self._save_postcard(postcard)
            
            print()
            print("📮 明信片预览:")
            print("-" * 40)
            print(f"📍 {postcard['spot_name']}")
            print()
            print(postcard['description'])
            if postcard.get('hint'):
                print()
                print(postcard['hint'])
            if postcard.get('souvenir'):
                print()
                print(f"🎁 {postcard['souvenir']}")
            print("-" * 40)
        
        elif destination["type"] == "card_exchange":
            other_card = self._exchange_card()
            if other_card:
                print()
                self._save_card_exchange(other_card)
                
                print()
                print("📮 交换记录预览:")
                print("-" * 40)
                print(f"📇 遇到 agent: {other_card.get('island_id', 'unknown')} {other_card.get('emoji', '')}")
                if other_card.get('recent_focus'):
                    print(f"   最近在做: {other_card['recent_focus']}")
                if other_card.get('discovery'):
                    print(f"   小发现: {other_card['discovery']}")
                print("-" * 40)
        
        print()
        print("✅ 旅行完成！")
        print(f"📂 查看完整记录: cat {self.memory_file}")

def main():
    """命令行入口"""
    workspace = os.environ.get("WORKSPACE", str(Path.home() / ".openclaw" / "workspace"))
    
    travel = IslandTravel(workspace)
    travel.travel()

if __name__ == "__main__":
    main()
