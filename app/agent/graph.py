# # """
# # ============================================
# # LangGraph状态图定义
# # ============================================

# # 【讲解】这是整个项目的"骨架"——用图结构定义Agent的完整流程。

# # LangGraph核心概念（面试必考）：
# # 1. StateGraph: 状态图，用状态来驱动流程
# # 2. Node: 节点，处理状态的函数
# # 3. Edge: 边，定义节点间的流转
# #    - 普通边: A → B（无条件跳转）
# #    - 条件边: A → {条件1: B, 条件2: C}（根据状态路由）
# # 4. START / END: 特殊节点，标记流程起止点

# # 画成图就是这样：

# #     START
# #       ↓
# #   [意图识别]
# #       ↓ (条件路由)
# #    ┌──┼──┬──┐
# #    ↓  ↓  ↓  ↓
# #  FAQ 工具 转人工 闲聊
# #    ↓  ↓  ↓  ↓
# # [RAG][调用][处理][直接]
# #    ↓  ↓  ↓  ↓
# # [回答][回答][回答][回答]
# #    ↓  ↓  ↓  ↓
# #     END

# # 【面试考点】为什么用LangGraph不用LangChain的AgentExecutor？
# # 1. AgentExecutor是线性链，无法做条件路由
# # 2. AgentExecutor的工具调用是"全都要试一遍"，效率低
# # 3. LangGraph可以精细控制每一步，加条件、加循环、加并行
# # 4. LangGraph的可观测性更好，每个节点都可以单独追踪
# # """

# # from langgraph.graph import StateGraph, START, END
# # from app.agent.state import AgentState
# # from app.agent.nodes import (
# #     intent_recognition,
# #     rag_retrieve,
# #     tool_call_node,
# #     generate_response,
# #     handle_transfer_human,
# # )
# # from config import MAX_ITERATIONS


# # def route_by_intent(state: AgentState) -> str:
# #     """
# #     条件路由函数：根据意图决定下一步
    
# #     【讲解】这是条件边的核心——根据状态中的intent字段，
# #     决定走哪条路径。返回值是目标节点的名称。
    
# #     返回值必须是图中已注册的节点名称之一。
# #     """
# #     intent = state.get("intent", "general")
    
# #     route_map = {
# #         "faq": "rag_retrieve",
# #         "tool_call": "tool_call_node",
# #         "transfer_human": "handle_transfer_human",
# #         "general": "generate_response",
# #     }
    
# #     target = route_map.get(intent, "generate_response")
# #     print(f"[Graph] 路由: intent={intent} → node={target}")
# #     return target


# # def should_continue_tool_call(state: AgentState) -> str:
# #     """
# #     工具调用后的判断：继续调用工具，还是生成回答？
    
# #     【讲解】这是Agent的"循环控制"——
# #     有些问题需要连续调用多个工具（比如先查订单再退款），
# #     有些一次工具调用就够了。
    
# #     判断逻辑：
# #     1. 如果LLM的最后一次消息包含工具调用请求 → 继续调用
# #     2. 如果迭代次数达到上限 → 生成回答
# #     3. 否则 → 生成回答
# #     """
# #     messages = state["messages"]
# #     iteration = state.get("iteration_count", 0)
    
# #     # 安全检查：达到最大迭代次数
# #     if iteration >= MAX_ITERATIONS:
# #         print(f"[Graph] 达到最大迭代次数 {MAX_ITERATIONS}，转向生成回答")
# #         return "generate_response"
    
# #     # 检查最后一条AI消息是否包含工具调用
# #     from langchain_core.messages import AIMessage
# #     for msg in reversed(messages):
# #         if isinstance(msg, AIMessage):
# #             if msg.tool_calls:
# #                 # LLM还想继续调用工具
# #                 print(f"[Graph] LLM请求继续调用工具: {[tc['name'] for tc in msg.tool_calls]}")
# #                 return "tool_call_node"
# #             break
    
# #     # 没有更多工具调用需求，生成最终回答
# #     return "generate_response"


# # def build_graph() -> StateGraph:
# #     """
# #     构建Agent状态图
    
# #     【讲解】这是整个项目的"组装车间"——
# #     把节点和边组合成一个完整的图。
    
# #     步骤：
# #     1. 创建StateGraph，指定状态类型
# #     2. 添加节点
# #     3. 添加边
# #     4. 编译图（编译后才能执行）
# #     """
    
# #     # 1. 创建状态图
# #     graph = StateGraph(AgentState)
    
# #     # 2. 添加节点
# #     graph.add_node("intent_recognition", intent_recognition)     # 意图识别
# #     graph.add_node("rag_retrieve", rag_retrieve)                 # RAG检索
# #     graph.add_node("tool_call_node", tool_call_node)             # 工具调用
# #     graph.add_node("generate_response", generate_response)       # 生成回答
# #     graph.add_node("handle_transfer_human", handle_transfer_human)  # 转人工
    
# #     # 3. 添加边
    
# #     # 3.1 入口边：START → 意图识别
# #     graph.add_edge(START, "intent_recognition")
    
# #     # 3.2 条件边：意图识别 → 根据意图路由到不同节点
# #     graph.add_conditional_edges(
# #         "intent_recognition",    # 源节点
# #         route_by_intent,         # 路由函数
# #         {                        # 路由映射
# #             "rag_retrieve": "rag_retrieve",
# #             "tool_call_node": "tool_call_node",
# #             "handle_transfer_human": "handle_transfer_human",
# #             "generate_response": "generate_response",
# #         }
# #     )
    
# #     # 3.3 RAG检索 → 生成回答（FAQ路径）
# #     graph.add_edge("rag_retrieve", "generate_response")
    
# #     # 3.4 工具调用 → 条件判断（继续调用还是生成回答）
# #     graph.add_conditional_edges(
# #         "tool_call_node",
# #         should_continue_tool_call,
# #         {
# #             "tool_call_node": "tool_call_node",       # 继续调用工具（循环）
# #             "generate_response": "generate_response",  # 生成回答
# #         }
# #     )
    
# #     # 3.5 生成回答 → END
# #     graph.add_edge("generate_response", END)
    
# #     # 3.6 转人工 → END
# #     graph.add_edge("handle_transfer_human", END)
    
# #     # 4. 编译图
# #     # 编译会做类型检查、拓扑排序等优化
# #     compiled_graph = graph.compile()
    
# #     print("[Graph] Agent状态图构建完成 ✅")
# #     return compiled_graph


# # # ========== 便捷调用函数 ==========

# # # 全局图实例
# # _graph = None


# # def get_graph():
# #     """获取编译后的图实例（单例）"""
# #     global _graph
# #     if _graph is None:
# #         _graph = build_graph()
# #     return _graph


# # def chat(query: str, user_id: str = "U1001") -> str:
# #     """
# #     与Agent对话的便捷接口
    
# #     【讲解】这是最简单的调用方式，一行代码就能和Agent聊天。
# #     适合：测试、调试、命令行交互
    
# #     Args:
# #         query: 用户消息
# #         user_id: 用户ID
        
# #     Returns:
# #         Agent的回复文本
    
# #     使用示例：
# #         >>> from app.agent.graph import chat
# #         >>> chat("我的订单到哪了？")
# #         >>> chat("怎么退货？", user_id="U1002")
# #     """
# #     graph = get_graph()
    
# #     # 初始化状态
# #     initial_state = {
# #         "messages": [HumanMessage(content=query)],
# #         "intent": "",
# #         "rag_context": "",
# #         "tool_results": [],
# #         "iteration_count": 0,
# #         "user_id": user_id,
# #     }
    
# #     # 执行图
# #     result = graph.invoke(initial_state)
    
# #     # 提取最后一条AI消息作为回复
# #     from langchain_core.messages import AIMessage
# #     for msg in reversed(result["messages"]):
# #         if isinstance(msg, AIMessage) and msg.content:
# #             return msg.content
    
# #     return "抱歉，我暂时无法处理您的问题，建议转接人工客服。"


# # # 需要在顶部导入
# # from langchain_core.messages import HumanMessage
# """
# ============================================
# LangGraph状态图定义
# ============================================

# 【讲解】这是整个项目的"骨架"——用图结构定义Agent的完整流程。

# LangGraph核心概念（面试必考）：
# 1. StateGraph: 状态图，用状态来驱动流程
# 2. Node: 节点，处理状态的函数
# 3. Edge: 边，定义节点间的流转
#    - 普通边: A → B（无条件跳转）
#    - 条件边: A → {条件1: B, 条件2: C}（根据状态路由）
# 4. START / END: 特殊节点，标记流程起止点

# 画成图就是这样：

#     START
#       ↓
#   [意图识别]
#       ↓ (条件路由)
#    ┌──┼──┬──┐
#    ↓  ↓  ↓  ↓
#  FAQ 工具 转人工 闲聊
#    ↓  ↓  ↓  ↓
# [RAG][调用][处理][直接]
#    ↓  ↓  ↓  ↓
# [回答][回答][回答][回答]
#    ↓  ↓  ↓  ↓
#     END

# 【面试考点】为什么用LangGraph不用LangChain的AgentExecutor？
# 1. AgentExecutor是线性链，无法做条件路由
# 2. AgentExecutor的工具调用是"全都要试一遍"，效率低
# 3. LangGraph可以精细控制每一步，加条件、加循环、加并行
# 4. LangGraph的可观测性更好，每个节点都可以单独追踪
# """

# from langgraph.graph import StateGraph, START, END
# from app.agent.state import AgentState
# from app.agent.nodes import (
#     intent_recognition,
#     rag_retrieve,
#     tool_call_node,
#     generate_response,
#     handle_transfer_human,
# )
# from config import MAX_ITERATIONS


# def route_by_intent(state: AgentState) -> str:
#     """
#     条件路由函数：根据意图决定下一步
    
#     【讲解】这是条件边的核心——根据状态中的intent字段，
#     决定走哪条路径。返回值是目标节点的名称。
    
#     返回值必须是图中已注册的节点名称之一。
#     """
#     intent = state.get("intent", "general")
    
#     route_map = {
#         "faq": "rag_retrieve",
#         "tool_call": "tool_call_node",
#         "transfer_human": "handle_transfer_human",
#         "general": "generate_response",
#     }
    
#     target = route_map.get(intent, "generate_response")
#     print(f"[Graph] 路由: intent={intent} → node={target}")
#     return target


# def should_continue_tool_call(state: AgentState) -> str:
#     """
#     工具调用后的判断：继续调用工具，还是生成回答？
    
#     【讲解】这是Agent的"循环控制"——
#     有些问题需要连续调用多个工具（比如先查订单再退款），
#     有些一次工具调用就够了。
    
#     判断逻辑：
#     1. 如果LLM的最后一次消息包含工具调用请求 → 继续调用
#     2. 如果迭代次数达到上限 → 生成回答
#     3. 否则 → 生成回答
#     """
#     messages = state["messages"]
#     iteration = state.get("iteration_count", 0)
    
#     # 安全检查：达到最大迭代次数
#     if iteration >= MAX_ITERATIONS:
#         print(f"[Graph] 达到最大迭代次数 {MAX_ITERATIONS}，转向生成回答")
#         return "generate_response"
    
#     # 检查最后一条AI消息是否包含工具调用
#     from langchain_core.messages import AIMessage
#     for msg in reversed(messages):
#         if isinstance(msg, AIMessage):
#             if msg.tool_calls:
#                 # LLM还想继续调用工具
#                 print(f"[Graph] LLM请求继续调用工具: {[tc['name'] for tc in msg.tool_calls]}")
#                 return "tool_call_node"
#             break
    
#     # 没有更多工具调用需求，生成最终回答
#     return "generate_response"


# def build_graph() -> StateGraph:
#     """
#     构建Agent状态图
    
#     【讲解】这是整个项目的"组装车间"——
#     把节点和边组合成一个完整的图。
    
#     步骤：
#     1. 创建StateGraph，指定状态类型
#     2. 添加节点
#     3. 添加边
#     4. 编译图（编译后才能执行）
#     """
    
#     # 1. 创建状态图
#     graph = StateGraph(AgentState)
    
#     # 2. 添加节点
#     graph.add_node("intent_recognition", intent_recognition)     # 意图识别
#     graph.add_node("rag_retrieve", rag_retrieve)                 # RAG检索
#     graph.add_node("tool_call_node", tool_call_node)             # 工具调用
#     graph.add_node("generate_response", generate_response)       # 生成回答
#     graph.add_node("handle_transfer_human", handle_transfer_human)  # 转人工
    
#     # 3. 添加边
    
#     # 3.1 入口边：START → 意图识别
#     graph.add_edge(START, "intent_recognition")
    
#     # 3.2 条件边：意图识别 → 根据意图路由到不同节点
#     graph.add_conditional_edges(
#         "intent_recognition",    # 源节点
#         route_by_intent,         # 路由函数
#         {                        # 路由映射
#             "rag_retrieve": "rag_retrieve",
#             "tool_call_node": "tool_call_node",
#             "handle_transfer_human": "handle_transfer_human",
#             "generate_response": "generate_response",
#         }
#     )
    
#     # 3.3 RAG检索 → 生成回答（FAQ路径）
#     graph.add_edge("rag_retrieve", "generate_response")
    
#     # 3.4 工具调用 → 条件判断（继续调用还是生成回答）
#     graph.add_conditional_edges(
#         "tool_call_node",
#         should_continue_tool_call,
#         {
#             "tool_call_node": "tool_call_node",       # 继续调用工具（循环）
#             "generate_response": "generate_response",  # 生成回答
#         }
#     )
    
#     # 3.5 生成回答 → END
#     graph.add_edge("generate_response", END)
    
#     # 3.6 转人工 → END
#     graph.add_edge("handle_transfer_human", END)
    
#     # 4. 编译图
#     # 编译会做类型检查、拓扑排序等优化
#     compiled_graph = graph.compile()
    
#     print("[Graph] Agent状态图构建完成 ✅")
#     return compiled_graph


# # ========== 便捷调用函数 ==========

# # 全局图实例
# _graph = None


# def get_graph():
#     """获取编译后的图实例（单例）"""
#     global _graph
#     if _graph is None:
#         _graph = build_graph()
#     return _graph


# def chat(query: str, user_id: str = "U1001") -> str:
#     """
#     与Agent对话的便捷接口
    
#     【讲解】这是最简单的调用方式，一行代码就能和Agent聊天。
#     适合：测试、调试、命令行交互
    
#     Args:
#         query: 用户消息
#         user_id: 用户ID
        
#     Returns:
#         Agent的回复文本
    
#     使用示例：
#         >>> from app.agent.graph import chat
#         >>> chat("我的订单到哪了？")
#         >>> chat("怎么退货？", user_id="U1002")
#     """
#     graph = get_graph()
    
#     # 初始化状态
#     initial_state = {
#         "messages": [HumanMessage(content=query)],
#         "intent": "",
#         "rag_context": "",
#         "tool_results": [],
#         "iteration_count": 0,
#         "user_id": user_id,
#         "subject_level": "未评估",
#     }
    
#     # 执行图
#     result = graph.invoke(initial_state)
    
#     # 提取最后一条AI消息作为回复
#     from langchain_core.messages import AIMessage
#     for msg in reversed(result["messages"]):
#         if isinstance(msg, AIMessage) and msg.content:
#             return msg.content
    
#     return "抱歉，我暂时无法处理您的问题，建议转接人工客服。"


# # 需要在顶部导入
# from langchain_core.messages import HumanMessage

"""
============================================
LangGraph状态图定义
============================================
"""

from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes import (
    intent_recognition,
    rag_retrieve,
    tool_call_node,
    tool_execution,
    generate_response,
    handle_transfer_human,
)
from config import MAX_ITERATIONS


def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "general")
    route_map = {
        "faq": "rag_retrieve",
        "tool_call": "tool_call_node",
        "transfer_human": "handle_transfer_human",
        "general": "generate_response",
    }
    target = route_map.get(intent, "generate_response")
    print(f"[Graph] 路由: intent={intent} → node={target}")
    return target


def should_continue_tool_call(state: AgentState) -> str:
    """
    tool_call_node后的判断：执行工具，还是直接生成回答？
    """
    messages = state["messages"]
    iteration = state.get("iteration_count", 0)
    
    if iteration >= MAX_ITERATIONS:
        print(f"[Graph] 达到最大迭代次数 {MAX_ITERATIONS}，转向生成回答")
        return "generate_response"
    
    from langchain_core.messages import AIMessage
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            if msg.tool_calls:
                print(f"[Graph] LLM请求调用工具: {[tc['name'] for tc in msg.tool_calls]}")
                return "tool_execution"
            break
    
    return "generate_response"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    
    # 添加节点
    graph.add_node("intent_recognition", intent_recognition)
    graph.add_node("rag_retrieve", rag_retrieve)
    graph.add_node("tool_call_node", tool_call_node)
    graph.add_node("tool_execution", tool_execution)
    graph.add_node("generate_response", generate_response)
    graph.add_node("handle_transfer_human", handle_transfer_human)
    
    # 添加边
    graph.add_edge(START, "intent_recognition")
    
    graph.add_conditional_edges(
        "intent_recognition",
        route_by_intent,
        {
            "rag_retrieve": "rag_retrieve",
            "tool_call_node": "tool_call_node",
            "handle_transfer_human": "handle_transfer_human",
            "generate_response": "generate_response",
        }
    )
    
    graph.add_edge("rag_retrieve", "generate_response")
    
    graph.add_conditional_edges(
        "tool_call_node",
        should_continue_tool_call,
        {
            "tool_execution": "tool_execution",
            "generate_response": "generate_response",
        }
    )
    
    # 关键：工具执行后回到tool_call_node，让LLM处理工具结果
    graph.add_edge("tool_execution", "tool_call_node")
    
    graph.add_edge("generate_response", END)
    graph.add_edge("handle_transfer_human", END)
    
    compiled_graph = graph.compile()
    print("[Graph] Agent状态图构建完成 ✅")
    return compiled_graph


# ========== 便捷调用函数 ==========

_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def chat(query: str, user_id: str = "U1001") -> str:
    graph = get_graph()
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "intent": "",
        "rag_context": "",
        "tool_results": [],
        "iteration_count": 0,
        "user_id": user_id,
        "subject_level": "未评估",
    }
    result = graph.invoke(initial_state)
    from langchain_core.messages import AIMessage
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "抱歉，我暂时无法处理您的问题，建议转接人工客服。"

from langchain_core.messages import HumanMessage
