#!/bin/bash

# 启动后端服务器脚本

echo "正在启动 FastAPI 后端服务器..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 启动服务器
echo "启动服务器在 http://localhost:8000"
uvicorn main:app --reload --port 8000

