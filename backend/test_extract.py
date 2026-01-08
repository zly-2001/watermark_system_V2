#!/usr/bin/env python3
"""
测试水印提取功能
用于调试 500 错误
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
import numpy as np

def test_invisible_watermark():
    """测试 invisible-watermark 库是否正常工作"""
    try:
        from imwatermark import WatermarkEncoder, WatermarkDecoder
        print("✅ invisible-watermark 库已导入")
        
        # 创建测试图像
        test_image = Image.new('RGB', (512, 512), color='white')
        bgr = np.array(test_image)[:, :, ::-1]
        
        # 测试编码器
        encoder = WatermarkEncoder()
        encoder.set_watermark('bytes', b'Test-2024')
        print("✅ 编码器创建成功")
        
        # 测试解码器
        try:
            decoder = WatermarkDecoder('bytes', 16)
            print("✅ 解码器创建成功（长度=16）")
        except Exception as e:
            print(f"⚠️ 解码器创建失败（长度=16）: {e}")
            try:
                decoder = WatermarkDecoder('bytes', 32)
                print("✅ 解码器创建成功（长度=32）")
            except Exception as e2:
                print(f"⚠️ 解码器创建失败（长度=32）: {e2}")
        
        return True
    except ImportError as e:
        print(f"❌ invisible-watermark 库未安装: {e}")
        print("安装方法: pip install invisible-watermark")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_watermark():
    """测试 SimpleWatermark 类"""
    try:
        from models.simple_watermark import get_simple_watermark
        print("\n测试 SimpleWatermark...")
        
        watermark = get_simple_watermark(method="dwtDct")
        if not watermark.is_available:
            print("❌ invisible-watermark 不可用")
            return False
        
        print("✅ SimpleWatermark 初始化成功")
        
        # 创建测试图像
        test_image = Image.new('RGB', (512, 512), color='white')
        
        # 测试编码
        try:
            watermarked, psnr, ssim = watermark.encode(test_image, "Test-2024", 0.5)
            print(f"✅ 编码成功: PSNR={psnr:.2f}, SSIM={ssim:.4f}")
        except Exception as e:
            print(f"❌ 编码失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试解码
        try:
            extracted, ber = watermark.decode(watermarked)
            print(f"✅ 解码成功: 文本='{extracted}', BER={ber:.4f}")
            return True
        except Exception as e:
            print(f"❌ 解码失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("水印提取功能测试")
    print("=" * 50)
    
    # 测试1：库导入
    if not test_invisible_watermark():
        sys.exit(1)
    
    # 测试2：SimpleWatermark
    if not test_simple_watermark():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！")
    print("=" * 50)

