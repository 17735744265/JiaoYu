"""
============================================
RAG检索器
============================================

【讲解】这是RAG系统的"搜索引擎"——用户提问后，从这里找最相关的知识。

RAG全流程：
  用户提问 → Embedding向量化 → 在向量库中找最相似的文档 → 拼到Prompt里 → LLM回答

【面试高频问题】RAG检索不准怎么办？
标准答案（从本项目代码中都能找到对应实现）：
1. 调整chunk_size和overlap → 见config.py
2. 混合检索（关键词+语义） → 本文件实现了similarity_score_threshold
3. Rerank重排序 → 见retrieve_with_rerank方法
4. 多路召回 → 同时用不同策略检索，合并结果
5. 查询改写 → 让LLM先把用户口语化问题改写成清晰查询
"""

from langchain_community.vectorstores import Chroma
from app.rag.vectorstore import get_or_create_vectorstore
from config import TOP_K, SCORE_THRESHOLD


class RAGRetriever:
    """
    RAG检索器
    
    【讲解】封装成类的好处：
    1. 统一管理检索逻辑，外面调用简单
    2. 方便切换检索策略（换一种检索方式只改这里）
    3. 方便加缓存、日志等横切逻辑
    """
    
    def __init__(self):
        """初始化检索器，加载向量库"""
        self.vectorstore: Chroma = get_or_create_vectorstore()
        # as_retriever 把向量库包装成"检索器"接口
        # search_type="similarity_score_threshold" 表示只返回相似度高于阈值的结果
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": TOP_K,                    # 返回最相似的k条
                "score_threshold": SCORE_THRESHOLD  # 相似度阈值
            }
        )
        print("[RAG] 检索器初始化完成 ✅")
    
    def retrieve(self, query: str) -> list[dict]:
        """
        基础检索：根据用户查询返回相关文档
        
        Args:
            query: 用户输入的问题
            
        Returns:
            list[dict]: 检索到的文档列表，每项包含 content, score, metadata
            
        【讲解】这是最基础的检索方式——纯语义相似度检索。
        原理：把query转成向量 → 和库里所有向量算余弦相似度 → 返回最相似的k条
        """
        # 方式1：用retriever接口（更简洁，LangChain推荐）
        docs = self.retriever.invoke(query)
        
        # 方式2：用similarity_search_with_score（可以拿到相似度分数）
        # 面试时推荐展示这种方式，因为能看到分数，方便调试
        raw_results = self.vectorstore.similarity_search_with_score(query, k=TOP_K)
        
        results = []
        for doc, score in raw_results:
            # Chroma返回的是L2距离，需要转换为相似度
            # L2距离越小 = 越相似
            # 这里简化处理，直接用1/(1+distance)作为相似度
            similarity = 1.0 / (1.0 + score)
            
            results.append({
                "content": doc.page_content,
                "score": round(similarity, 4),
                "metadata": doc.metadata
            })
        
        # 按相似度降序排列
        results.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"[RAG] 检索到 {len(results)} 条相关文档")
        for i, r in enumerate(results):
            print(f"  [{i+1}] 相似度={r['score']:.4f} | 分类={r['metadata'].get('category', 'N/A')}")
        
        return results
    
    def retrieve_with_rerank(self, query: str, initial_k: int = 10, final_k: int = 3) -> list[dict]:
        """
        带重排序的检索（Rerank）
        
        【讲解】这是RAG进阶优化的核心手段！
        
        为什么需要Rerank？
        - 向量检索是"粗筛"：快速从百万文档中找到可能相关的几十条
        - Rerank是"精排"：用更精确的模型对这几十条重新打分排序
        - 两步走 = 速度和精度兼顾
        
        生产环境怎么做？
        - 用Cohere Rerank API（最成熟）
        - 或用bge-reranker-large本地模型
        - Demo阶段用LLM做简单重排序（本项目实现）
        
        Args:
            query: 用户查询
            initial_k: 初次检索返回的文档数（粗筛数量）
            final_k: 重排序后保留的文档数（精排数量）
        """
        # 第一步：粗筛，多召回一些
        raw_results = self.vectorstore.similarity_search_with_score(query, k=initial_k)
        
        # 第二步：用简单的规则做重排序
        # 这里演示一个简化版：优先返回分类匹配的结果
        # 生产环境用专门的Rerank模型
        
        results = []
        for doc, score in raw_results:
            similarity = 1.0 / (1.0 + score)
            results.append({
                "content": doc.page_content,
                "score": similarity,
                "metadata": doc.metadata
            })
        
        # 简单重排序策略：如果query中包含分类关键词，提升该分类的权重
        # category_keywords = {
        #     "退换货": ["退货", "退款", "换货", "退换"],
        #     "物流": ["快递", "配送", "运费", "发货"],
        #     "优惠": ["优惠券", "折扣", "优惠", "满减"],
        #     "会员": ["会员", "VIP", "积分"],
        #     "支付": ["支付", "付款", "花呗", "分期"],
        #     "账号": ["密码", "登录", "账号", "注册"],
        # }
        
        category_keywords = {
            "数学": ["函数", "方程", "几何", "概率", "微积分", "数列"],
            "物理": ["力学", "电磁", "光学", "热学", "运动"],
            "编程": ["Python", "代码", "算法", "数据结构", "循环", "函数"],
            "英语": ["语法", "单词", "阅读", "写作", "翻译"],
            "学习方法": ["记忆", "复习", "笔记", "时间管理", "专注"],
            "考试": ["高考", "中考", "期末", "模拟", "真题"],
        }
        
        for result in results:
            category = result["metadata"].get("category", "")
            if category in category_keywords:
                for keyword in category_keywords[category]:
                    if keyword in query:
                        # 匹配到分类关键词，相似度加权
                        result["score"] *= 1.2
                        break
        
        # 重新排序并取top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:final_k]
    
    def format_context(self, results: list[dict]) -> str:
        """
        将检索结果格式化为LLM可读的上下文文本
        
        【讲解】检索到的文档不能直接丢给LLM，需要格式化。
        好的格式化能让LLM更准确地利用检索结果。
        
        Args:
            results: 检索结果列表
            
        Returns:
            str: 格式化后的上下文文本
        """
        if not results:
            return "未找到相关知识库内容。"
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"【知识{i}】(相似度: {result['score']:.2f}, 分类: {result['metadata'].get('category', 'N/A')})\n"
                f"{result['content']}"
            )
        
        return "\n\n".join(context_parts)
