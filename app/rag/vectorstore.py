"""
============================================
向量数据库操作
============================================

【讲解】向量数据库是RAG的"记忆库"——把知识存进去，检索时取出来。

为什么选 Chroma？
- 最轻量：pip install 就能用，不需要单独部署服务
- 够用：支持持久化、相似度检索、元数据过滤
- 面试友好：主流选择之一，面试官认

生产环境可能换什么？
- Milvus：分布式，支持亿级向量，大厂标配
- Pinecone：云服务，免运维，但收费
- Weaviate：功能全，支持混合检索

【面试考点】向量库选型的三个维度：
1. 数据规模（Chroma适合百万级以下，Milvus适合亿级）
2. 是否需要分布式（单机 vs 集群）
3. 运维成本（自建 vs 云服务）
"""

import json
from langchain_community.vectorstores import Chroma
from langchain_community.docstore.document import Document
from app.rag.embeddings import get_embedding_model
from config import (
    CHROMA_PERSIST_DIR, CHUNK_SIZE, CHUNK_OVERLAP,
    TOP_K, SCORE_THRESHOLD
)


def create_vectorstore_from_faq(faq_path: str = "data/faq.json") -> Chroma:
    """
    从FAQ数据创建向量数据库
    
    【讲解】这是RAG系统的"建库"步骤，整个流程是：
    1. 读取FAQ数据
    2. 把每条FAQ包装成Document对象
    3. 用Embedding模型把文本转为向量
    4. 存入Chroma向量库
    
    Args:
        faq_path: FAQ数据文件路径
        
    Returns:
        Chroma: 已构建好的向量数据库实例
    """
    # 1. 读取FAQ数据
    with open(faq_path, "r", encoding="utf-8") as f:
        # FAQ文件是Python格式，需要特殊处理
        # 实际项目中推荐用标准JSON格式
        content = f.read()
    
    # 用exec安全地加载Python格式的数据
    # （因为我们的faq.json实际上是Python代码格式）
    local_vars = {}
    exec(content, {}, local_vars)
    faq_data = local_vars.get("faq_data", [])
    
    print(f"[VectorStore] 加载了 {len(faq_data)} 条FAQ数据")
    
    # 2. 转换为LangChain Document对象
    # Document = 页面内容(page_content) + 元数据(metadata)
    # page_content: 被向量化、被检索的文本
    # metadata: 不参与检索，但可以用来过滤和展示
    documents = []
    for item in faq_data:
        # 把问题和答案拼在一起作为检索内容
        # 【面试考点】为什么要拼在一起？
        # - 只存问题：检索到了但不知道答案
        # - 只存答案：用户问法多样，检索不到
        # - 拼在一起：既匹配问题，又包含答案
        content = f"问题：{item['question']}\n答案：{item['answer']}"
        
        doc = Document(
            page_content=content,
            metadata={
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "answer": item["answer"]
            }
        )
        documents.append(doc)
    
    # 3. 构建向量库
    # from_documents 会自动：
    #   - 对每个文档调用Embedding模型生成向量
    #   - 创建Chroma集合
    #   - 存储文档和向量
    print("[VectorStore] 正在构建向量库，首次运行需加载Embedding模型...")
    
    embedding = get_embedding_model()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=CHROMA_PERSIST_DIR  # 持久化目录，下次启动不用重建
    )
    
    # 持久化到磁盘
    vectorstore.persist()
    print(f"[VectorStore] 向量库构建完成，共 {len(documents)} 条文档 ✅")
    
    return vectorstore


def load_vectorstore() -> Chroma:
    """
    加载已有的向量数据库
    
    【讲解】如果之前已经建过库，直接从磁盘加载，不用重新计算向量。
    这就是 persist_directory 的作用——持久化存储。
    
    Returns:
        Chroma: 从磁盘加载的向量数据库实例
    """
    embedding = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding
    )
    return vectorstore


def get_or_create_vectorstore(faq_path: str = "data/faq.json") -> Chroma:
    """
    智能获取向量库：有就加载，没有就创建
    
    【讲解】这是推荐的使用方式，避免每次都要手动判断。
    """
    import os
    if os.path.exists(CHROMA_PERSIST_DIR):
        print("[VectorStore] 检测到已有向量库，直接加载...")
        return load_vectorstore()
    else:
        print("[VectorStore] 未检测到向量库，开始创建...")
        return create_vectorstore_from_faq(faq_path)
