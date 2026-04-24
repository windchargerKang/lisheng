"""
操作日志服务
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import csv
from io import StringIO

from app.models.operation_log import OperationLog


class OperationLogService:
    """操作日志服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 10,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        """获取操作日志列表"""
        # 构建查询条件
        conditions = []
        if user_id:
            conditions.append(OperationLog.user_id == user_id)
        if action:
            conditions.append(OperationLog.action == action)
        if resource_type:
            conditions.append(OperationLog.resource_type == resource_type)
        if start_date:
            conditions.append(OperationLog.created_at >= start_date)
        if end_date:
            conditions.append(OperationLog.created_at <= end_date)

        # 查询总数
        count_query = select(func.count()).select_from(OperationLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 查询日志列表
        query = (
            select(OperationLog)
            .options(selectinload(OperationLog.user))
            .order_by(OperationLog.created_at.desc())
        )
        if conditions:
            query = query.where(and_(*conditions))

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return {
            "items": logs,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def create(
        self,
        user_id: int,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> OperationLog:
        """创建操作日志"""
        log = OperationLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def export_to_csv(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_rows: int = 10000,
    ) -> str:
        """导出操作日志为 CSV"""
        # 构建查询条件
        conditions = []
        if user_id:
            conditions.append(OperationLog.user_id == user_id)
        if action:
            conditions.append(OperationLog.action == action)
        if resource_type:
            conditions.append(OperationLog.resource_type == resource_type)
        if start_date:
            conditions.append(OperationLog.created_at >= start_date)
        if end_date:
            conditions.append(OperationLog.created_at <= end_date)

        # 查询日志（限制最大条数）
        query = (
            select(OperationLog)
            .options(selectinload(OperationLog.user))
            .order_by(OperationLog.created_at.desc())
            .limit(max_rows)
        )
        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        logs = result.scalars().all()

        # 生成 CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "用户", "操作", "资源类型", "资源 ID", "IP 地址", "时间"])

        for log in logs:
            writer.writerow([
                log.id,
                log.user.username if log.user else "Unknown",
                log.action,
                log.resource_type or "",
                log.resource_id or "",
                log.ip_address or "",
                log.created_at.isoformat() if log.created_at else "",
            ])

        return output.getvalue()
