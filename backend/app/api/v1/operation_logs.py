"""
操作日志 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.operation_log_service import OperationLogService

router = APIRouter(prefix="/operation-logs", tags=["操作日志管理"])


def get_log_service(db: AsyncSession = Depends(get_db)) -> OperationLogService:
    """获取操作日志服务实例"""
    return OperationLogService(db)


@router.get("")
async def list_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    log_service: OperationLogService = Depends(get_log_service),
):
    """获取操作日志列表"""
    result = await log_service.get_list(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "username": log.user.username if log.user else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in result["items"]
        ],
        "total": result["total"],
        "page": page,
        "page_size": page_size,
    }


@router.get("/export")
async def export_operation_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    log_service: OperationLogService = Depends(get_log_service),
):
    """导出操作日志为 CSV"""
    try:
        # 限制最大导出条数为 10000
        csv_content = await log_service.export_to_csv(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            max_rows=10000,
        )

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=operation_logs.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")
