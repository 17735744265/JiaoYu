"""
============================================
学习相关工具
============================================

教育场景的核心工具：
1. 查询学习进度
2. 查询作业和成绩
3. 生成个性化学习计划
4. 管理错题本
"""

from langchain_core.tools import tool
import json
import os


def _load_mock_data():
    """加载模拟学习数据"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_study_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read()
    local_vars = {}
    exec(content, {}, local_vars)
    return local_vars


@tool
def query_study_progress(student_id: str, subject: str = "") -> str:
    """
    查询学生的学习进度和成绩。

    当学生询问"我学到哪了"、"我的学习进度"、"最近学了什么"时调用。

    Args:
        student_id: 学生ID，格式如 S1001
        subject: 可选，指定科目名称，如"数学"、"英语"，不填则返回所有科目

    Returns:
        学习进度的JSON字符串
    """
    data = _load_mock_data()
    students = data.get("students", [])

    for student in students:
        if student["student_id"] == student_id:
            progress = student.get("progress", {})
            if subject:
                if subject in progress:
                    return json.dumps(progress[subject], ensure_ascii=False, indent=2)
                else:
                    return json.dumps({"error": f"未找到科目 {subject}，当前可选: {', '.join(progress.keys())}"}, ensure_ascii=False)
            return json.dumps(progress, ensure_ascii=False, indent=2)

    return json.dumps({"error": f"未找到学生 {student_id}"}, ensure_ascii=False)


@tool
def query_homework(student_id: str, status: str = "") -> str:
    """
    查询学生的作业列表。

    当学生询问"有什么作业"、"作业完成了没"、"还没做的作业"时调用。

    Args:
        student_id: 学生ID
        status: 可选，筛选状态："pending"待完成、"completed"已完成、"overdue"已逾期

    Returns:
        作业列表的JSON字符串
    """
    data = _load_mock_data()
    homework = data.get("homework", [])

    student_hw = [h for h in homework if h["student_id"] == student_id]

    if status:
        student_hw = [h for h in student_hw if h["status"] == status]

    if not student_hw:
        return json.dumps({"message": f"学生 {student_id} 暂无{'该状态的' if status else ''}作业"}, ensure_ascii=False)

    result = []
    for h in student_hw:
        result.append({
            "作业ID": h["homework_id"],
            "科目": h["subject"],
            "标题": h["title"],
            "截止时间": h["deadline"],
            "状态": {"pending": "待完成", "completed": "已完成", "overdue": "已逾期"}.get(h["status"], h["status"]),
            "得分": h.get("score", "未批改")
        })

    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def generate_study_plan(student_id: str, subject: str, duration_days: int = 7, goal: str = "巩固基础") -> str:
    """
    生成个性化学习计划。

    当学生说"帮我制定学习计划"、"怎么复习"、"接下来该学什么"时调用。

    Args:
        student_id: 学生ID
        subject: 目标科目
        duration_days: 计划天数，默认7天
        goal: 学习目标，如"巩固基础"、"冲刺考试"、"查漏补缺"

    Returns:
        学习计划的JSON字符串
    """
    data = _load_mock_data()
    students = data.get("students", [])

    student_info = None
    for s in students:
        if s["student_id"] == student_id:
            student_info = s
            break

    if not student_info:
        return json.dumps({"error": f"未找到学生 {student_id}"}, ensure_ascii=False)

    # 获取学生在该科目的弱项
    progress = student_info.get("progress", {}).get(subject, {})
    weak_points = progress.get("weak_points", ["未指定"])

    plan = {
        "student_id": student_id,
        "subject": subject,
        "goal": goal,
        "duration_days": duration_days,
        "weak_points": weak_points,
        "daily_plan": []
    }

    # 生成每日计划
    for day in range(1, duration_days + 1):
        plan["daily_plan"].append({
            "day": day,
            "focus": weak_points[(day - 1) % len(weak_points)] if weak_points != ["未指定"] else "基础练习",
            "duration_min": 45,
            "type": "练习" if day % 2 == 0 else "学习+练习",
            "note": "完成后做5道巩固题" if day % 2 == 0 else "先看知识点再做题"
        })

    return json.dumps(plan, ensure_ascii=False, indent=2)


@tool
def manage_mistakes(student_id: str, action: str = "list", subject: str = "", mistake_id: str = "") -> str:
    """
    管理学生错题本。

    当学生说"看看我的错题"、"错题本"、"这道题做错了帮我记录"时调用。

    Args:
        student_id: 学生ID
        action: 操作类型 - "list"查看列表, "add"添加错题, "review"标记已复习
        subject: 可选，筛选科目
        mistake_id: 错题ID，add和review操作时需要

    Returns:
        错题信息的JSON字符串
    """
    data = _load_mock_data()
    mistakes = data.get("mistakes", [])

    student_mistakes = [m for m in mistakes if m["student_id"] == student_id]

    if subject:
        student_mistakes = [m for m in student_mistakes if m["subject"] == subject]

    if action == "list":
        if not student_mistakes:
            return json.dumps({"message": f"暂无错题记录，继续保持！", "total": 0}, ensure_ascii=False)

        result = []
        for m in student_mistakes:
            result.append({
                "错题ID": m["mistake_id"],
                "科目": m["subject"],
                "题目摘要": m["question_summary"],
                "错误类型": m["error_type"],
                "正确解法": m["correct_approach"],
                "已复习": m.get("reviewed", False)
            })
        return json.dumps({"total": len(result), "mistakes": result}, ensure_ascii=False, indent=2)

    elif action == "add":
        return json.dumps({"message": "错题已添加，建议7天后复习巩固", "mistake_id": mistake_id or "M_NEW"}, ensure_ascii=False)

    elif action == "review":
        return json.dumps({"message": f"错题 {mistake_id} 已标记为已复习", "status": "reviewed"}, ensure_ascii=False)

    return json.dumps({"error": f"未知操作: {action}"}, ensure_ascii=False)
