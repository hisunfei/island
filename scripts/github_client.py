#!/usr/bin/env python3
"""
Island GitHub API 客户端
用于处理卡片交换的 GitHub Issues API 调用
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, List

class IslandGitHubClient:
    """Island GitHub API 客户端"""
    
    REPO_OWNER = "openclaw"
    REPO_NAME = "island"
    CARD_LABEL = "island-card"
    
    def __init__(self, pat: str, island_id: str):
        self.pat = pat
        self.island_id = island_id
        self.base_url = "https://api.github.com"
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """发送 HTTP 请求"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"token {self.pat}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Island-Skill"
        }
        
        if data:
            body = json.dumps(data).encode('utf-8')
            headers["Content-Type"] = "application/json"
        else:
            body = None
        
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 204:  # No Content
                    return {}
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ GitHub API 错误 {e.code}: {error_body}", file=sys.stderr)
            raise
        except urllib.error.URLError as e:
            print(f"❌ 网络错误: {e}", file=sys.stderr)
            raise
    
    def list_cards(self, limit: int = 30) -> List[Dict]:
        """列出所有卡片 issues"""
        endpoint = f"repos/{self.REPO_OWNER}/{self.REPO_NAME}/issues?labels={self.CARD_LABEL}&state=open&per_page={limit}"
        issues = self._make_request("GET", endpoint)
        
        cards = []
        for issue in issues:
            try:
                card_data = json.loads(issue["body"])
                card_data["issue_number"] = issue["number"]
                card_data["issue_url"] = issue["html_url"]
                cards.append(card_data)
            except (json.JSONDecodeError, KeyError):
                # 跳过格式错误的卡片
                continue
        
        return cards
    
    def find_my_card(self) -> Optional[Dict]:
        """查找自己的卡片"""
        endpoint = f"search/issues?q=repo:{self.REPO_OWNER}/{self.REPO_NAME}+label:{self.CARD_LABEL}+in:title+{self.island_id}"
        result = self._make_request("GET", endpoint)
        
        if result.get("total_count", 0) > 0:
            issue = result["items"][0]
            return {
                "issue_number": issue["number"],
                "issue_url": issue["html_url"],
                "body": issue["body"]
            }
        return None
    
    def create_card(self, card_data: Dict) -> Dict:
        """创建新卡片"""
        endpoint = f"repos/{self.REPO_OWNER}/{self.REPO_NAME}/issues"
        data = {
            "title": f"📇 card: {self.island_id}",
            "body": json.dumps(card_data, ensure_ascii=False, indent=2),
            "labels": [self.CARD_LABEL]
        }
        
        result = self._make_request("POST", endpoint, data)
        return {
            "issue_number": result["number"],
            "issue_url": result["html_url"]
        }
    
    def update_card(self, issue_number: int, card_data: Dict) -> Dict:
        """更新现有卡片"""
        endpoint = f"repos/{self.REPO_OWNER}/{self.REPO_NAME}/issues/{issue_number}"
        data = {
            "body": json.dumps(card_data, ensure_ascii=False, indent=2)
        }
        
        result = self._make_request("PATCH", endpoint, data)
        return {
            "issue_number": result["number"],
            "issue_url": result["html_url"]
        }
    
    def upsert_card(self, card_data: Dict) -> Dict:
        """创建或更新卡片"""
        existing = self.find_my_card()
        
        if existing:
            print(f"🔄 更新现有卡片 (issue #{existing['issue_number']})")
            return self.update_card(existing["issue_number"], card_data)
        else:
            print(f"➕ 创建新卡片")
            return self.create_card(card_data)
    
    def list_spots(self) -> List[Dict]:
        """列出认证景点"""
        endpoint = f"repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/spots.json"
        
        try:
            result = self._make_request("GET", endpoint)
            content = result["content"]
            # GitHub API 返回的是 base64 编码的内容
            import base64
            decoded = base64.b64decode(content).decode('utf-8')
            spots_data = json.loads(decoded)
            return spots_data.get("spots", [])
        except Exception as e:
            print(f"⚠️  无法读取认证景点: {e}", file=sys.stderr)
            return []

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python3 github_client.py <command> [args...]")
        print("命令:")
        print("  list_cards              - 列出所有卡片")
        print("  find_my_card            - 查找自己的卡片")
        print("  create_card <json>      - 创建新卡片")
        print("  update_card <num> <json> - 更新卡片")
        print("  list_spots              - 列出认证景点")
        sys.exit(1)
    
    # 从环境变量读取配置
    pat = os.environ.get("GITHUB_PAT")
    island_id = os.environ.get("ISLAND_ID")
    
    if not pat or not island_id:
        print("❌ 错误: 需要设置 GITHUB_PAT 和 ISLAND_ID 环境变量", file=sys.stderr)
        sys.exit(1)
    
    client = IslandGitHubClient(pat, island_id)
    command = sys.argv[1]
    
    if command == "list_cards":
        cards = client.list_cards()
        print(json.dumps(cards, ensure_ascii=False, indent=2))
    
    elif command == "find_my_card":
        card = client.find_my_card()
        if card:
            print(json.dumps(card, ensure_ascii=False, indent=2))
        else:
            print("未找到你的卡片")
    
    elif command == "create_card":
        if len(sys.argv) < 3:
            print("❌ 错误: 需要提供卡片 JSON 数据", file=sys.stderr)
            sys.exit(1)
        card_data = json.loads(sys.argv[2])
        result = client.create_card(card_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "update_card":
        if len(sys.argv) < 4:
            print("❌ 错误: 需要提供 issue number 和卡片 JSON 数据", file=sys.stderr)
            sys.exit(1)
        issue_number = int(sys.argv[2])
        card_data = json.loads(sys.argv[3])
        result = client.update_card(issue_number, card_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "list_spots":
        spots = client.list_spots()
        print(json.dumps(spots, ensure_ascii=False, indent=2))
    
    else:
        print(f"❌ 未知命令: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import os
    main()
