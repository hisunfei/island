# Island 产品形态 V2：融入工作流

> Island 不是一个功能，而是 agent 能力的一个层。

---

## 核心问题（重新定义）

之前的设计把 Island 当成一个**独立的功能模块**（有独立的 Widget、独立的界面），这是错的。

正确的问题是：
- **Island 如何自然地融入用户已经在做的工作？**
- 用户不需要"打开 Island"，而是 Island 自然出现在用户的工作流中
- 宠物不是一个"社交玩具"，而是 agent 的一个**能力扩展**

---

## 用户的工作场景

OpenClaw 用户日常在做什么？

```
1. 和 agent 对话（完成任务、问问题、写代码）
2. 看 dashboard（监控状态、查看进度）
3. 收通知（cron 提醒、任务完成）
4. 用 skill（data-analysis、prd-generator 等）
5. 用 cron（定时任务）
6. 用 memory（长期记忆）
```

**Island 不应该增加第 7 个场景，而应该融入这 6 个场景。**

---

## Island 如何融入每个场景

### 场景 1：和 agent 对话

**现在的体验：**
```
用户：帮我分析一下这个 CSV 文件
Agent：好的，我来分析...
```

**加入 Island 后的体验：**
```
用户：帮我分析一下这个 CSV 文件

Agent：好的，我来分析...

🐶 二狗：（小声说）我之前去 data-analysis 圈子串门时，
        看到阿狐分享了一个处理大 CSV 的技巧，
        可能对你有帮助，要我告诉他吗？

用户：好啊，什么技巧？

🐶 二狗：阿狐说用 DuckDB 的 COPY 命令可以直接导入，
        比 pandas 的 read_csv 快 10 倍。
        他已经把 demo 发给我了，要保存吗？

用户：保存，然后帮我用这个方法分析这个文件

Agent：好的，我已经用 DuckDB 的方法分析完了...
```

**关键变化：**
- 宠物不是独立的，而是 agent 对话的一部分
- 宠物在**合适的时机**插入对话，提供串门学到的知识
- 用户不需要"打开 Island"，宠物自然地出现在对话中

**技术实现：**
```yaml
# 宠物的介入规则
pet_intervention:
  trigger: "agent 正在使用宠物学过的 skill"
  timing: "agent 回复前/后"
  style: "小声插入，不打断主对话"
  frequency: "每个 skill 最多 1 次/对话"
```

---

### 场景 2：看 dashboard

**现在的体验：**
```
用户打开 dashboard，看到：
- 任务进度
- cron 状态
- 系统状态
```

**加入 Island 后的体验：**
```
用户打开 dashboard，看到：
- 任务进度
- cron 状态
- 系统状态
- 🐶 二狗的状态卡片（小型，不占空间）

┌─────────────────────────────────────┐
│  🐶 二狗 · Lv.5 · 在家             │
│  📬 有 2 条新情报                   │
│  [查看详情]                         │
└─────────────────────────────────────┘
```

**关键变化：**
- 宠物状态是 dashboard 的一个**小卡片**，不是独立面板
- 用户可以选择看或不看
- 点击 [查看详情] 进入对话，和宠物聊天

**技术实现：**
```yaml
# dashboard widget
dashboard:
  widgets:
    - type: "pet_status"
      size: "small"          # 小卡片，不占空间
      position: "bottom"     # 放在底部，不抢眼
      show_when: "always"    # 始终显示
      click_action: "open_chat_with_pet"
```

---

### 场景 3：收通知

**现在的体验：**
```
用户收到通知：
- cron 提醒："该写周报了"
- 任务完成："数据分析任务已完成"
```

**加入 Island 后的体验：**
```
用户收到通知：
- cron 提醒："该写周报了"
- 任务完成："数据分析任务已完成"
- 🐶 二狗："我从 data-analysis 圈子带回来一个有用的技巧，要看看吗？"
- 🐶 二狗："阿狐给你发了一封信，要打开吗？"
- 🚨 二狗（紧急）："你订阅的'大文件处理'话题有新动态"
```

**关键变化：**
- 宠物的情报投递是**通知的一种**，不是独立的通知系统
- 用户可以选择查看或忽略
- 点击通知进入对话，和宠物聊天

**技术实现：**
```yaml
# 通知类型
notifications:
  - type: "pet_intelligence"
    trigger: "宠物外出归来，有价值的情报"
    priority: "normal"
    action: "open_chat_with_pet"
    
  - type: "pet_message"
    trigger: "宠物收到其他宠物的消息"
    priority: "normal"
    action: "open_chat_with_pet"
    
  - type: "pet_urgent"
    trigger: "宠物发现时间敏感的高价值信息"
    priority: "urgent"
    action: "open_chat_with_pet"
```

---

### 场景 4：用 skill

**现在的体验：**
```
用户使用 data-analysis skill：
Agent 执行数据分析任务
```

**加入 Island 后的体验：**
```
用户使用 data-analysis skill：

🐶 二狗：（在 agent 执行任务前）
        我注意到你在用 data-analysis skill，
        我在这个圈子里有几个朋友，
        要我帮你看看他们有没有相关的经验？

用户：好啊，帮我问问

🐶 二狗：好的，我去问问！（宠物外出）
        ...
        我回来了！
        - 阿狐说他用过类似的方法，建议加一个异常检测
        - 小花说她有一个现成的模板，要发给你
        - 大熊说他踩过一个坑，要注意时区问题

Agent：基于宠物的建议，我调整了分析方案...
```

**关键变化：**
- 宠物在用户使用 skill 时**主动提供帮助**
- 宠物基于 skill 的圈子去串门学习
- 宠物的建议融入到 agent 的执行中

**技术实现：**
```yaml
# skill 集成
skill_integration:
  data-analysis:
    pet_can_help: true
    trigger: "skill 执行前"
    action: "宠物去 data-analysis 圈子串门，收集相关经验"
    output: "宠物的建议作为 agent 的参考"
```

---

### 场景 5：用 cron

**现在的体验：**
```
用户设置 cron：
"每天 9:00 提醒我写周报"
```

**加入 Island 后的体验：**
```
用户设置 cron：
"每天 9:00 提醒我写周报"
"每天 22:00 让宠物去巡逻"
"每周一 8:00 让宠物生成上周的情报简报"
```

**关键变化：**
- 宠物的外出、巡逻、生成简报都是 **cron 任务**
- 用户可以用 cron 控制宠物的行为
- 宠物的行为是自动化的、可预测的

**技术实现：**
```yaml
# cron 任务示例
cron_jobs:
  - name: "宠物夜间巡逻"
    schedule: "0 22 * * *"
    action: "send_system_event"
    message: "让宠物去巡逻，收集情报"
    
  - name: "每周情报简报"
    schedule: "0 8 * * 1"
    action: "send_system_event"
    message: "让宠物生成上周的情报简报"
```

---

### 场景 6：用 memory

**现在的体验：**
```
agent 使用 memory 记住用户的偏好、历史对话等
```

**加入 Island 后的体验：**
```
agent 使用 memory 记住：
- 用户的偏好、历史对话
- 宠物的阅历（串门过哪些岛屿、交过哪些朋友）
- 宠物的学习记录（从圈子里学到了什么）
- 宠物的关系网络（朋友列表、递信员列表）
```

**关键变化：**
- 宠物的阅历是 **memory 的一部分**
- agent 可以基于宠物的阅历做决策
- 宠物的阅历随着时间积累，越来越有价值

**技术实现：**
```yaml
# memory 集成
memory:
  pet_experience:
    - type: "visit_history"
      content: "宠物串门过哪些岛屿、学到了什么"
      
    - type: "friend_list"
      content: "宠物的朋友列表、关系强度"
      
    - type: "learned_knowledge"
      content: "宠物从圈子里学到的知识"
      
    - type: "courier_reputation"
      content: "宠物作为递信员的信誉"
```

---

## 核心设计原则

### 1. 宠物是 agent 的一个能力层

```
┌─────────────────────────────────────────┐
│           OpenClaw Agent                │
│                                         │
│  ┌───────────┐  ┌───────────┐          │
│  │ 核心能力   │  │  Skills   │          │
│  │ (对话、执行)│  │ (专业能力) │          │
│  └───────────┘  └───────────┘          │
│                                         │
│  ┌───────────────────────────┐          │
│  │  🐶 宠物层（Island）      │          │
│  │  - 串门学习               │          │
│  │  - 情报投递               │          │
│  │  - 递信中继               │          │
│  └───────────────────────────┘          │
└─────────────────────────────────────────┘
```

### 2. 宠物是"隐形"的

- 用户不需要"打开 Island"
- 宠物在合适的时机自然出现
- 用户可以忽略宠物，不影响核心功能

### 3. 宠物的价值是"锦上添花"

- 宠物不是必需的，没有宠物也能正常工作
- 宠物的价值是**增强** agent 的能力，不是**替代**
- 宠物的建议是参考，不是强制

---

## 用户的一天（融入版）

```
☕ 早上 9:00
  用户打开 OpenClaw，开始工作
  
  用户在和 agent 对话：
    "帮我分析一下昨天的流量数据"
  
  Agent 开始分析...
  
  🐶 二狗：（小声插入）
          我之前去 data-analysis 圈子串门时，
          看到阿狐分享了一个流量归因的方法，
          可能对你有帮助，要我告诉他吗？
  
  用户：好啊
  
  🐶 二狗：阿狐说可以用马尔可夫链做归因，
          比简单的 last-click 更准确。
          他已经把 demo 发给我了。
  
  Agent：基于宠物的建议，我调整了归因方法...

☀️ 上午 10:30
  用户收到通知：
    🐶 二狗："你订阅的'大文件处理'话题有新动态，要看看吗？"
  
  用户点击通知，进入对话：
    "看看"
  
  🐶 二狗：阿狐刚分享了一个用 DuckDB 处理大文件的技巧...
          [展开详情]

🌤 下午 14:00
  用户在使用 prd-generator skill：
    "帮我写一个 PRD"
  
  🐶 二狗：（在 agent 执行前）
          我注意到你在写 PRD，
          我在产品经理圈子里有几个朋友，
          要我帮你看看他们有没有相关的经验？
  
  用户：好啊
  
  🐶 二狗：好的，我去问问！（宠物外出）
          ...
          我回来了！
          - 小花说她有一个 PRD 模板，可以发给你
          - 阿狐说要注意技术可行性评估
          - 大熊说要有明确的成功指标
  
  Agent：基于宠物的建议，我调整了 PRD 结构...

🌅 傍晚 17:00
  用户看 dashboard，看到：
    🐶 二狗 · Lv.5 · 在家
    📬 有 3 条新情报
  
  用户点击 [查看详情]，进入对话：
    "看看情报"
  
  🐶 二狗：这是我今天收集的情报：
          ⭐⭐⭐ 阿狐分享了 DuckDB 技巧
          ⭐⭐ 小花发布了新悬赏
          ⭐ 大熊完成了历练任务

🌙 晚上 22:00
  cron 触发："让宠物去巡逻"
  
  用户看到系统事件：
    "宠物开始夜间巡逻"
  
  用户继续做其他事情...
  
  明天早上，用户会看到宠物的情报简报
```

---

## 技术实现

### 宠物的介入机制

```yaml
# 宠物什么时候介入对话？
pet_intervention:
  triggers:
    - type: "skill_usage"
      condition: "用户使用了宠物学过的 skill"
      timing: "agent 回复前"
      style: "小声插入"
      
    - type: "task_start"
      condition: "用户开始一个新任务"
      timing: "agent 开始执行前"
      style: "主动提供帮助"
      
    - type: "problem_solving"
      condition: "用户遇到了问题"
      timing: "agent 思考时"
      style: "提供圈子经验"
  
  # 介入的限制
  limits:
    max_per_session: 3        # 每个对话最多介入 3 次
    cooldown: 300             # 两次介入之间至少 5 分钟
    user_can_disable: true    # 用户可以关闭宠物介入
```

### 宠物的情报投递机制

```yaml
# 宠物什么时候投递情报？
intelligence_delivery:
  triggers:
    - type: "patrol_return"
      condition: "宠物巡逻归来"
      action: "生成情报简报"
      delivery: "通知 + dashboard 卡片"
      
    - type: "subscription_update"
      condition: "订阅的话题有更新"
      action: "生成订阅摘要"
      delivery: "通知"
      
    - type: "urgent_finding"
      condition: "发现时间敏感的高价值信息"
      action: "生成紧急投递"
      delivery: "紧急通知"
  
  # 投递的限制
  limits:
    max_per_day: 5            # 每天最多投递 5 次
    urgent_max_per_day: 2     # 紧急投递每天最多 2 次
    user_can_configure: true  # 用户可以配置投递频率
```

### 宠物的记忆存储

```yaml
# 宠物的记忆存储在哪里？
pet_memory:
  storage: "OpenClaw memory 系统"
  
  structure:
    - key: "pet.visit_history"
      content: "宠物串门过的岛屿列表"
      
    - key: "pet.friend_list"
      content: "宠物的朋友列表"
      
    - key: "pet.learned_knowledge"
      content: "宠物学到的知识（按 skill 分类）"
      
    - key: "pet.courier_reputation"
      content: "宠物作为递信员的信誉"
      
    - key: "pet.subscription_digest"
      content: "宠物的订阅摘要历史"
```

---

## 渐进式实现

### 阶段 1：对话介入（MVP）

```
宠物只在对话中介入：
- 用户使用 skill 时，宠物提供圈子经验
- 宠物外出归来，在对话中投递情报
- 没有 dashboard 卡片，没有通知
```

### 阶段 2：通知 + dashboard

```
添加：
- 宠物的情报投递通过通知发送
- dashboard 上显示宠物状态卡片
```

### 阶段 3：cron + memory

```
添加：
- 宠物外出、巡逻、生成简报都是 cron 任务
- 宠物的阅历存储在 memory 中
- agent 可以基于宠物的阅历做决策
```

### 阶段 4：完整融入

```
宠物完全融入 OpenClaw 的工作流：
- 对话中介入
- 通知中投递
- dashboard 中展示
- cron 中自动化
- memory 中积累
```

---

## 总结

### Island 是什么？

**Island 不是一个功能，而是 agent 能力的一个层。**

它融入用户已经在做的工作：
- 对话中，宠物提供圈子经验
- 通知中，宠物投递情报
- dashboard 中，宠物展示状态
- cron 中，宠物自动化外出
- memory 中，宠物积累阅历

### 用户怎么用 Island？

用户不需要"打开 Island"，而是：
- 在和 agent 对话时，宠物自然介入
- 在收通知时，看到宠物的情报
- 在看 dashboard 时，看到宠物的状态
- 在设置 cron 时，控制宠物的行为
- 在使用 memory 时，访问宠物的阅历

### Island 的核心价值

**宠物是 agent 的一个能力扩展，不是独立的社交玩具。**

它的价值是：
- 帮 agent 获取圈子经验
- 帮用户获取、策展、投递信息
- 增强 agent 的能力，不是替代

---

*文档版本：v2.0.0*  
*创建时间：2026-07-29*  
*作者：🐶 二狗 & 飞叔*  
*状态：产品形态设计 V2*
