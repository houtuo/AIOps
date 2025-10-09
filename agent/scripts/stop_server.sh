#!/bin/bash

# AIOps Agent 服务器停止脚本

set -e

echo "🛑 停止 AIOps Agent 服务器"
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

# 查找服务器进程
find_server_process() {
    log_info "查找服务器进程..."

    # 方法1: 通过PID文件
    if [ -f "/var/run/aiops-agent.pid" ]; then
        PID=$(cat /var/run/aiops-agent.pid)
        if kill -0 $PID 2>/dev/null; then
            log_info "通过PID文件找到进程: $PID"
            echo $PID
            return 0
        else
            log_warning "PID文件存在但进程不存在，清理PID文件"
            rm -f /var/run/aiops-agent.pid
        fi
    fi

    # 方法2: 通过进程名
    if command -v pgrep &> /dev/null; then
        PIDS=$(pgrep -f "server.py")
        if [ -n "$PIDS" ]; then
            log_info "通过进程名找到进程: $PIDS"
            echo $PIDS
            return 0
        fi
    fi

    # 方法3: 通过端口
    if command -v lsof &> /dev/null; then
        PIDS=$(lsof -ti:8443)
        if [ -n "$PIDS" ]; then
            log_info "通过端口找到进程: $PIDS"
            echo $PIDS
            return 0
        fi
    fi

    # 方法4: 通过ps命令
    PIDS=$(ps aux | grep "server.py" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        log_info "通过ps命令找到进程: $PIDS"
        echo $PIDS
        return 0
    fi

    log_warning "未找到服务器进程"
    return 1
}

# 检查服务器是否在运行
check_server_running() {
    log_info "检查服务器状态..."

    if curl -k https://localhost:8443/health &>/dev/null; then
        log_info "服务器正在运行"
        return 0
    else
        log_warning "服务器未运行"
        return 1
    fi
}

# 优雅停止服务器
graceful_stop() {
    local pids=$1

    log_info "发送优雅停止信号..."

    for pid in $pids; do
        if kill -0 $pid 2>/dev/null; then
            log_info "向进程 $pid 发送 SIGTERM 信号"
            kill -TERM $pid
        fi
    done

    # 等待进程退出
    local timeout=10
    local interval=1
    local elapsed=0

    while [ $elapsed -lt $timeout ]; do
        local all_stopped=true

        for pid in $pids; do
            if kill -0 $pid 2>/dev/null; then
                all_stopped=false
                break
            fi
        done

        if $all_stopped; then
            log_success "所有进程已优雅停止"
            return 0
        fi

        sleep $interval
        elapsed=$((elapsed + interval))
        echo -n "."
    done

    echo
    log_warning "优雅停止超时，将强制停止"
    return 1
}

# 强制停止服务器
force_stop() {
    local pids=$1

    log_warning "强制停止服务器..."

    for pid in $pids; do
        if kill -0 $pid 2>/dev/null; then
            log_info "向进程 $pid 发送 SIGKILL 信号"
            kill -KILL $pid
        fi
    done

    # 确认进程已停止
    sleep 2

    for pid in $pids; do
        if kill -0 $pid 2>/dev/null; then
            log_error "进程 $pid 无法停止"
            return 1
        fi
    done

    log_success "所有进程已强制停止"
    return 0
}

# 清理资源
cleanup() {
    log_info "清理资源..."

    # 删除PID文件
    if [ -f "/var/run/aiops-agent.pid" ]; then
        rm -f /var/run/aiops-agent.pid
        log_info "✓ 删除PID文件"
    fi

    # 删除临时文件
    TEMP_DIR="/tmp/aiops"
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        log_info "✓ 清理临时目录"
    fi

    # 检查是否有其他相关进程
    if command -v pgrep &> /dev/null; then
        REMAINING_PIDS=$(pgrep -f "server.py")
        if [ -n "$REMAINING_PIDS" ]; then
            log_warning "发现残留进程: $REMAINING_PIDS"
            kill -KILL $REMAINING_PIDS 2>/dev/null || true
        fi
    fi
}

# 显示停止信息
show_stop_info() {
    log_info "停止完成信息:"
    echo "  - 服务器端口: 8443"
    echo "  - 协议: HTTPS"
    echo "  - 日志文件: logs/server.log"

    # 验证服务器已停止
    if ! curl -k https://localhost:8443/health &>/dev/null; then
        log_success "✓ 服务器确认已停止"
    else
        log_error "✗ 服务器可能仍在运行"
    fi
}

# 主函数
main() {
    local force=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                force=true
                shift
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

    # 检查服务器是否在运行
    if ! check_server_running; then
        log_warning "服务器未运行，无需停止"
        exit 0
    fi

    # 查找服务器进程
    PIDS=$(find_server_process)
    if [ -z "$PIDS" ]; then
        log_warning "未找到服务器进程，但服务器似乎在运行"
        log_info "可能是其他进程占用了端口 8443"
        exit 1
    fi

    # 停止服务器
    if [ "$force" = true ]; then
        log_warning "使用强制停止模式"
        force_stop "$PIDS"
    else
        log_info "使用优雅停止模式"
        if ! graceful_stop "$PIDS"; then
            log_warning "优雅停止失败，尝试强制停止"
            force_stop "$PIDS"
        fi
    fi

    # 清理资源
    cleanup

    # 显示停止信息
    show_stop_info

    log_success "服务器停止完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [选项]

停止 AIOps Agent 服务器

选项:
  -f, --force    强制停止模式
  -h, --help     显示此帮助信息

示例:
  $0              # 优雅停止
  $0 --force      # 强制停止

停止过程:
  1. 查找服务器进程
  2. 发送停止信号 (默认SIGTERM，强制模式SIGKILL)
  3. 等待进程退出
  4. 清理资源 (PID文件、临时文件等)
  5. 验证停止状态

EOF
}

# 执行主函数
main "$@"