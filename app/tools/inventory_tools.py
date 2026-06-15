"""
============================================
库存查询工具
============================================

【讲解】这个工具演示了"只读工具"——Agent只能查，不能改。
设计工具时要区分"查询"和"操作"，操作类工具需要更严格的安全控制。
"""

from langchain_core.tools import tool
import json
import os


def _load_mock_inventory():
    """加载模拟库存数据"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_orders.json")
    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read()
    local_vars = {}
    exec(content, {}, local_vars)
    return local_vars.get("mock_inventory", {})


@tool
def check_inventory(product_id: str) -> str:
    """
    查询商品库存状态。
    
    当用户询问商品是否有货、库存情况、什么时候补货时，调用此工具。
    
    Args:
        product_id: 商品编号，格式如 P001
        
    Returns:
        库存信息的JSON字符串
    
    【讲解】库存查询是典型的"只读工具"。
    面试时注意区分：
    - 只读工具（查询类）：安全，可以放开
    - 写入工具（操作类）：危险，需要权限控制和确认
    """
    inventory = _load_mock_inventory()
    
    if product_id not in inventory:
        return json.dumps({
            "error": f"未找到商品 {product_id}",
            "hint": "请检查商品编号，当前支持: " + ", ".join(inventory.keys())
        }, ensure_ascii=False)
    
    item = inventory[product_id]
    
    # 库存状态判断
    if item["stock"] == 0:
        stock_status = "缺货"
        suggestion = "可以订阅到货通知，补货后第一时间通知您"
    elif item["stock"] < 10:
        stock_status = "库存紧张"
        suggestion = "建议尽快下单"
    else:
        stock_status = "有货"
        suggestion = "可正常购买"
    
    return json.dumps({
        "商品编号": product_id,
        "商品名称": item["name"],
        "库存数量": item["stock"],
        "价格": f"¥{item['price']:.2f}",
        "库存状态": stock_status,
        "购买建议": suggestion
    }, ensure_ascii=False, indent=2)


@tool
def search_product(keyword: str) -> str:
    """
    根据关键词搜索商品。
    
    当用户说"有没有xxx"、"我想买xxx"、"搜索xxx"时调用。
    
    Args:
        keyword: 搜索关键词，如"耳机"、"T恤"
        
    Returns:
        搜索结果的JSON字符串
    """
    inventory = _load_mock_inventory()
    
    results = []
    for pid, item in inventory.items():
        if keyword in item["name"]:
            stock_status = "缺货" if item["stock"] == 0 else "有货"
            results.append({
                "商品编号": pid,
                "商品名称": item["name"],
                "价格": f"¥{item['price']:.2f}",
                "库存状态": stock_status
            })
    
    if not results:
        return json.dumps({
            "message": f"未找到与「{keyword}」相关的商品",
            "suggestion": "请尝试其他关键词，或联系客服获取帮助"
        }, ensure_ascii=False)
    
    return json.dumps(results, ensure_ascii=False, indent=2)
