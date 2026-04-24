"""
订单 Schema 定义
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderShipRequest(BaseModel):
    """发货请求"""
    courier_company: str
    courier_no: str


class OrderItemResponse(BaseModel):
    """订单明细响应"""
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class AdminOrderResponse(BaseModel):
    """管理端订单列表响应"""
    id: int
    order_no: str
    user_id: int
    total_amount: float
    status: str
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    courier_company: Optional[str] = None
    courier_no: Optional[str] = None
    shipped_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminOrderDetailResponse(BaseModel):
    """管理端订单详情响应"""
    id: int
    order_no: str
    user_id: int
    total_amount: float
    status: str
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    remark: Optional[str] = None
    courier_company: Optional[str] = None
    courier_no: Optional[str] = None
    shipped_at: Optional[datetime] = None
    shipper_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderShipResponse(BaseModel):
    """发货操作响应"""
    id: int
    order_no: str
    status: str
    courier_company: Optional[str] = None
    courier_no: Optional[str] = None
    shipped_at: Optional[datetime] = None

    class Config:
        from_attributes = True
