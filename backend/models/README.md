# 模型文件存放说明

## 📁 目录结构

```
backend/models/
├── __init__.py                 # 模块初始化
├── model_loader.py             # 模型加载器
├── README.md                   # 本说明文件
├── checkpoints/                # 存放 .pth 模型文件 ⭐
│   ├── stegastamp_encoder.pth  # 编码器权重
│   ├── stegastamp_decoder.pth  # 解码器权重
│   ├── hidden_encoder.pth      # (可选) HiDDeN 模型
│   └── hidden_decoder.pth
└── configs/                    # 存放配置文件
    ├── stegastamp_config.yaml  # (可选) 模型配置
    └── training_params.json
```

## 🎯 如何放置模型

### 方法1：直接放置（推荐）

将你的 `.pth` 模型文件直接放到 `checkpoints/` 目录下：

```bash
# 复制模型文件
cp your_encoder.pth backend/models/checkpoints/stegastamp_encoder.pth
cp your_decoder.pth backend/models/checkpoints/stegastamp_decoder.pth
```

### 方法2：通过命令行

```bash
cd backend/models/checkpoints

# 下载预训练模型（如果有链接）
wget https://example.com/models/encoder.pth -O stegastamp_encoder.pth
wget https://example.com/models/decoder.pth -O stegastamp_decoder.pth
```

### 方法3：从训练脚本保存

在你的训练代码中：

```python
import torch

# 保存编码器
torch.save(encoder.state_dict(), 
          'backend/models/checkpoints/stegastamp_encoder.pth')

# 保存解码器
torch.save(decoder.state_dict(), 
          'backend/models/checkpoints/stegastamp_decoder.pth')
```

## 📋 支持的模型格式

### PyTorch (.pth)
```python
# 标准 state_dict 格式
checkpoint = {
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),  # 可选
    'epoch': epoch,  # 可选
    'loss': loss,    # 可选
}
torch.save(checkpoint, 'model.pth')

# 或者只保存模型权重
torch.save(model.state_dict(), 'model.pth')
```

### 其他格式
- `.pt`: PyTorch 格式（与 .pth 相同）
- `.ckpt`: Lightning checkpoint（需要适配）
- `.pkl`: Pickle 格式（不推荐）

## 🔧 模型命名规范

### 标准命名
- `{model_name}_encoder.pth` - 编码器（嵌入水印）
- `{model_name}_decoder.pth` - 解码器（提取水印）

### 示例
```
stegastamp_encoder.pth
stegastamp_decoder.pth

hidden_encoder.pth
hidden_decoder.pth

rivagan_encoder.pth
rivagan_decoder.pth
```

## 💡 使用示例

### 在代码中加载模型

```python
from models import WatermarkModel

# 创建模型实例
model = WatermarkModel(model_type="stegastamp")

# 加载模型权重
model.load_checkpoint(
    encoder_path="stegastamp_encoder.pth",
    decoder_path="stegastamp_decoder.pth"
)

# 嵌入水印
watermarked_image, psnr, ssim = model.encode(
    image=pil_image,
    message="Thesis-2024",
    strength=0.5
)

# 提取水印
extracted_text, ber = model.decode(watermarked_image)
```

## 🎓 常见水印模型

### 1. StegaStamp (CVPR 2020)
- **论文**: "StegaStamp: Invisible Hyperlinks in Physical Photographs"
- **GitHub**: https://github.com/tancik/StegaStamp
- **模型文件**: 
  - encoder: 约 50MB
  - decoder: 约 20MB

### 2. HiDDeN (ICCV 2019)
- **论文**: "HiDDeN: Hiding Data With Deep Networks"
- **GitHub**: https://github.com/ando-khachatryan/HiDDeN
- **模型文件**: 各约 100MB

### 3. RivaGAN (NeurIPS 2019)
- **论文**: "RivaGAN: Steganography with GANs"
- **模型文件**: Encoder + Decoder + Discriminator

## 🔍 验证模型

运行测试脚本验证模型是否正确加载：

```bash
cd backend
python -c "from models import get_model; model = get_model(); print('✓ 模型加载成功' if model.is_loaded else '✗ 模型未加载')"
```

## ⚠️ 注意事项

1. **文件大小**: 
   - 单个 .pth 文件通常 20MB - 200MB
   - 确保服务器有足够存储空间

2. **GPU 内存**:
   - 推理时会占用 1-4GB GPU 内存
   - CPU 模式较慢但不需要 GPU

3. **版本兼容**:
   - PyTorch 版本需要兼容
   - 建议使用 PyTorch 1.8+

4. **模型架构**:
   - 需要在 `model_loader.py` 中定义对应的网络结构
   - 或者将模型架构代码也包含在 checkpoint 中

## 🚀 快速开始

```bash
# 1. 创建目录
mkdir -p backend/models/checkpoints

# 2. 放置模型文件
cp your_encoder.pth backend/models/checkpoints/stegastamp_encoder.pth
cp your_decoder.pth backend/models/checkpoints/stegastamp_decoder.pth

# 3. 启动服务
cd backend
uvicorn main:app --reload

# 4. 测试
# 访问 http://localhost:8000 开始使用
```

## 📚 更多资源

- [PyTorch 模型保存与加载](https://pytorch.org/tutorials/beginner/saving_loading_models.html)
- [水印论文集合](https://github.com/topics/watermarking)
- [StegaStamp 官方实现](https://github.com/tancik/StegaStamp)

