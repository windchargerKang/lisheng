"""
核销码管理服务
"""
import random
import string
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.verification_code import VerificationCode, VerificationCodeStatus
from app.models.order import Order


class VerificationCodeService:
    """核销码服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_code(self) -> str:
        """生成 12 位随机数字核销码"""
        # 生成 12 位纯数字
        return ''.join(random.choices(string.digits, k=12))

    async def generate_verification_code(self, order_id: int) -> VerificationCode:
        """
        为订单生成核销码
        如果生成冲突则重试（概率极低）
        """
        max_retries = 3

        for _ in range(max_retries):
            code = self._generate_code()

            # 检查是否已存在
            existing = await self.db.execute(
                select(VerificationCode).where(VerificationCode.code == code)
            )
            if existing.scalar_one_or_none() is None:
                # 不存在冲突，创建核销码
                verification_code = VerificationCode(
                    code=code,
                    order_id=order_id,
                    status=VerificationCodeStatus.UNUSED
                )
                self.db.add(verification_code)
                await self.db.flush()
                return verification_code

        # 重试 3 次后仍然冲突（极罕见），抛出异常
        raise ValueError("生成核销码失败：多次尝试均产生重复码")

    async def get_by_code(self, code: str) -> Optional[VerificationCode]:
        """根据核销码查询"""
        result = await self.db.execute(
            select(VerificationCode)
            .options(selectinload(VerificationCode.order))
            .where(VerificationCode.code == code)
        )
        return result.scalar_one_or_none()

    async def verify_and_use(
        self,
        code: str,
        verified_by: int
    ) -> Tuple[VerificationCode, Order]:
        """
        验证并使用核销码（核销操作）

        Args:
            code: 12 位核销码
            verified_by: 核销店铺 user_id

        Returns:
            (VerificationCode, Order) 元组

        Raises:
            ValueError: 核销码无效或已使用
        """
        # 获取核销码（带订单关联）
        result = await self.db.execute(
            select(VerificationCode)
            .options(selectinload(VerificationCode.order))
            .where(VerificationCode.code == code)
            .with_for_update()  # 行锁，防止并发核销
        )
        verification_code = result.scalar_one_or_none()

        if not verification_code:
            raise ValueError("核销码不存在")

        if verification_code.status == VerificationCodeStatus.USED:
            raise ValueError("核销码已被使用")

        # 更新核销码状态
        verification_code.status = VerificationCodeStatus.USED
        verification_code.used_at = verification_code.order.updated_at
        verification_code.verified_by = verified_by

        # 更新订单状态
        order = verification_code.order
        from app.models.order import OrderStatus
        order.status = OrderStatus.VERIFIED

        await self.db.flush()

        return verification_code, order
