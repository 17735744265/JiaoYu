"""
============================================
Embedding模型初始化
============================================

【讲解】Embedding是RAG系统的"翻译官"——把文字翻译成向量。
向量 = 一串数字，语义相近的文字 → 向量也相近。
这样就能用数学计算（余弦相似度）来衡量"两段文字有多像"。

为什么选 BGE-small-zh？
- BAAI出品，中文效果最好的一批模型之一
- small版本只有33M参数，CPU就能跑，不需要GPU
- 面试时说"选型考虑了部署成本和中文效果"，很加分

【面试考点】Embedding模型选择的三要素：
1. 语言覆盖（中文场景必须选中文模型）
2. 维度大小（影响存储和检索速度）
3. 部署成本（CPU能跑 vs 需要GPU）
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL


# 全局单例，避免重复加载模型（加载一次约3-5秒）
_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    获取Embedding模型单例
    
    【讲解】为什么用单例模式？
    - Embedding模型加载到内存需要几百MB
    - 每次请求都重新加载 = 服务器直接卡死
    - 单例 = 只加载一次，之后重复使用
    
    Returns:
        HuggingFaceEmbeddings: 已加载的Embedding模型实例
    """
    global _embedding_model
    if _embedding_model is None:
        print(f"[Embedding] 正在加载模型: {EMBEDDING_MODEL}")
        print("[Embedding] 首次加载需下载模型文件，请耐心等待...")
        
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            # model_kwargs: 传给底层sentence-transformers的参数
            model_kwargs={"device": "cpu"},  # 使用CPU推理，小模型CPU够用
            # encode_kwargs: 传给encode方法的参数
            encode_kwargs={"normalize_embeddings": True}  
            # normalize_embeddings=True: 归一化向量
            # 归一化后可以用点积代替余弦相似度，计算更快
        )
        print("[Embedding] 模型加载完成 ✅")
    
    return _embedding_model


def embed_query(text: str) -> list:
    """
    将单条文本转为向量（用于检索时的query）
    
    Args:
        text: 用户输入的查询文本
        
    Returns:
        list: 向量表示（维度取决于模型，BGE-small-zh是512维）
    
    【讲解】为什么区分 embed_query 和 embed_documents？
    - 有些模型对query和document有不同的编码策略
    - query通常加前缀"为这个句子生成表示..."
    - BGE模型会自动处理，但养成好习惯分开调用
    """
    model = get_embedding_model()
    return model.embed_query(text)


def embed_documents(texts: list[str]) -> list[list]:
    """
    将多条文本转为向量（用于建索引时的文档）
    
    Args:
        texts: 文档文本列表
        
    Returns:
        list[list]: 向量列表
    
    【讲解】批量编码比逐条编码快3-5倍
    因为GPU/CPU的并行计算能力，一次处理多条效率更高
    """
    model = get_embedding_model()
    return model.embed_documents(texts)
