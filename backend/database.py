"""
数据库配置和模型定义
使用 SQLAlchemy + SQLite
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "watermark_history.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要这个参数
    echo=False  # 设置为 True 可以看到 SQL 日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


class WatermarkRecord(Base):
    """水印嵌入记录"""
    __tablename__ = "watermark_records"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, nullable=False)  # 用户标识
    watermark_text = Column(String(500), nullable=False)  # 水印文本
    model_type = Column(String(50), nullable=False)  # 模型类型: dwtdct, stegastamp, etc.
    balance = Column(Float, nullable=False)  # 平衡参数
    psnr = Column(Float)  # 峰值信噪比
    ssim = Column(Float)  # 结构相似性
    original_image_size = Column(String(50))  # 原始图片尺寸 (width×height)
    original_image_format = Column(String(20))  # 原始图片格式
    watermarked_image_base64 = Column(Text)  # 水印图片 Base64（可选，可能很大）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关联的攻击记录
    attacks = relationship("AttackRecord", back_populates="watermark_record", cascade="all, delete-orphan")
    # 关联的提取记录
    extractions = relationship("ExtractionRecord", back_populates="watermark_record", cascade="all, delete-orphan")


class AttackRecord(Base):
    """攻击记录"""
    __tablename__ = "attack_records"
    
    id = Column(Integer, primary_key=True, index=True)
    watermark_record_id = Column(Integer, ForeignKey("watermark_records.id"), nullable=False)
    attack_type = Column(String(50), nullable=False)  # 攻击类型: jpeg, noise, blur, etc.
    intensity = Column(Float, nullable=False)  # 攻击强度
    attacked_image_base64 = Column(Text)  # 攻击后图片 Base64（可选）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关联的水印记录
    watermark_record = relationship("WatermarkRecord", back_populates="attacks")


class ExtractionRecord(Base):
    """水印提取记录"""
    __tablename__ = "extraction_records"
    
    id = Column(Integer, primary_key=True, index=True)
    watermark_record_id = Column(Integer, ForeignKey("watermark_records.id"), nullable=False)
    attack_record_id = Column(Integer, ForeignKey("attack_records.id"), nullable=True)  # 如果是从攻击后图片提取
    model_type = Column(String(50), nullable=False)  # 使用的提取模型
    extracted_text = Column(String(500))  # 提取的文本
    original_text = Column(String(500))  # 原始文本（用于对比）
    ber = Column(Float)  # 误码率 (Bit Error Rate)
    status = Column(String(20), nullable=False)  # Success 或 Fail
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关联的水印记录
    watermark_record = relationship("WatermarkRecord", back_populates="extractions")
    # 关联的攻击记录（可选）
    attack_record = relationship("AttackRecord")


def init_db():
    """初始化数据库（创建表）"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库初始化完成: {DB_PATH}")


def get_db():
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 初始化数据库（如果不存在）
if not os.path.exists(DB_PATH):
    init_db()

