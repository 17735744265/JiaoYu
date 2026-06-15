"""
============================================
转人工工具
============================================

【讲解】这是客服系统的"兜底机制"——Agent解决不了的问题，转给真人。

面试必问："什么情况下转人工？"
标准回答：
1. 情绪识别：用户明显生气、投诉升级
2. 超出能力：涉及退款金额争议、法律问题
3. 多次失败：Agent连续2次无法解决问题
4. 用户要求：用户主动说"找人工客服"
5. 敏感操作：大额退款、账号变更等

这是客服Agent和普通聊天机器人的关键区别——知道什么时候该求助。
"""

from langchain_core.tools import tool
import json
import datetime



# 改动点1：docstring描述
@tool
def transfer_to_teacher(reason: str, urgency: str = "普通") -> str:
    """
    转接真人教师。

    当出现以下情况时调用此工具：
    1. 学生明确要求找真人老师
    2. 学生对某个知识点极度困惑，多次引导仍不理解
    3. 问题超出AI助教的处理范围（如需要实验操作指导）
    4. 涉及心理健康等需要专业人员介入的情况
    """

    # 改动点2：等待时间话术
    wait_time = {
        "普通": "约3-5分钟",
        "紧急": "约1-2分钟",
        "非常紧急": "立即转接"
    }.get(urgency, "约3-5分钟")

    # 改动点3：回复话术
    return json.dumps({
        "action": "transfer_to_teacher",
        "ticket_id": ticket_id,
        "reason": reason,
        "urgency": urgency,
        "wait_time": wait_time,
        "message": f"正在为您转接真人教师，工单号：{ticket_id}，预计等待{wait_time}。请稍等片刻～"
    }, ensure_ascii=False, indent=2)




# """
# ============================================
# 转人工工具
# ============================================

# 【讲解】这是客服系统的"兜底机制"——Agent解决不了的问题，转给真人。

# 面试必问："什么情况下转人工？"
# 标准回答：
# 1. 情绪识别：用户明显生气、投诉升级
# 2. 超出能力：涉及退款金额争议、法律问题
# 3. 多次失败：Agent连续2次无法解决问题
# 4. 用户要求：用户主动说"找人工客服"
# 5. 敏感操作：大额退款、账号变更等

# 这是客服Agent和普通聊天机器人的关键区别——知道什么时候该求助。
# """

# from langchain_core.tools import tool
# import json
# import datetime




# @tool
# def transfer_to_human(reason: str, urgency: str = "普通") -> str:
#     """
#     转接人工客服。
    
#     当出现以下情况时调用此工具：
#     1. 用户明确要求转人工
#     2. 用户情绪激动或表达不满
#     3. 问题超出AI客服处理范围
#     4. 涉及大额退款或账号安全等敏感操作
    
#     Args:
#         reason: 转人工的原因，如"用户要求"、"问题超出范围"等
#         urgency: 紧急程度，可选"普通"、"紧急"、"非常紧急"
        
#     Returns:
#         转接信息的JSON字符串
    
#     【讲解】转人工工具的设计要点：
#     1. 要记录原因——方便后续分析Agent短板
#     2. 要有紧急程度——紧急的优先排队
#     3. 要给用户反馈——"正在为您转接"而不是沉默
#     """
#     # 生成工单号
#     ticket_id = f"TK{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
#     # 等待时间估算
#     wait_time = {
#         "普通": "约3-5分钟",
#         "紧急": "约1-2分钟",
#         "非常紧急": "立即转接"
#     }.get(urgency, "约3-5分钟")
    
#     return json.dumps({
#         "action": "transfer_to_human",
#         "ticket_id": ticket_id,
#         "reason": reason,
#         "urgency": urgency,
#         "wait_time": wait_time,
#         "message": f"正在为您转接人工客服，工单号：{ticket_id}，预计等待{wait_time}。感谢您的耐心！"
#     }, ensure_ascii=False, indent=2)



