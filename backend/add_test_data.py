"""
添加测试数据到历史记录数据库
"""
import sys
from datetime import datetime, timedelta
from database import SessionLocal, WatermarkRecord, AttackRecord, ExtractionRecord
import random

def add_test_data():
    """添加测试数据"""
    db = SessionLocal()
    
    try:
        # 清空现有数据（可选）
        print("清理现有数据...")
        db.query(ExtractionRecord).delete()
        db.query(AttackRecord).delete()
        db.query(WatermarkRecord).delete()
        db.commit()
        print("✅ 已清空现有数据")
        
        # 创建测试用户
        test_username = "admin"
        
        # 模型类型列表
        model_types = ["dwtdct", "stegastamp", "treering", "stablesig"]
        model_names = {
            "dwtdct": "DWT-DCT",
            "stegastamp": "StegaStamp",
            "treering": "Tree-Ring",
            "stablesig": "Stable Signature"
        }
        
        # 攻击类型列表
        attack_types = ["jpeg", "noise", "blur", "crop", "rotate", "aigc_sim", "inpaint", "super_resolution"]
        attack_names = {
            "jpeg": "JPEG 压缩",
            "noise": "高斯噪声",
            "blur": "高斯模糊",
            "crop": "裁剪攻击",
            "rotate": "旋转攻击",
            "aigc_sim": "AIGC 重绘模拟",
            "inpaint": "图像修复",
            "super_resolution": "超分辨率重建"
        }
        
        # 水印文本列表
        watermark_texts = [
            "Thesis-2024",
            "Copyright-2024",
            "AI-Generated-Content",
            "Watermark-Test-001",
            "Research-Paper-2024",
            "Digital-Signature-001",
            "AIGC-Detection-2024",
            "StegaStamp-Demo"
        ]
        
        print("\n开始添加测试数据...")
        
        # 创建 8 条水印记录
        watermark_records = []
        base_time = datetime.utcnow() - timedelta(days=7)
        
        for i in range(8):
            model_type = random.choice(model_types)
            watermark_text = watermark_texts[i]
            balance = round(random.uniform(0.3, 0.9), 2)
            psnr = round(random.uniform(28.0, 42.0), 2)
            ssim = round(random.uniform(0.88, 0.98), 4)
            
            # 随机图片尺寸
            sizes = ["512×512", "1024×1024", "2048×2048", "512×768", "768×1024"]
            image_size = random.choice(sizes)
            image_format = random.choice(["JPG", "PNG", "WEBP"])
            
            watermark = WatermarkRecord(
                username=test_username,
                watermark_text=watermark_text,
                model_type=model_type,
                balance=balance,
                psnr=psnr,
                ssim=ssim,
                original_image_size=image_size,
                original_image_format=image_format,
                watermarked_image_base64=None,
                created_at=base_time + timedelta(hours=i*3)
            )
            
            db.add(watermark)
            db.flush()  # 获取 ID
            watermark_records.append(watermark)
            
            print(f"✅ 创建水印记录 {i+1}/8: {watermark_text} ({model_names[model_type]})")
        
        db.commit()
        print(f"\n✅ 已创建 {len(watermark_records)} 条水印记录")
        
        # 为每个水印记录创建 1-3 条攻击记录
        print("\n开始添加攻击记录...")
        attack_count = 0
        
        for watermark in watermark_records:
            num_attacks = random.randint(1, 3)
            
            for j in range(num_attacks):
                attack_type = random.choice(attack_types)
                intensity = round(random.uniform(0.2, 0.9), 2)
                
                attack = AttackRecord(
                    watermark_record_id=watermark.id,
                    attack_type=attack_type,
                    intensity=intensity,
                    attacked_image_base64=None,
                    created_at=watermark.created_at + timedelta(minutes=random.randint(5, 60))
                )
                
                db.add(attack)
                attack_count += 1
                
                print(f"  ⚔️  攻击记录: {attack_names[attack_type]} (强度: {intensity:.2f})")
        
        db.commit()
        print(f"\n✅ 已创建 {attack_count} 条攻击记录")
        
        # 为每个水印记录创建 1-2 条提取记录
        print("\n开始添加提取记录...")
        extraction_count = 0
        
        for watermark in watermark_records:
            num_extractions = random.randint(1, 2)
            
            # 获取该水印的攻击记录
            attacks = db.query(AttackRecord).filter(
                AttackRecord.watermark_record_id == watermark.id
            ).all()
            
            for j in range(num_extractions):
                # 随机决定是否从攻击后的图片提取
                attack_record = random.choice(attacks) if attacks and random.random() > 0.3 else None
                
                # 提取成功率：未攻击 90%，攻击后 60%
                is_success = random.random() > (0.4 if attack_record else 0.1)
                
                if is_success:
                    # 成功提取：文本相似，BER 低
                    extracted_text = watermark.watermark_text
                    if random.random() < 0.2:  # 20% 概率有小错误
                        extracted_text = watermark.watermark_text[:-1] + "X"
                    ber = round(random.uniform(0.0, 0.08), 4)
                    status = "Success"
                else:
                    # 失败提取：文本不同，BER 高
                    extracted_text = "提取失败或错误文本"
                    ber = round(random.uniform(0.5, 1.0), 4)
                    status = "Fail"
                
                extraction = ExtractionRecord(
                    watermark_record_id=watermark.id,
                    attack_record_id=attack_record.id if attack_record else None,
                    model_type=watermark.model_type,
                    extracted_text=extracted_text,
                    original_text=watermark.watermark_text,
                    ber=ber,
                    status=status,
                    created_at=(attack_record.created_at if attack_record else watermark.created_at) + timedelta(minutes=random.randint(1, 30))
                )
                
                db.add(extraction)
                extraction_count += 1
                
                status_icon = "✅" if status == "Success" else "❌"
                print(f"  {status_icon} 提取记录: BER={ber:.2%}, 状态={status}")
        
        db.commit()
        print(f"\n✅ 已创建 {extraction_count} 条提取记录")
        
        # 统计信息
        print("\n" + "="*50)
        print("📊 数据统计")
        print("="*50)
        
        total_watermarks = db.query(WatermarkRecord).count()
        total_attacks = db.query(AttackRecord).count()
        total_extractions = db.query(ExtractionRecord).count()
        success_extractions = db.query(ExtractionRecord).filter(
            ExtractionRecord.status == "Success"
        ).count()
        
        print(f"总水印记录: {total_watermarks}")
        print(f"总攻击记录: {total_attacks}")
        print(f"总提取记录: {total_extractions}")
        print(f"成功提取: {success_extractions} ({success_extractions/total_extractions*100:.1f}%)")
        
        # 模型使用统计
        print("\n模型使用统计:")
        for model_type in model_types:
            count = db.query(WatermarkRecord).filter(
                WatermarkRecord.model_type == model_type
            ).count()
            if count > 0:
                print(f"  {model_names[model_type]}: {count} 次")
        
        print("\n" + "="*50)
        print("✅ 测试数据添加完成！")
        print("="*50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 开始添加测试数据到历史记录数据库...")
    print("="*50)
    add_test_data()

