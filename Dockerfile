# ============================================
# Dockerfile - Agent客服系统容器化
# ============================================
# 构建镜像: docker build -t agent-cs .
# 运行容器: docker run -p 8000:8000 -e DEEPSEEK_API_KEY=sk-xxx agent-cs

# 使用官方Python镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# 【讲解】PYTHONDONTWRITEBYTECODE=1 不生成.pyc文件
# PYTHONUNBUFFERED=1 实时输出日志
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 先复制依赖文件，利用Docker缓存层
# 【讲解】只要requirements.txt没变，这层缓存就不用重建
# 这是Docker最佳实践，加速构建
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
# 【讲解】不用--reload，生产环境不需要自动重启
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
