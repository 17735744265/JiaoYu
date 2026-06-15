"""
工具模块初始化 - 注册所有工具
"""

# from app.tools.order_tools import query_order, refund_order, list_user_orders
# from app.tools.inventory_tools import check_inventory, search_product
# from app.tools.human_transfer import transfer_to_human

from app.tools.study_tools import query_study_progress, query_homework, generate_study_plan, manage_mistakes
from app.tools.quiz_tools import generate_quiz, grade_answer
from app.tools.human_transfer import transfer_to_teacher

ALL_TOOLS = [
    query_study_progress, query_homework, generate_study_plan, manage_mistakes,
    generate_quiz, grade_answer,
    transfer_to_teacher,
]

# 所有工具的列表，Agent会用到
# ALL_TOOLS = [
#     query_order,
#     refund_order,
#     list_user_orders,
#     check_inventory,
#     search_product,
#     transfer_to_human,
# ]

__all__ = ["ALL_TOOLS"]
