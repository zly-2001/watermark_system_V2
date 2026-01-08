#!/bin/bash

# 安装三种水印模型的脚本
# 运行方式: bash install_models.sh

set -e  # 遇到错误立即退出

echo "========================================"
echo "  水印系统 - 模型安装脚本"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ 错误: 未找到 Python3${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python3 已安装: $(python3 --version)${NC}"
echo ""

# 创建必要的目录
echo "1. 创建模型目录..."
mkdir -p models/checkpoints
mkdir -p models/configs
echo -e "${GREEN}✓ 目录创建完成${NC}"
echo ""

# 安装 Python 依赖
echo "2. 安装 Python 依赖..."
echo -e "${YELLOW}   这可能需要几分钟时间...${NC}"
pip3 install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

# 安装 invisible-watermark (DWT-DCT)
echo "3. 安装 DWT-DCT 水印库..."
pip3 install invisible-watermark opencv-python PyWavelets
echo -e "${GREEN}✓ DWT-DCT 已安装 (invisible-watermark)${NC}"
echo ""

# StegaStamp 模型说明
echo "4. StegaStamp 模型配置..."
echo -e "${YELLOW}   ⚠️  StegaStamp 需要预训练模型:${NC}"
echo ""
echo "   下载链接 (任选其一):"
echo "   1. 官方 GitHub: https://github.com/tancik/StegaStamp"
echo "   2. 百度网盘: [请联系作者获取]"
echo ""
echo "   下载后，将模型放置到:"
echo "   - models/checkpoints/stegastamp_encoder.pth"
echo "   - models/checkpoints/stegastamp_decoder.pth"
echo ""
echo -e "${YELLOW}   如果没有模型文件，系统将使用 Mock 模式${NC}"
echo ""

# Tree-Ring 模型说明
echo "5. Tree-Ring 模型配置..."
echo -e "${YELLOW}   ⚠️  Tree-Ring 是基于扩散模型的最新方法:${NC}"
echo ""
echo "   参考论文: Tree-Ring Watermarks for Diffusion Models (2023)"
echo "   GitHub: https://github.com/YuxinWenRick/tree-ring-watermark"
echo ""
echo "   当前系统使用频域模拟实现，如需完整功能:"
echo "   1. 安装 diffusers 库: pip install diffusers"
echo "   2. 下载 Stable Diffusion 模型"
echo "   3. 参考 models/treering_watermark.py 进行集成"
echo ""
echo -e "${YELLOW}   如果没有扩散模型，系统将使用模拟模式${NC}"
echo ""

# 验证安装
echo "6. 验证安装..."
python3 -c "
import torch
import numpy as np
from PIL import Image
import cv2
from invisible_watermark import WatermarkEncoder

print('✓ PyTorch:', torch.__version__)
print('✓ NumPy:', np.__version__)
print('✓ OpenCV:', cv2.__version__)
print('✓ invisible-watermark: 已安装')
print('✓ 设备:', 'CUDA' if torch.cuda.is_available() else 'CPU')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 所有依赖验证通过${NC}"
else
    echo -e "${RED}✗ 依赖验证失败，请检查错误信息${NC}"
    exit 1
fi

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo -e "${GREEN}下一步:${NC}"
echo "1. 如果有 StegaStamp 模型，放置到 models/checkpoints/"
echo "2. 运行后端: uvicorn main:app --reload"
echo "3. 打开前端查看三种模型对比"
echo ""
echo "模型使用说明:"
echo "- DWT-DCT: 开箱即用，适合传统攻击"
echo "- StegaStamp: 需要 .pth 模型，抵抗 AIGC 攻击"
echo "- Tree-Ring: 需要扩散模型，最强 AIGC 抵抗力"
echo ""
echo "详细文档: backend/models/ATTACK_RESISTANCE.md"
echo ""

