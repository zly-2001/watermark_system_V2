"""
水印模型加载器 - 支持 PyTorch .pth 格式
"""
import os
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# 模型路径配置
BASE_DIR = Path(__file__).parent
CHECKPOINT_DIR = BASE_DIR / "checkpoints"
CONFIG_DIR = BASE_DIR / "configs"


class WatermarkModel:
    """
    水印模型统一接口
    支持加载 .pth 格式的 PyTorch 模型
    """
    
    def __init__(self, model_type: str = "stegastamp"):
        """
        初始化模型
        
        Args:
            model_type: 模型类型 ("stegastamp", "hidden", "rivagan" 等)
        """
        self.model_type = model_type
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.encoder = None
        self.decoder = None
        self.is_loaded = False
        
        logger.info(f"初始化 {model_type} 模型，使用设备: {self.device}")
    
    def load_checkpoint(self, encoder_path: str, decoder_path: str):
        """
        从 .pth 文件加载模型权重
        
        Args:
            encoder_path: 编码器权重路径 (相对于 checkpoints/ 目录)
            decoder_path: 解码器权重路径 (相对于 checkpoints/ 目录)
        
        Example:
            model.load_checkpoint(
                "stegastamp_encoder.pth",
                "stegastamp_decoder.pth"
            )
        """
        try:
            encoder_full_path = CHECKPOINT_DIR / encoder_path
            decoder_full_path = CHECKPOINT_DIR / decoder_path
            
            # 检查文件是否存在
            if not encoder_full_path.exists():
                raise FileNotFoundError(f"编码器模型不存在: {encoder_full_path}")
            if not decoder_full_path.exists():
                raise FileNotFoundError(f"解码器模型不存在: {decoder_full_path}")
            
            # 加载模型权重
            logger.info(f"加载编码器: {encoder_full_path}")
            encoder_checkpoint = torch.load(encoder_full_path, map_location=self.device)
            
            logger.info(f"加载解码器: {decoder_full_path}")
            decoder_checkpoint = torch.load(decoder_full_path, map_location=self.device)
            
            # 根据模型类型初始化网络结构
            if self.model_type == "stegastamp":
                self.encoder = self._build_stegastamp_encoder()
                self.decoder = self._build_stegastamp_decoder()
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")
            
            # 加载权重
            self.encoder.load_state_dict(encoder_checkpoint)
            self.decoder.load_state_dict(decoder_checkpoint)
            
            # 设置为评估模式
            self.encoder.eval()
            self.decoder.eval()
            
            # 移动到目标设备
            self.encoder.to(self.device)
            self.decoder.to(self.device)
            
            self.is_loaded = True
            logger.info("模型加载成功！")
            
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            raise
    
    def _build_stegastamp_encoder(self):
        """
        构建 StegaStamp 编码器网络
        TODO: 根据你的实际模型架构修改
        """
        # 这里是示例结构，需要根据实际模型修改
        import torch.nn as nn
        
        class StegaStampEncoder(nn.Module):
            def __init__(self):
                super().__init__()
                # 示例网络结构
                self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
                self.conv2 = nn.Conv2d(64, 64, 3, padding=1)
                self.conv3 = nn.Conv2d(64, 3, 3, padding=1)
                self.relu = nn.ReLU(inplace=True)
            
            def forward(self, image, message):
                x = self.relu(self.conv1(image))
                x = self.relu(self.conv2(x))
                x = self.conv3(x)
                return image + x  # 残差连接
        
        return StegaStampEncoder()
    
    def _build_stegastamp_decoder(self):
        """
        构建 StegaStamp 解码器网络
        TODO: 根据你的实际模型架构修改
        """
        import torch.nn as nn
        
        class StegaStampDecoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
                self.conv2 = nn.Conv2d(64, 64, 3, padding=1)
                self.conv3 = nn.Conv2d(64, 100, 3, padding=1)  # 假设输出100位
                self.relu = nn.ReLU(inplace=True)
                self.pool = nn.AdaptiveAvgPool2d(1)
            
            def forward(self, image):
                x = self.relu(self.conv1(image))
                x = self.relu(self.conv2(x))
                x = self.conv3(x)
                x = self.pool(x)
                return x.view(x.size(0), -1)
        
        return StegaStampDecoder()
    
    def encode(self, image: Image.Image, message: str, strength: float = 0.5) -> Tuple[Image.Image, float, float]:
        """
        嵌入水印
        
        Args:
            image: PIL Image 对象
            message: 水印文本
            strength: 水印强度 (0.1-1.0)
        
        Returns:
            (水印图像, PSNR, SSIM)
        """
        if not self.is_loaded:
            raise RuntimeError("模型未加载！请先调用 load_checkpoint()")
        
        try:
            # 预处理图像
            img_tensor = self._preprocess_image(image)
            
            # 将消息转换为张量
            msg_tensor = self._text_to_tensor(message)
            
            # 推理
            with torch.no_grad():
                watermarked_tensor = self.encoder(img_tensor, msg_tensor)
            
            # 后处理
            watermarked_image = self._postprocess_image(watermarked_tensor)
            
            # 计算质量指标
            psnr, ssim = self._calculate_metrics(image, watermarked_image)
            
            return watermarked_image, psnr, ssim
            
        except Exception as e:
            logger.error(f"编码失败: {str(e)}")
            raise
    
    def decode(self, image: Image.Image) -> Tuple[str, float]:
        """
        提取水印
        
        Args:
            image: 带水印的 PIL Image 对象
        
        Returns:
            (提取的文本, 误码率 BER)
        """
        if not self.is_loaded:
            raise RuntimeError("模型未加载！请先调用 load_checkpoint()")
        
        try:
            # 预处理图像
            img_tensor = self._preprocess_image(image)
            
            # 推理
            with torch.no_grad():
                message_bits = self.decoder(img_tensor)
            
            # 解码为文本
            extracted_text = self._tensor_to_text(message_bits)
            
            # 计算误码率 (需要与原始消息比对)
            ber = 0.0  # TODO: 实现 BER 计算
            
            return extracted_text, ber
            
        except Exception as e:
            logger.error(f"解码失败: {str(e)}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """将 PIL Image 转换为模型输入张量"""
        # 转换为 RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 转换为 numpy 数组
        img_array = np.array(image).astype(np.float32) / 255.0
        
        # 转换为 PyTorch 张量 [1, C, H, W]
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
        
        # 移动到设备
        img_tensor = img_tensor.to(self.device)
        
        return img_tensor
    
    def _postprocess_image(self, tensor: torch.Tensor) -> Image.Image:
        """将模型输出张量转换为 PIL Image"""
        # 移动到 CPU 并转换为 numpy
        img_array = tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        
        # 裁剪到 [0, 1] 范围
        img_array = np.clip(img_array, 0, 1)
        
        # 转换为 [0, 255]
        img_array = (img_array * 255).astype(np.uint8)
        
        # 转换为 PIL Image
        return Image.fromarray(img_array)
    
    def _text_to_tensor(self, text: str) -> torch.Tensor:
        """将文本转换为模型输入张量"""
        # TODO: 实现文本到比特流的编码
        # 这里是示例实现
        bit_length = 100  # 假设固定长度
        bits = [0] * bit_length
        
        # 简单的 ASCII 编码
        for i, char in enumerate(text[:bit_length//8]):
            byte_val = ord(char)
            for j in range(8):
                if i*8 + j < bit_length:
                    bits[i*8 + j] = (byte_val >> (7-j)) & 1
        
        tensor = torch.FloatTensor(bits).unsqueeze(0).to(self.device)
        return tensor
    
    def _tensor_to_text(self, tensor: torch.Tensor) -> str:
        """将模型输出张量转换为文本"""
        # TODO: 实现比特流到文本的解码
        bits = (tensor.cpu().numpy() > 0.5).astype(int).flatten()
        
        text = ""
        for i in range(0, len(bits), 8):
            if i+8 <= len(bits):
                byte_val = 0
                for j in range(8):
                    byte_val = (byte_val << 1) | bits[i+j]
                if 32 <= byte_val <= 126:  # 可打印 ASCII
                    text += chr(byte_val)
        
        return text.strip()
    
    def _calculate_metrics(self, original: Image.Image, watermarked: Image.Image) -> Tuple[float, float]:
        """计算 PSNR 和 SSIM"""
        from skimage.metrics import peak_signal_noise_ratio as psnr
        from skimage.metrics import structural_similarity as ssim
        
        orig_array = np.array(original)
        water_array = np.array(watermarked)
        
        psnr_value = psnr(orig_array, water_array)
        ssim_value = ssim(orig_array, water_array, channel_axis=2)
        
        return psnr_value, ssim_value


# 全局模型实例（支持多种模型类型）
_model_instances: dict = {}


def get_model(model_type: str = "stegastamp") -> WatermarkModel:
    """
    获取全局模型实例（支持多模型切换）
    
    Args:
        model_type: 模型类型 ("stegastamp", "dwtdct", "treering")
    
    Returns:
        WatermarkModel 实例
    """
    global _model_instances
    
    # 如果该类型的模型已经加载，直接返回
    if model_type in _model_instances:
        return _model_instances[model_type]
    
    # 创建新的模型实例
    _model_instances[model_type] = WatermarkModel(model_type)
    
    # 尝试自动加载模型
    try:
        _model_instances[model_type].load_checkpoint(
            f"{model_type}_encoder.pth",
            f"{model_type}_decoder.pth"
        )
    except FileNotFoundError:
        logger.warning(f"未找到 {model_type} 预训练模型，使用 Mock 模式")
    
    return _model_instances[model_type]


def get_available_models() -> list[str]:
    """
    获取所有可用的模型类型
    
    Returns:
        模型类型列表
    """
    return ["dwtdct", "stablesig", "stegastamp", "treering"]


def get_model_info(model_type: str) -> dict:
    """
    获取模型信息
    
    Args:
        model_type: 模型类型
        
    Returns:
        模型信息字典
    """
    model_info = {
        "dwtdct": {
            "name": "DWT-DCT (invisible-watermark)",
            "year": "2021",
            "strength": {
                "traditional": "⭐⭐⭐⭐",
                "aigc": "⭐"
            },
            "description": "传统频域水印，对 JPEG/噪声等传统攻击有效",
            "requires_training": False,
            "provider": "开源社区"
        },
        "stablesig": {
            "name": "Stable Signature (Meta + INRIA)",
            "year": "2023",
            "strength": {
                "traditional": "⭐⭐⭐⭐⭐",
                "aigc": "⭐⭐⭐⭐⭐"
            },
            "description": "Meta开源，专门针对扩散模型，会自动下载预训练模型",
            "requires_training": False,
            "provider": "Meta + INRIA"
        },
        "stegastamp": {
            "name": "StegaStamp",
            "year": "2020",
            "strength": {
                "traditional": "⭐⭐⭐⭐⭐",
                "aigc": "⭐⭐⭐⭐"
            },
            "description": "深度学习水印，对 AIGC 攻击有较强抵抗力",
            "requires_training": True,
            "provider": "学术研究"
        },
        "treering": {
            "name": "Tree-Ring",
            "year": "2023",
            "strength": {
                "traditional": "⭐⭐⭐⭐",
                "aigc": "⭐⭐⭐⭐⭐"
            },
            "description": "专门针对扩散模型的水印，AIGC 抵抗力最强",
            "requires_training": True,
            "provider": "学术研究"
        }
    }
    
    return model_info.get(model_type, {
        "name": model_type,
        "description": "未知模型"
    })

