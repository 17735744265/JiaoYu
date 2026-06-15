"""
============================================
Agent状态定义
============================================

【讲解】这是LangGraph的"数据结构"——定义Agent在流程中传递什么信息。

LangGraph的核心概念：
- State（状态）：节点之间传递的数据容器
- Node（节点）：处理状态的函数
- Edge（边）：节点之间的流转规则

为什么用TypedDict而不是普通dict？
- 类型提示：IDE自动补全，减少bug
- LangGraph根据类型定义自动管理状态的更新和合并
- 面试体现"工程规范"

【面试考点】LangGraph vs LangChain Agent？
- LangChain Agent：线性链，tool → observe → tool → observe ...
- LangGraph：图结构，可以有条件路由、循环、并行分支
- 客服场景需要条件路由（FAQ走RAG，查询走工具），所以用LangGraph
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Agent状态定义
    
    【讲解】每个字段的含义：
    - messages: 对话历史（最核心的字段）
    - intent: 意图识别结果
    - rag_context: RAG检索到的上下文
    - tool_results: 工具调用的结果
    - iteration_count: 当前推理轮数（防死循环）
    - user_id: 用户ID（用于查订单等个性化操作）
    
    Annotated[..., add_messages] 的含义：
    - add_messages 是LangGraph提供的reducer函数
    - 作用：新消息追加到列表，而不是覆盖
    - 这样每个节点往messages里加消息时，之前的消息不会丢
    """
    # 对话消息列表（使用add_messages reducer，新消息自动追加）
    messages: Annotated[list, add_messages]
    
    # 意图识别结果
    intent: str  # "faq" | "tool_call" | "general" | "transfer_human"
    
    # RAG检索上下文
    rag_context: str
    
    # 工具调用结果
    tool_results: list[str]
    
    # 推理轮数计数
    iteration_count: int
    
    # 用户ID（从请求中获取，用于个性化服务）
    user_id: str

    subject_level: str          # 新增：用户当前学科水平，如"高中数学-基础薄弱"