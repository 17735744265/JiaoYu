# # # """
# # # ============================================
# # # Agent节点逻辑
# # # ============================================

# # # 【讲解】这是LangGraph的"加工车间"——每个节点是一个处理步骤。

# # # LangGraph流程图：
# # #   用户消息 → [意图识别] → 条件路由
# # #                             ├─ faq → [RAG检索] → [生成回答]
# # #                             ├─ tool_call → [工具调用] → [判断是否解决] → 循环或回答
# # #                             ├─ transfer_human → [转人工]
# # #                             └─ general → [直接回答]

# # # 每个节点的输入和输出都是 AgentState。
# # # 节点之间通过"修改状态"来传递信息。

# # # 【面试考点】为什么要拆成多个节点，而不是一个函数搞定？
# # # 1. 可观测性：每个节点可以单独监控、日志、调试
# # # 2. 可扩展性：加新功能只需加新节点和边
# # # 3. 可测试性：每个节点可以单独测试
# # # 4. 条件路由：不同意图走不同路径，一个函数做不到
# # # """

# # # from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
# # # from langchain_openai import ChatOpenAI
# # # from app.agent.state import AgentState
# # # from app.rag.retriever import RAGRetriever
# # # from app.tools import ALL_TOOLS
# # # from config import (
# # #     LLM_API_KEY, LLM_BASE_URL, LLM_MODEL,
# # #     LLM_TEMPERATURE, LLM_MAX_TOKENS, MAX_ITERATIONS
# # # )
# # # import json


# # # # ========== LLM 初始化 ==========

# # # def get_llm(with_tools: bool = False):
# # #     """
# # #     获取LLM实例
    
# # #     【讲解】为什么区分 with_tools？
# # #     - 意图识别不需要工具，用纯LLM就行（更快更省token）
# # #     - 工具调用需要LLM绑定工具定义（Function Call模式）
# # #     - 分开创建避免不必要的token开销
    
# # #     Args:
# # #         with_tools: 是否绑定工具定义
# # #     """
# # #     llm = ChatOpenAI(
# # #         api_key=LLM_API_KEY,
# # #         base_url=LLM_BASE_URL,
# # #         model=LLM_MODEL,
# # #         temperature=LLM_TEMPERATURE,
# # #         max_tokens=LLM_MAX_TOKENS,
# # #     )
    
# # #     if with_tools:
# # #         # bind_tools 把工具定义注入LLM，LLM就知道有哪些工具可用
# # #         # LLM不会直接执行工具，而是输出"我想调用xxx工具"
# # #         llm = llm.bind_tools(ALL_TOOLS)
    
# # #     return llm


# # # # ========== 全局RAG检索器 ==========

# # # _rag_retriever = None

# # # def get_rag_retriever() -> RAGRetriever:
# # #     """获取RAG检索器单例"""
# # #     global _rag_retriever
# # #     if _rag_retriever is None:
# # #         _rag_retriever = RAGRetriever()
# # #     return _rag_retriever


# # # # ========== 系统Prompt ==========

# # # # SYSTEM_PROMPT = """你是一个专业的电商客服助手。你的职责是：

# # # # 1. **回答常见问题**：关于退换货、物流、优惠、会员、支付、发票等问题
# # # # 2. **查询订单**：帮用户查订单状态、物流信息
# # # # 3. **处理退款**：帮用户发起退款申请
# # # # 4. **查询库存**：帮用户查商品是否有货
# # # # 5. **转接人工**：处理不了的问题，及时转接人工客服

# # # # 工作原则：
# # # # - 回答要准确、简洁、友好
# # # # - 涉及订单操作时，先确认订单号
# # # # - 涉及退款等敏感操作时，确认用户意图后再执行
# # # # - 不知道的问题不要编造，明确告知并建议转人工
# # # # - 始终用中文回答

# # # # 当前用户ID: {user_id}
# # # # """

# # # SYSTEM_PROMPT = """你是一个专业的AI教育助教。你的职责是：

# # # 1. **知识答疑**：回答学生在各学科中遇到的问题，提供清晰的讲解和示例
# # # 2. **出题练习**：根据学生的学科和水平，生成个性化练习题
# # # 3. **批改反馈**：对学生的答题进行批改，给出详细解析和改进建议
# # # 4. **学习规划**：帮助学生制定学习计划，追踪学习进度
# # # 5. **错题管理**：整理学生的错题，提供针对性复习方案
# # # 6. **转接老师**：遇到无法解答的问题，及时转接真人教师

# # # 教学原则：
# # # - 回答要准确、详细、有启发性，而非直接给答案
# # # - 根据学生水平调整讲解深度和语言风格
# # # - 优先使用苏格拉底式提问引导思考，而非直接告知结论
# # # - 涉及敏感操作（如删除学习记录）时，先确认用户意图
# # # - 不确定的知识不要编造，明确告知并建议转接老师
# # # - 始终用中文回答
# # # - 鼓励学生，保持积极的教学态度

# # # 当前学生ID: {user_id}
# # # 当前学生水平: {subject_level}
# # # """



# # # # ========== 节点函数 ==========

# # # def intent_recognition(state: AgentState) -> dict:
# # #     """
# # #     节点1：意图识别
    
# # #     【讲解】这是Agent的"大脑"——分析用户想做什么，决定走哪条路。
    
# # #     意图分类：
# # #     - faq: 常见问题，走RAG检索
# # #     - tool_call: 需要查订单/退款/库存，走工具调用
# # #     - general: 普通聊天/闲聊，直接回答
# # #     - transfer_human: 要求转人工
    
# # #     面试考点：为什么不让LLM直接决定用哪个工具？
# # #     - 加意图识别层可以做条件路由，避免不必要的工具调用
# # #     - RAG和工具调用是两个独立流程，混在一起会互相干扰
# # #     - 意图识别可以加规则辅助（关键词匹配），降低LLM调用成本
# # #     """
# # #     messages = state["messages"]
# # #     user_id = state.get("user_id", "U1001")  # 默认用户
    
# # #     # 构建意图识别的Prompt
# # # #     intent_prompt = """分析用户最新消息的意图，从以下选项中选择一个：

# # # # - faq: 用户在询问常见问题（退换货政策、运费、优惠券使用、配送时效、会员权益、支付方式、发票等）
# # # # - tool_call: 用户需要执行具体操作（查订单、退款、查库存、搜索商品）
# # # # - transfer_human: 用户明确要求转人工客服，或表达强烈不满
# # # # - general: 闲聊、打招呼、或不在以上分类的问题

# # # # 只输出意图类别，不要解释。"""


# # #     #改动1
# # #     intent_prompt = """分析学生最新消息的意图，从以下选项中选择一个：

# # # - faq: 学生在询问学科知识问题（数学公式、物理原理、编程语法、历史事件等）
# # # - tool_call: 学生需要执行具体操作（查成绩、做练习、看错题、制定学习计划）
# # # - transfer_human: 学生明确要求找真人老师，或表达对学习极度困惑
# # # - general: 闲聊、打招呼、或不在以上分类的问题

# # # 只输出意图类别，不要解释。"""

# # #     # 调用LLM做意图识别
# # #     llm = get_llm(with_tools=False)
# # #     response = llm.invoke([
# # #         SystemMessage(content=intent_prompt),
# # #         messages[-1]  # 只取最后一条用户消息
# # #     ])
    
# # #     intent = response.content.strip().lower()
    
# # #     # 规则辅助：关键词匹配可以纠正LLM的误判
# # #     last_message = messages[-1].content if messages else ""
# # #     # tool_keywords = ["订单", "退款", "退货", "物流", "快递", "库存", "有货", "发货", "取消"]
# # #     # human_keywords = ["人工", "转人工", "投诉", "经理", "负责人"]
# # #     #改动2
# # #     # 关键词匹配
# # #     tool_keywords = ["成绩", "练习", "做题", "错题", "作业", "考试", "复习", "进度", "计划"]
# # #     human_keywords = ["老师", "找老师", "真人", "教不会", "听不懂", "太难了"]
    
# # #     if any(kw in last_message for kw in human_keywords):
# # #         intent = "transfer_human"
# # #     elif any(kw in last_message for kw in tool_keywords):
# # #         if intent not in ["transfer_human"]:
# # #             intent = "tool_call"
    
# # #     print(f"[Agent] 意图识别: {intent}")
    
# # #     return {"intent": intent, "iteration_count": 0}


# # # def rag_retrieve(state: AgentState) -> dict:
# # #     """
# # #     节点2：RAG知识检索
    
# # #     【讲解】意图是FAQ时走这个节点。
# # #     流程：用户问题 → 向量检索 → 拼接上下文
# # #     """
# # #     messages = state["messages"]
# # #     query = messages[-1].content
    
# # #     # 调用RAG检索器
# # #     retriever = get_rag_retriever()
# # #     results = retriever.retrieve_with_rerank(query)
# # #     context = retriever.format_context(results)
    
# # #     return {"rag_context": context}


# # # def tool_call_node(state: AgentState) -> dict:
# # #     """
# # #     节点3：工具调用
    
# # #     【讲解】意图是tool_call时走这个节点。
    
# # #     关键流程：
# # #     1. 把对话历史 + 系统Prompt + 工具定义 传给LLM
# # #     2. LLM决定调用哪个工具，输出工具调用请求
# # #     3. LangGraph自动执行工具，把结果返回
    
# # #     这里的 iteration_count 检查是防死循环：
# # #     如果Agent连续调用工具5次还没解决，就强制退出。
# # #     """
# # #     messages = state["messages"]
# # #     user_id = state.get("user_id", "U1001")
# # #     iteration = state.get("iteration_count", 0)
    
# # #     if iteration >= MAX_ITERATIONS:
# # #         return {
# # #             "intent": "transfer_human",
# # #             "tool_results": ["已达到最大推理轮数，需要转接人工客服"]
# # #         }
    
# # #     # 构建完整消息列表
# # #     system_msg = SystemMessage(content=SYSTEM_PROMPT.format(user_id=user_id))
# # #     full_messages = [system_msg] + messages
    
# # #     # 调用带工具的LLM
# # #     llm = get_llm(with_tools=True)
# # #     response = llm.invoke(full_messages)
    
# # #     # 更新迭代计数
# # #     new_iteration = iteration + 1
    
# # #     # 如果LLM返回了工具调用请求，messages会自动更新
# # #     return {
# # #         "messages": [response],
# # #         "iteration_count": new_iteration
# # #     }


# # # def generate_response(state: AgentState) -> dict:
# # #     """
# # #     节点4：生成最终回答
    
# # #     【讲解】所有路径最终汇聚到这里，生成给用户的回答。
    
# # #     根据不同意图，构建不同的Prompt：
# # #     - faq: 系统Prompt + RAG上下文 + 用户问题
# # #     - tool_call: 系统Prompt + 工具调用结果 + 用户问题
# # #     - general: 系统Prompt + 用户问题
# # #     """
# # #     messages = state["messages"]
# # #     user_id = state.get("user_id", "U1001")
# # #     intent = state.get("intent", "general")
# # #     rag_context = state.get("rag_context", "")
    
# # #     # 根据意图构建不同的上下文
# # #     # if intent == "faq" and rag_context:
# # #     #     context_section = f"\n\n【知识库参考】\n{rag_context}\n\n请基于以上知识库内容回答用户问题。如果知识库中没有相关信息，请明确告知。"
# # #     # elif intent == "general":
# # #     #     context_section = "\n\n这是一个一般性问题，请友好地回答。如果问题超出你的能力范围，建议转人工客服。"
# # #     # else:
# # #     #     context_section = ""
    
# # #     #改动4
# # #     if intent == "faq" and rag_context:
# # #         context_section = f"\n\n【知识库参考】\n{rag_context}\n\n请基于以上知识库内容回答学生问题。注意：不要直接给出最终答案，先引导思考，必要时再给出详细讲解。如果知识库中没有相关信息，请明确告知并建议转接老师。"
# # #     elif intent == "general":
# # #         context_section = "\n\n这是一般性对话，请以友好、鼓励的态度回应。可以适当引导学生聊回学习话题。"
# # #     else:
# # #         context_section = ""

    
# # #     # 构建系统Prompt
# # #     system_content = SYSTEM_PROMPT.format(user_id=user_id) + context_section
    
# # #     # 调用LLM生成回答
# # #     llm = get_llm(with_tools=False)
# # #     response = llm.invoke([
# # #         SystemMessage(content=system_content),
# # #         *messages
# # #     ])
    
# # #     print(f"[Agent] 生成回答 (意图: {intent})")
    
# # #     return {"messages": [response]}


# # # def handle_transfer_human(state: AgentState) -> dict:
# # #     """
# # #     节点5：转人工处理
    
# # #     【讲解】当意图是transfer_human或Agent解决不了时走这里。
# # #     """
# # #     messages = state["messages"]
# # #     last_user_msg = ""
# # #     for msg in reversed(messages):
# # #         if isinstance(msg, HumanMessage):
# # #             last_user_msg = msg.content
# # #             break
    
# # #     # 调用转人工工具
# # #     from app.tools.human_transfer import transfer_to_human
# # #     result = transfer_to_human.invoke({
# # #         "reason": f"用户请求: {last_user_msg[:50]}",
# # #         "urgency": "普通"
# # #     })
    
# # #     result_data = json.loads(result)
    
# # #     # 生成转人工的回复
# # #     transfer_msg = AIMessage(
# # #         content=result_data["message"] + "\n\n如果您还有其他问题，我也可以帮您解答。"
# # #     )
    
# # #     return {"messages": [transfer_msg]}
# # """
# # ============================================
# # Agent节点逻辑
# # ============================================

# # 【讲解】这是LangGraph的"加工车间"——每个节点是一个处理步骤。

# # LangGraph流程图：
# #   用户消息 → [意图识别] → 条件路由
# #                             ├─ faq → [RAG检索] → [生成回答]
# #                             ├─ tool_call → [工具调用] → [判断是否解决] → 循环或回答
# #                             ├─ transfer_human → [转人工]
# #                             └─ general → [直接回答]

# # 每个节点的输入和输出都是 AgentState。
# # 节点之间通过"修改状态"来传递信息。

# # 【面试考点】为什么要拆成多个节点，而不是一个函数搞定？
# # 1. 可观测性：每个节点可以单独监控、日志、调试
# # 2. 可扩展性：加新功能只需加新节点和边
# # 3. 可测试性：每个节点可以单独测试
# # 4. 条件路由：不同意图走不同路径，一个函数做不到
# # """

# # from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
# # from langchain_openai import ChatOpenAI
# # from app.agent.state import AgentState
# # from app.rag.retriever import RAGRetriever
# # from app.tools import ALL_TOOLS
# # from config import (
# #     LLM_API_KEY, LLM_BASE_URL, LLM_MODEL,
# #     LLM_TEMPERATURE, LLM_MAX_TOKENS, MAX_ITERATIONS
# # )
# # import json


# # # ========== LLM 初始化 ==========

# # def get_llm(with_tools: bool = False):
# #     """
# #     获取LLM实例
    
# #     【讲解】为什么区分 with_tools？
# #     - 意图识别不需要工具，用纯LLM就行（更快更省token）
# #     - 工具调用需要LLM绑定工具定义（Function Call模式）
# #     - 分开创建避免不必要的token开销
    
# #     Args:
# #         with_tools: 是否绑定工具定义
# #     """
# #     llm = ChatOpenAI(
# #         api_key=LLM_API_KEY,
# #         base_url=LLM_BASE_URL,
# #         model=LLM_MODEL,
# #         temperature=LLM_TEMPERATURE,
# #         max_tokens=LLM_MAX_TOKENS,
# #     )
    
# #     if with_tools:
# #         # bind_tools 把工具定义注入LLM，LLM就知道有哪些工具可用
# #         # LLM不会直接执行工具，而是输出"我想调用xxx工具"
# #         llm = llm.bind_tools(ALL_TOOLS)
    
# #     return llm


# # # ========== 全局RAG检索器 ==========

# # _rag_retriever = None

# # def get_rag_retriever() -> RAGRetriever:
# #     """获取RAG检索器单例"""
# #     global _rag_retriever
# #     if _rag_retriever is None:
# #         _rag_retriever = RAGRetriever()
# #     return _rag_retriever


# # # ========== 系统Prompt ==========

# # SYSTEM_PROMPT = """你是一个专业的AI教育助教。你的职责是：

# # 1. **知识答疑**：回答学生在各学科中遇到的问题，提供清晰的讲解和示例
# # 2. **出题练习**：根据学生的学科和水平，生成个性化练习题
# # 3. **批改反馈**：对学生的答题进行批改，给出详细解析和改进建议
# # 4. **学习规划**：帮助学生制定学习计划，追踪学习进度
# # 5. **错题管理**：整理学生的错题，提供针对性复习方案
# # 6. **转接老师**：遇到无法解答的问题，及时转接真人教师

# # 教学原则：
# # - 回答要准确、详细、有启发性，而非直接给答案
# # - 根据学生水平调整讲解深度和语言风格
# # - 优先使用苏格拉底式提问引导思考，而非直接告知结论
# # - 涉及敏感操作（如删除学习记录）时，先确认用户意图
# # - 不确定的知识不要编造，明确告知并建议转接老师
# # - 始终用中文回答
# # - 鼓励学生，保持积极的教学态度

# # 当前学生ID: {user_id}
# # 当前学生水平: {subject_level}
# # """


# # # ========== 节点函数 ==========

# # def intent_recognition(state: AgentState) -> dict:
# #     """
# #     节点1：意图识别
    
# #     【讲解】这是Agent的"大脑"——分析用户想做什么，决定走哪条路。
    
# #     意图分类：
# #     - faq: 常见问题，走RAG检索
# #     - tool_call: 需要查订单/退款/库存，走工具调用
# #     - general: 普通聊天/闲聊，直接回答
# #     - transfer_human: 要求转人工
    
# #     面试考点：为什么不让LLM直接决定用哪个工具？
# #     - 加意图识别层可以做条件路由，避免不必要的工具调用
# #     - RAG和工具调用是两个独立流程，混在一起会互相干扰
# #     - 意图识别可以加规则辅助（关键词匹配），降低LLM调用成本
# #     """
# #     messages = state["messages"]
# #     user_id = state.get("user_id", "U1001")  # 默认用户
    
# #     # 构建意图识别的Prompt
# #     intent_prompt = """分析学生最新消息的意图，从以下选项中选择一个：

# # - faq: 学生在询问学科知识问题（数学公式、物理原理、编程语法、历史事件等）
# # - tool_call: 学生需要执行具体操作（查成绩、做练习、看错题、制定学习计划）
# # - transfer_human: 学生明确要求找真人老师，或表达对学习极度困惑
# # - general: 闲聊、打招呼、或不在以上分类的问题

# # 只输出意图类别，不要解释。"""

# #     # 调用LLM做意图识别
# #     llm = get_llm(with_tools=False)
# #     response = llm.invoke([
# #         SystemMessage(content=intent_prompt),
# #         messages[-1]  # 只取最后一条用户消息
# #     ])
    
# #     intent = response.content.strip().lower()
    
# #     # 规则辅助：关键词匹配可以纠正LLM的误判
# #     last_message = messages[-1].content if messages else ""
# #     tool_keywords = ["成绩", "练习", "做题", "错题", "作业", "考试", "复习", "进度", "计划"]
# #     human_keywords = ["老师", "找老师", "真人", "教不会", "听不懂", "太难了"]
    
# #     if any(kw in last_message for kw in human_keywords):
# #         intent = "transfer_human"
# #     elif any(kw in last_message for kw in tool_keywords):
# #         if intent not in ["transfer_human"]:
# #             intent = "tool_call"
    
# #     print(f"[Agent] 意图识别: {intent}")
    
# #     return {"intent": intent, "iteration_count": 0}


# # def rag_retrieve(state: AgentState) -> dict:
# #     """
# #     节点2：RAG知识检索
    
# #     【讲解】意图是FAQ时走这个节点。
# #     流程：用户问题 → 向量检索 → 拼接上下文
# #     """
# #     messages = state["messages"]
# #     query = messages[-1].content
    
# #     # 调用RAG检索器
# #     retriever = get_rag_retriever()
# #     results = retriever.retrieve_with_rerank(query)
# #     context = retriever.format_context(results)
    
# #     return {"rag_context": context}


# # def tool_call_node(state: AgentState) -> dict:
# #     """
# #     节点3：工具调用
    
# #     【讲解】意图是tool_call时走这个节点。
    
# #     关键流程：
# #     1. 把对话历史 + 系统Prompt + 工具定义 传给LLM
# #     2. LLM决定调用哪个工具，输出工具调用请求
# #     3. LangGraph自动执行工具，把结果返回
    
# #     这里的 iteration_count 检查是防死循环：
# #     如果Agent连续调用工具5次还没解决，就强制退出。
# #     """
# #     messages = state["messages"]
# #     user_id = state.get("user_id", "S1001")
# #     iteration = state.get("iteration_count", 0)
    
# #     if iteration >= MAX_ITERATIONS:
# #         return {
# #             "intent": "transfer_human",
# #             "tool_results": ["已达到最大推理轮数，需要转接真人教师"]
# #         }
    
# #     # 构建完整消息列表
# #     subject_level = state.get("subject_level", "未评估")
# #     system_msg = SystemMessage(content=SYSTEM_PROMPT.format(user_id=user_id, subject_level=subject_level))
# #     full_messages = [system_msg] + messages
    
# #     # 调用带工具的LLM
# #     llm = get_llm(with_tools=True)
# #     response = llm.invoke(full_messages)
    
# #     # 更新迭代计数
# #     new_iteration = iteration + 1
    
# #     # 如果LLM返回了工具调用请求，messages会自动更新
# #     return {
# #         "messages": [response],
# #         "iteration_count": new_iteration
# #     }


# # def generate_response(state: AgentState) -> dict:
# #     """
# #     节点4：生成最终回答
    
# #     【讲解】所有路径最终汇聚到这里，生成给用户的回答。
    
# #     根据不同意图，构建不同的Prompt：
# #     - faq: 系统Prompt + RAG上下文 + 用户问题
# #     - tool_call: 系统Prompt + 工具调用结果 + 用户问题
# #     - general: 系统Prompt + 用户问题
# #     """
# #     messages = state["messages"]
# #     user_id = state.get("user_id", "S1001")
# #     intent = state.get("intent", "general")
# #     rag_context = state.get("rag_context", "")
    
# #     # 根据意图构建不同的上下文
# #     if intent == "faq" and rag_context:
# #         context_section = f"\n\n【知识库参考】\n{rag_context}\n\n请基于以上知识库内容回答学生问题。注意：不要直接给出最终答案，先引导思考，必要时再给出详细讲解。如果知识库中没有相关信息，请明确告知并建议转接老师。"
# #     elif intent == "general":
# #         context_section = "\n\n这是一般性对话，请以友好、鼓励的态度回应。可以适当引导学生聊回学习话题。"
# #     else:
# #         context_section = ""
    
# #     # 构建系统Prompt
# #     subject_level = state.get("subject_level", "未评估")
# #     system_content = SYSTEM_PROMPT.format(user_id=user_id, subject_level=subject_level) + context_section
    
# #     # 调用LLM生成回答
# #     llm = get_llm(with_tools=False)
# #     response = llm.invoke([
# #         SystemMessage(content=system_content),
# #         *messages
# #     ])
    
# #     print(f"[Agent] 生成回答 (意图: {intent})")
    
# #     return {"messages": [response]}


# # def handle_transfer_human(state: AgentState) -> dict:
# #     """
# #     节点5：转人工处理
    
# #     【讲解】当意图是transfer_human或Agent解决不了时走这里。
# #     """
# #     messages = state["messages"]
# #     last_user_msg = ""
# #     for msg in reversed(messages):
# #         if isinstance(msg, HumanMessage):
# #             last_user_msg = msg.content
# #             break
    
# #     # 调用转接老师工具
# #     from app.tools.human_transfer import transfer_to_teacher
# #     result = transfer_to_teacher.invoke({
# #         "reason": f"用户请求: {last_user_msg[:50]}",
# #         "urgency": "普通"
# #     })
    
# #     result_data = json.loads(result)
    
# #     # 生成转人工的回复
# #     transfer_msg = AIMessage(
# #         content=result_data["message"] + "\n\n如果您还有其他问题，我也可以帮您解答。"
# #     )
    
# #     return {"messages": [transfer_msg]}
# """
# ============================================
# Agent状态定义
# ============================================

# 【讲解】这是LangGraph的"数据结构"——定义Agent在流程中传递什么信息。

# LangGraph的核心概念：
# - State（状态）：节点之间传递的数据容器
# - Node（节点）：处理状态的函数
# - Edge（边）：节点之间的流转规则

# 为什么用TypedDict而不是普通dict？
# - 类型提示：IDE自动补全，减少bug
# - LangGraph根据类型定义自动管理状态的更新和合并
# - 面试体现"工程规范"

# 【面试考点】LangGraph vs LangChain Agent？
# - LangChain Agent：线性链，tool → observe → tool → observe ...
# - LangGraph：图结构，可以有条件路由、循环、并行分支
# - 客服场景需要条件路由（FAQ走RAG，查询走工具），所以用LangGraph
# """

# from typing import TypedDict, Annotated, Literal
# from langgraph.graph.message import add_messages


# class AgentState(TypedDict):
#     """
#     Agent状态定义
    
#     【讲解】每个字段的含义：
#     - messages: 对话历史（最核心的字段）
#     - intent: 意图识别结果
#     - rag_context: RAG检索到的上下文
#     - tool_results: 工具调用的结果
#     - iteration_count: 当前推理轮数（防死循环）
#     - user_id: 用户ID（用于查订单等个性化操作）
    
#     Annotated[..., add_messages] 的含义：
#     - add_messages 是LangGraph提供的reducer函数
#     - 作用：新消息追加到列表，而不是覆盖
#     - 这样每个节点往messages里加消息时，之前的消息不会丢
#     """
#     # 对话消息列表（使用add_messages reducer，新消息自动追加）
#     messages: Annotated[list, add_messages]
    
#     # 意图识别结果
#     intent: str  # "faq" | "tool_call" | "general" | "transfer_human"
    
#     # RAG检索上下文
#     rag_context: str
    
#     # 工具调用结果
#     tool_results: list[str]
    
#     # 推理轮数计数
#     iteration_count: int
    
#     # 用户ID（从请求中获取，用于个性化服务）
#     user_id: str
    
#     # 学生学科水平（新增：教育场景个性化）
#     subject_level: str
"""
============================================
Agent节点逻辑
============================================

LangGraph流程图：
  用户消息 → [意图识别] → 条件路由
                            ├─ faq → [RAG检索] → [生成回答]
                            ├─ tool_call → [工具调用] → [判断是否解决] → 循环或回答
                            ├─ transfer_human → [转接老师]
                            └─ general → [直接回答]
"""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from app.agent.state import AgentState
from app.rag.retriever import RAGRetriever
from app.tools import ALL_TOOLS
from config import (
    LLM_API_KEY, LLM_BASE_URL, LLM_MODEL,
    LLM_TEMPERATURE, LLM_MAX_TOKENS, MAX_ITERATIONS
)
import json


# ========== LLM 初始化 ==========

def get_llm(with_tools: bool = False):
    llm = ChatOpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )
    if with_tools:
        llm = llm.bind_tools(ALL_TOOLS)
    return llm


# ========== 全局RAG检索器 ==========

_rag_retriever = None

def get_rag_retriever() -> RAGRetriever:
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetriever()
    return _rag_retriever


# ========== 系统Prompt ==========

SYSTEM_PROMPT = """你是一个专业的AI教育助教。你的职责是：

1. **知识答疑**：回答学生在各学科中遇到的问题，提供清晰的讲解和示例
2. **出题练习**：根据学生的学科和水平，生成个性化练习题
3. **批改反馈**：对学生的答题进行批改，给出详细解析和改进建议
4. **学习规划**：帮助学生制定学习计划，追踪学习进度
5. **错题管理**：整理学生的错题，提供针对性复习方案
6. **转接老师**：遇到无法解答的问题，及时转接真人教师

教学原则：
- 回答要准确、详细、有启发性，而非直接给答案
- 根据学生水平调整讲解深度和语言风格
- 优先使用苏格拉底式提问引导思考，而非直接告知结论
- 涉及敏感操作（如删除学习记录）时，先确认用户意图
- 不确定的知识不要编造，明确告知并建议转接老师
- 始终用中文回答
- 鼓励学生，保持积极的教学态度

当前学生ID: {user_id}
当前学生水平: {subject_level}
"""


# ========== 节点函数 ==========

def intent_recognition(state: AgentState) -> dict:
    messages = state["messages"]

    intent_prompt = """分析学生最新消息的意图，从以下选项中选择一个：

- faq: 学生在询问学科知识问题（数学公式、物理原理、编程语法、历史事件等）
- tool_call: 学生需要执行具体操作（查成绩、做练习、看错题、制定学习计划）
- transfer_human: 学生明确要求找真人老师，或表达对学习极度困惑
- general: 闲聊、打招呼、或不在以上分类的问题

只输出意图类别，不要解释。"""

    llm = get_llm(with_tools=False)
    response = llm.invoke([
        SystemMessage(content=intent_prompt),
        messages[-1]
    ])

    intent = response.content.strip().lower()

    last_message = messages[-1].content if messages else ""
    tool_keywords = ["成绩", "练习", "做题", "错题", "作业", "考试", "复习", "进度", "计划"]
    human_keywords = ["老师", "找老师", "真人", "教不会", "听不懂", "太难了"]

    if any(kw in last_message for kw in human_keywords):
        intent = "transfer_human"
    elif any(kw in last_message for kw in tool_keywords):
        if intent not in ["transfer_human"]:
            intent = "tool_call"

    print(f"[Agent] 意图识别: {intent}")

    return {"intent": intent, "iteration_count": 0}


def rag_retrieve(state: AgentState) -> dict:
    messages = state["messages"]
    query = messages[-1].content

    retriever = get_rag_retriever()
    results = retriever.retrieve_with_rerank(query)
    context = retriever.format_context(results)

    return {"rag_context": context}


def tool_call_node(state: AgentState) -> dict:
    messages = state["messages"]
    user_id = state.get("user_id", "S1001")
    iteration = state.get("iteration_count", 0)

    if iteration >= MAX_ITERATIONS:
        return {
            "intent": "transfer_human",
            "tool_results": ["已达到最大推理轮数，需要转接真人教师"]
        }

    subject_level = state.get("subject_level", "未评估")
    system_msg = SystemMessage(content=SYSTEM_PROMPT.format(user_id=user_id, subject_level=subject_level))
    full_messages = [system_msg] + messages

    llm = get_llm(with_tools=True)
    response = llm.invoke(full_messages)

    new_iteration = iteration + 1

    return {
        "messages": [response],
        "iteration_count": new_iteration
    }


def generate_response(state: AgentState) -> dict:
    messages = state["messages"]
    user_id = state.get("user_id", "S1001")
    intent = state.get("intent", "general")
    rag_context = state.get("rag_context", "")

    if intent == "faq" and rag_context:
        context_section = f"\n\n【知识库参考】\n{rag_context}\n\n请基于以上知识库内容回答学生问题。注意：不要直接给出最终答案，先引导思考，必要时再给出详细讲解。如果知识库中没有相关信息，请明确告知并建议转接老师。"
    elif intent == "general":
        context_section = "\n\n这是一般性对话，请以友好、鼓励的态度回应。可以适当引导学生聊回学习话题。"
    else:
        context_section = ""

    subject_level = state.get("subject_level", "未评估")
    system_content = SYSTEM_PROMPT.format(user_id=user_id, subject_level=subject_level) + context_section

    llm = get_llm(with_tools=False)
    response = llm.invoke([
        SystemMessage(content=system_content),
        *messages
    ])

    print(f"[Agent] 生成回答 (意图: {intent})")

    return {"messages": [response]}


def handle_transfer_human(state: AgentState) -> dict:
    messages = state["messages"]
    last_user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break

    from app.tools.human_transfer import transfer_to_teacher
    result = transfer_to_teacher.invoke({
        "reason": f"用户请求: {last_user_msg[:50]}",
        "urgency": "普通"
    })

    result_data = json.loads(result)

    transfer_msg = AIMessage(
        content=result_data["message"] + "\n\n如果您还有其他问题，我也可以帮您解答。"
    )

    return {"messages": [transfer_msg]}

def tool_execution(state: AgentState) -> dict:
    """
    节点6：工具执行
    
    当LLM决定调用工具后，这个节点负责真正执行工具，
    并把结果作为ToolMessage返回给对话。
    """
    messages = state["messages"]
    
    # 找到最后一条包含tool_calls的AIMessage
    last_ai_msg = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            last_ai_msg = msg
            break
    
    if not last_ai_msg:
        return {"messages": []}
    
    tool_messages = []
    for tool_call in last_ai_msg.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        
        # 在ALL_TOOLS中查找工具
        tool_func = None
        for tool in ALL_TOOLS:
            if tool.name == tool_name:
                tool_func = tool
                break
        
        if tool_func:
            try:
                result = tool_func.invoke(tool_args)
                tool_messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_id)
                )
                print(f"[Agent] 工具执行成功: {tool_name}")
            except Exception as e:
                tool_messages.append(
                    ToolMessage(content=f"工具执行出错: {str(e)}", tool_call_id=tool_id)
                )
                print(f"[Agent] 工具执行出错: {tool_name} - {str(e)}")
        else:
            tool_messages.append(
                ToolMessage(content=f"未找到工具: {tool_name}", tool_call_id=tool_id)
            )
            print(f"[Agent] 未找到工具: {tool_name}")
    
    return {"messages": tool_messages}
