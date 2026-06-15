# """
# ============================================
# FastAPI 应用入口
# ============================================

# 【讲解】这是整个后端服务的"启动文件"。

# 启动命令:
#   uvicorn main:app --reload --host 0.0.0.0 --port 8000
  
# 启动后访问:
#   - API文档(Swagger): http://localhost:8000/docs
#   - 健康检查: http://localhost:8000/api/health
  
# FastAPI 特色（面试加分）：
# 1. 自动生成Swagger文档 → /docs
# 2. 自动生成OpenAPI规范 → /openapi.json  
# 3. 请求参数自动校验（Pydantic）
# 4. 异步支持（ASGI）
# 5. 类型提示驱动开发

# 为什么选 FastAPI 不选 Flask？
# - 异步：FastAPI原生支持async，Flask需要额外配置
# - 文档：自动生成，Flask需要手动写
# - 校验：Pydantic内置，Flask需要WTForms
# - 性能：FastAPI基于Starlette，比Flask快3-5倍
# """

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.api.routes import router
# from config import HOST, PORT

# # 创建FastAPI应用
# app = FastAPI(
#     title="Agent智能客服系统",
#     description="基于LangGraph + RAG + Function Call的智能客服Agent",
#     version="1.0.0",
#     docs_url="/docs",       # Swagger文档地址
#     redoc_url="/redoc",     # ReDoc文档地址
# )

# # ========== 跨域配置 ==========
# # 【讲解】为什么需要CORS？
# # - 前端(localhost:8501)和后端(localhost:8000)端口不同
# # - 浏览器安全策略会阻止跨域请求
# # - CORS中间件告诉浏览器"允许跨域"
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],        # 生产环境应该限制为具体域名
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 注册路由
# app.include_router(router)


# # ========== 启动事件 ==========
# @app.on_event("startup")
# async def startup():
#     """
#     应用启动时执行
    
#     【讲解】启动时预加载模型和向量库，
#     避免第一次请求时慢。
#     """
#     print("=" * 50)
#     print("🤖 Agent智能客服系统启动中...")
#     print("=" * 50)
    
#     # 预加载向量库（首次会下载Embedding模型，约1-3分钟）
#     from app.rag.vectorstore import get_or_create_vectorstore
#     print("[启动] 正在初始化向量库...")
#     get_or_create_vectorstore()
    
#     # 预编译Agent图
#     from app.agent.graph import get_graph
#     print("[启动] 正在编译Agent状态图...")
#     get_graph()
    
#     print("=" * 50)
#     print("✅ 系统启动完成！")
#     print(f"📖 API文档: http://{HOST}:{PORT}/docs")
#     print(f"💬 健康检查: http://{HOST}:{PORT}/api/health")
#     print("=" * 50)


# # ========== 根路由 ==========
# @app.get("/")
# async def root():
#     """根路径，返回服务信息"""
#     return {
#         "service": "Agent智能客服系统",
#         "version": "1.0.0",
#         "docs": "/docs",
#         "health": "/api/health"
#     }


# # ========== 直接运行 ==========
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host=HOST,
#         port=PORT,
#         reload=True  # 开发模式，代码修改自动重启
#     )
"""
============================================
FastAPI 应用入口
============================================

【讲解】这是整个后端服务的"启动文件"。

启动命令:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  
启动后访问:
  - API文档(Swagger): http://localhost:8000/docs
  - 健康检查: http://localhost:8000/api/health
  
FastAPI 特色（面试加分）：
1. 自动生成Swagger文档 → /docs
2. 自动生成OpenAPI规范 → /openapi.json  
3. 请求参数自动校验（Pydantic）
4. 异步支持（ASGI）
5. 类型提示驱动开发

为什么选 FastAPI 不选 Flask？
- 异步：FastAPI原生支持async，Flask需要额外配置
- 文档：自动生成，Flask需要手动写
- 校验：Pydantic内置，Flask需要WTForms
- 性能：FastAPI基于Starlette，比Flask快3-5倍
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from config import HOST, PORT

# 创建FastAPI应用
app = FastAPI(
    title="AI教育助教系统",
    description="基于LangGraph + RAG + Function Call的智能教学Agent",
    version="1.0.0",
    docs_url="/docs",       # Swagger文档地址
    redoc_url="/redoc",     # ReDoc文档地址
)

# ========== 跨域配置 ==========
# 【讲解】为什么需要CORS？
# - 前端(localhost:8501)和后端(localhost:8000)端口不同
# - 浏览器安全策略会阻止跨域请求
# - CORS中间件告诉浏览器"允许跨域"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 生产环境应该限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


# ========== 启动事件 ==========
@app.on_event("startup")
async def startup():
    """
    应用启动时执行
    
    【讲解】启动时预加载模型和向量库，
    避免第一次请求时慢。
    """
    print("=" * 50)
    print("📚 AI教育助教系统启动中...")
    print("=" * 50)
    
    # 预加载向量库（首次会下载Embedding模型，约1-3分钟）
    from app.rag.vectorstore import get_or_create_vectorstore
    print("[启动] 正在初始化向量库...")
    get_or_create_vectorstore()
    
    # 预编译Agent图
    from app.agent.graph import get_graph
    print("[启动] 正在编译Agent状态图...")
    get_graph()
    
    print("=" * 50)
    print("✅ 系统启动完成！")
    print(f"📖 API文档: http://{HOST}:{PORT}/docs")
    print(f"💬 健康检查: http://{HOST}:{PORT}/api/health")
    print("=" * 50)


# ========== 根路由 ==========
@app.get("/")
async def root():
    """根路径，返回服务信息"""
    return {
        "service": "AI教育助教系统",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# ========== 直接运行 ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True  # 开发模式，代码修改自动重启
    )
