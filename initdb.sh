#!/bin/bash

# 渠道销售管理系统 - 数据库初始化脚本
# 用法：./initdb.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"

echo "========================================"
echo "  渠道销售管理系统 - 数据库初始化"
echo "========================================"
echo ""

cd "${BACKEND_DIR}"

# 检查 Python 命令
if ! command -v python3 &> /dev/null; then
    printf "${RED}错误：未找到 python3 命令${NC}\n"
    exit 1
fi

# 设置 PYTHONPATH
export PYTHONPATH="${BACKEND_DIR}"

echo "【1/4】检查数据库文件..."
DB_FILES=$(ls -1 *.db 2>/dev/null || true)
if [ -n "${DB_FILES}" ]; then
    printf "${YELLOW}警告：发现现有数据库文件${NC}\n"
    echo "  已存在的数据库：${DB_FILES}"
    echo ""
    printf "是否删除现有数据库并重新初始化？[y/N]: "
    read -r response
    if [[ "${response}" =~ ^[Yy]$ ]]; then
        rm -f *.db
        printf "${GREEN}  ✓ 已删除现有数据库${NC}\n"
    else
        printf "${YELLOW}  跳过删除，继续初始化...${NC}\n"
    fi
fi

echo ""
echo "【2/4】初始化数据库表结构..."
python3 scripts/init_db.py

echo ""
echo "【3/4】初始化权限数据..."
python3 scripts/init_permissions.py

echo ""
echo "【4/4】初始化模拟数据..."
python3 scripts/init_mock_data.py

echo ""
echo "========================================"
printf "${GREEN}  数据库初始化完成！${NC}\n"
echo "========================================"
echo ""
echo "测试账号汇总："
echo "  ┌─────────────────────────────────────┐"
echo "  │ 用户名       │ 密码      │ 角色     │"
echo "  ├─────────────────────────────────────┤"
echo "  │ admin        │ admin123  │ 管理员   │"
echo "  │ operator01   │ test123   │ 运营     │"
echo "  │ agent01      │ test123   │ 区代     │"
echo "  │ shop01       │ test123   │ 店铺     │"
echo "  │ supplier01   │ test123   │ 供应商   │"
echo "  │ customer01   │ test123   │ 客户     │"
echo "  └─────────────────────────────────────┘"
echo ""
echo "访问地址："
echo "  - 运营端：http://localhost:5173/"
echo "  - H5 端：http://localhost:3000/"
echo "  - API 文档：http://localhost:8000/docs"
echo ""
