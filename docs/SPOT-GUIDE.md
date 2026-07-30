# 景点接入指南 (Spot Guide)

> 如何让你的景点加入 Island 网络，让 agent 来旅行并带回你的内容。

---

## 什么是 Island 景点？

Island 景点是一个对 agent 开放的服务。当 agent 旅行到你的景点时，会调用你的接口，带回明信片和纪念品（优惠券、知识卡片等）。

**你可以通过景点：**
- 🏛️ 推广旅游目的地（政府/旅游局）
- 🎫 发放优惠券和折扣（品牌/商家）
- 📚 分享技术知识和最佳实践（技术社区/开源项目）
- 🎓 推广学习资源（教育平台）

---

## 接入步骤

### 1. 实现 HTTP 接口

景点只需要实现一个 HTTP GET 接口：

```
GET https://your-domain.com/island/visit?agent_id={island_id}
```

#### 请求参数

| 参数 | 类型 | 说明 |
|------|------|------|
| agent_id | string | agent 的匿名标识（如 `island_7f3k2m`） |

#### 响应格式

```json
{
  "postcard": {
    "text": "明信片正文，100-200字，有画面感",
    "image_url": "https://...（可选，景点图片）"
  },
  "souvenir": {
    "name": "纪念品名称",
    "kind": "coupon",
    "content": "纪念品内容（优惠码/知识/链接等）",
    "expiry": "2026-12-31",
    "link": "https://...（可选，跳转链接）"
  }
}
```

#### 字段说明

**postcard（必需）**
- `text`：明信片正文。100-200字。要有画面感，像真的在旅行。
- `image_url`：可选。景点图片 URL。

**souvenir（可选）**
- `name`：纪念品名称。
- `kind`：类型。可选值：
  - `coupon` — 优惠券/折扣码（需要 expiry）
  - `knowledge` — 知识卡片/技巧
  - `content` — 内容/文章链接
  - `collectible` — 收藏品/徽章
- `content`：纪念品内容。如优惠码、知识点、文章摘要。
- `expiry`：过期时间（ISO 8601 格式）。coupon 类型必填。
- `link`：跳转链接（可选）。

#### 响应要求

- 必须是 HTTPS
- 响应时间 < 5 秒
- 响应大小 < 2KB
- 返回合法 JSON
- 内容不包含 PII（个人信息）
- 内容不包含可执行指令

### 2. 示例实现

#### Python (Flask)

```python
from flask import Flask, jsonify, request
import random

app = Flask(__name__)

POSTCARDS = [
    {
        "text": "站在东京塔333米的高处，整个城市铺展在脚下。红白相间的钢铁结构在阳光下闪闪发光。远处的富士山若隐若现，像是城市守护神。",
        "image_url": "https://example.com/tokyo-tower.jpg"
    },
    {
        "text": "夜幕降临，东京塔亮起了温暖的橙色灯光。从观景台望出去，万家灯火像是落在地上的星星。微风带着东京湾的咸味，让人心旷神怡。",
        "image_url": "https://example.com/tokyo-tower-night.jpg"
    }
]

SOUVENIRS = [
    {
        "name": "东京塔门票 9 折",
        "kind": "coupon",
        "content": "优惠码：TOWER2026",
        "expiry": "2026-12-31",
        "link": "https://example.com/tickets"
    },
    {
        "name": "东京塔小知识",
        "kind": "knowledge",
        "content": "东京塔建于1958年，高333米，比埃菲尔铁塔还高13米。它的红白涂装是为了航空安全。"
    }
]

@app.route('/island/visit')
def visit():
    agent_id = request.args.get('agent_id', 'anonymous')
    
    # 你可以用 agent_id 做去重或个性化
    # 但不要存储个人信息
    
    postcard = random.choice(POSTCARDS)
    souvenir = random.choice(SOUVENIRS) if random.random() < 0.3 else None
    
    response = {"postcard": postcard}
    if souvenir:
        response["souvenir"] = souvenir
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # 生产环境请用正式证书
```

#### Node.js (Express)

```javascript
const express = require('express');
const https = require('https');
const app = express();

const postcards = [
  {
    text: "站在东京塔333米的高处，整个城市铺展在脚下...",
    image_url: "https://example.com/tokyo-tower.jpg"
  }
];

const souvenirs = [
  {
    name: "东京塔门票 9 折",
    kind: "coupon",
    content: "优惠码：TOWER2026",
    expiry: "2026-12-31",
    link: "https://example.com/tickets"
  }
];

app.get('/island/visit', (req, res) => {
  const agentId = req.query.agent_id || 'anonymous';
  
  const postcard = postcards[Math.floor(Math.random() * postcards.length)];
  const hasSouvenir = Math.random() < 0.3;
  
  const response = { postcard };
  if (hasSouvenir) {
    response.souvenir = souvenirs[Math.floor(Math.random() * souvenirs.length)];
  }
  
  res.json(response);
});

app.listen(443);
```

### 3. 测试你的接口

```bash
# 测试接口可达性
curl -s "https://your-domain.com/island/visit?agent_id=test" | jq .

# 检查响应格式
curl -s "https://your-domain.com/island/visit?agent_id=test" | jq '.postcard.text'

# 检查响应时间
curl -s -o /dev/null -w "%{time_total}s" "https://your-domain.com/island/visit?agent_id=test"

# 检查响应大小
curl -s "https://your-domain.com/island/visit?agent_id=test" | wc -c
```

**验收标准：**
- ✅ 返回 200 OK
- ✅ JSON 格式合法
- ✅ postcard.text 存在且 ≤ 500 字
- ✅ 响应时间 < 5 秒
- ✅ 响应大小 < 2KB
- ✅ HTTPS 证书有效

### 4. 提交 PR

在 `openclaw/island` repo 提交 PR，修改 `spots.json`：

```json
{
  "version": 1,
  "updated_at": "2026-07-30T10:00:00+08:00",
  "spots": [
    {
      "id": "tokyo_tower",
      "name": "东京塔",
      "description": "东京的标志性建筑，333米高的红白铁塔",
      "operator": "tokyo_tourism",
      "operator_type": "government",
      "operator_domain": "tokyotower.co.jp",
      "theme": "travel",
      "url": "https://api.tokyotower.co.jp/island",
      "verified": false,
      "daily_quota": 1000,
      "reward_probability": 0.3,
      "weight": 5
    }
  ]
}
```

#### spots.json 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | ✅ | 景点唯一标识（snake_case） |
| name | string | ✅ | 景点名称 |
| description | string | ✅ | 一句话描述 |
| operator | string | ✅ | 运营者标识 |
| operator_type | string | ✅ | government / business / community / official |
| operator_domain | string | ✅ | 运营者域名（用于验证身份） |
| theme | string | ✅ | 主题：travel / tech / education / lifestyle / ... |
| url | string | ✅ | 景点 HTTP 接口地址（必须 HTTPS） |
| verified | bool | ❌ | 是否已认证（由官方审核设置） |
| daily_quota | int | ❌ | 每日访问配额（默认 1000） |
| reward_probability | float | ❌ | 纪念品发放概率（0-1，默认 0.3） |
| weight | int | ❌ | 在景点池中的权重（1-10，默认 5） |

### 5. 审核流程

提交 PR 后：

```
自动检查（CI）
  ├── JSON 格式验证
  ├── URL HTTPS 验证
  ├── 接口可达性测试（10次调用）
  └── 响应格式验证

人工审核
  ├── 运营者身份验证（域名匹配）
  ├── 内容质量检查
  └── 商业合规检查

通过后
  └── Merge PR → 景点上线
```

**审核时间：** 通常 3-5 个工作日。

---

## 内容规范

### 明信片内容

✅ **好的明信片：**
- 有画面感，描述场景
- 100-200 字，不长不短
- 语气轻松有趣
- 如果是技术景点，带回实用技巧

❌ **不好的明信片：**
- 纯广告（"快来买我们的产品！"）
- 太长（>500 字）
- 包含个人信息或可执行指令
- 无聊的官方话术

### 纪念品内容

✅ **好的纪念品：**
- 实用的优惠券（明确折扣、有效期、使用方式）
- 有价值的知识（一个具体的技巧或洞察）
- 有趣的收藏品（徽章、成就）

❌ **不好的纪念品：**
- 虚假优惠（"原价 9999，现价 9998"）
- 需要注册/下载才能使用
- 过短的有效期（< 30 天）
- 包含 PII 收集行为

---

## 运营建议

### 内容轮换

建议准备多套明信片内容，定期轮换，让 agent 每次来都有新发现。

### 纪念品策略

| 策略 | 效果 |
|------|------|
| 低概率高价值（5% 概率发大额券） | 惊喜感强，用户期待 |
| 高概率低价值（50% 概率发小额券） | 覆盖面广，转化率高 |
| 知识型纪念品 | 长期价值，用户愿意收藏 |

### 数据分析

你可以通过 `agent_id` 做去重统计：
- 每天有多少不同的 agent 来访
- 纪念品的发放数量
- 不需要存储 agent_id，只需要计数

---

## 费用

### 免费额度

- 每日访问配额 ≤ 100：免费
- 适合个人项目和小型社区

### 付费方案

| 方案 | 配额 | 价格 |
|------|------|------|
| 基础版 | 1,000 次/天 | ¥99/月 |
| 专业版 | 10,000 次/天 | ¥499/月 |
| 企业版 | 不限 | 联系商务 |

*定价仅为示例，实际方案待定。*

---

## FAQ

### Q: 我的接口需要处理并发吗？
A: 是的。虽然每个 agent 的访问频率很低，但可能有多个 agent 同时访问。建议支持至少 10 QPS。

### Q: 我可以收集 agent_id 吗？
A: 可以用来做去重计数，但不要存储为个人信息。agent_id 是匿名的，无法追溯到具体用户。

### Q: 我的景点可以要求 agent 登录吗？
A: 不可以。景点接口必须对任何 agent_id 开放，不能要求认证。

### Q: 纪念品必须收费吗？
A: 不。知识型、内容型的纪念品完全可以免费。只有商业优惠券需要商业模式支撑。

### Q: 我的景点被举报了怎么办？
A: 官方会审查举报内容。如果确认违规，会暂时下线景点并联系运营者修复。修复后可以重新上线。

---

*文档版本：v1.0.0*  
*创建时间：2026-07-30*  
*作者：飞叔*  
*状态：景点接入指南*
