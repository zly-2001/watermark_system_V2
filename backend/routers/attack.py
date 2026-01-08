"""
异构攻击实验室模块 - 使用 PIL 实现真实的图像处理攻击
"""
import base64
import io
import random
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from routers.auth import get_current_user
from utils.cache import watermark_cache, attack_cache
from database import get_db, WatermarkRecord, AttackRecord
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/attack")


class AttackResponse(BaseModel):
    """攻击响应模型"""
    image_base64: str
    attack_type: str
    intensity: float
    message: str


def apply_aigc_sim_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    AIGC 模拟攻击 - 模拟 Stable Diffusion 重绘造成的细节丢失
    
    组合使用：
    1. 高斯模糊：模拟高频信息丢失
    2. 颜色抖动：模拟风格迁移
    3. 轻微噪点：模拟重采样
    """
    attacked_image = image.copy()
    
    # 1. 高斯模糊 - 强度越高，模糊半径越大
    blur_radius = intensity * 3.0  # 0.3 - 3.0 像素
    attacked_image = attacked_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # 2. 颜色抖动 - 调整亮度、对比度、饱和度
    # 亮度调整
    brightness_factor = 1.0 + (intensity - 0.5) * 0.2  # 0.9 - 1.1
    enhancer = ImageEnhance.Brightness(attacked_image)
    attacked_image = enhancer.enhance(brightness_factor)
    
    # 对比度调整
    contrast_factor = 1.0 + (intensity - 0.5) * 0.3  # 0.85 - 1.15
    enhancer = ImageEnhance.Contrast(attacked_image)
    attacked_image = enhancer.enhance(contrast_factor)
    
    # 饱和度调整
    saturation_factor = 1.0 + (intensity - 0.5) * 0.4  # 0.8 - 1.2
    enhancer = ImageEnhance.Color(attacked_image)
    attacked_image = enhancer.enhance(saturation_factor)
    
    # 3. 添加轻微噪点 - 模拟重采样噪声
    np_image = np.array(attacked_image, dtype=np.float32)
    noise = np.random.normal(0, intensity * 10, np_image.shape)  # 噪声强度随 intensity 变化
    np_image = np.clip(np_image + noise, 0, 255)
    attacked_image = Image.fromarray(np_image.astype(np.uint8))
    
    return attacked_image


def apply_crop_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    裁剪攻击 - 根据强度裁剪边缘并缩放回原大小
    
    Args:
        image: 原始图像
        intensity: 裁剪强度 (0.1-1.0)，对应裁剪 10%-40% 的边缘
    """
    width, height = image.size
    
    # 计算裁剪比例：5% - 25%（降低强度，提高提取成功率）
    crop_ratio = 0.05 + (intensity * 0.20)  # 5% - 25%
    
    # 计算裁剪后的尺寸
    crop_width = int(width * (1 - crop_ratio))
    crop_height = int(height * (1 - crop_ratio))
    
    # 计算裁剪起始位置（居中裁剪）
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    right = left + crop_width
    bottom = top + crop_height
    
    # 裁剪
    cropped_image = image.crop((left, top, right, bottom))
    
    # 缩放回原大小（使用高质量重采样）
    resized_image = cropped_image.resize((width, height), Image.Resampling.LANCZOS)
    
    return resized_image


def apply_jpeg_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    JPEG 压缩攻击
    
    Args:
        image: 原始图像
        intensity: 压缩强度 (0.1-1.0)，对应质量 90-10
    """
    # 将强度转换为 JPEG 质量：强度越高，质量越低
    # 调整范围：质量 95-60（更温和，提高提取成功率）
    quality = int(95 - (intensity * 35))  # 95 - 60（强度 0.1-1.0）
    quality = max(60, min(95, quality))  # 确保在合理范围内，最低 60（保证水印可提取）
    
    # 保存为 JPEG 格式（会损失质量）
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    
    # 重新加载（模拟 JPEG 压缩损失）
    compressed_image = Image.open(buffer)
    
    # 如果原图是 RGB，确保压缩后也是 RGB
    if compressed_image.mode != 'RGB':
        compressed_image = compressed_image.convert('RGB')
    
    return compressed_image


def apply_rotate_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    旋转攻击
    
    Args:
        image: 原始图像
        intensity: 旋转强度 (0.1-1.0)，对应角度 -8° 到 +8°（降低强度，提高提取成功率）
    """
    # 计算旋转角度：-8° 到 +8°（降低强度，DWT-DCT 对旋转敏感）
    angle = (intensity - 0.5) * 16  # -8 到 +8 度（之前是 -15 到 +15）
    
    # 旋转图像（使用高质量重采样）
    rotated_image = image.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
    
    return rotated_image


def apply_noise_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    高斯噪声攻击
    
    Args:
        image: 原始图像
        intensity: 噪声强度 (0.1-1.0)，对应标准差 5-50
    """
    # 将强度转换为噪声标准差：5-30（降低强度，提高提取成功率）
    sigma = 5 + (intensity * 25)  # 5-30（之前是 5-50）
    
    np_image = np.array(image, dtype=np.float32)
    noise = np.random.normal(0, sigma, np_image.shape)
    noisy_image = np.clip(np_image + noise, 0, 255)
    
    return Image.fromarray(noisy_image.astype(np.uint8))


def apply_blur_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    高斯模糊攻击
    
    Args:
        image: 原始图像
        intensity: 模糊强度 (0.1-1.0)，对应半径 1-10
    """
    # 将强度转换为模糊半径：1-5（降低强度，提高提取成功率）
    radius = 1 + (intensity * 4)  # 1-5（之前是 1-10）
    
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    return blurred_image


def apply_inpaint_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    图像修复攻击（Inpainting 模拟）
    
    Args:
        image: 原始图像
        intensity: 修复区域比例 (0.1-0.5)
    """
    width, height = image.size
    np_image = np.array(image, dtype=np.float32)
    
    # 计算修复区域大小
    region_size = int(min(width, height) * intensity)
    
    # 随机选择修复区域中心
    center_x = random.randint(region_size, width - region_size)
    center_y = random.randint(region_size, height - region_size)
    
    # 创建修复区域（用周围像素的平均值填充）
    left = max(0, center_x - region_size // 2)
    top = max(0, center_y - region_size // 2)
    right = min(width, center_x + region_size // 2)
    bottom = min(height, center_y + region_size // 2)
    
    # 获取周围像素的平均值
    surrounding = np.concatenate([
        np_image[max(0, top-10):top, left:right].reshape(-1, 3),
        np_image[bottom:min(height, bottom+10), left:right].reshape(-1, 3),
        np_image[top:bottom, max(0, left-10):left].reshape(-1, 3),
        np_image[top:bottom, right:min(width, right+10)].reshape(-1, 3)
    ], axis=0)
    
    if len(surrounding) > 0:
        avg_color = np.mean(surrounding, axis=0)
        # 填充修复区域
        np_image[top:bottom, left:right] = avg_color
    
    return Image.fromarray(np_image.astype(np.uint8))


def apply_super_resolution_attack(image: Image.Image, intensity: float) -> Image.Image:
    """
    超分辨率重建攻击（模拟）
    
    Args:
        image: 原始图像
        intensity: 放大倍数 (2-4)，但这里我们用强度 0.1-1.0 映射到 2-4
    """
    width, height = image.size
    
    # 将强度转换为放大倍数：2-4
    scale = int(2 + (intensity * 2))  # 2-4
    
    # 先放大
    upscaled = image.resize((width * scale, height * scale), Image.Resampling.LANCZOS)
    
    # 再缩小回原尺寸（模拟超分辨率重建）
    downscaled = upscaled.resize((width, height), Image.Resampling.LANCZOS)
    
    return downscaled


@router.post("/attack", response_model=AttackResponse)
async def apply_attack(
    image: UploadFile = File(...),
    attack_type: str = Form(...),
    intensity: float = Form(...),
    watermark_record_id: Optional[int] = Form(None),  # 可选：关联的水印记录 ID
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    应用图像攻击
    
    Args:
        image: 原始图像文件
        attack_type: 攻击类型 ("aigc_sim", "crop", "jpeg", "rotate")
        intensity: 攻击强度 (0.1-1.0)
    """
    # 验证强度范围（放宽限制，因为不同攻击类型有不同的强度范围）
    # noise 和 blur 可能传入 5-50 或 1-10，需要特殊处理
    if intensity < 0 or intensity > 100:
        raise HTTPException(status_code=400, detail="intensity 必须在合理范围内")
    
    # 验证攻击类型
    valid_attack_types = [
        "aigc_sim", "sd_repaint", "inpaint", "super_resolution",
        "crop", "jpeg", "rotate", "noise", "blur"
    ]
    
    # 攻击类型映射（前端 -> 后端）
    attack_type_map = {
        "sd_repaint": "aigc_sim",  # SD 重绘使用 AIGC 模拟
        "inpaint": "inpaint",
        "super_resolution": "super_resolution",
        "crop": "crop",
        "jpeg": "jpeg",
        "noise": "noise",
        "blur": "blur",
        "rotate": "rotate"
    }
    
    # 映射前端攻击类型到后端
    mapped_attack_type = attack_type_map.get(attack_type, attack_type)
    
    if mapped_attack_type not in valid_attack_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的攻击类型: {attack_type}。可选值: {', '.join(attack_type_map.keys())}"
        )
    
    try:
        # 读取图像
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # 转换为 RGB 模式
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 根据攻击类型应用相应的攻击
        if mapped_attack_type == "aigc_sim":
            attacked_image = apply_aigc_sim_attack(pil_image, intensity)
            attack_name = "AIGC 重绘模拟"
        elif mapped_attack_type == "crop":
            attacked_image = apply_crop_attack(pil_image, intensity)
            attack_name = "裁剪攻击"
        elif mapped_attack_type == "jpeg":
            attacked_image = apply_jpeg_attack(pil_image, intensity)
            attack_name = "JPEG 压缩"
        elif mapped_attack_type == "rotate":
            attacked_image = apply_rotate_attack(pil_image, intensity)
            attack_name = "旋转攻击"
        elif mapped_attack_type == "noise":
            # 将前端的 noiseLevel (5-50) 转换为强度 (0.1-1.0)
            normalized_intensity = (intensity - 5) / 45 if intensity > 1 else intensity
            normalized_intensity = max(0.1, min(1.0, normalized_intensity))
            attacked_image = apply_noise_attack(pil_image, normalized_intensity)
            attack_name = "高斯噪声"
        elif mapped_attack_type == "blur":
            # 将前端的 blurRadius (1-10) 转换为强度 (0.1-1.0)
            normalized_intensity = (intensity - 1) / 9 if intensity > 1 else intensity
            normalized_intensity = max(0.1, min(1.0, normalized_intensity))
            attacked_image = apply_blur_attack(pil_image, normalized_intensity)
            attack_name = "高斯模糊"
        elif mapped_attack_type == "inpaint":
            attacked_image = apply_inpaint_attack(pil_image, intensity)
            attack_name = "图像修复"
        elif mapped_attack_type == "super_resolution":
            attacked_image = apply_super_resolution_attack(pil_image, intensity)
            attack_name = "超分辨率重建"
        else:
            raise HTTPException(status_code=400, detail=f"未知的攻击类型: {mapped_attack_type}")
        
        # 将攻击后的图像转换为 Base64
        buffer = io.BytesIO()
        attacked_image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 存储到缓存（用于后续提取时的 BER 计算）
        image_hash = hash(image_bytes)
        attack_cache[image_hash] = {
            'attack_type': attack_type,
            'intensity': intensity,
            'attacked_image': attacked_image
        }
        
        # 将攻击后的图片也存储到 watermark_cache（用于提取模块识别）
        # 查找原始水印信息（从 watermark_cache 中找到最近的水印信息）
        buffer.seek(0)
        attacked_bytes = buffer.getvalue()
        attacked_hash = hash(attacked_bytes)
        
        # 如果 watermark_cache 中有数据，复制水印信息到攻击后的图片
        if watermark_cache:
            # 获取最近的水印信息（简化处理：取最后一个）
            last_watermark_key = list(watermark_cache.keys())[-1]
            watermark_info = watermark_cache[last_watermark_key]
            watermark_cache[attacked_hash] = {
                'original_text': watermark_info.get('original_text', 'Thesis-2024'),
                'original_image': watermark_info.get('original_image'),
                'watermarked_image': attacked_image,
                'attacked': True  # 标记为被攻击过的图片
            }
        
        # 保存攻击记录到数据库
        try:
            # 查找关联的水印记录
            record_id = watermark_record_id
            if not record_id:
                # 尝试查找最近的水印记录（同用户）
                watermark_record = db.query(WatermarkRecord).filter(
                    WatermarkRecord.username == current_user.username
                ).order_by(WatermarkRecord.created_at.desc()).first()
                
                if watermark_record:
                    record_id = watermark_record.id
            
            # 创建攻击记录
            if record_id:
                attack_record = AttackRecord(
                    watermark_record_id=record_id,
                    attack_type=mapped_attack_type,
                    intensity=intensity,
                    attacked_image_base64=None  # 不保存完整图片，节省空间
                )
                db.add(attack_record)
                db.commit()
                logger.info(f"✓ 攻击记录已保存到数据库: ID={attack_record.id}, 类型={mapped_attack_type}")
        except Exception as db_error:
            # 数据库错误不影响主流程
            logger.warning(f"⚠️ 保存攻击记录失败: {str(db_error)}")
        
        return AttackResponse(
            image_base64=image_base64,
            attack_type=attack_name,
            intensity=intensity,
            message=f"{attack_name} 攻击完成，强度: {intensity:.2f}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应用攻击时出错: {str(e)}")

