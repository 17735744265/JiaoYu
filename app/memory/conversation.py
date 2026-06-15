# """
# ============================================
# 对话记忆管理
# ============================================

# 【讲解】这是Agent的"短期记忆"——记住当前对话的上下文。

# 为什么需要记忆管理？
# - LLM是无状态的：每次调用都不记得之前说了什么
# - 但客服场景需要多轮对话："我的订单呢？"→"哪个订单？ORD20240601001"→"已发货"
# - 解决方案：把历史消息一起传给LLM

# 【面试考点】对话记忆的三种策略：
# 1. 全量记忆：把所有历史都传（简单但贵，token浪费）
# 2. 窗口记忆：只保留最近N轮（本项目使用，性价比最高）
# 3. 摘要记忆：长对话压缩成摘要（最智能，但需要额外LLM调用）

# 生产环境通常组合使用：窗口 + 摘要
# """

# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
# from config import CONVERSATION_WINDOW


# class ConversationMemory:
#     """
#     对话记忆管理器
    
#     【讲解】使用滑动窗口策略：
#     - 保留最近 CONVERSATION_WINDOW 轮对话
#     - 每轮 = 一条用户消息 + 一条AI回复
#     - 超出窗口的旧消息自动丢弃
#     """
    
#     def __init__(self, window: int = CONVERSATION_WINDOW):
#         """
#         Args:
#             window: 记忆窗口大小（轮数）
#         """
#         self.window = window
#         self.history: list[BaseMessage] = []
    
#     def add_user_message(self, content: str):
#         """添加用户消息"""
#         self.history.append(HumanMessage(content=content))
#         self._trim()
    
#     def add_ai_message(self, content: str):
#         """添加AI回复"""
#         self.history.append(AIMessage(content=content))
#         self._trim()
    
#     def get_messages(self) -> list[BaseMessage]:
#         """获取当前记忆中的所有消息"""
#         return self.history.copy()
    
#     def _trim(self):
#         """
#         裁剪历史消息，保持窗口大小
        
#         【讲解】裁剪逻辑：
#         - 每轮对话 = 2条消息（1条用户 + 1条AI）
#         - window=10 表示保留最近10轮 = 20条消息
#         - 裁剪时从头部删除（删最旧的）
#         """
#         max_messages = self.window * 2
#         if len(self.history) > max_messages:
#             self.history = self.history[-max_messages:]
    
#     def get_summary(self) -> str:
#         """
#         获取对话摘要（简化版）
        
#         【讲解】生产环境会用LLM生成摘要，这里用简单拼接。
#         摘要的用途：当用户切换话题时，用摘要提供背景。
#         """
#         if not self.history:
#             return "暂无对话历史"
        
#         summary_parts = []
#         for i, msg in enumerate(self.history):
#             role = "用户" if isinstance(msg, HumanMessage) else "AI"
#             summary_parts.append(f"{role}: {msg.content[:50]}...")
        
#         return "\n".join(summary_parts)
    
#     def clear(self):
#         """清空记忆（新会话时调用）"""
#         self.history = []


# # ========== 会话管理器 ==========

# # 全局会话存储（生产环境用Redis/数据库）
# _sessions: dict[str, ConversationMemory] = {}


# def get_session(session_id: str) -> ConversationMemory:
#     """
#     获取或创建会话
    
#     【讲解】每个用户一个独立的记忆空间。
#     session_id 通常是用户的唯一标识。
#     """
#     if session_id not in _sessions:
#         _sessions[session_id] = ConversationMemory()
#     return _sessions[session_id]


# def clear_session(session_id: str):
#     """清除指定会话"""
#     if session_id in _sessions:
#         del _sessions[session_id]
"""
============================================
对话记忆管理
============================================

【讲解】这是Agent的"短期记忆"——记住当前对话的上下文。

为什么需要记忆管理？
- LLM是无状态的：每次调用都不记得之前说了什么
- 但客服场景需要多轮对话："我的订单呢？"→"哪个订单？ORD20240601001"→"已发货"
- 解决方案：把历史消息一起传给LLM

【面试考点】对话记忆的三种策略：
1. 全量记忆：把所有历史都传（简单但贵，token浪费）
2. 窗口记忆：只保留最近N轮（本项目使用，性价比最高）
3. 摘要记忆：长对话压缩成摘要（最智能，但需要额外LLM调用）

生产环境通常组合使用：窗口 + 摘要
"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from config import CONVERSATION_WINDOW


class ConversationMemory:
    """
    对话记忆管理器
    
    【讲解】使用滑动窗口策略：
    - 保留最近 CONVERSATION_WINDOW 轮对话
    - 每轮 = 一条用户消息 + 一条AI回复
    - 超出窗口的旧消息自动丢弃
    """
    
    def __init__(self, window: int = CONVERSATION_WINDOW):
        """
        Args:
            window: 记忆窗口大小（轮数）
        """
        self.window = window
        self.history: list[BaseMessage] = []
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.history.append(HumanMessage(content=content))
        self._trim()
    
    def add_ai_message(self, content: str):
        """添加AI回复"""
        self.history.append(AIMessage(content=content))
        self._trim()
    
    def get_messages(self) -> list[BaseMessage]:
        """获取当前记忆中的所有消息"""
        return self.history.copy()
    
    def _trim(self):
        """
        裁剪历史消息，保持窗口大小
        
        【讲解】裁剪逻辑：
        - 每轮对话 = 2条消息（1条用户 + 1条AI）
        - window=10 表示保留最近10轮 = 20条消息
        - 裁剪时从头部删除（删最旧的）
        """
        max_messages = self.window * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]
    
    def get_summary(self) -> str:
        """
        获取对话摘要（简化版）
        
        【讲解】生产环境会用LLM生成摘要，这里用简单拼接。
        摘要的用途：当用户切换话题时，用摘要提供背景。
        """
        if not self.history:
            return "暂无对话历史"
        
        summary_parts = []
        for i, msg in enumerate(self.history):
            role = "用户" if isinstance(msg, HumanMessage) else "AI"
            summary_parts.append(f"{role}: {msg.content[:50]}...")
        
        return "\n".join(summary_parts)
    
    def clear(self):
        """清空记忆（新会话时调用）"""
        self.history = []


# ========== 会话管理器 ==========

# 全局会话存储（生产环境用Redis/数据库）
_sessions: dict[str, ConversationMemory] = {}


def get_session(session_id: str) -> ConversationMemory:
    """
    获取或创建会话
    
    【讲解】每个用户一个独立的记忆空间。
    session_id 通常是用户的唯一标识。
    """
    if session_id not in _sessions:
        _sessions[session_id] = ConversationMemory()
    return _sessions[session_id]


def clear_session(session_id: str):
    """清除指定会话"""
    if session_id in _sessions:
        del _sessions[session_id]
