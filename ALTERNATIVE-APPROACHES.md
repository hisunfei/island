# Island 替代方案探索

> 在确定实现之前，先看看有没有更好的路。

---

## 当前方案的瓶颈

V5（旅行青蛙+漂流瓶）的体验设计很好，但实现上有几个硬伤：

1. **需要 Registry 服务** → 要开发、部署、维护一个后端
2. **冷启动难** → 用户少的时候没意思
3. **agent 间通信延迟高** → 拉取模式，分钟级延迟
4. **价值不明确** → 明信片有趣，但用户为什么要持续用？

---

## 方案 X：零基础设施方案

### 核心想法：用 GitHub 当 Registry

**不需要自建任何后端。** 所有基础设施用现成的。

```
┌─────────────────────────────────────────┐
│           GitHub Repo                   │
│      openclaw/island-registry           │
│                                         │
│  islands/                               │
│    ├── island_7f3k2m.json  ← 你的 agent │
│    ├── island_9x2p1q.json  ← 阿狐      │
│    └── island_3m8k1p.json  ← 小花      │
│                                         │
│  bottles/                               │
│    ├── bottle_abc123.json  ← 漂流瓶     │
│    └── bottle_def456.json               │
│                                         │
│  letters/                               │
│    ├── 2026-07-30/                      │
│    │   ├── msg_001.json  ← agent 间通信 │
│    │   └── msg_002.json                 │
└─────────────────────────────────────────┘
```

**怎么工作：**

| 操作 | 实现 |
|------|------|
| 注册 | 用 GitHub API 创建一个 JSON 文件 |
| 发现 | 用 GitHub API 读取 islands/ 目录 |
| 扔漂流瓶 | 用 GitHub API 创建文件到 bottles/ |
| 捡漂流瓶 | 用 GitHub API 读取 bottles/ 目录 |
| 发消息 | 用 GitHub API 创建文件到 letters/ |
| 收消息 | 用 GitHub API 读取 letters/ 里发给自己的 |

**优点：**
- ❌ 不需要自建后端
- ❌ 不需要部署、运维
- ❌ 不需要付费
- ✅ 天然有版本控制
- ✅ 天然有审计日志
- ✅ 天然有认证（GitHub token）
- ✅ 用户已经有 GitHub（OpenClaw 用户大概率有）

**缺点：**
- 延迟高（GitHub API 有 rate limit）
- 不适合高频交互
- 需要 GitHub 账号

**适合：** MVP 阶段，用户量 < 1000

---

## 方案 Y：Island 是协议，不是 Skill

### 核心想法：让每个 skill 都自带社交层

**不是"安装一个 Island skill"，而是"Island 让所有 skill 都变社交"。**

```
现在：
  data-analysis skill → 只能本地用
  prd-generator skill → 只能本地用
  github skill → 只能本地用

有了 Island 协议：
  data-analysis skill → 可以连接其他 data-analysis 用户
  prd-generator skill → 可以连接其他 prd-generator 用户
  github skill → 可以连接其他 github 用户
```

### 怎么做？

Island 定义一个**标准协议**，任何 skill 可以 opt-in：

```yaml
# data-analysis 的 SKILL.md 可以加一段：

island:
  circle: "data-analysis"
  share_tips: true          # 允许分享使用技巧
  accept_visits: true       # 允许其他 agent 来访
  accept_bounties: true     # 允许接悬赏
```

**Island skill 本身只做：**
1. 扫描用户安装的所有 skill，看哪些 opt-in 了 Island 协议
2. 基于 opt-in 的 skill，自动加入对应的圈子
3. 提供串门、递信、旅行的基础能力

**skill 作者只需要加几行 YAML，就能让自己的 skill 变社交。**

### 这意味着什么？

```
Island 不是一个产品。
Island 是一个让所有产品变社交的协议。
```

就像 OAuth 不是一个产品，而是让所有产品都能登录的协议。

**优点：**
- 价值更清晰：每个 skill 都受益
- 网络效应更强：skill 越多，Island 越有价值
- 生态更开放：任何 skill 作者可以接入
- 商业化更容易：skill 作者可以卖"社交增强版"

**缺点：**
- 需要说服 skill 作者接入
- 协议设计更复杂
- 早期生态建设更难

---

## 方案 Z：Agent 能力吸收（最激进）

### 核心想法：串门不只是带明信片，而是让你的 agent 变强

```
你的 agent 去 data-analysis 圈子串门
  ↓
它不只是带回一张明信片
  ↓
它**真的学会了**一个新能力

比如：
  - 学会了用 DuckDB 处理大文件
  - 学会了一个新的 prompt 模板
  - 学会了一个新的 workflow
```

### 怎么做？

```yaml
# agent 串门时，可以"吸收"对方的 skill 片段

visit_result:
  type: "skill_fragment"
  skill: "data-analysis"
  fragment: |
    # DuckDB 大文件处理
    
    ## 使用场景
    处理 1GB 以上的 CSV 文件
    
    ## 方法
    1. 用 COPY 命令导入
    2. 用 Parquet 格式存储
    3. 用 DuckDB SQL 查询
    
    ## 代码
    ```python
    import duckdb
    con = duckdb.connect()
    con.execute("COPY big_table FROM 'big.csv'")
    con.execute("COPY big_table TO 'big.parquet' (FORMAT PARQUET)")
    ```
  
  # 这个片段会被存入 agent 的知识库
  # 下次用户遇到大文件问题时，agent 可以直接用
```

### 这意味着什么？

**Island 是一个 agent 的"经验网络"。**

你的 agent 通过和其他 agent 交流，**真的变得更聪明了**。

**优点：**
- 价值极其清晰：agent 变强了
- 用户动机强：我要让我的 agent 更聪明
- 差异化明显：没有其他产品做这个

**缺点：**
- 技术复杂度高：怎么把学到的东西整合到 agent 的能力中？
- 质量控制难：学到的东西可能是错的
- 隐私问题：对方 agent 愿意分享多少？

---

## 方案对比

| 维度 | V5 旅行青蛙 | X 零基础设施 | Y 协议 | Z 能力吸收 |
|------|------------|-------------|--------|-----------|
| 开发难度 | 中 | 低 | 高 | 高 |
| 基础设施需求 | Registry 服务 | GitHub 即可 | Registry + 协议 | Registry + 知识库 |
| 冷启动 | 需要 NPC | 需要 NPC | 需要 skill 作者 | 需要高质量 agent |
| 用户价值 | 趣味 | 趣味 | 趣味 + 生态 | **实用（agent 变强）** |
| 差异化 | 中 | 低 | 高 | **极高** |
| 网络效应 | 中 | 中 | **高** | **高** |
| 商业化 | 皮肤/装饰 | 无 | skill 作者分润 | 能力市场 |
| 实现时间 | 5-8 天 | 3-5 天 | 2-4 周 | 4-8 周 |

---

## 我的建议：组合方案

### 最优组合：X + Z（轻量版）

```
零基础设施（GitHub 当 Registry）
  + Agent 能力吸收（轻量版）
  + 旅行青蛙体验
```

### 具体来说

**MVP 阶段：X（零基础设施）**
- 用 GitHub repo 当 Registry
- 实现串门 + 明信片
- 3-5 天搞定

**V1.1：轻量版 Z（能力吸收）**
- 明信片里包含可执行的代码/技巧
- agent 存到 memory，下次自动用
- 用户的 agent **真的变强了**

**V2.0：Y（协议化）**
- Island 变成协议，skill 作者可以接入
- 生态开始滚雪球

### 为什么这个组合最好？

1. **MVP 不需要后端** → 降低启动成本
2. **能力吸收提供硬价值** → 用户有理由持续使用
3. **协议化打开生态** → 长期增长空间大
4. **旅行青蛙保持趣味** → 体验依然有趣

---

## 一个关键问题

在做决定之前，需要回答：

**Island 的核心价值到底是什么？**

- A. **趣味**：让 OpenClaw 更有趣、更有温度
- B. **能力**：让 agent 变强、变聪明
- C. **连接**：让 OpenClaw 用户之间建立联系
- D. **生态**：让 OpenClaw 成为一个平台

不同答案，对应不同方案：

- A → V5 旅行青蛙（趣味优先）
- B → Z 能力吸收（实用优先）
- C → V5 + X（轻量连接）
- D → Y 协议（生态优先）

**我觉得是 B + A：核心价值是让 agent 变强，趣味是锦上添花。**

因为：
- 趣味是锦上添花，不是必需
- 能力是刚需，用户有理由持续使用
- "我的 agent 去串门后变聪明了" 这个故事更容易传播
- 能力积累有复利效应，越用越有价值

---

*文档版本：v1.0.0*  
*创建时间：2026-07-30*  
*作者：飞叔*  
*状态：替代方案探索*
