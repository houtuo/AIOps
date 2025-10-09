#!/bin/bash

# AIOps Agent 服务器启动脚本

set -e

echo "🚀 启动 AIOps Agent 服务器"
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

# 检查Python
check_python() {
    log_info "检查Python环境..."

    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python命令"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_info "Python版本: $PYTHON_VERSION"

    # 检查Python版本
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 8 ]); then
        log_error "Python版本过低，需要3.8或以上"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖包..."

    REQUIRED_PACKAGES=("flask" "pyjwt" "cryptography" "pyyaml" "werkzeug")

    for package in "${REQUIRED_PACKAGES[@]}"; do
        if $PYTHON_CMD -c "import $package" 2>/dev/null; then
            log_info "✓ $package"
        else
            log_error "✗ 缺少依赖包: $package"
            log_info "安装命令: $PYTHON_CMD -m pip install $package"
            exit 1
        fi
    done
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."

    if [ ! -f "config/default.yaml" ]; then
        log_warning "配置文件不存在，生成默认配置..."

        if [ -f "scripts/generate_keys.py" ]; then
            $PYTHON_CMD scripts/generate_keys.py
        else
            log_error "密钥生成脚本不存在"
            exit 1
        fi
    else
        log_info "✓ 配置文件存在"
    fi

    # 检查SSL证书
    if [ ! -f "config/server.crt" ] || [ ! -f "config/server.key" ]; then
        log_warning "SSL证书不存在，重新生成..."

        if [ -f "scripts/generate_keys.py" ]; then
            $PYTHON_CMD scripts/generate_keys.py
        else
            log_error "密钥生成脚本不存在"
            exit 1
        fi
    else
        log_info "✓ SSL证书存在"
    fi
}

# 检查端口占用
check_port() {
    local port=${1:-8443}

    log_info "检查端口 $port 占用情况..."

    if command -v netstat &> /dev/null; then
        if netstat -tln | grep ":$port " &> /dev/null; then
            log_warning "端口 $port 已被占用"
            return 1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tln | grep ":$port " &> /dev/null; then
            log_warning "端口 $port 已被占用"
            return 1
        fi
    fi

    log_info "✓ 端口 $port 可用"
    return 0
}

# 检查服务器是否已在运行
check_server_running() {
    log_info "检查服务器状态..."

    if curl -k https://localhost:8443/health &>/dev/null; then
        log_warning "服务器已在运行"
        return 0
    fi

    return 1
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."

    mkdir -p logs
    mkdir -p config

    log_info "✓ 目录创建完成"
}

# 启动服务器
start_server() {
    local mode=$1

    log_info "启动服务器 (模式: $mode)..."

    # 设置环境变量
    export PYTHONPATH=$(pwd)

    case $mode in
        "foreground")
            log_info "前台启动模式..."
            $PYTHON_CMD src/server.py
            ;;
        "background")
            log_info "后台启动模式..."
            nohup $PYTHON_CMD src/server.py > logs/server.log 2>&1 &
            SERVER_PID=$!
            echo $SERVER_PID > /var/run/aiops-agent.pid
            log_success "服务器已启动 (PID: $SERVER_PID)"
            ;;
        "debug")
            log_info "调试模式启动..."
            export AIOPS_LOG_LEVEL=DEBUG
            $PYTHON_CMD src/server.py
            ;;
        *)
            log_error "未知启动模式: $mode"
            exit 1
            ;;
    esac
}

# 等待服务器启动
wait_for_server() {
    local timeout=30
    local interval=1
    local elapsed=0

    log_info "等待服务器启动..."

    while [ $elapsed -lt $timeout ]; do
        if curl -k https://localhost:8443/health &>/dev/null; then
            log_success "服务器启动成功"
            return 0
        fi

        sleep $interval
        elapsed=$((elapsed + interval))
        echo -n "."
    done

    echo
    log_error "服务器启动超时"
    return 1
}

# 显示服务器信息
show_server_info() {
    log_info "服务器信息:"

    # 获取服务器状态
    if curl -k https://localhost:8443/health &>/dev/null; then
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
}

# 主函数
main() {
    local mode="background"

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--foreground)
                mode="foreground"
                shift
                ;;
            -d|--debug)
                mode="debug"
                shift
                ;;
            -b|--background)
                mode="background"
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

    # 检查环境
    check_python
    check_dependencies

    # 检查服务器是否已在运行
    if check_server_running; then
        log_warning "服务器已在运行，跳过启动"
        show_server_info
        exit 0
    fi

    # 准备工作
    create_directories
    check_config
    check_port 8443

    # 启动服务器
    start_server "$mode"

    # 如果是后台模式，等待启动
    if [ "$mode" = "background" ]; then
        if wait_for_server; then
            show_server_info
            log_success "服务器启动完成"

            # 显示日志文件位置
            echo
            log_info "日志文件: logs/server.log"
            log_info "PID文件: /var/run/aiops-agent.pid"
        else
            log_error "服务器启动失败，请检查日志: logs/server.log"
            exit 1
        fi
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [选项]

启动 AIOps Agent 服务器

选项:
  -f, --foreground   前台启动模式
  -b, --background   后台启动模式 (默认)
  -d, --debug        调试模式启动
  -h, --help         显示此帮助信息

示例:
  $0                    # 后台启动
  $0 --foreground       # 前台启动
  $0 --debug            # 调试模式启动

环境变量:
  PYTHONPATH          设置Python路径
  AIOPS_LOG_LEVEL     设置日志级别 (DEBUG, INFO, WARNING, ERROR)

EOF
}

# 执行主函数
main "$@"