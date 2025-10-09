#!/bin/bash

# AIOps Agent 测试执行脚本
# 用于自动化执行所有测试

set -e

echo "🚀 AIOps Agent 测试套件"
echo "========================"

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

    REQUIRED_PACKAGES=("flask" "pyjwt" "cryptography" "pyyaml" "werkzeug" "pytest")

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

# 生成测试配置
generate_test_config() {
    log_info "生成测试配置..."

    if [ ! -f "config/default.yaml" ]; then
        log_info "生成密钥和证书..."
        $PYTHON_CMD scripts/generate_keys.py
    else
        log_info "配置文件已存在，跳过生成"
    fi
}

# 启动测试服务器
start_test_server() {
    log_info "启动测试服务器..."

    # 检查服务器是否已在运行
    if curl -k https://localhost:8443/health &>/dev/null; then
        log_info "服务器已在运行"
        return 0
    fi

    # 启动服务器
    export PYTHONPATH=$(pwd)
    nohup $PYTHON_CMD src/server.py > logs/server.log 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > /tmp/aiops_test_server.pid

    # 等待服务器启动
    log_info "等待服务器启动..."
    for i in {1..30}; do
        if curl -k https://localhost:8443/health &>/dev/null; then
            log_success "服务器启动成功 (PID: $SERVER_PID)"
            return 0
        fi
        sleep 1
    done

    log_error "服务器启动超时"
    stop_test_server
    exit 1
}

# 停止测试服务器
stop_test_server() {
    if [ -f "/tmp/aiops_test_server.pid" ]; then
        SERVER_PID=$(cat /tmp/aiops_test_server.pid)
        if kill -0 $SERVER_PID 2>/dev/null; then
            log_info "停止测试服务器 (PID: $SERVER_PID)..."
            kill $SERVER_PID
            rm -f /tmp/aiops_test_server.pid
            sleep 2
        fi
    fi
}

# 运行单元测试
run_unit_tests() {
    log_info "运行单元测试..."

    if [ -d "tests" ]; then
        $PYTHON_CMD -m pytest tests/ -v --tb=short
        UNIT_TEST_RESULT=$?
    else
        log_warning "tests目录不存在，跳过单元测试"
        UNIT_TEST_RESULT=0
    fi

    return $UNIT_TEST_RESULT
}

# 运行基础功能测试
run_basic_tests() {
    log_info "运行基础功能测试..."

    if [ -f "test_basic.py" ]; then
        $PYTHON_CMD test_basic.py
        BASIC_TEST_RESULT=$?
    else
        log_warning "test_basic.py不存在，跳过基础功能测试"
        BASIC_TEST_RESULT=0
    fi

    return $BASIC_TEST_RESULT
}

# 运行本地模块测试
run_local_tests() {
    log_info "运行本地模块测试..."

    if [ -f "test_local.py" ]; then
        $PYTHON_CMD test_local.py
        LOCAL_TEST_RESULT=$?
    else
        log_warning "test_local.py不存在，跳过本地模块测试"
        LOCAL_TEST_RESULT=0
    fi

    return $LOCAL_TEST_RESULT
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."

    if [ -f "test_integration.py" ]; then
        # 生成API密钥用于测试
        log_info "生成测试API密钥..."
        API_RESPONSE=$(curl -k -s -X POST https://localhost:8443/auth/api-key \
            -H "Content-Type: application/json" \
            -d '{"user_id": "test_user", "permissions": ["exec:command", "exec:script"]}')

        API_KEY=$(echo $API_RESPONSE | grep -o '"api_key":"[^"]*' | cut -d'"' -f4)
        TOKEN=$(echo $API_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

        if [ -n "$API_KEY" ] && [ -n "$TOKEN" ]; then
            log_info "使用API密钥运行集成测试..."
            $PYTHON_CMD test_integration.py --auth-token "$TOKEN"
        else
            log_warning "API密钥生成失败，运行无认证集成测试..."
            $PYTHON_CMD test_integration.py
        fi

        INTEGRATION_TEST_RESULT=$?
    else
        log_warning "test_integration.py不存在，跳过集成测试"
        INTEGRATION_TEST_RESULT=0
    fi

    return $INTEGRATION_TEST_RESULT
}

# 生成测试报告
generate_test_report() {
    log_info "生成测试报告..."

    REPORT_DIR="test_reports"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    REPORT_FILE="$REPORT_DIR/test_summary_$TIMESTAMP.txt"

    mkdir -p $REPORT_DIR

    cat > $REPORT_FILE << EOF
AIOps Agent 测试报告
===================
测试时间: $(date)
测试环境: $(uname -a)
Python版本: $PYTHON_VERSION

测试结果:
- 单元测试: $([ $UNIT_TEST_RESULT -eq 0 ] && echo "通过" || echo "失败")
- 基础功能测试: $([ $BASIC_TEST_RESULT -eq 0 ] && echo "通过" || echo "失败")
- 本地模块测试: $([ $LOCAL_TEST_RESULT -eq 0 ] && echo "通过" || echo "失败")
- 集成测试: $([ $INTEGRATION_TEST_RESULT -eq 0 ] && echo "通过" || echo "失败")

总体结果: $([ $OVERALL_RESULT -eq 0 ] && echo "✅ 所有测试通过" || echo "❌ 部分测试失败")

详细日志:
- 服务器日志: logs/server.log
- 测试报告: $REPORT_DIR/
EOF

    log_success "测试报告已生成: $REPORT_FILE"
}

# 清理函数
cleanup() {
    log_info "执行清理..."
    stop_test_server
}

# 主函数
main() {
    log_info "开始执行AIOps Agent测试套件"

    # 设置陷阱，确保清理函数在退出时执行
    trap cleanup EXIT

    # 检查环境
    check_python
    check_dependencies

    # 生成配置
    generate_test_config

    # 启动服务器
    start_test_server

    # 运行测试
    run_unit_tests
    UNIT_TEST_RESULT=$?

    run_basic_tests
    BASIC_TEST_RESULT=$?

    run_local_tests
    LOCAL_TEST_RESULT=$?

    run_integration_tests
    INTEGRATION_TEST_RESULT=$?

    # 计算总体结果
    OVERALL_RESULT=$((UNIT_TEST_RESULT + BASIC_TEST_RESULT + LOCAL_TEST_RESULT + INTEGRATION_TEST_RESULT))

    # 生成报告
    generate_test_report

    # 显示总体结果
    echo
    echo "=" * 50
    if [ $OVERALL_RESULT -eq 0 ]; then
        log_success "🎉 所有测试通过！"
    else
        log_error "❌ 部分测试失败"
        echo "失败详情:"
        [ $UNIT_TEST_RESULT -ne 0 ] && echo "  - 单元测试失败"
        [ $BASIC_TEST_RESULT -ne 0 ] && echo "  - 基础功能测试失败"
        [ $LOCAL_TEST_RESULT -ne 0 ] && echo "  - 本地模块测试失败"
        [ $INTEGRATION_TEST_RESULT -ne 0 ] && echo "  - 集成测试失败"
    fi
    echo "=" * 50

    exit $OVERALL_RESULT
}

# 执行主函数
main "$@"