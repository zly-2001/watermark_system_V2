"""
历史记录模块 - 查询、删除、统计水印历史数据
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from database import get_db, WatermarkRecord, AttackRecord, ExtractionRecord
from routers.auth import get_current_user

router = APIRouter()


# ==================== 响应模型 ====================

class WatermarkRecordResponse(BaseModel):
    """水印记录响应"""
    id: int
    username: str
    watermark_text: str
    model_type: str
    balance: float
    psnr: Optional[float]
    ssim: Optional[float]
    original_image_size: Optional[str]
    original_image_format: Optional[str]
    has_image: bool  # 是否有保存图片（不返回实际 Base64）
    created_at: datetime
    attack_count: int
    extraction_count: int
    
    class Config:
        from_attributes = True


class AttackRecordResponse(BaseModel):
    """攻击记录响应"""
    id: int
    watermark_record_id: int
    attack_type: str
    intensity: float
    has_image: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExtractionRecordResponse(BaseModel):
    """提取记录响应"""
    id: int
    watermark_record_id: int
    attack_record_id: Optional[int]
    model_type: str
    extracted_text: Optional[str]
    original_text: Optional[str]
    ber: Optional[float]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class HistoryStatsResponse(BaseModel):
    """历史统计响应"""
    total_watermarks: int
    total_attacks: int
    total_extractions: int
    success_extractions: int
    avg_psnr: Optional[float]
    avg_ssim: Optional[float]
    avg_ber: Optional[float]
    model_usage: dict  # 各模型使用次数
    recent_activity: List[dict]  # 最近活动


class WatermarkDetailResponse(BaseModel):
    """水印详情响应（包含关联的攻击和提取记录）"""
    watermark: WatermarkRecordResponse
    attacks: List[AttackRecordResponse]
    extractions: List[ExtractionRecordResponse]


# ==================== API 端点 ====================

@router.get("/history/watermarks", response_model=List[WatermarkRecordResponse])
async def get_watermark_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    model_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取水印嵌入历史记录
    
    Args:
        skip: 跳过记录数（分页）
        limit: 返回记录数
        model_type: 过滤模型类型
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    """
    query = db.query(WatermarkRecord).filter(
        WatermarkRecord.username == current_user.username
    )
    
    # 模型类型过滤
    if model_type:
        query = query.filter(WatermarkRecord.model_type == model_type)
    
    # 日期过滤
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(WatermarkRecord.created_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(WatermarkRecord.created_at < end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    
    # 排序和分页
    records = query.order_by(desc(WatermarkRecord.created_at)).offset(skip).limit(limit).all()
    
    # 转换为响应模型
    result = []
    for record in records:
        # 统计关联记录
        attack_count = db.query(func.count(AttackRecord.id)).filter(
            AttackRecord.watermark_record_id == record.id
        ).scalar() or 0
        
        extraction_count = db.query(func.count(ExtractionRecord.id)).filter(
            ExtractionRecord.watermark_record_id == record.id
        ).scalar() or 0
        
        result.append(WatermarkRecordResponse(
            id=record.id,
            username=record.username,
            watermark_text=record.watermark_text,
            model_type=record.model_type,
            balance=record.balance,
            psnr=record.psnr,
            ssim=record.ssim,
            original_image_size=record.original_image_size,
            original_image_format=record.original_image_format,
            has_image=bool(record.watermarked_image_base64),
            created_at=record.created_at,
            attack_count=attack_count,
            extraction_count=extraction_count
        ))
    
    return result


@router.get("/history/watermarks/{record_id}", response_model=WatermarkDetailResponse)
async def get_watermark_detail(
    record_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取水印记录详情（包含关联的攻击和提取记录）"""
    # 查询水印记录
    watermark = db.query(WatermarkRecord).filter(
        WatermarkRecord.id == record_id,
        WatermarkRecord.username == current_user.username
    ).first()
    
    if not watermark:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 查询关联的攻击记录
    attacks = db.query(AttackRecord).filter(
        AttackRecord.watermark_record_id == record_id
    ).order_by(desc(AttackRecord.created_at)).all()
    
    # 查询关联的提取记录
    extractions = db.query(ExtractionRecord).filter(
        ExtractionRecord.watermark_record_id == record_id
    ).order_by(desc(ExtractionRecord.created_at)).all()
    
    # 统计
    attack_count = len(attacks)
    extraction_count = len(extractions)
    
    return WatermarkDetailResponse(
        watermark=WatermarkRecordResponse(
            id=watermark.id,
            username=watermark.username,
            watermark_text=watermark.watermark_text,
            model_type=watermark.model_type,
            balance=watermark.balance,
            psnr=watermark.psnr,
            ssim=watermark.ssim,
            original_image_size=watermark.original_image_size,
            original_image_format=watermark.original_image_format,
            has_image=bool(watermark.watermarked_image_base64),
            created_at=watermark.created_at,
            attack_count=attack_count,
            extraction_count=extraction_count
        ),
        attacks=[AttackRecordResponse(
            id=a.id,
            watermark_record_id=a.watermark_record_id,
            attack_type=a.attack_type,
            intensity=a.intensity,
            has_image=bool(a.attacked_image_base64),
            created_at=a.created_at
        ) for a in attacks],
        extractions=[ExtractionRecordResponse(
            id=e.id,
            watermark_record_id=e.watermark_record_id,
            attack_record_id=e.attack_record_id,
            model_type=e.model_type,
            extracted_text=e.extracted_text,
            original_text=e.original_text,
            ber=e.ber,
            status=e.status,
            created_at=e.created_at
        ) for e in extractions]
    )


@router.delete("/history/watermarks/{record_id}")
async def delete_watermark_record(
    record_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除水印记录（级联删除关联的攻击和提取记录）"""
    watermark = db.query(WatermarkRecord).filter(
        WatermarkRecord.id == record_id,
        WatermarkRecord.username == current_user.username
    ).first()
    
    if not watermark:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(watermark)
    db.commit()
    
    return {"message": "记录已删除", "id": record_id}


@router.get("/history/stats", response_model=HistoryStatsResponse)
async def get_history_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取历史统计信息"""
    username = current_user.username
    
    # 统计总数
    total_watermarks = db.query(func.count(WatermarkRecord.id)).filter(
        WatermarkRecord.username == username
    ).scalar() or 0
    
    total_attacks = db.query(func.count(AttackRecord.id)).join(
        WatermarkRecord
    ).filter(WatermarkRecord.username == username).scalar() or 0
    
    total_extractions = db.query(func.count(ExtractionRecord.id)).join(
        WatermarkRecord
    ).filter(WatermarkRecord.username == username).scalar() or 0
    
    success_extractions = db.query(func.count(ExtractionRecord.id)).join(
        WatermarkRecord
    ).filter(
        WatermarkRecord.username == username,
        ExtractionRecord.status == "Success"
    ).scalar() or 0
    
    # 平均值
    avg_psnr = db.query(func.avg(WatermarkRecord.psnr)).filter(
        WatermarkRecord.username == username,
        WatermarkRecord.psnr.isnot(None)
    ).scalar()
    
    avg_ssim = db.query(func.avg(WatermarkRecord.ssim)).filter(
        WatermarkRecord.username == username,
        WatermarkRecord.ssim.isnot(None)
    ).scalar()
    
    avg_ber = db.query(func.avg(ExtractionRecord.ber)).join(
        WatermarkRecord
    ).filter(
        WatermarkRecord.username == username,
        ExtractionRecord.ber.isnot(None)
    ).scalar()
    
    # 模型使用统计
    model_usage = {}
    model_counts = db.query(
        WatermarkRecord.model_type,
        func.count(WatermarkRecord.id)
    ).filter(
        WatermarkRecord.username == username
    ).group_by(WatermarkRecord.model_type).all()
    
    for model_type, count in model_counts:
        model_usage[model_type] = count
    
    # 最近活动（最近 10 条水印记录）
    recent_watermarks = db.query(WatermarkRecord).filter(
        WatermarkRecord.username == username
    ).order_by(desc(WatermarkRecord.created_at)).limit(10).all()
    
    recent_activity = []
    for wm in recent_watermarks:
        recent_activity.append({
            "type": "watermark",
            "id": wm.id,
            "text": wm.watermark_text[:20] + "..." if len(wm.watermark_text) > 20 else wm.watermark_text,
            "model": wm.model_type,
            "created_at": wm.created_at.isoformat()
        })
    
    return HistoryStatsResponse(
        total_watermarks=total_watermarks,
        total_attacks=total_attacks,
        total_extractions=total_extractions,
        success_extractions=success_extractions,
        avg_psnr=float(avg_psnr) if avg_psnr else None,
        avg_ssim=float(avg_ssim) if avg_ssim else None,
        avg_ber=float(avg_ber) if avg_ber else None,
        model_usage=model_usage,
        recent_activity=recent_activity
    )


@router.delete("/history/watermarks")
async def delete_all_watermark_records(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除当前用户的所有水印记录"""
    deleted = db.query(WatermarkRecord).filter(
        WatermarkRecord.username == current_user.username
    ).delete()
    
    db.commit()
    
    return {"message": f"已删除 {deleted} 条记录"}

