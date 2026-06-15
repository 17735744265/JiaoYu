"""
============================================
出题与判题工具
============================================

教育场景的特色工具：
1. 根据学科和难度生成练习题
2. 批改学生答案
3. 查询历史答题记录
"""

from langchain_core.tools import tool
import json


@tool
def generate_quiz(subject: str, topic: str = "", difficulty: str = "medium", count: int = 3) -> str:
    """
    生成练习题。

    当学生说"出几道题"、"练一练"、"做练习"时调用。

    Args:
        subject: 科目，如"数学"、"英语"、"Python"
        topic: 可选，具体知识点，如"二次函数"、"定语从句"、"列表推导式"
        difficulty: 难度 - "easy"基础, "medium"中等, "hard"困难
        count: 题目数量，默认3题

    Returns:
        练习题的JSON字符串
    """
    # 实际项目中应调用题库API或LLM动态生成
    # Demo阶段返回模拟题目
    quiz_templates = {
        "数学": [
            {"question": "求函数 f(x) = x² - 4x + 3 的零点", "type": "计算题", "hint": "令f(x)=0，用因式分解"},
            {"question": "已知等差数列前3项为 2, 5, 8，求第10项", "type": "计算题", "hint": "先求公差d"},
            {"question": "若 sin(θ) = 3/5，求 cos(2θ)", "type": "计算题", "hint": "用二倍角公式"},
        ],
        "Python": [
            {"question": "写一个列表推导式，生成1到100中的所有偶数", "type": "编程题", "hint": "使用if条件过滤"},
            {"question": "解释Python中 *args 和 **kwargs 的区别", "type": "概念题", "hint": "分别对应位置参数和关键字参数"},
            {"question": "用递归实现斐波那契数列（前N项）", "type": "编程题", "hint": "base case: f(0)=0, f(1)=1"},
        ],
    }

    questions = quiz_templates.get(subject, [
        {"question": f"请描述{subject}中{topic or '核心概念'}的含义", "type": "概念题", "hint": "结合例子说明"}
    ])

    result = {
        "subject": subject,
        "topic": topic or "综合",
        "difficulty": {"easy": "基础", "medium": "中等", "hard": "困难"}.get(difficulty, "中等"),
        "count": min(count, len(questions)),
        "questions": questions[:count]
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def grade_answer(question: str, student_answer: str, correct_answer: str = "", subject: str = "") -> str:
    """
    批改学生答案。

    当学生提交答题结果时调用。

    Args:
        question: 原始题目
        student_answer: 学生的答案
        correct_answer: 可选，标准答案（有则精确比对，无则由LLM评判）
        subject: 科目，用于辅助判断

    Returns:
        批改结果的JSON字符串
    """
    if correct_answer:
        # 有标准答案，精确比对
        is_correct = student_answer.strip() == correct_answer.strip()
        result = {
            "question": question,
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "feedback": "回答正确！👍" if is_correct else f"回答有误，正确答案是：{correct_answer}。建议重新复习相关知识点。"
        }
    else:
        # 无标准答案，标记为需要LLM评判
        result = {
            "question": question,
            "student_answer": student_answer,
            "needs_llm_grading": True,
            "hint": "此题需AI老师评判，请稍候"
        }

    return json.dumps(result, ensure_ascii=False, indent=2)
