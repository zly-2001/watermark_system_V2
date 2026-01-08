#!/bin/bash
# 安装水印库的快速脚本

echo "🚀 开始安装水印相关库..."
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo "✗ 未找到虚拟环境"
    exit 1
fi

echo ""
echo "📦 安装 invisible-watermark（核心库）..."
pip install invisible-watermark

echo ""
echo "📦 安装 OpenCV（图像处理）..."
pip install opencv-python

echo ""
echo "📦 安装 PyWavelets（小波变换）..."
pip install PyWavelets

echo ""
echo "🎉 安装完成！"
echo ""
echo "测试水印功能："
python -c "
try:
    from models.simple_watermark import get_simple_watermark
    wm = get_simple_watermark()
    if wm.is_available:
        print('✓ 水印系统已就绪，可以使用！')
    else:
        print('✗ 水印库未正确安装')
except Exception as e:
    print(f'✗ 错误: {e}')
"

echo ""
echo "💡 提示：重启后端服务以应用更改"
echo "   uvicorn main:app --reload --port 8000"

