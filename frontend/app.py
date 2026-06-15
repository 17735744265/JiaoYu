# """
# ============================================
# Streamlit 前端界面 — 教育助教版
# ============================================

# 启动命令:
#   streamlit run frontend/app.py --server.port 8501

# 启动后访问: http://localhost:8501
# """

# import httpx
# import streamlit as st
# import json

# # ========== 页面配置 ==========
# st.set_page_config(
#     page_title="AI教育助教",
#     page_icon="📚",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ========== 样式 ==========
# st.markdown("""
# <style>
#     .stChatMessage {
#         padding: 10px;
#         border-radius: 10px;
#         margin: 5px 0;
#     }
#     .main-title {
#         text-align: center;
#         color: #1f77b4;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ========== 后端API地址 ==========
# API_BASE = "http://127.0.0.1:8000/api"

# # ========== 会话状态初始化 ==========
# if "session_id" not in st.session_state:
#     st.session_state.session_id = "streamlit_student"
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # ========== 侧边栏 ==========
# with st.sidebar:
#     st.title("⚙️ 设置")

#     # 学生ID输入
#     user_id = st.text_input("学生ID", value="S1001", help="用于查询你的学习进度和作业")

#     # 科目选择
#     subject = st.selectbox("当前科目", ["数学", "Python", "物理", "英语"], index=0)

#     # 快捷问题
#     st.subheader("💡 试试这些问题")
#     quick_questions = [
#         "我的学习进度怎样？",
#         "有什么作业没做？",
#         "帮我出3道Python题",
#         "看看我的错题本",
#         "帮我制定学习计划",
#         "找真人老师",
#     ]
#     for q in quick_questions:
#         if st.button(q, key=f"quick_{q}"):
#             st.session_state.pending_query = q

#     # 清除对话
#     if st.button("🗑️ 清除对话"):
#         try:
#             with httpx.Client(timeout=10) as client:
#                 client.delete(f"{API_BASE}/session/{st.session_state.session_id}")
#         except Exception:
#             pass
#         st.session_state.messages = []
#         st.rerun()

#     # 测试连接
#     if st.button("🔍 测试连接"):
#         try:
#             with httpx.Client(timeout=10) as client:
#                 r = client.get(f"{API_BASE}/health")
#                 st.success(f"健康检查: {r.text}")
#         except Exception as e:
#             st.error(f"连接失败: {e}")
#             st.info("请确认后端已启动: uvicorn main:app --reload --port 8000")

#     # 系统信息
#     st.divider()
#     st.caption("🔧 技术栈: LangGraph + RAG + Function Call")
#     st.caption("📦 模型: DeepSeek + BGE-small-zh")
#     st.caption("📚 后端: FastAPI + Chroma")

# # ========== 主界面 ==========
# st.title("📚 AI教育助教")
# st.caption("基于 RAG知识库 + Function Call工具调用 + LangGraph编排 的智能教学助手")

# # 显示历史消息
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # 处理快捷问题
# pending = st.session_state.get("pending_query", "")
# if pending:
#     st.session_state.pending_query = ""

# # 聊天输入
# if prompt := st.chat_input("请输入你的问题，可以问知识、做练习、查进度...") or pending:
#     # 显示用户消息
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     # 调用后端API
#     with st.chat_message("assistant"):
#         with st.spinner("思考中..."):
#             try:
#                 with httpx.Client(timeout=120) as client:
#                     response = client.post(
#                         f"{API_BASE}/chat",
#                         json={
#                             "query": prompt,
#                             "user_id": user_id,
#                             "session_id": st.session_state.session_id
#                         }
#                     )
#                     if response.status_code == 200:
#                         data = response.json()
#                         reply = data.get("data", {}).get("reply", "抱歉，出了点问题")
#                     else:
#                         reply = f"服务异常（{response.status_code}），请稍后重试"

#             except httpx.ConnectError:
#                 reply = "⚠️ 无法连接后端，请确认已启动: uvicorn main:app --reload --port 8000"
#             except httpx.TimeoutException:
#                 reply = "⚠️ 请求超时，助教可能在思考复杂问题，请稍后重试"
#             except Exception as e:
#                 reply = f"⚠️ 发生错误: {type(e).__name__}: {e}"

#     st.markdown(reply)
#     st.session_state.messages.append({"role": "assistant", "content": reply})
"""
============================================
Streamlit 前端界面 — 教育助教版
============================================

启动命令:
  streamlit run frontend/app.py --server.port 8501

启动后访问: http://localhost:8501
"""

import httpx
import streamlit as st
import json

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI教育助教",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 样式 ==========
st.markdown("""
<style>
    .stChatMessage {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .main-title {
        text-align: center;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# ========== 后端API地址 ==========
API_BASE = "http://127.0.0.1:8000/api"

# ========== 会话状态初始化 ==========
if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit_student"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========== 侧边栏 ==========
with st.sidebar:
    st.title("⚙️ 设置")

    # 学生ID输入
    user_id = st.text_input("学生ID", value="S1001", help="用于查询你的学习进度和作业")

    # 科目选择
    subject = st.selectbox("当前科目", ["数学", "Python", "物理", "英语"], index=0)

    # 快捷问题
    st.subheader("💡 试试这些问题")
    quick_questions = [
        "我的学习进度怎样？",
        "有什么作业没做？",
        "帮我出3道Python题",
        "看看我的错题本",
        "帮我制定学习计划",
        "找真人老师",
    ]
    for q in quick_questions:
        if st.button(q, key=f"quick_{q}"):
            st.session_state.pending_query = q

    # 清除对话
    if st.button("🗑️ 清除对话"):
        try:
            with httpx.Client(timeout=10) as client:
                client.delete(f"{API_BASE}/session/{st.session_state.session_id}")
        except Exception:
            pass
        st.session_state.messages = []
        st.rerun()

    # 测试连接
    if st.button("🔍 测试连接"):
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(f"{API_BASE}/health")
                st.success(f"健康检查: {r.text}")
        except Exception as e:
            st.error(f"连接失败: {e}")
            st.info("请确认后端已启动: uvicorn main:app --reload --port 8000")

    # 系统信息
    st.divider()
    st.caption("🔧 技术栈: LangGraph + RAG + Function Call")
    st.caption("📦 模型: DeepSeek + BGE-small-zh")
    st.caption("📚 后端: FastAPI + Chroma")

# ========== 主界面 ==========
st.title("📚 AI教育助教")
st.caption("基于 RAG知识库 + Function Call工具调用 + LangGraph编排 的智能教学助手")

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 处理快捷问题
pending = st.session_state.get("pending_query", "")
if pending:
    st.session_state.pending_query = ""

# 聊天输入
if prompt := st.chat_input("请输入你的问题，可以问知识、做练习、查进度...") or pending:
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用后端API
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                with httpx.Client(timeout=120) as client:
                    response = client.post(
                        f"{API_BASE}/chat",
                        json={
                            "query": prompt,
                            "user_id": user_id,
                            "session_id": st.session_state.session_id
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        reply = data.get("data", {}).get("reply", "抱歉，出了点问题")
                    else:
                        reply = f"服务异常（{response.status_code}），请稍后重试"

            except httpx.ConnectError:
                reply = "⚠️ 无法连接后端，请确认已启动: uvicorn main:app --reload --port 8000"
            except httpx.TimeoutException:
                reply = "⚠️ 请求超时，助教可能在思考复杂问题，请稍后重试"
            except Exception as e:
                reply = f"⚠️ 发生错误: {type(e).__name__}: {e}"

    st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
