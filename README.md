# 🤖 Agent智能客服系统

> 基于 **LangGraph + RAG + Function Call** 的智能客服Agent，5天可完成，面试级项目。

---

## 📐 架构总览

```
用户提问 → [意图识别] → 条件路由
                         ├─ FAQ问题 → [RAG知识检索] → [生成回答]
                         ├─ 查询操作 → [Function Call] → [判断是否解决] → 循环/回答
                         ├─ 转人工 → [生成工单+转接]
                         └─ 闲聊 → [直接回答]
```

### 三大核心模块

| 模块 | 做什么 | 用到的技术 |
|------|--------|-----------|
| **RAG知识库** | 把FAQ存进向量库，用户提问时检索最相关的知识 | Chroma + BGE-small-zh + Rerank |
| **Function Call** | Agent调用业务工具（查订单、退款、查库存等） | LangChain Tools + OpenAI Function Call |
| **Agent编排** | 用图结构定义"意图→路由→处理"的完整流程 | LangGraph StateGraph |

---

## 📁 项目结构

```
agent-customer-service/
├── main.py                      # 🚀 FastAPI入口（启动服务）
├── config.py                    # ⚙️ 全局配置（LLM/RAG/Agent参数）
├── requirements.txt             # 📦 依赖清单
├── .env.example                 # 🔑 环境变量模板
├── Dockerfile                   # 🐳 Docker部署
│
├── app/
│   ├── rag/                     # 📚 RAG模块
│   │   ├── embeddings.py        #   Embedding模型（BGE-small-zh）
│   │   ├── vectorstore.py       #   向量库（Chroma）
│   │   └── retriever.py         #   检索器（相似度+Rerank）
│   │
│   ├── tools/                   # 🔧 工具模块（Agent的手脚）
│   │   ├── order_tools.py       #   订单查询/退款
│   │   ├── inventory_tools.py   #   库存查询/商品搜索
│   │   └── human_transfer.py    #   转人工
│   │
│   ├── agent/                   # 🧠 Agent核心
│   │   ├── state.py             #   状态定义（AgentState）
│   │   ├── nodes.py             #   节点逻辑（意图识别/RAG/工具/回答）
│   │   └── graph.py             #   状态图（LangGraph编排）
│   │
│   ├── api/                     # 🌐 API接口
│   │   └── routes.py            #   FastAPI路由
│   │
│   ├── memory/                  # 💾 对话记忆
│   │   └── conversation.py      #   滑动窗口记忆管理
│   │
│   └── utils/                   # 🛡️ 工具类
│       └── guardrails.py        #   安全过滤（输入/输出/注入检测）
│
├── data/                        # 📊 数据
│   ├── faq.json                 #   FAQ知识库（12条示例）
│   └── mock_orders.json         #   模拟订单/库存数据
│
└── frontend/
    └── app.py                   # 🖥️ Streamlit前端
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd agent-customer-service

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的DeepSeek API Key
# 注册地址: https://platform.deepseek.com/（有免费额度）
```

### 3. 启动后端

```bash
# 启动FastAPI服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 首次启动会自动：
# 1. 下载BGE-small-zh Embedding模型（约100MB，1-3分钟）
# 2. 构建Chroma向量库
# 3. 编译LangGraph状态图
```

### 4. 启动前端（可选）

```bash
# 新开一个终端
streamlit run frontend/app.py --server.port 8501
```

### 5. 测试

```bash
# 方式1：浏览器打开 http://localhost:8501（Streamlit界面）

# 方式2：浏览器打开 http://localhost:8000/docs（Swagger API文档）

# 方式3：命令行测试
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "怎么退货？", "user_id": "U1001"}'
```

---

## 🔥 面试攻略：怎么聊这个项目

### 项目介绍话术（1分钟版）

> 我做了一个基于LangGraph的智能客服Agent。核心是三层架构：
> 第一层是意图识别，用LLM判断用户想做什么；
> 第二层是条件路由，FAQ走RAG检索，业务操作走Function Call；
> 第三层是工具执行，Agent可以查订单、退款、查库存，处理不了就转人工。
> 技术栈是LangGraph编排 + Chroma向量库 + DeepSeek LLM + FastAPI后端 + Streamlit前端。

### 必考问题 & 标准答案

| 面试问题 | 回答要点 | 代码位置 |
|---------|---------|---------|
| **为什么用LangGraph？** | 图结构支持条件路由，客服场景需要FAQ/工具/转人工多分支；AgentExecutor是线性链做不到 | `app/agent/graph.py` |
| **RAG检索不准怎么办？** | 调chunk_size + 混合检索 + Rerank重排序 + 查询改写，本项目实现了前三个 | `app/rag/retriever.py` |
| **chunk_size怎么选？** | 中文FAQ场景500字符是甜点；太小上下文不够，太大噪声多 | `config.py` |
| **Function Call怎么工作？** | LLM输出工具调用请求（name+args），系统执行后把结果喂回LLM，LLM组织语言回答 | `app/tools/` |
| **工具调用失败怎么办？** | 重试1次 → 降级转人工 → 记录日志；达到最大迭代次数自动转人工 | `app/agent/nodes.py` |
| **怎么防Prompt注入？** | 输入层：敏感词+注入模式检测；处理层：话题限制；输出层：敏感信息脱敏 | `app/utils/guardrails.py` |
| **对话记忆怎么管理？** | 滑动窗口策略，保留最近10轮；生产环境用窗口+摘要组合 | `app/memory/conversation.py` |
| **怎么评估效果？** | 准备50条标注QA，跑准确率/召回率；人工抽检；埋点统计转人工率 | — |
| **为什么选Chroma？** | 轻量免部署，百万级以下够用；生产环境换Milvus支持亿级 | `app/rag/vectorstore.py` |

### 你的差异化加分项（别人做不出来的）

1. **多模态入口**：用户截图商品问题 → PaddleOCR识别 → 自动关联订单
2. **模型量化经验**：部署时BGE模型INT8量化，CPU推理速度提升3倍
3. **边缘部署**：Embedding模型ONNX化跑CPU，降低GPU成本

---

## 📈 进阶优化方向

| 方向 | 做什么 | 难度 | 面试加分 |
|------|--------|------|---------|
| 流式输出 | 打字机效果，用户体验大幅提升 | ⭐⭐ | ⭐⭐⭐⭐ |
| 对话摘要 | 长对话压缩，节省token | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 多Agent协作 | 订单Agent+退款Agent+推荐Agent | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 情绪识别 | 用户生气时自动转人工 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 评估体系 | 准确率/召回率/转人工率指标 | ⭐⭐ | ⭐⭐⭐⭐ |
| Redis记忆 | 分布式会话存储 | ⭐⭐ | ⭐⭐⭐ |
| Milvus向量库 | 亿级向量检索 | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🐛 常见问题

**Q: 首次启动很慢？**
A: 正常现象。首次需要下载BGE-small-zh模型（约100MB），后续启动秒级。

**Q: API返回500错误？**
A: 检查 .env 中的 DEEPSEEK_API_KEY 是否正确，网络是否能访问 api.deepseek.com。

**Q: 前端连不上后端？**
A: 确认后端已启动（`uvicorn main:app --reload`），端口8000未被占用。

**Q: 想换OpenAI的模型？**
A: 修改 .env 中的 LLM_BASE_URL 和 LLM_API_KEY，模型名改成 gpt-4o-mini。

---

## 📝 许可

本项目仅供学习使用，面试展示效果极佳 ✨
