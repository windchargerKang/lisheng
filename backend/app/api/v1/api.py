"""
API v1 路由注册
"""
from fastapi import APIRouter

from app.api.v1 import auth, regions, shops, agents, products, cart, orders, profit, referral, suppliers, purchase_orders, purchase_inbounds, supplier_portal, purchase_order_adjustments, roles, users, permissions, operation_logs, addresses, admin_orders, wallet, verification, store_applications


api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(regions.router, prefix="/regions", tags=["区域管理"])
api_router.include_router(shops.router, prefix="/shops", tags=["店铺管理"])
api_router.include_router(agents.router, prefix="/agents", tags=["区代管理"])
api_router.include_router(products.router, prefix="/products", tags=["产品管理"])
api_router.include_router(cart.router, prefix="/cart", tags=["购物车"])
api_router.include_router(orders.router, prefix="/orders", tags=["订单管理"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["地址管理"])
api_router.include_router(admin_orders.router, prefix="/admin/orders", tags=["运营管理 - 订单"])
api_router.include_router(profit.router, prefix="/profit", tags=["收益管理"])
api_router.include_router(referral.router, prefix="/referral", tags=["分享管理"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["供应商管理"])
api_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["采购订单管理"])
api_router.include_router(purchase_inbounds.router, prefix="/purchase-inbounds", tags=["采购入库管理"])
api_router.include_router(supplier_portal.router, prefix="/supplier-portal", tags=["供应商门户"])
api_router.include_router(purchase_order_adjustments.router, prefix="/purchase-orders", tags=["订单调整管理"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["权限管理"])
api_router.include_router(operation_logs.router, tags=["操作日志管理"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["钱包管理"])
api_router.include_router(verification.router, prefix="/verification", tags=["核销管理"])
api_router.include_router(store_applications.router, prefix="/store-applications", tags=["店铺/区代申请"])
