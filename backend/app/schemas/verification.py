"""
核销管理 Schema
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VerificationRequest(BaseModel):
    """核销请求"""
    verification_code: str  # 12 位核销码


class VerificationResponse(BaseModel):
    """核销响应"""
    message: str
    order_id: int
    order_no: str
    service_fee: float
    agent_profit: float


class VerificationCodeResponse(BaseModel):
    """核销码查询响应"""
    code: str
    status: str
    order_id: int
    order_no: Optional[str]
    created_at: datetime
    used_at: Optional[datetime]
