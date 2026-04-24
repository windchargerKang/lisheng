"""
Supplier 数据模型 - 供应商管理
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Supplier(Base):
    """供应商模型"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # 供应商名称
    credit_code = Column(String(50), nullable=True)  # 统一社会信用代码
    contact_name = Column(String(50), nullable=True)  # 联系人
    contact_phone = Column(String(20), nullable=True)  # 联系电话
    address = Column(String(255), nullable=True)  # 地址
    bank_name = Column(String(100), nullable=True)  # 开户行
    bank_account = Column(String(50), nullable=True)  # 银行账号
    settlement_type = Column(String(20), nullable=False, default="cash")  # 结算方式：cash/credit
    status = Column(String(20), nullable=False, default="active")  # 状态：active/inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
