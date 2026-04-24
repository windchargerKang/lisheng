"""
钱包相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class WalletResponse(BaseModel):
    """钱包响应"""
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletTransactionResponse(BaseModel):
    """钱包流水响应"""
    id: int
    wallet_id: int
    transaction_type: str
    amount: Decimal
    balance_after: Decimal
    transaction_no: str
    status: str
    withdraw_method: Optional[str] = None
    withdraw_account: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RechargeRequest(BaseModel):
    """充值请求（管理员）"""
    user_id: int = Field(..., description="用户 ID")
    amount: Decimal = Field(..., description="充值金额", gt=0)
    remark: Optional[str] = Field(None, description="备注")


class WithdrawRequest(BaseModel):
    """提现申请请求（用户）"""
    amount: Decimal = Field(..., description="提现金额", gt=0)
    withdraw_method: str = Field(..., description="提现方式（银行卡/支付宝/微信）")
    withdraw_account: str = Field(..., description="提现账号")
    remark: Optional[str] = Field(None, description="备注")


class ApproveWithdrawRequest(BaseModel):
    """审核提现请求（管理员）"""
    approved: bool = Field(..., description="是否审核通过")


class WalletListResponse(BaseModel):
    """钱包列表响应"""
    items: List[WalletResponse]
    total: int
    page: int
    page_size: int


class WalletTransactionListResponse(BaseModel):
    """钱包流水列表响应"""
    items: List[WalletTransactionResponse]
    total: int
    page: int
    page_size: int
