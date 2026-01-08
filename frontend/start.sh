#!/bin/bash

# 启动前端开发服务器脚本

echo "正在启动 Vue 3 前端开发服务器..."

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

# 启动开发服务器
echo "启动开发服务器在 http://localhost:5173"
npm run dev

