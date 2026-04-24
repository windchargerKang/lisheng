#!/bin/bash

# 渠道销售管理系统 - Docker 一键部署脚本
# 用法：./docker-deploy.sh {build|start|stop|restart|logs|status}

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目路径
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# 检测 Docker Compose 版本 (V2 使用 docker compose，V1 使用 docker-compose)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}错误：未找到 Docker Compose，请先安装${NC}"
    echo "参考：https://docs.docker.com/compose/install/"
    exit 1
fi

echo "========================================"
echo "  渠道销售管理系统 - Docker 部署"
echo "  使用命令：${DOCKER_COMPOSE}"
echo "========================================"

case "${1:-help}" in
    build)
        echo -e "${YELLOW}正在构建 Docker 镜像...${NC}"
        cd "${PROJECT_ROOT}"
        ${DOCKER_COMPOSE} build
        echo -e "${GREEN}构建完成！${NC}"
        ;;

    start)
        echo -e "${YELLOW}正在启动服务...${NC}"
        cd "${PROJECT_ROOT}"
        ${DOCKER_COMPOSE} up -d
        echo ""
        echo -e "${GREEN}服务启动完成！${NC}"
        echo ""
        echo "访问地址："
        echo "  - H5 前端（C 端）：http://localhost:3000/"
        echo "  - 运营管理端（B 端）：http://localhost:5173/"
        echo "  - 后端 API: http://localhost:8000/"
        echo "  - API 文档：http://localhost:8000/docs"
        ;;

    stop)
        echo -e "${YELLOW}正在停止服务...${NC}"
        cd "${PROJECT_ROOT}"
        ${DOCKER_COMPOSE} down
        echo -e "${GREEN}服务已停止${NC}"
        ;;

    restart)
        echo -e "${YELLOW}正在重启服务...${NC}"
        cd "${PROJECT_ROOT}"
        ${DOCKER_COMPOSE} restart
        echo -e "${GREEN}服务已重启${NC}"
        ;;

    logs)
        cd "${PROJECT_ROOT}"
        if [ -n "$2" ]; then
            ${DOCKER_COMPOSE} logs -f "$2"
        else
            ${DOCKER_COMPOSE} logs -f
        fi
        ;;

    status)
        echo -e "${YELLOW}服务状态：${NC}"
        cd "${PROJECT_ROOT}"
        ${DOCKER_COMPOSE} ps
        ;;

    clean)
        echo -e "${YELLOW}正在清理 Docker 资源...${NC}"
        cd "${PROJECT_ROOT}"
        ${DOCKER_COMPOSE} down -v
        ${DOCKER_COMPOSE} rm -f
        echo -e "${GREEN}清理完成${NC}"
        ;;

    *)
        echo "用法：$0 {build|start|stop|restart|logs|status|clean}"
        echo ""
        echo "命令说明："
        echo "  build   - 构建 Docker 镜像"
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  logs    - 查看日志 (可指定服务名：backend/h5/frontend)"
        echo "  status  - 查看服务状态"
        echo "  clean   - 清理所有 Docker 资源（包括数据卷）"
        echo ""
        exit 1
        ;;
esac
