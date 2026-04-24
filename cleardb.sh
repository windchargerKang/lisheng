#!/bin/bash

# 渠道销售管理系统 - 清空数据库脚本
# 用法：./cleardb.sh

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
echo "  渠道销售管理系统 - 清空数据库"
echo "========================================"
echo ""

cd "${BACKEND_DIR}"

# 查找数据库文件
DB_FILES=$(ls -1 *.db 2>/dev/null || true)

if [ -z "${DB_FILES}" ]; then
    printf "${YELLOW}未发现数据库文件，无需清空${NC}\n"
    exit 0
fi

printf "${RED}⚠️  警告：此操作将删除以下数据库文件：${NC}\n"
echo "${DB_FILES}"
echo ""
printf "${RED}⚠️  此操作不可恢复，确定要继续吗？[y/N]: ${NC}"
read -r response

if [[ "${response}" =~ ^[Yy]$ ]]; then
    echo ""
    echo "正在删除数据库文件..."

    for db in ${DB_FILES}; do
        rm -f "${db}"
        printf "${GREEN}  ✓ 已删除：%s${NC}\n" "${db}"
    done

    echo ""
    printf "${GREEN}数据库已清空！${NC}\n"
    echo ""
    echo "如需重新初始化，请运行：./initdb.sh"
else
    printf "${YELLOW}已取消操作${NC}\n"
    exit 0
fi
