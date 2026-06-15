"""
============================================
项目全局配置文件
============================================

【讲解】为什么要把配置单独放一个文件？
1. 所有常量集中管理，改配置不用翻代码
2. 环境变量统一加载，敏感信息不入代码
3. 面试时体现工程规范意识

面试加分点：能说出"配置与代码分离"这个原则
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


# ========== LLM 配置 ==========
# 从环境变量读取，避免API Key硬编码
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
LLM_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# LLM 生成参数
LLM_TEMPERATURE = 0.1       # 低温度 = 更确定性的回答，客服场景需要稳定输出
LLM_MAX_TOKENS = 2048       # 单次回复最大token数
LLM_TIMEOUT = 30            # API超时时间（秒）


# ========== Embedding 配置 ==========
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


# ========== RAG 配置 ==========
# 这些是面试高频话题的参数，理解它们很重要
# CHUNK_SIZE = 500            # 文本切分块大小（字符数）
# CHUNK_OVERLAP = 50          # 切分重叠区（防止语义断裂）

# ========== 改动1：RAG参数调整 ==========
# 教育知识通常比电商FAQ更长（含公式、代码、步骤），需要更大的chunk
CHUNK_SIZE = 800            # 原500 → 800，教育内容更完整
CHUNK_OVERLAP = 100         # 原50 → 100，教育内容上下文衔接更重要

TOP_K = 3                   # 检索返回的文档数量
SCORE_THRESHOLD = 0.7       # 相似度阈值，低于此值认为没找到相关内容

# 【面试考点】CHUNK_SIZE怎么选？
# - 太小（<200）：上下文不够，回答不完整
# - 太大（>1000）：检索不精确，噪声多
# - 500是中文FAQ的甜点值，面试说这个数字很加分


# ========== Agent 配置 ==========
MAX_ITERATIONS = 5          # Agent最大推理轮数（防止死循环）
CONVERSATION_WINDOW = 10    # 对话记忆窗口（保留最近几轮）


# ========== 安全配置 ==========
# SENSITIVE_WORDS = ["密码", "身份证号", "银行卡号"]  # 敏感词过滤列表
# MAX_QUERY_LENGTH = 500      # 用户输入最大长度（防注入）

# ========== 改动3：安全配置 ==========
SENSITIVE_WORDS = ["密码", "身份证号", "银行卡号", "手机号"]  # 新增手机号
MAX_QUERY_LENGTH = 1000     # 原500 → 1000，学生可能会贴题目或代码

# ========== 新增：教育业务配置 ==========
DEFAULT_SUBJECT = "数学"              # 默认科目
QUIZ_DIFFICULTY_LEVELS = ["easy", "medium", "hard"]  # 出题难度等级
SPACED_REPETITION_INTERVALS = [1, 2, 4, 7, 15, 30]  # 艾宾浩斯复习间隔（天）

# ========== 业务配置 ==========
MOCK_API_BASE = "http://localhost:8001"  # 模拟业务API地址


# ========== 服务器配置 ==========
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))