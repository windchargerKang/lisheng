#!/bin/bash
#
# 编译检查 Hook - 每次 Edit/Write 后自动运行
# 配合 settings.json 使用：
# {
#   "hooks": {
#     "PostToolUse": [{
#       "matcher": "Edit|Write",
#       "hooks": [{
#         "type": "command",
#         "command": "bash .claude/hooks/run_checks.sh"
#       }]
#     }]
#   }
# }
#
# 注意：此脚本为通用模板，编译命令需根据实际项目类型调整
# - Java/Maven: mvn -q -DskipTests compile && mvn test
# - Frontend: npm run lint && npm test
# - Android: ./gradlew lint test
# - iOS: xcodebuild (需 Mac 环境)
#

set -euo pipefail

# 1. 获取当前所有被修改、新增或删除的文件列表
CHANGED_FILES=$(git status --porcelain 2>/dev/null | awk '{print $2}') || {
    echo "[Hook] 无法获取 git status，跳过检查"
    exit 0
}

# 2. 如果没有文件变动，直接退出
if [ -z "$CHANGED_FILES" ]; then
    exit 0
fi

# 3. 检查是否只修改了文档文件（不需要编译检查）
NON_DOC_CHANGES=$(echo "$CHANGED_FILES" | grep -vE '\.(md|txt|csv|json|yaml|yml|properties)$') || true

if [ -z "$NON_DOC_CHANGES" ]; then
    echo "[Hook 拦截] 仅检测到文档变动，跳过编译检查。"
    exit 0
fi

# 4. 执行编译检查
# ============================================
# TODO: 根据项目类型取消注释对应的命令
# ============================================

# --- Java/Maven 项目 ---
# echo "[Hook] 执行 Maven 编译检查..."
# mvn -q -DskipTests compile
# echo "[Hook] 执行单元测试..."
# mvn test

# --- Frontend/Node.js 项目 ---
# echo "[Hook] 执行 Lint 检查..."
# npm run lint 2>/dev/null || echo "[Hook] 无 lint 命令，跳过"
# echo "[Hook] 执行单元测试..."
# npm test -- --passWithNoTests

# --- Android/Gradle 项目 ---
# echo "[Hook] 执行 Gradle 检查..."
# ./gradlew lint test --no-daemon

# --- 通用：仅编译检查（安全 baseline）---
echo "[Hook] 检测到代码变动，执行通用检查..."

# 检测项目类型
if [ -f "pom.xml" ]; then
    echo "[Hook] 检测到 Maven 项目，执行编译..."
    mvn -q -DskipTests compile 2>/dev/null || echo "[Hook] Maven 编译失败，请检查"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    echo "[Hook] 检测到 Gradle 项目，执行编译..."
    ./gradlew compileJava --no-daemon 2>/dev/null || echo "[Hook] Gradle 编译失败，请检查"
elif [ -f "package.json" ]; then
    echo "[Hook] 检测到 Node.js 项目..."
    # npm run build 2>/dev/null || echo "[Hook] 构建失败，请检查"
    echo "[Hook] 跳过（请根据需要配置）"
else
    echo "[Hook] 未知项目类型，跳过编译检查"
fi

echo "[Hook] 检查完成"
