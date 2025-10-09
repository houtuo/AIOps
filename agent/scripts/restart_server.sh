#!/bin/bash

# AIOps Agent 服务器重启脚本

set -e

echo "🔄 重启 AIOps Agent 服务器"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [选项]

重启 AIOps Agent 服务器

选项:
  -f, --force    强制重启模式
  -w, --wait     重启后等待服务器就绪
  -t, --timeout  等待超时时间 (秒，默认: 30)
  -h, --help     显示此帮助信息

示例:
  $0                    # 正常重启
  $0 --force            # 强制重启
  $0 --wait --timeout 60 # 重启并等待60秒

重启过程:
  1. 停止当前运行的服务器
  2. 等待进程完全停止
  3. 启动新的服务器实例
  4. (可选) 等待服务器就绪

EOF
}

# 主函数
main() {
    local force=false
    local wait_for_ready=false
    local timeout=30

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                force=true
                shift
                ;;
            -w|--wait)
                wait_for_ready=true
                shift
                ;;
            -t|--timeout)
                timeout=$2
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 获取脚本目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    # 切换到项目根目录
    cd "$PROJECT_ROOT"

    log_info "项目目录: $(pwd)"

    # 步骤1: 停止服务器
    log_info "步骤1: 停止服务器..."

    if [ "$force" = true ]; then
        log_info "使用强制停止模式"
        if ! "$SCRIPT_DIR/stop_server.sh" --force; then
            log_warning "停止脚本执行失败，继续重启过程"
        fi
    else
        if ! "$SCRIPT_DIR/stop_server.sh"; then
            log_warning "优雅停止失败，尝试强制停止"
            "$SCRIPT_DIR/stop_server.sh" --force
        fi
    fi

    # 等待进程完全停止
    log_info "等待进程完全停止..."
    sleep 3

    # 验证服务器已停止
    if curl -k https://localhost:8443/health &>/dev/null; then
        log_error "服务器仍在运行，重启失败"
        exit 1
    else
        log_success "服务器确认已停止"
    fi

    # 步骤2: 启动服务器
    log_info "步骤2: 启动服务器..."

    if ! "$SCRIPT_DIR/start_server.sh" --background; then
        log_error "服务器启动失败"
        exit 1
    fi

    # 步骤3: 等待服务器就绪 (可选)
    if [ "$wait_for_ready" = true ]; then
        log_info "步骤3: 等待服务器就绪 (超时: ${timeout}秒)..."

        local elapsed=0
        local interval=1

        while [ $elapsed -lt $timeout ]; do
            if curl -k https://localhost:8443/health &>/dev/null; then
                log_success "服务器已就绪"
                break
            fi

            sleep $interval
            elapsed=$((elapsed + interval))
            echo -n "."
        done

        echo

        if [ $elapsed -ge $timeout ]; then
            log_error "等待服务器就绪超时"
            exit 1
        fi
    fi

    # 显示重启完成信息
    log_success "服务器重启完成"

    # 显示服务器信息
    if curl -k https://localhost:8443/health &>/dev/null; then
        echo
        log_info "服务器当前状态:"
        STATUS_RESPONSE=$(curl -k -s https://localhost:8443/status)
        HOSTNAME=$(echo "$STATUS_RESPONSE" | grep -o '"hostname":"[^"]*' | cut -d'"' -f4)
        PLATFORM=$(echo "$STATUS_RESPONSE" | grep -o '"platform":"[^"]*' | cut -d'"' -f4)
        VERSION=$(echo "$STATUS_RESPONSE" | grep -o '"version":"[^"]*' | cut -d'"' -f4)

        echo "  - 主机名: $HOSTNAME"
        echo "  - 平台: $PLATFORM"
        echo "  - 版本: $VERSION"
        echo "  - 端口: 8443"
        echo "  - 协议: HTTPS"
    fi

    # 显示有用的信息
    echo
    log_info "有用的命令:"
    echo "  查看日志: tail -f logs/server.log"
    echo "  停止服务: $SCRIPT_DIR/stop_server.sh"
    echo "  查看状态: curl -k https://localhost:8443/health"
}

# 执行主函数
main "$@"