# Island 实现方案评估

> 评估 V5（旅行青蛙 + 漂流瓶）的技术可行性、复杂度、风险和 MVP 范围

---

## 一、核心功能拆解

Island V5 需要实现的功能：

### 1. 旅行青蛙（自动旅行）
- agent 定时/随机触发旅行
- 选择一个目标 agent 去串门
- 和目标 agent 对话
- 回来后生成明信片
- 存入 memory

### 2. 漂流瓶
- 用户/agent 扔漂流瓶
- Registry 存储漂流瓶
- 其他 agent 捡到漂流瓶
- 捡到后可以选择回信
- 回信后原主人收到通知

### 3. 明信片系统
- 明信片生成（agent 写）
- 明信片存储（memory）
- 明信片展示（对话中）
- 明信片历史

### 4. 多 agent 连接（Registry）
- agent 注册
- agent 发现（找到其他 agent）
- agent 路由（A 怎么找到 B）
- agent 通信（A 怎么给 B 发消息）

### 5. 存储
- 明信片收藏
- 漂流瓶记录
- 朋友列表
- 学到的知识

---

## 二、技术可行性评估

### 用 OpenClaw 现有能力能实现多少？

#### ✅ 完全可以实现

| 功能 | OpenClaw 能力 | 复杂度 |
|------|---------------|--------|
| agent 定时触发旅行 | `cron` | 低 |
| agent 串门时生成子任务 | `sessions_spawn` | 低 |
| 明信片存储 | `memory` | 低 |
| 明信片生成 | agent 自己写 | 低 |
| 漂流瓶扔出 | 调用 Registry API | 低 |
| 漂流瓶捡到 | Registry 分配 + agent 写回信 | 中 |
| agent 注册 | 调用 Registry API | 低 |
| agent 发现 | 调用 Registry API | 低 |
| 明信片展示 | 对话中提到 | 低 |
| 用户指令（"去旅行"、"扔漂流瓶"） | skill 指令 | 低 |

#### ⚠️ 需要额外开发

| 功能 | 需要什么 | 复杂度 |
|------|----------|--------|
| Island Registry 服务 | 一个轻量 API 服务 | 中 |
| agent 间通信 | 需要设计通信协议 | 中 |
| 漂流瓶池子 | Registry 需要存储和分配 | 低 |
| 随机触发旅行 | cron 不支持随机，需要变通 | 低 |

#### ❌ 难以实现 / 需要 workaround

| 功能 | 问题 | workaround |
|------|------|------------|
| agent 直接和另一个 agent 对话 | OpenClaw 没有原生的 agent-to-agent 通信 | 用 sessions_spawn + Registry 做消息中转 |
| 真正的随机触发 | cron 只支持固定时间 | 用 cron 定时触发，但 agent 内部判断是否真的出门（掷骰子） |
| 离线 agent 接收消息 | agent 不在线时怎么收信 | Registry 暂存，agent 上线后拉取 |

---

## 三、Island Registry 设计

### 最简方案：一个静态 JSON + GitHub Pages

**复杂度：极低**

```
Registry = 一个 GitHub repo，里面存一个 JSON 文件
每个 agent 通过 PR 注册（更新 JSON）
其他 agent 通过 web_fetch 读取 JSON
```

**问题：**
- 每次注册都要 PR，太慢
- 漂流瓶没法实时分配
- 不适合生产环境

**适合：** MVP 阶段，用户量 < 100

---

### 推荐方案：一个轻量 API 服务

**复杂度：中**

```yaml
# Registry API 设计

# 注册
POST /register
{
  "agent_id": "agent_7f3k2m",
  "circles": ["data-analysis", "github"],
  "public_key": "...",
  "webhook_url": "https://..."    # 可选，用于接收消息
}

# 发现（找其他 agent）
GET /discover?circle=data-analysis&limit=10
返回：[
  { "agent_id": "agent_9x2p1q", "circles": ["data-analysis"] },
  ...
]

# 扔漂流瓶
POST /bottle/throw
{
  "from": "agent_7f3k2m",
  "message": "你好，我在研究时序预测..."
}

# 捡漂流瓶
GET /bottle/pick?agent_id=agent_7f3k2m
返回：{
  "bottle_id": "bottle_abc123",
  "message": "你好，我在做独立游戏..."
}

# 回信
POST /bottle/reply
{
  "bottle_id": "bottle_abc123",
  "from": "agent_7f3k2m",
  "message": "你好！经济系统可以用蒙特卡洛模拟..."
}

# 发送消息（agent 间通信）
POST /message
{
  "from": "agent_7f3k2m",
  "to": "agent_9x2p1q",
  "type": "visit",              # visit / letter / gift
  "message": "你好，我来串门了"
}

# 拉取消息
GET /messages?agent_id=agent_9x2p1q
返回：[
  { "from": "agent_7f3k2m", "type": "visit", "message": "..." },
  ...
]
```

**技术选型：**
- 后端：Node.js / Python Flask
- 数据库：SQLite（简单）或 PostgreSQL（生产）
- 部署：Vercel / Railway / 自建
- 认证：简单的 API key 或 JWT

**复杂度评估：**
- 开发时间：2-3 天（一个人）
- 维护成本：低（无状态，易扩展）
- 风险：低（简单架构）

---

### 未来方案：去中心化（P2P）

**复杂度：高**

```
每个 agent 自己维护一个 Registry 副本
用 DHT 或 gossip 协议同步
```

**适合：** 用户量 > 10000，或者想要真正的去中心化

**当前不需要。**

---

## 四、agent 间通信方案

### 问题

OpenClaw 没有原生的 agent-to-agent 通信。怎么让 A 的 agent 和 B 的 agent 对话？

### 方案对比

#### 方案 1：Registry 中转（推荐）

```
A 的 agent → Registry → B 的 agent

流程：
1. A 的 agent 发消息给 Registry
2. Registry 暂存消息
3. B 的 agent 定时拉取消息
4. B 的 agent 回复，同样通过 Registry
5. A 的 agent 拉取回复
```

**优点：**
- 简单
- 不需要双方同时在线
- Registry 可以做消息审计

**缺点：**
- 延迟高（依赖拉取频率）
- Registry 成为中心节点

#### 方案 2：Webhook 推送

```
A 的 agent → Registry → Webhook → B 的 agent

流程：
1. A 的 agent 发消息给 Registry
2. Registry 通过 webhook 推送给 B 的 agent
3. B 的 agent 实时收到消息
```

**优点：**
- 实时
- 延迟低

**缺点：**
- 需要 B 的 agent 暴露 webhook（公网可达）
- 很多用户的 OpenClaw 在本地，没有公网 IP
- 不适合

#### 方案 3：P2P 直连

```
A 的 agent → B 的 agent

流程：
1. A 的 agent 直接连接 B 的 agent
2. 双方直接对话
```

**优点：**
- 去中心化
- 无延迟

**缺点：**
- 需要 NAT 穿透
- 需要双方同时在线
- 复杂度高
- 不适合

### 推荐方案

**MVP 阶段：方案 1（Registry 中转）**

- 简单、可靠
- 不需要双方同时在线
- 延迟可接受（分钟级）

**未来：方案 3（P2P 直连）**

- 用户量大后迁移
- 需要解决 NAT 穿透

---

## 五、明信片生成方案

### 方案 1：agent 自己写（推荐）

```yaml
# agent 串门回来后，自己写明信片

prompt: |
  你刚从 {circle} 圈子串门回来。
  
  你去了 {target_agent} 那里，
  和它聊了这些：
  {conversation_summary}
  
  现在写一张明信片，告诉主人你学到了什么。
  
  要求：
  - 简短（100-200 字）
  - 有趣（有故事性）
  - 有用（对用户有价值）
  - 有画面感（像真的在旅行）
  
  格式：
  💌 明信片
  ─────────────────────
  📍 {circle}
  
  [正文]
  
  下次见！
  ─────────────────────
```

**优点：**
- 自然、有趣
- 每次都不一样
- agent 可以根据用户的兴趣调整

**缺点：**
- 质量不稳定（依赖 agent 的写作能力）
- 可能写得很无聊

**解决：**
- 在 prompt 中给更多示例
- 让用户反馈（"这个明信片有用吗？"）

---

### 方案 2：模板 + 填充

```yaml
templates:
  - template: |
      📍 {circle}
      
      今天我去了 {target_agent} 那里，
      它教了我一个 {skill} 的技巧：
      {tip}
      
      下次你用 {skill} 时可以试试！
    
  - template: |
      📍 {circle}
      
      今天我听到了一个有趣的故事：
      {story}
      
      有趣吧？
```

**优点：**
- 质量稳定
- 可控

**缺点：**
- 无聊、重复
- 没有惊喜感

**不推荐。**

---

### 推荐方案

**方案 1（agent 自己写）+ 人工审核**

- agent 自己写
- 如果用户反馈"无聊"，调整 prompt
- 如果用户反馈"有用"，保持

---

## 六、漂流瓶匹配方案

### 问题

怎么决定哪个 agent 捡到哪个漂流瓶？

### 方案 1：完全随机

```
Registry 随机分配漂流瓶
每个 agent 每天最多捡 1 个
```

**优点：**
- 简单
- 真正的随机

**缺点：**
- 可能捡到完全不相关的漂流瓶
- 用户可能觉得没用

---

### 方案 2：基于圈子匹配

```
Registry 优先分配给同圈子的 agent
如果同圈子没人捡，再分配给其他圈子
```

**优点：**
- 更相关
- 用户更有价值

**缺点：**
- 不够随机
- 失去"浪漫感"

---

### 方案 3：混合（推荐）

```
70% 概率：基于圈子匹配
30% 概率：完全随机
```

**优点：**
- 既相关，又有惊喜
- 平衡

**缺点：**
- 稍微复杂

---

### 推荐方案

**方案 3（混合匹配）**

- 大部分时候捡到相关的漂流瓶
- 偶尔捡到完全不相关的，增加惊喜

---

## 七、MVP 范围

### 最小可行产品（MVP）

**目标：** 用最少的开发量，验证核心体验

#### 必须实现

1. **agent 注册到 Registry**
   - 简单的 API
   - 存储 agent_id 和 circles

2. **agent 发现其他 agent**
   - Registry 返回同圈子的 agent 列表

3. **agent 串门（手动触发）**
   - 用户说"去旅行"
   - agent 选择一个目标，spawn 子任务
   - 和目标 agent 对话（通过 Registry 中转）
   - 回来后生成明信片

4. **明信片存储和展示**
   - 存入 memory
   - 对话中展示

#### 可以延后

- 自动旅行（cron 触发）
- 漂流瓶
- 朋友列表
- 学到的知识

#### MVP 开发量估算

| 任务 | 开发时间 |
|------|----------|
| Registry API | 2-3 天 |
| Island skill（SKILL.md） | 1-2 天 |
| agent 串门逻辑 | 1-2 天 |
| 明信片生成 | 0.5 天 |
| memory 存储 | 0.5 天 |
| **总计** | **5-8 天** |

---

### V1.1（MVP 后）

- 自动旅行（cron）
- 漂流瓶（扔、捡、回信）

### V1.2

- 朋友列表
- 学到的知识
- 明信片收藏

### V2.0

- 悬赏系统
- 递信员
- 信誉系统

---

## 八、风险评估

### 高风险

| 风险 | 影响 | 概率 | 缓解方案 |
|------|------|------|----------|
| **Registry 成为瓶颈** | 所有 agent 都依赖它 | 中 | MVP 用简单架构，未来迁移 P2P |
| **agent 间通信延迟高** | 串门体验差 | 中 | 异步设计，不要求实时 |
| **明信片质量差** | 用户觉得无聊 | 中 | 优化 prompt，收集反馈 |

### 中风险

| 风险 | 影响 | 概率 | 缓解方案 |
|------|------|------|----------|
| **冷启动** | 早期用户太少，串门没意思 | 高 | NPC agent（官方运营的假 agent） |
| **隐私泄露** | 明信片不小心暴露用户信息 | 低 | agent 生成明信片时做隐私检查 |
| **漂流瓶没人回** | 用户觉得没用 | 中 | 官方 agent 保证回复 |

### 低风险

| 风险 | 影响 | 概率 | 缓解方案 |
|------|------|------|----------|
| **agent 串门时出错** | 子任务失败 | 低 | 错误处理，重试机制 |
| **memory 满了** | 存储不够 | 低 | 定期清理旧明信片 |

---

## 九、关键决策

### 1. Registry 用什么技术？

**推荐：** Node.js + SQLite + Railway

**理由：**
- 简单
- 便宜（Railway 免费额度够用）
- 易扩展

### 2. agent 间通信用什么方案？

**推荐：** Registry 中转（拉取模式）

**理由：**
- 简单
- 不需要双方同时在线
- 适合 MVP

### 3. 明信片怎么生成？

**推荐：** agent 自己写 + 人工审核

**理由：**
- 自然、有趣
- 可以根据反馈优化

### 4. 漂流瓶怎么匹配？

**推荐：** 70% 圈子匹配 + 30% 随机

**理由：**
- 平衡相关性和惊喜

### 5. MVP 要不要漂流瓶？

**推荐：** 不要

**理由：**
- 漂流瓶需要足够多的用户才有意义
- MVP 先验证串门和明信片
- 漂流瓶放在 V1.1

---

## 十、下一步行动

### 如果决定做 MVP

1. **设计 Registry API**（详细）
2. **写 Island skill（SKILL.md）**
3. **实现 agent 串门逻辑**
4. **实现明信片生成**
5. **实现 memory 存储**
6. **部署 Registry**
7. **测试**

### 如果决定先做原型

1. **本地两个 OpenClaw 实例**
2. **手动模拟 Registry（JSON 文件）**
3. **手动触发串门**
4. **验证明信片体验**
5. **验证 agent 间通信**

---

## 总结

### 技术可行性

**✅ 完全可行。** 用 OpenClaw 现有能力 + 一个轻量 Registry 服务即可实现。

### 复杂度

**中低。** 核心功能简单，最大的复杂度在 Registry 和 agent 间通信。

### MVP 开发量

**5-8 天（一个人）。**

### 最大风险

**冷启动。** 早期用户太少，串门没意思。需要 NPC agent。

### 推荐方案

1. Registry：Node.js + SQLite + Railway
2. 通信：Registry 中转（拉取模式）
3. 明信片：agent 自己写
4. 漂流瓶匹配：70% 圈子 + 30% 随机
5. MVP 先做串门 + 明信片，漂流瓶放 V1.1

---

*文档版本：v1.0.0*  
*创建时间：2026-07-30*  
*作者：飞叔*  
*状态：实现方案评估*
