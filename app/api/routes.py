# # """
# # ============================================
# # API路由
# # ============================================

# # 【讲解】这是对外暴露的HTTP接口，前端/客户端通过这些接口和Agent交互。

# # 接口设计原则（面试加分）：
# # 1. RESTful风格：资源 + 动词
# # 2. 统一响应格式：code + message + data
# # 3. 错误处理：业务错误和系统错误分开
# # 4. 异步优先：FastAPI的异步能力让并发更高效

# # 接口列表：
# # - POST /api/chat     → 发送消息，获取Agent回复
# # - POST /api/chat/stream → 流式回复（打字机效果）
# # - GET  /api/history  → 获取对话历史
# # - DELETE /api/session → 清除会话
# # - GET  /api/health   → 健康检查
# # """

# # from fastapi import APIRouter, HTTPException
# # from pydantic import BaseModel, Field
# # from typing import Optional
# # from app.agent.graph import get_graph, chat
# # from app.memory.conversation import get_session, clear_session
# # from app.utils.guardrails import Guardrails
# # from langchain_core.messages import HumanMessage, AIMessage

# # router = APIRouter(prefix="/api", tags=["客服Agent"])


# # # ========== 请求/响应模型 ==========

# # class ChatRequest(BaseModel):
# #     """聊天请求"""
# #     query: str = Field(..., min_length=1, max_length=500, description="用户消息")
# #     user_id: str = Field(default="U1001", description="用户ID")
# #     session_id: str = Field(default="default", description="会话ID")


# # class ChatResponse(BaseModel):
# #     """聊天响应"""
# #     code: int = Field(default=200, description="状态码")
# #     message: str = Field(default="success", description="状态信息")
# #     data: dict = Field(default_factory=dict, description="响应数据")


# # class SessionRequest(BaseModel):
# #     """会话请求"""
# #     session_id: str = Field(default="default", description="会话ID")


# # # ========== 接口实现 ==========

# # @router.post("/chat", response_model=ChatResponse)
# # async def chat_endpoint(request: ChatRequest):
# #     """
# #     发送消息并获取Agent回复
    
# #     【讲解】这是最核心的接口，流程：
# #     1. 安全校验（Guardrails）
# #     2. 加载对话记忆
# #     3. 执行Agent图
# #     4. 保存记忆
# #     5. 返回结果
# #     """
# #     # 1. 安全校验
# #     is_safe, reason = Guardrails.check_input(request.query)
# #     if not is_safe:
# #         return ChatResponse(
# #             code=400,
# #             message=reason,
# #             data={"reply": f"输入不安全：{reason}"}
# #         )
    
# #     try:
# #         # 2. 获取会话记忆
# #         session = get_session(request.session_id)
        
# #         # 3. 构建完整的消息列表（历史 + 当前）
# #         history = session.get_messages()
# #         current_msg = HumanMessage(content=request.query)
# #         all_messages = history + [current_msg]
        
# #         # 4. 执行Agent
# #         graph = get_graph()
# #         result = graph.invoke({
# #             "messages": all_messages,
# #             "intent": "",
# #             "rag_context": "",
# #             "tool_results": [],
# #             "iteration_count": 0,
# #             "user_id": request.user_id,
# #         })
        
# #         # 5. 提取回复
# #         reply = ""
# #         for msg in reversed(result["messages"]):
# #             if isinstance(msg, AIMessage) and msg.content:
# #                 reply = msg.content
# #                 break
        
# #         # 6. 输出安全过滤
# #         reply = Guardrails.check_output(reply)
        
# #         # 7. 保存记忆
# #         session.add_user_message(request.query)
# #         session.add_ai_message(reply)
        
# #         return ChatResponse(
# #             code=200,
# #             message="success",
# #             data={
# #                 "reply": reply,
# #                 "session_id": request.session_id
# #             }
# #         )
        
# #     except Exception as e:
# #         print(f"[API] 错误: {str(e)}")
# #         return ChatResponse(
# #             code=500,
# #             message="服务内部错误，请稍后重试",
# #             data={"reply": "抱歉，系统出了点问题，请稍后再试或联系人工客服。"}
# #         )


# # @router.get("/history/{session_id}")
# # async def get_history(session_id: str):
# #     """获取对话历史"""
# #     session = get_session(session_id)
# #     messages = session.get_messages()
    
# #     history = []
# #     for msg in messages:
# #         role = "user" if isinstance(msg, HumanMessage) else "assistant"
# #         history.append({
# #             "role": role,
# #             "content": msg.content
# #         })
    
# #     return {"code": 200, "data": {"history": history, "session_id": session_id}}


# # @router.delete("/session/{session_id}")
# # async def delete_session(session_id: str):
# #     """清除会话记忆"""
# #     clear_session(session_id)
# #     return {"code": 200, "message": "会话已清除"}


# # @router.get("/health")
# # async def health_check():
# #     """
# #     健康检查接口
    
# #     【讲解】生产环境必须有！
# #     - K8s/Docker用来检测服务是否存活
# #     - 负载均衡器用来判断是否转发流量
# #     - 监控系统用来告警
# #     """
# #     return {"status": "healthy", "service": "agent-customer-service"}


# """
# ============================================
# API路由
# ============================================

# 【讲解】这是对外暴露的HTTP接口，前端/客户端通过这些接口和Agent交互。

# 接口设计原则（面试加分）：
# 1. RESTful风格：资源 + 动词
# 2. 统一响应格式：code + message + data
# 3. 错误处理：业务错误和系统错误分开
# 4. 异步优先：FastAPI的异步能力让并发更高效

# 接口列表：
# - POST /api/chat     → 发送消息，获取Agent回复
# - POST /api/chat/stream → 流式回复（打字机效果）
# - GET  /api/history  → 获取对话历史
# - DELETE /api/session → 清除会话
# - GET  /api/health   → 健康检查
# """

# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, Field
# from typing import Optional
# from app.agent.graph import get_graph, chat
# from app.memory.conversation import get_session, clear_session
# from app.utils.guardrails import Guardrails
# from langchain_core.messages import HumanMessage, AIMessage

# router = APIRouter(prefix="/api", tags=["教育助教Agent"])


# # ========== 请求/响应模型 ==========

# class ChatRequest(BaseModel):
#     """聊天请求"""
#     query: str = Field(..., min_length=1, max_length=500, description="用户消息")
#     user_id: str = Field(default="U1001", description="用户ID")
#     session_id: str = Field(default="default", description="会话ID")


# class ChatResponse(BaseModel):
#     """聊天响应"""
#     code: int = Field(default=200, description="状态码")
#     message: str = Field(default="success", description="状态信息")
#     data: dict = Field(default_factory=dict, description="响应数据")


# class SessionRequest(BaseModel):
#     """会话请求"""
#     session_id: str = Field(default="default", description="会话ID")


# # ========== 接口实现 ==========

# @router.post("/chat", response_model=ChatResponse)
# async def chat_endpoint(request: ChatRequest):
#     """
#     发送消息并获取Agent回复
    
#     【讲解】这是最核心的接口，流程：
#     1. 安全校验（Guardrails）
#     2. 加载对话记忆
#     3. 执行Agent图
#     4. 保存记忆
#     5. 返回结果
#     """
#     # 1. 安全校验
#     is_safe, reason = Guardrails.check_input(request.query)
#     if not is_safe:
#         return ChatResponse(
#             code=400,
#             message=reason,
#             data={"reply": f"输入不安全：{reason}"}
#         )
    
#     try:
#         # 2. 获取会话记忆
#         session = get_session(request.session_id)
        
#         # 3. 构建完整的消息列表（历史 + 当前）
#         history = session.get_messages()
#         current_msg = HumanMessage(content=request.query)
#         all_messages = history + [current_msg]
        
#         # 4. 执行Agent
#         graph = get_graph()
#         result = graph.invoke({
#             "messages": all_messages,
#             "intent": "",
#             "rag_context": "",
#             "tool_results": [],
#             "iteration_count": 0,
#             "user_id": request.user_id,
#         })
        
#         # 5. 提取回复
#         reply = ""
#         for msg in reversed(result["messages"]):
#             if isinstance(msg, AIMessage) and msg.content:
#                 reply = msg.content
#                 break
        
#         # 6. 输出安全过滤
#         reply = Guardrails.check_output(reply)
        
#         # 7. 保存记忆
#         session.add_user_message(request.query)
#         session.add_ai_message(reply)
        
#         return ChatResponse(
#             code=200,
#             message="success",
#             data={
#                 "reply": reply,
#                 "session_id": request.session_id
#             }
#         )
        
#     except Exception as e:
#         print(f"[API] 错误: {str(e)}")
#         return ChatResponse(
#             code=500,
#             message="服务内部错误，请稍后重试",
#             data={"reply": "抱歉，系统出了点问题，请稍后再试或联系真人教师。"}
#         )


# @router.get("/history/{session_id}")
# async def get_history(session_id: str):
#     """获取对话历史"""
#     session = get_session(session_id)
#     messages = session.get_messages()
    
#     history = []
#     for msg in messages:
#         role = "user" if isinstance(msg, HumanMessage) else "assistant"
#         history.append({
#             "role": role,
#             "content": msg.content
#         })
    
#     return {"code": 200, "data": {"history": history, "session_id": session_id}}


# @router.delete("/session/{session_id}")
# async def delete_session(session_id: str):
#     """清除会话记忆"""
#     clear_session(session_id)
#     return {"code": 200, "message": "会话已清除"}


# @router.get("/health")
# async def health_check():
#     """
#     健康检查接口
    
#     【讲解】生产环境必须有！
#     - K8s/Docker用来检测服务是否存活
#     - 负载均衡器用来判断是否转发流量
#     - 监控系统用来告警
#     """
#     return {"status": "healthy", "service": "education-assistant-agent"}
"""
============================================
API路由
============================================

【讲解】这是对外暴露的HTTP接口，前端/客户端通过这些接口和Agent交互。

接口设计原则（面试加分）：
1. RESTful风格：资源 + 动词
2. 统一响应格式：code + message + data
3. 错误处理：业务错误和系统错误分开
4. 异步优先：FastAPI的异步能力让并发更高效

接口列表：
- POST /api/chat     → 发送消息，获取Agent回复
- POST /api/chat/stream → 流式回复（打字机效果）
- GET  /api/history  → 获取对话历史
- DELETE /api/session → 清除会话
- GET  /api/health   → 健康检查
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.agent.graph import get_graph, chat
from app.memory.conversation import get_session, clear_session
from app.utils.guardrails import Guardrails
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/api", tags=["教育助教Agent"])


# ========== 请求/响应模型 ==========

class ChatRequest(BaseModel):
    """聊天请求"""
    query: str = Field(..., min_length=1, max_length=500, description="用户消息")
    user_id: str = Field(default="U1001", description="用户ID")
    session_id: str = Field(default="default", description="会话ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="状态信息")
    data: dict = Field(default_factory=dict, description="响应数据")


class SessionRequest(BaseModel):
    """会话请求"""
    session_id: str = Field(default="default", description="会话ID")


# ========== 接口实现 ==========

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    发送消息并获取Agent回复
    
    【讲解】这是最核心的接口，流程：
    1. 安全校验（Guardrails）
    2. 加载对话记忆
    3. 执行Agent图
    4. 保存记忆
    5. 返回结果
    """
    # 1. 安全校验
    is_safe, reason = Guardrails.check_input(request.query)
    if not is_safe:
        return ChatResponse(
            code=400,
            message=reason,
            data={"reply": f"输入不安全：{reason}"}
        )
    
    try:
        # 2. 获取会话记忆
        session = get_session(request.session_id)
        
        # 3. 构建完整的消息列表（历史 + 当前）
        history = session.get_messages()
        current_msg = HumanMessage(content=request.query)
        all_messages = history + [current_msg]
        
        # 4. 执行Agent
        graph = get_graph()
        result = graph.invoke({
            "messages": all_messages,
            "intent": "",
            "rag_context": "",
            "tool_results": [],
            "iteration_count": 0,
            "user_id": request.user_id,
            "subject_level": "未评估",
        })
        
        # 5. 提取回复
        reply = ""
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                reply = msg.content
                break
        
        # 6. 输出安全过滤
        reply = Guardrails.check_output(reply)
        
        # 7. 保存记忆
        session.add_user_message(request.query)
        session.add_ai_message(reply)
        
        return ChatResponse(
            code=200,
            message="success",
            data={
                "reply": reply,
                "session_id": request.session_id
            }
        )
        
    except Exception as e:
        print(f"[API] 错误: {str(e)}")
        return ChatResponse(
            code=500,
            message="服务内部错误，请稍后重试",
            data={"reply": "抱歉，系统出了点问题，请稍后再试或联系真人教师。"}
        )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """获取对话历史"""
    session = get_session(session_id)
    messages = session.get_messages()
    
    history = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        history.append({
            "role": role,
            "content": msg.content
        })
    
    return {"code": 200, "data": {"history": history, "session_id": session_id}}


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """清除会话记忆"""
    clear_session(session_id)
    return {"code": 200, "message": "会话已清除"}


@router.get("/health")
async def health_check():
    """
    健康检查接口
    
    【讲解】生产环境必须有！
    - K8s/Docker用来检测服务是否存活
    - 负载均衡器用来判断是否转发流量
    - 监控系统用来告警
    """
    return {"status": "healthy", "service": "education-assistant-agent"}
