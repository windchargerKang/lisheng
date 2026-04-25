#!/bin/bash

# 远程部署脚本 - 构建前端并部署到远程服务器
# 用法：./deploy-remote.sh [h5|frontend|all]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
REMOTE_HOST="100.4.14.23"
REMOTE_USER="root"
REMOTE_PASS="passwd"
REMOTE_DIR="/opt/lisheng/lisheng-project"
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# 安装 sshpass（如未安装）
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}正在安装 sshpass...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}请先安装 Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
            exit 1
        fi
        brew install sshpass
    else
        sudo apt-get update && sudo apt-get install -y sshpass
    fi
fi

# SSH 命令封装
ssh_cmd() {
    sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE_USER@$REMOTE_HOST" "$1"
}

# SCP 上传封装
scp_upload() {
    sshpass -p "$REMOTE_PASS" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$1" "$REMOTE_USER@$REMOTE_HOST:$2"
}

echo "========================================"
echo "  远程部署脚本"
echo "  服务器：$REMOTE_USER@$REMOTE_HOST"
echo "  目标目录：$REMOTE_DIR"
echo "========================================"
echo ""

# 选择部署目标
DEPLOY_TARGET="${1:-all}"

case "$DEPLOY_TARGET" in
    h5)
        echo -e "${BLUE}[1/4] 正在构建 H5 前端...${NC}"
        cd "${PROJECT_ROOT}/h5"
        npm install
        npm run build

        echo -e "${BLUE}[2/4] 正在打包 H5 构建产物...${NC}"
        tar -czf /tmp/h5-dist.tar.gz -C dist .

        echo -e "${BLUE}[3/4] 正在上传 H5 到服务器...${NC}"
        scp_upload /tmp/h5-dist.tar.gz "${REMOTE_DIR}/h5-dist.tar.gz"

        echo -e "${BLUE}[4/4] 正在服务器部署 H5...${NC}"
        ssh_cmd "cd ${REMOTE_DIR}/h5 && rm -rf dist && tar -xzf ../h5-dist.tar.gz -C . && rm -f dist.tar.gz"

        rm -f /tmp/h5-dist.tar.gz
        echo -e "${GREEN}H5 部署完成！（volume 挂载自动生效）${NC}"
        echo "访问地址：http://$REMOTE_HOST:3000/"
        ;;

    frontend)
        echo -e "${BLUE}[1/4] 正在构建运营管理前端...${NC}"
        cd "${PROJECT_ROOT}/frontend"
        npm install
        npm run build

        echo -e "${BLUE}[2/4] 正在打包构建产物...${NC}"
        tar -czf /tmp/frontend-dist.tar.gz -C dist .

        echo -e "${BLUE}[3/4] 正在上传到服务器...${NC}"
        scp_upload /tmp/frontend-dist.tar.gz "${REMOTE_DIR}/frontend-dist.tar.gz"

        echo -e "${BLUE}[4/4] 正在服务器部署...${NC}"
        ssh_cmd "cd ${REMOTE_DIR}/frontend && rm -rf dist && tar -xzf ../frontend-dist.tar.gz -C . && rm -f frontend-dist.tar.gz"

        rm -f /tmp/frontend-dist.tar.gz
        echo -e "${GREEN}运营管理前端部署完成！（volume 挂载自动生效）${NC}"
        echo "访问地址：http://$REMOTE_HOST:5173/admin/"
        ;;

    all)
        # 构建 H5
        echo -e "${BLUE}[1/6] 正在构建 H5 前端...${NC}"
        cd "${PROJECT_ROOT}/h5"
        npm install
        npm run build

        # 打包 H5
        echo -e "${BLUE}[2/6] 正在打包 H5 构建产物...${NC}"
        tar -czf /tmp/h5-dist.tar.gz -C "${PROJECT_ROOT}/h5/dist" .

        # 构建运营管理前端
        echo -e "${BLUE}[3/6] 正在构建运营管理前端...${NC}"
        cd "${PROJECT_ROOT}/frontend"
        npm install
        npm run build

        # 打包运营管理前端
        echo -e "${BLUE}[4/6] 正在打包运营管理前端构建产物...${NC}"
        tar -czf /tmp/frontend-dist.tar.gz -C "${PROJECT_ROOT}/frontend/dist" .

        # 上传
        echo -e "${BLUE}[5/6] 正在上传到服务器...${NC}"
        scp_upload /tmp/h5-dist.tar.gz "${REMOTE_DIR}/h5-dist.tar.gz"
        scp_upload /tmp/frontend-dist.tar.gz "${REMOTE_DIR}/frontend-dist.tar.gz"

        # 部署
        echo -e "${BLUE}[6/6] 正在服务器部署...${NC}"
        ssh_cmd "cd ${REMOTE_DIR}/h5 && rm -rf dist && tar -xzf ../h5-dist.tar.gz -C . && rm -f h5-dist.tar.gz"
        ssh_cmd "cd ${REMOTE_DIR}/frontend && rm -rf dist && tar -xzf ../frontend-dist.tar.gz -C . && rm -f frontend-dist.tar.gz"

        # 重启容器（使 volume 挂载生效）
        echo -e "${BLUE}正在重启容器使挂载生效...${NC}"
        ssh_cmd "cd ${REMOTE_DIR} && docker-compose stop h5 frontend && docker rm lisheng-h5 lisheng-frontend && docker-compose up -d h5 frontend"

        rm -f /tmp/h5-dist.tar.gz /tmp/frontend-dist.tar.gz
        echo -e "${GREEN}全部部署完成！${NC}"
        echo ""
        echo "访问地址："
        echo "  - H5 前端（C 端）: http://$REMOTE_HOST:3000/"
        echo "  - 运营管理端（B 端）: http://$REMOTE_HOST:5173/admin/"
        ;;

    *)
        echo "用法：$0 [h5|frontend|all]"
        echo ""
        echo "  h5       - 只部署 H5 前端"
        echo "  frontend - 只部署运营管理前端"
        echo "  all      - 部署所有前端（默认）"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署成功完成！${NC}"
echo -e "${GREEN}========================================${NC}"
