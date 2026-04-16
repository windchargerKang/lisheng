"""
API v1 路由注册
"""
from fastapi import APIRouter

from app.api.v1 import auth, regions, shops, agents, products


api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(regions.router, prefix="/regions", tags=["区域管理"])
api_router.include_router(shops.router, prefix="/shops", tags=["店铺管理"])
api_router.include_router(agents.router, prefix="/agents", tags=["区代管理"])
api_router.include_router(products.router, prefix="/products", tags=["产品管理"])
