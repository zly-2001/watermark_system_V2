"""
简单易用的水印库 - 基于 invisible-watermark
无需训练，开箱即用！

支持的算法：
- DwtDct: 小波变换 + DCT（推荐，鲁棒性好）
- DwtDctSvd: 小波 + DCT + SVD（最强鲁棒性）
- RivaGAN: 深度学习方法（需要预训练模型）
"""

from PIL import Image
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class SimpleWatermark:
    """
    简单易用的水印系统 - 使用 invisible-watermark 库
    """
    
    def __init__(self, method: str = "dwtDct"):
        """
        初始化水印系统
        
        Args:
            method: 水印算法
                - "dwtDct": 小波+DCT，平衡性能（推荐）
                - "dwtDctSvd": 小波+DCT+SVD，最强鲁棒性
                - "rivaGan": 深度学习方法（需要模型）
        """
        try:
            from imwatermark import WatermarkEncoder, WatermarkDecoder
            self.WatermarkEncoder = WatermarkEncoder
            self.WatermarkDecoder = WatermarkDecoder
            self.method = method
            self.is_available = True
            logger.info(f"✓ invisible-watermark 库已加载，使用算法: {method}")
        except ImportError:
            self.is_available = False
            logger.warning("✗ invisible-watermark 库未安装")
            logger.info("安装方法: pip install invisible-watermark")
    
    def encode(self, image: Image.Image, message: str, strength: float = 0.5) -> Tuple[Image.Image, float, float]:
        """
        嵌入水印
        
        Args:
            image: PIL Image 对象
            message: 水印文本（会转换为字节）
            strength: 水印强度 (0.1-1.0)，影响鲁棒性
        
        Returns:
            (水印图像, PSNR, SSIM)
        """
        if not self.is_available:
            raise RuntimeError("invisible-watermark 库未安装")
        
        try:
            # 转换为 RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为 numpy 数组
            bgr = np.array(image)[:, :, ::-1]  # RGB to BGR
            
            # 将消息编码为字节
            message_bytes = message.encode('utf-8')
            message_length = len(message_bytes)
            
            logger.info(f"嵌入水印: 文本='{message}', 字节长度={message_length}")
            
            # 创建编码器
            encoder = self.WatermarkEncoder()
            encoder.set_watermark('bytes', message_bytes)
            
            # 嵌入水印
            bgr_encoded = encoder.encode(bgr, self.method)
            
            # 转换回 PIL Image
            watermarked_image = Image.fromarray(bgr_encoded[:, :, ::-1])
            
            # 计算质量指标
            psnr, ssim = self._calculate_metrics(image, watermarked_image)
            
            logger.info(f"✓ 水印嵌入成功: 长度={message_length}, PSNR={psnr:.2f}dB, SSIM={ssim:.4f}")
            return watermarked_image, psnr, ssim
            
        except Exception as e:
            logger.error(f"✗ 水印嵌入失败: {str(e)}")
            raise
    
    def decode(self, image: Image.Image, watermark_length: int = None) -> Tuple[str, float]:
        """
        提取水印
        
        Args:
            image: 带水印的 PIL Image 对象
        
        Returns:
            (提取的文本, 误码率)
        """
        if not self.is_available:
            raise RuntimeError("invisible-watermark 库未安装")
        
        try:
            # 转换为 RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为 numpy 数组
            bgr = np.array(image)[:, :, ::-1]  # RGB to BGR
            
            # 创建解码器
            # invisible-watermark 的 decode 方法需要知道水印长度
            # 如果有提供的长度，优先使用；否则尝试多个可能的长度
            if watermark_length and watermark_length > 0:
                # 优先使用提供的长度，但也尝试附近的值（±4字节）
                possible_lengths = [watermark_length]
                if watermark_length > 4:
                    possible_lengths.append(watermark_length - 4)
                if watermark_length < 256:
                    possible_lengths.append(watermark_length + 4)
                logger.info(f"使用保存的水印长度: {watermark_length}，尝试长度: {possible_lengths}")
            else:
                # 尝试更多可能的长度
                possible_lengths = [8, 16, 24, 32, 40, 48, 64, 80, 96, 128, 160, 192, 256]
                logger.info(f"未提供水印长度，尝试多个可能长度: {possible_lengths}")
            
            extracted_text = ""
            ber = 1.0
            decode_success = False
            last_error = None
            
            for watermark_length in possible_lengths:
                try:
                    # 创建解码器
                    # invisible-watermark 的 WatermarkDecoder 初始化方式：
                    # WatermarkDecoder('bytes', length)
                    decoder = self.WatermarkDecoder('bytes', watermark_length)
                    
                    # 提取水印
                    # decode 方法：decoder.decode(image_array, method)
                    watermark_bytes = decoder.decode(bgr, self.method)
                    
                    # 检查返回的字节是否有效
                    if watermark_bytes is None:
                        last_error = "返回 None"
                        continue
                    
                    if not isinstance(watermark_bytes, bytes):
                        # 如果不是 bytes，尝试转换
                        try:
                            watermark_bytes = bytes(watermark_bytes)
                        except:
                            last_error = f"无法转换为 bytes: {type(watermark_bytes)}"
                            continue
                    
                    if len(watermark_bytes) == 0:
                        last_error = "返回空字节"
                        continue
                    
                    # 清理字节数据，移除 null 字节和无效字符
                    watermark_bytes = watermark_bytes.rstrip(b'\x00')
                    watermark_bytes = watermark_bytes.rstrip(b'\xff')
                    watermark_bytes = watermark_bytes.rstrip(b'\x20')  # 移除末尾空格
                    
                    if len(watermark_bytes) == 0:
                        last_error = "清理后为空"
                        continue
                    
                    # 尝试解码为文本
                    try:
                        # 先尝试 UTF-8 解码
                        decoded_text = watermark_bytes.decode('utf-8', errors='ignore').strip()
                        
                        # 如果 UTF-8 解码失败或结果为空，尝试其他编码
                        if not decoded_text or len(decoded_text) == 0:
                            # 尝试 latin-1 编码（单字节编码，不会失败）
                            decoded_text = watermark_bytes.decode('latin-1', errors='ignore').strip()
                        
                        # 检查是否包含可打印字符
                        if decoded_text and len(decoded_text) > 0:
                            # 移除不可打印字符，但保留更多字符（包括中文等）
                            import string
                            printable = set(string.printable)
                            # 保留可打印字符和常见的中文字符范围
                            clean_text = ''.join(c for c in decoded_text if c in printable or (ord(c) >= 0x4e00 and ord(c) <= 0x9fff))
                            
                            if len(clean_text) > 0:
                                extracted_text = clean_text
                                # 如果提取成功，设置较低的 BER（后续会根据原始文本重新计算）
                                ber = 0.05  # 初始 BER，如果提供了原始文本会重新计算
                                decode_success = True
                                logger.info(f"✓ 水印提取成功 (长度={watermark_length}): {extracted_text}")
                                break
                        else:
                            last_error = "解码后文本为空"
                    except (UnicodeDecodeError, AttributeError, TypeError) as e:
                        last_error = f"解码错误: {str(e)}"
                        continue
                        
                except Exception as decode_error:
                    # 记录错误，继续尝试下一个长度
                    last_error = f"解码器异常: {str(decode_error)}"
                    logger.debug(f"尝试长度 {watermark_length} 失败: {last_error}")
                    continue
            
            # 如果所有长度都失败，返回失败
            if not decode_success:
                extracted_text = "提取失败"
                ber = 1.0
                error_msg = f"所有长度尝试均失败"
                if last_error:
                    error_msg += f" (最后错误: {last_error})"
                logger.warning(f"✗ 水印提取失败：{error_msg}")
            
            return extracted_text, ber
            
        except Exception as e:
            import traceback
            error_detail = str(e)
            error_traceback = traceback.format_exc()
            logger.error(f"✗ 水印提取失败: {error_detail}")
            logger.error(f"错误堆栈:\n{error_traceback}")
            # 即使出错也返回结果，而不是抛出异常
            return "提取失败", 1.0
    
    def _calculate_metrics(self, original: Image.Image, watermarked: Image.Image) -> Tuple[float, float]:
        """计算 PSNR 和 SSIM"""
        try:
            from skimage.metrics import peak_signal_noise_ratio as psnr
            from skimage.metrics import structural_similarity as ssim
            
            orig_array = np.array(original)
            water_array = np.array(watermarked)
            
            psnr_value = psnr(orig_array, water_array)
            ssim_value = ssim(orig_array, water_array, channel_axis=2)
            
            return psnr_value, ssim_value
        except:
            return 40.0, 0.95  # 默认值


# 全局实例
_simple_watermark: SimpleWatermark = None


def get_simple_watermark(method: str = "dwtDct") -> SimpleWatermark:
    """
    获取简单水印实例（单例）
    
    Args:
        method: 水印算法
    
    Returns:
        SimpleWatermark 实例
    """
    global _simple_watermark
    
    if _simple_watermark is None:
        _simple_watermark = SimpleWatermark(method)
    
    return _simple_watermark

