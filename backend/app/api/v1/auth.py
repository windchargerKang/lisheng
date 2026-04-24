"""
认证 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import User, UserStatus
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.operation_log import OperationLog
from app.models.wallet import Wallet
from app.schemas.auth import LoginRequest, LoginResponse, UserInDB, UserRoleInfo, UserRoleListResponse, UserCreate, UserCreatePhone

from app.core.security import get_password_hash
from app.services.wallet_service import WalletService

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=LoginResponse)
async def register(request: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册（用户名方式）"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == request.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 获取客户角色（默认角色）
    customer_role = await db.execute(select(Role).where(Role.code == "customer"))
    customer_role = customer_role.scalar_one_or_none()

    # 创建新用户
    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        role_id=customer_role.id if customer_role else None  # 默认角色为客户
    )
    db.add(user)
    await db.flush()  # 获取 user.id 但不提交

    # 创建钱包
    wallet_service = WalletService(db)
    await wallet_service.create_wallet(user_id=user.id)

    await db.commit()
    await db.refresh(user)

    # 生成 token
    token = create_access_token(data={"sub": str(user.id), "username": user.username})

    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "role_id": user.role_id,
            "role_code": user.role.code if user.role else None
        }
    )


@router.post("/register-by-phone", response_model=LoginResponse)
async def register_by_phone(request: UserCreatePhone, db: AsyncSession = Depends(get_db)):
    """手机号注册"""
    # 验证请求
    try:
        request.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 检查手机号是否已存在
    result = await db.execute(select(User).where(User.phone_number == request.phone_number))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="该手机号已被注册")

    # 获取客户角色（默认角色）
    customer_role = await db.execute(select(Role).where(Role.code == "customer"))
    customer_role = customer_role.scalar_one_or_none()

    # 创建新用户（手机号同时作为 username）
    user = User(
        username=request.phone_number,  # 手机号作为用户名
        password_hash=get_password_hash(request.password),
        phone_number=request.phone_number,
        role_id=customer_role.id if customer_role else None  # 默认角色为客户
    )
    db.add(user)
    await db.flush()  # 获取 user.id 但不提交

    # 创建钱包
    wallet_service = WalletService(db)
    await wallet_service.create_wallet(user_id=user.id)

    await db.commit()
    await db.refresh(user)

    # 生成 token
    token = create_access_token(data={"sub": str(user.id), "username": user.username})

    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "phone_number": user.phone_number,
            "role_id": user.role_id,
            "role_code": user.role.code if user.role else None
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest, request: Request = None, db: AsyncSession = Depends(get_db)):
    """用户登录（支持用户名或手机号登录）"""
    # 自动识别手机号/用户名：11 位数字按手机号匹配，否则按用户名匹配
    identifier = login_request.username
    import re
    is_phone = bool(re.match(r"^1\d{10}$", identifier))

    # 查询用户（预加载 role）
    if is_phone:
        # 手机号登录：匹配 phone_number 字段，同时兼容 username 等于手机号的情况
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where((User.phone_number == identifier) | (User.username == identifier))
        )
    else:
        # 用户名登录
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.username == identifier)
        )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 检查用户状态
    if user.status == UserStatus.DISABLED:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")

    # 验证密码
    if not verify_password(login_request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 更新登录信息
    client_ip = request.client.host if request else None
    user.last_login_at = datetime.now()
    user.last_login_ip = client_ip
    await db.commit()

    # 生成 token
    token = create_access_token(data={"sub": str(user.id), "username": user.username})

    # 获取用户角色信息
    role_info = None
    if user.role_id and user.role:
        role_info = {"id": user.role.id, "code": user.role.code, "name": user.role.name}

    # 记录登录日志
    log = OperationLog(
        user_id=user.id,
        action="LOGIN",
        resource_type="USER",
        resource_id=user.id,
        ip_address=client_ip,
        details={"username": user.username},
    )
    db.add(log)
    await db.commit()

    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "role_id": user.role_id,
            "role_code": user.role.code if user.role else None,
            "role": role_info,
        }
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
        role_id=current_user.role_id,
        role_code=current_user.role.code if current_user.role else None
    )


@router.get("/roles", response_model=UserRoleListResponse)
async def get_user_roles(current_user: User = Depends(get_current_user)):
    """获取当前用户的角色列表"""
    # 根据用户的 role_code 生成角色列表
    role_mapping = {
        "customer": {"role_name": "客户", "description": "普通客户"},
        "shop": {"role_name": "店铺", "description": "店铺老板"},
        "agent": {"role_name": "区代", "description": "区域代理"},
        "admin": {"role_name": "管理员", "description": "系统管理员"},
        "operator": {"role_name": "运营人员", "description": "负责日常运营"},
        "supplier": {"role_name": "供应商", "description": "供应商"},
    }

    roles = []
    # 添加当前用户的主角色
    if current_user.role and current_user.role.code in role_mapping:
        role_code = current_user.role.code
        roles.append(UserRoleInfo(
            id=current_user.role.id,
            role_code=role_code,
            role_name=role_mapping[role_code]["role_name"],
            is_active=True
        ))

    # TODO: 查询用户实际拥有的其他角色（店铺、区代等）
    # 这里可以根据用户是否有关联的 shop 或 agent 记录来添加额外角色

    return UserRoleListResponse(
        roles=roles,
        current_role_id=roles[0].id if roles else None
    )


@router.post("/roles/switch")
async def switch_role(
    role_id: int,
    current_user: User = Depends(get_current_user)
):
    """切换用户角色"""
    # TODO: 实现角色切换逻辑
    # 1. 验证用户是否拥有该角色
    # 2. 更新用户的当前角色
    # 3. 返回新的角色信息

    # 临时实现：直接返回成功
    return {"message": "角色切换成功", "role_id": role_id}
