"""
认证 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserInDB

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    # 查询用户
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成 token
    token = create_access_token(data={"sub": str(user.id), "username": user.username})

    return LoginResponse(
        token=token,
        user={"id": user.id, "username": user.username, "role_type": user.role_type}
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    if not credentials:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    user_id = int(payload.get("sub"))
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user


@router.get("/profile", response_model=UserInDB)
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInDB(
        id=current_user.id,
        username=current_user.username,
        role_type=current_user.role_type
    )
