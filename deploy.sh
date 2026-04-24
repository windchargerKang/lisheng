#!/bin/bash

# 渠道销售管理系统 - 一键部署脚本
# 用法：./deploy.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
H5_DIR="${PROJECT_ROOT}/h5"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

# 日志文件
LOG_DIR="${PROJECT_ROOT}/logs"
BACKEND_LOG="${LOG_DIR}/backend.log"
H5_LOG="${LOG_DIR}/h5.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"

# PID 文件
PID_DIR="${PROJECT_ROOT}/.pids"
BACKEND_PID="${PID_DIR}/backend.pid"
H5_PID="${PID_DIR}/h5.pid"
FRONTEND_PID="${PID_DIR}/frontend.pid"

# 端口配置
BACKEND_PORT=8000
H5_PORT=3000
FRONTEND_PORT=5173

echo "========================================"
echo "  渠道销售管理系统 - 一键部署脚本"
echo "========================================"
echo ""

# 创建必要目录
mkdir -p "${LOG_DIR}"
mkdir -p "${PID_DIR}"

# 函数：检查端口是否被占用
check_port() {
    local port=$1
    lsof -ti:${port} > /dev/null 2>&1
    return $?
}

# 函数：获取占用端口的 PID
get_pid_by_port() {
    local port=$1
    lsof -ti:${port} 2>/dev/null
}

# 函数：检查进程是否存在
check_process() {
    local pid_file=$1
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if ps -p ${pid} > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 函数：停止服务
stop_service() {
    local name=$1
    local port=$2
    local pid_file=$3

    printf "${YELLOW}正在停止 %s...${NC}\n" "${name}"

    # 先尝试通过 PID 文件停止
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if ps -p ${pid} > /dev/null 2>&1; then
            kill ${pid} 2>/dev/null
            sleep 1
            if ps -p ${pid} > /dev/null 2>&1; then
                kill -9 ${pid} 2>/dev/null
            fi
            echo "  ✓ 通过 PID 停止成功 (PID: ${pid})"
        else
            echo "  - 进程已不存在 (PID 文件残留)"
        fi
        rm -f "${pid_file}"
    fi

    # 如果端口仍被占用，强制释放
    if check_port ${port}; then
        local force_pid=$(get_pid_by_port ${port})
        if [ -n "${force_pid}" ]; then
            kill -9 ${force_pid} 2>/dev/null
            echo "  ✓ 强制释放端口 ${port} (PID: ${force_pid})"
        fi
    fi

    printf "${GREEN}  %s 已停止${NC}\n" "${name}"
}

# 函数：启动服务
start_service() {
    local name=$1
    local cmd=$2
    local port=$3
    local pid_file=$4
    local log_file=$5

    printf "${YELLOW}正在启动 %s...${NC}\n" "${name}"

    # 检查端口是否可用
    if check_port ${port}; then
        printf "${RED}  错误：端口 %s 已被占用${NC}\n" "${port}"
        echo "  请运行：./deploy.sh stop"
        return 1
    fi

    # 启动进程
    cd "$(dirname "${cmd}")"
    nohup $(basename "${cmd}") > "${log_file}" 2>&1 &
    local pid=$!
    echo ${pid} > "${pid_file}"

    # 等待服务启动
    sleep 3

    # 检查是否启动成功
    if ps -p ${pid} > /dev/null 2>&1; then
        printf "${GREEN}  ✓ %s 启动成功 (PID: %s)${NC}\n" "${name}" "${pid}"
        echo "  访问地址：http://localhost:${port}"
        echo "  日志文件：${log_file}"
        return 0
    else
        printf "${RED}  ✗ %s 启动失败${NC}\n" "${name}"
        echo "  查看日志：tail -100 ${log_file}"
        rm -f "${pid_file}"
        return 1
    fi
}

# 函数：检查 Python 依赖
check_backend_deps() {
    printf "${YELLOW}检查后端依赖...${NC}\n"

    local deps=("fastapi" "uvicorn" "sqlalchemy" "aiosqlite" "python-jose" "passlib" "bcrypt")
    local missing=()

    for dep in "${deps[@]}"; do
        if ! python3 -c "import ${dep}" 2>/dev/null; then
            missing+=("${dep}")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo "  安装缺失的依赖：${missing[*]}"
        pip install "${missing[@]}" > /dev/null 2>&1
        printf "${GREEN}  ✓ 依赖安装完成${NC}\n"
    else
        printf "${GREEN}  ✓ 所有依赖已安装${NC}\n"
    fi
}

# 函数：检查 Node 依赖
check_h5_deps() {
    printf "${YELLOW}检查 H5 前端依赖...${NC}\n"

    if [ ! -d "${H5_DIR}/node_modules" ]; then
        echo "  安装 npm 依赖..."
        cd "${H5_DIR}"
        npm install --silent > /dev/null 2>&1
        printf "${GREEN}  ✓ 依赖安装完成${NC}\n"
    else
        printf "${GREEN}  ✓ 依赖已安装${NC}\n"
    fi
}

# 主流程
main() {
    case "${1:-start}" in
        start)
            echo "【1/4】检查后端依赖..."
            check_backend_deps

            echo ""
            echo "【2/4】检查 H5 前端依赖..."
            check_h5_deps

            echo ""
            echo "【3/4】启动后端服务..."
            cd "${BACKEND_DIR}"
            PYTHONPATH="${BACKEND_DIR}" start_service "后端服务" "python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}" ${BACKEND_PORT} "${BACKEND_PID}" "${BACKEND_LOG}"

            echo ""
            echo "【4/4】启动 H5 前端..."
            cd "${H5_DIR}"
            start_service "H5 前端" "npm run dev" ${H5_PORT} "${H5_PID}" "${H5_LOG}"

            echo ""
            echo "【5/5】启动运营管理端..."
            cd "${FRONTEND_DIR}"
            start_service "运营管理端" "npm run dev" ${FRONTEND_PORT} "${FRONTEND_PID}" "${FRONTEND_LOG}"

            echo ""
            echo "========================================"
            printf "${GREEN}  部署完成！${NC}\n"
            echo "========================================"
            echo ""
            echo "服务访问："
            echo "  - H5 前端（C 端）：http://localhost:${H5_PORT}/"
            echo "  - 运营管理端（B 端）：http://localhost:${FRONTEND_PORT}/"
            echo "  - 后端 API: http://localhost:${BACKEND_PORT}/"
            echo "  - API 文档：http://localhost:${BACKEND_PORT}/docs"
            echo ""
            echo "管理命令："
            echo "  - 停止服务：./deploy.sh stop"
            echo "  - 重启服务：./deploy.sh restart"
            echo "  - 查看状态：./deploy.sh status"
            echo ""
            ;;

        stop)
            echo "【1/3】停止 H5 前端..."
            stop_service "H5 前端" ${H5_PORT} "${H5_PID}"

            echo ""
            echo "【2/3】停止运营管理端..."
            stop_service "运营管理端" ${FRONTEND_PORT} "${FRONTEND_PID}"

            echo ""
            echo "【3/3】停止后端服务..."
            stop_service "后端服务" ${BACKEND_PORT} "${BACKEND_PID}"

            echo ""
            echo "========================================"
            printf "${GREEN}  所有服务已停止${NC}\n"
            echo "========================================"
            ;;

        restart)
            echo "重启所有服务..."
            echo ""
            "$0" stop
            echo ""
            sleep 2
            "$0" start
            ;;

        status)
            echo "服务状态："
            echo ""

            # 后端状态
            echo -n "  后端服务 (端口 ${BACKEND_PORT}): "
            if check_process "${BACKEND_PID}"; then
                local pid=$(cat "${BACKEND_PID}")
                printf "${GREEN}运行中${NC} (PID: %s)\n" "${pid}"
            elif check_port ${BACKEND_PORT}; then
                local pid=$(get_pid_by_port ${BACKEND_PORT})
                printf "${YELLOW}运行中${NC} (PID: %s, PID 文件缺失)\n" "${pid}"
            else
                printf "${RED}已停止${NC}\n"
            fi

            # H5 状态
            echo -n "  H5 前端 (端口 ${H5_PORT}): "
            if check_process "${H5_PID}"; then
                local pid=$(cat "${H5_PID}")
                printf "${GREEN}运行中${NC} (PID: %s)\n" "${pid}"
            elif check_port ${H5_PORT}; then
                local pid=$(get_pid_by_port ${H5_PORT})
                printf "${YELLOW}运行中${NC} (PID: %s, PID 文件缺失)\n" "${pid}"
            else
                printf "${RED}已停止${NC}\n"
            fi

            # 运营管理端状态
            echo -n "  运营管理端 (端口 ${FRONTEND_PORT}): "
            if check_process "${FRONTEND_PID}"; then
                local pid=$(cat "${FRONTEND_PID}")
                printf "${GREEN}运行中${NC} (PID: %s)\n" "${pid}"
            elif check_port ${FRONTEND_PORT}; then
                local pid=$(get_pid_by_port ${FRONTEND_PORT})
                printf "${YELLOW}运行中${NC} (PID: %s, PID 文件缺失)\n" "${pid}"
            else
                printf "${RED}已停止${NC}\n"
            fi

            echo ""
            ;;

        *)
            echo "用法：$0 {start|stop|restart|status}"
            echo ""
            echo "命令说明："
            echo "  start   - 启动服务（检查依赖，启动后端、H5 端、运营管理端）"
            echo "  stop    - 停止服务（优雅关闭，释放端口）"
            echo "  restart - 重启服务"
            echo "  status  - 查看服务状态"
            echo ""
            exit 1
            ;;
    esac
}

main "$@"
