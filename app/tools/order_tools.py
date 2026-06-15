"""
============================================
订单相关工具
============================================

【讲解】这是Agent的"手脚"——LLM本身只会"说话"，不会"做事"。
工具 = 让Agent能真正操作业务系统的接口。

Function Call 工作流程：
1. 用户说"我的订单到哪了"
2. LLM判断：需要调用 query_order 工具
3. LLM输出：{"name": "query_order", "arguments": {"order_id": "ORD20240601001"}}
4. 系统执行工具，拿到结果
5. 把结果喂回LLM，LLM组织语言回答用户

【面试考点】Function Call vs 直接让LLM生成代码？
- Function Call：安全、可控、确定性高（生产环境必须用）
- LLM生成代码：灵活但危险（可能删库跑路）
- 面试说"生产环境只用Function Call，不允许LLM直接执行代码"

工具设计原则（面试加分）：
1. 每个工具只做一件事（单一职责）
2. 输入输出都是简单数据类型（方便LLM理解）
3. 工具描述要写清楚（LLM根据描述决定是否调用）
"""

from langchain_core.tools import tool
import json
import os


def _load_mock_orders():
    """加载模拟订单数据"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_orders.json")
    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read()
    local_vars = {}
    exec(content, {}, local_vars)
    return local_vars.get("mock_orders", [])


@tool
def query_order(order_id: str) -> str:
    """
    查询订单状态和物流信息。
    
    当用户询问订单状态、物流进度、快递信息、包裹到哪了等与订单相关的问题时，调用此工具。
    
    Args:
        order_id: 订单编号，格式如 ORD20240601001
        
    Returns:
        订单详情的JSON字符串
    
    【讲解】@tool 装饰器做了什么？
    1. 把这个函数注册为LangChain工具
    2. 自动从函数签名和docstring提取工具描述
    3. LLM看到描述后知道什么时候该调用这个工具
    4. docstring很重要！写不好LLM就不会调用或调错
    """
    orders = _load_mock_orders()
    
    for order in orders:
        if order["order_id"] == order_id:
            # 返回结构化的订单信息
            result = {
                "订单号": order["order_id"],
                "商品": order["product"],
                "金额": f"¥{order['amount']:.2f}",
                "状态": order["status"],
                "下单时间": order["create_time"]
            }
            
            # 如果有物流信息，追加
            if order.get("shipping_info"):
                shipping = order["shipping_info"]
                result["物流"] = f"{shipping['carrier']} {shipping.get('tracking_no', '')}"
                if "current_location" in shipping:
                    result["当前位置"] = shipping["current_location"]
                if "estimated_delivery" in shipping:
                    result["预计送达"] = shipping["estimated_delivery"]
                if "signed_by" in shipping:
                    result["签收人"] = shipping["signed_by"]
                    result["签收时间"] = shipping["signed_time"]
            
            # 如果有退款信息，追加
            if order.get("refund_info"):
                refund = order["refund_info"]
                result["退款"] = f"退款单号: {refund['refund_id']}, 原因: {refund['reason']}, 状态: {refund['status']}"
            
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    return json.dumps({"error": f"未找到订单 {order_id}，请检查订单号是否正确"}, ensure_ascii=False)


@tool
def refund_order(order_id: str, reason: str) -> str:
    """
    发起退款申请。
    
    当用户要求退货、退款、取消订单时，调用此工具。
    注意：已签收的订单需要用户说明退款原因。
    
    Args:
        order_id: 订单编号
        reason: 退款原因，如"商品与描述不符"、"不想要了"等
        
    Returns:
        退款申请结果的JSON字符串
    
    【讲解】退款是敏感操作，面试必问：
    "你怎么保证Agent不会误操作？"
    回答：1) 工具内部有状态校验 2) 敏感操作需要确认 3) 有操作日志
    """
    orders = _load_mock_orders()
    
    for order in orders:
        if order["order_id"] == order_id:
            # 业务校验：哪些状态可以退款
            if order["status"] == "已取消":
                return json.dumps({
                    "error": "该订单已取消，无需退款",
                    "order_id": order_id
                }, ensure_ascii=False)
            
            if order["status"] == "退款中":
                return json.dumps({
                    "message": "该订单已在退款流程中",
                    "refund_id": order.get("refund_info", {}).get("refund_id", "未知"),
                    "status": order.get("refund_info", {}).get("status", "审核中"),
                    "estimated_time": order.get("refund_info", {}).get("estimated_time", "1-2个工作日")
                }, ensure_ascii=False)
            
            # 模拟创建退款单
            refund_id = f"REF{order_id[3:]}"  # 简单生成退款单号
            return json.dumps({
                "success": True,
                "message": "退款申请已提交",
                "refund_id": refund_id,
                "order_id": order_id,
                "amount": f"¥{order['amount']:.2f}",
                "reason": reason,
                "estimated_process_time": "1-2个工作日",
                "note": "审核通过后3-5个工作日退款到原支付方式"
            }, ensure_ascii=False)
    
    return json.dumps({"error": f"未找到订单 {order_id}"}, ensure_ascii=False)


@tool
def list_user_orders(user_id: str) -> str:
    """
    查询用户的所有订单列表。
    
    当用户说"我的订单"、"我买过什么"、"查看我的订单"时调用。
    
    Args:
        user_id: 用户ID，格式如 U1001
        
    Returns:
        用户订单列表的JSON字符串
    """
    orders = _load_mock_orders()
    user_orders = [o for o in orders if o["user_id"] == user_id]
    
    if not user_orders:
        return json.dumps({"message": f"用户 {user_id} 暂无订单"}, ensure_ascii=False)
    
    result = []
    for order in user_orders:
        result.append({
            "订单号": order["order_id"],
            "商品": order["product"],
            "金额": f"¥{order['amount']:.2f}",
            "状态": order["status"],
            "下单时间": order["create_time"]
        })
    
    return json.dumps(result, ensure_ascii=False, indent=2)
