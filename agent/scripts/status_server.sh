#!/bin/bash

# AIOps Agent 服务器状态检查脚本

set -e

echo "📊 AIOps Agent 服务器状态"
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

# 检查服务器进程
check_process() {
    log_info "检查服务器进程..."

    # 方法1: 通过PID文件
    if [ -f "/var/run/aiops-agent.pid" ]; then
        PID=$(cat /var/run/aiops-agent.pid)
        if kill -0 $PID 2>/dev/null; then
            log_success "通过PID文件找到进程: $PID"
            echo $PID
            return 0
        else
            log_warning "PID文件存在但进程不存在"
        fi
    fi

    # 方法2: 通过进程名
    if command -v pgrep &> /dev/null; then
        PIDS=$(pgrep -f "server.py")
        if [ -n "$PIDS" ]; then
            log_success "通过进程名找到进程: $PIDS"
            echo $PIDS
            return 0
        fi
    fi

    # 方法3: 通过端口
    if command -v lsof &> /dev/null; then
        PIDS=$(lsof -ti:8443)
        if [ -n "$PIDS" ]; then
            log_success "通过端口找到进程: $PIDS"
            echo $PIDS
            return 0
        fi
    fi

    log_error "未找到服务器进程"
    return 1
}

# 检查服务器健康状态
check_health() {
    log_info "检查服务器健康状态..."

    if curl -k https://localhost:8443/health &>/dev/null; then
        RESPONSE=$(curl -k -s https://localhost:8443/health)
        STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
        SERVICE=$(echo "$RESPONSE" | grep -o '"service":"[^"]*' | cut -d'"' -f4)

        if [ "$STATUS" = "healthy" ]; then
            log_success "服务器健康状态: $STATUS"
            echo "  - 服务: $SERVICE"
            echo "  - 状态: $STATUS"
            return 0
        else
            log_warning "服务器状态异常: $STATUS"
            return 1
        fi
    else
        log_error "无法连接到服务器"
        return 1
    fi
}

# 检查服务器详细信息
check_status() {
    log_info "获取服务器详细信息..."

    if curl -k https://localhost:8443/status &>/dev/null; then
        RESPONSE=$(curl -k -s https://localhost:8443/status)
        HOSTNAME=$(echo "$RESPONSE" | grep -o '"hostname":"[^"]*' | cut -d'"' -f4)
        PLATFORM=$(echo "$RESPONSE" | grep -o '"platform":"[^"]*' | cut -d'"' -f4)
        STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
        VERSION=$(echo "$RESPONSE" | grep -o '"version":"[^"]*' | cut -d'"' -f4)

        echo "  - 主机名: $HOSTNAME"
        echo "  - 平台: $PLATFORM"
        echo "  - 运行状态: $STATUS"
        echo "  - 版本: $VERSION"
    else
        log_warning "无法获取服务器详细信息"
    fi
}

# 检查端口占用
check_port() {
    log_info "检查端口占用情况..."

    local port=8443

    if command -v netstat &> /dev/null; then
        if netstat -tln | grep ":$port " &> /dev/null; then
            log_success "端口 $port 已被占用"
            return 0
        else
            log_warning "端口 $port 未被占用"
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tln | grep ":$port " &> /dev/null; then
            log_success "端口 $port 已被占用"
            return 0
        else
            log_warning "端口 $port 未被占用"
            return 1
        fi
    else
        log_warning "无法检查端口占用情况"
        return 1
    fi
}

# 检查日志文件
check_logs() {
    log_info "检查日志文件..."

    LOG_FILE="logs/server.log"

    if [ -f "$LOG_FILE" ]; then
        FILE_SIZE=$(du -h "$LOG_FILE" | cut -f1)
        LAST_MODIFIED=$(stat -c %y "$LOG_FILE" 2>/dev/null || stat -f %Sm "$LOG_FILE")
        LINE_COUNT=$(wc -l < "$LOG_FILE")

        echo "  - 日志文件: $LOG_FILE"
        echo "  - 文件大小: $FILE_SIZE"
        echo "  - 最后修改: $LAST_MODIFIED"
        echo "  - 行数: $LINE_COUNT"

        # 显示最近的错误
        RECENT_ERRORS=$(grep -i "error\|exception\|fail" "$LOG_FILE" | tail -5)
        if [ -n "$RECENT_ERRORS" ]; then
            echo
            log_warning "最近的错误日志:"
            echo "$RECENT_ERRORS"
        fi
    else
        log_warning "日志文件不存在: $LOG_FILE"
    fi
}

# 检查系统资源
check_resources() {
    log_info "检查系统资源..."

    # 检查内存使用
    if command -v free &> /dev/null; then
        MEMORY_INFO=$(free -h)
        echo "  - 内存信息:"
        echo "$MEMORY_INFO" | head -2
    fi

    # 检查磁盘使用
    if command -v df &> /dev/null; then
        DISK_INFO=$(df -h .)
        echo "  - 磁盘信息:"
        echo "$DISK_INFO"
    fi

    # 检查负载
    if command -v uptime &> /dev/null; then
        LOAD_INFO=$(uptime)
        echo "  - 系统负载:"
        echo "    $LOAD_INFO"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [选项]

检查 AIOps Agent 服务器状态

选项:
  -d, --detailed   显示详细信息
  -l, --logs       显示日志信息
  -r, --resources  显示系统资源信息
  -h, --help       显示此帮助信息

示例:
  $0              # 基本状态检查
  $0 --detailed   # 详细状态检查
  $0 --logs       # 包含日志检查
  $0 --resources  # 包含系统资源检查

EOF
}

# 主函数
main() {
    local detailed=false
    local show_logs=false
    local show_resources=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--detailed)
                detailed=true
                shift
                ;;
            -l|--logs)
                show_logs=true
                shift
                ;;
            -r|--resources)
                show_resources=true
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

    # 获取脚本目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    # 切换到项目根目录
    cd "$PROJECT_ROOT"

    log_info "项目目录: $(pwd)"

    # 基本状态检查
    echo
    log_info "=== 基本状态检查 ==="

    # 检查进程
    if check_process; then
        PROCESS_FOUND=true
    else
        PROCESS_FOUND=false
    fi

    # 检查端口
    check_port

    # 检查健康状态
    if check_health; then
        HEALTHY=true
    else
        HEALTHY=false
    fi

    # 详细状态检查
    if [ "$detailed" = true ] || [ "$HEALTHY" = true ]; then
        echo
        log_info "=== 详细状态检查 ==="
        check_status
    fi

    # 日志检查
    if [ "$show_logs" = true ] || [ "$detailed" = true ]; then
        echo
        log_info "=== 日志检查 ==="
        check_logs
    fi

    # 系统资源检查
    if [ "$show_resources" = true ] || [ "$detailed" = true ]; then
        echo
        log_info "=== 系统资源检查 ==="
        check_resources
    fi

    # 总体状态评估
    echo
    log_info "=== 总体状态评估 ==="

    if [ "$HEALTHY" = true ] && [ "$PROCESS_FOUND" = true ]; then
        log_success "✅ 服务器运行正常"
    elif [ "$PROCESS_FOUND" = true ] && [ "$HEALTHY" = false ]; then
        log_warning "⚠️ 服务器进程存在但无法连接"
    elif [ "$PROCESS_FOUND" = false ] && [ "$HEALTHY" = false ]; then
        log_error "❌ 服务器未运行"
    else
        log_warning "⚠️ 服务器状态异常"
    fi

    # 显示有用的命令
    echo
    log_info "有用的命令:"
    echo "  启动服务: $SCRIPT_DIR/start_server.sh"
    echo "  停止服务: $SCRIPT_DIR/stop_server.sh"
    echo "  重启服务: $SCRIPT_DIR/restart_server.sh"
    echo "  查看日志: tail -f logs/server.log"
}

# 执行主函数
main "$@"