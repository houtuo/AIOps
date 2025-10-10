#!/bin/bash

# AIOps Agent API 完整测试脚本
# 使用 curl 命令手动测试所有API接口

set -e

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

# 配置
SERVER="10.0.0.30"
URL="https://${SERVER}:8443"
TOKEN_FILE="/tmp/aiops_token.txt"

# 检查依赖
check_dependencies() {
    log_info "检查依赖工具..."

    if ! command -v curl &> /dev/null; then
        log_error "需要安装 curl"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_warning "建议安装 jq 用于更好的JSON输出"
    fi

    log_success "依赖检查通过"
}

# 获取API令牌
get_api_token() {
    log_info "获取API令牌..."

    RESPONSE=$(curl -s -X POST "${URL}/auth/api-key" \
        -H "Content-Type: application/json" \
        -d '{
            "user_id": "test_user",
            "permissions": ["execute", "read", "write"]
        }' \
        -k)

    TOKEN=$(echo "$RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

    if [ -z "$TOKEN" ]; then
        log_error "获取令牌失败"
        echo "响应: $RESPONSE"
        exit 1
    fi

    echo "$TOKEN" > "$TOKEN_FILE"
    log_success "令牌获取成功: ${TOKEN:0:20}..."
    echo "$TOKEN"
}

# 读取或获取令牌
ensure_token() {
    if [ -f "$TOKEN_FILE" ]; then
        TOKEN=$(cat "$TOKEN_FILE")
        log_info "使用现有令牌: ${TOKEN:0:20}..."
    else
        TOKEN=$(get_api_token)
    fi
}

# 健康检查
test_health() {
    log_info "测试健康检查接口..."

    curl -s -X GET "${URL}/health" \
        -H "Authorization: Bearer $TOKEN" \
        -k | jq . 2>/dev/null || cat

    log_success "健康检查完成"
}

# 状态检查
test_status() {
    log_info "测试状态检查接口..."

    curl -s -X GET "${URL}/status" \
        -H "Authorization: Bearer $TOKEN" \
        -k | jq . 2>/dev/null || cat

    log_success "状态检查完成"
}

# 基本命令执行
test_basic_commands() {
    log_info "测试基本命令执行..."

    commands=(
        "echo \"Hello World\""
        "whoami"
        "pwd"
        "cat /etc/redhat-release"
        "ls -la /home/app/"
    )

    for cmd in "${commands[@]}"; do
        log_info "执行命令: $cmd"
        # 转义双引号
        escaped_cmd=$(echo "$cmd" | sed 's/"/\\"/g')
        curl -s -X POST "${URL}/exec/command" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "{\"command\": \"$escaped_cmd\"}" \
            -k | jq . 2>/dev/null || cat
        echo
    done

    log_success "基本命令测试完成"
}

# 用户切换测试
test_user_switch() {
    log_info "测试用户切换功能..."

    commands=(
        "sudo -u app bash -c 'whoami && pwd'"
        "sudo -u app bash -c 'cd /home/app/script && pwd'"
        "sudo -u app bash -c 'cd /home/app/script && ./test.sh'"
    )

    for cmd in "${commands[@]}"; do
        log_info "执行命令: $cmd"
        curl -s -X POST "${URL}/exec/command" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "{\"command\": \"$cmd\"}" \
            -k | jq . 2>/dev/null || cat
        echo
    done

    log_success "用户切换测试完成"
}

# 脚本内容执行
test_script_content() {
    log_info "测试脚本内容执行..."

    # 使用换行符转义，确保JSON格式正确
    SCRIPT_CONTENT='#!/bin/bash\necho \"动态脚本测试\"\ndate\nwhoami\npwd\nhostname'

    curl -s -X POST "${URL}/exec/script/content" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"script\": \"$SCRIPT_CONTENT\", \"user\": \"app\", \"working_dir\": \"/tmp\"}" \
        -k | jq . 2>/dev/null || cat

    log_success "脚本内容测试完成"
}

# 用户信息查询
test_user_info() {
    log_info "测试用户信息查询..."

    curl -s -X GET "${URL}/users" \
        -H "Authorization: Bearer $TOKEN" \
        -k | jq . 2>/dev/null || cat

    echo

    curl -s -X GET "${URL}/users/app" \
        -H "Authorization: Bearer $TOKEN" \
        -k | jq . 2>/dev/null || cat

    log_success "用户信息查询完成"
}

# API密钥验证
test_api_verify() {
    log_info "测试API密钥验证..."

    # 这里需要实际的api_key，通常从生成令牌的响应中获取
    log_warning "API密钥验证需要实际的api_key参数"

    log_success "API验证测试跳过"
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [选项]

AIOps Agent API 完整测试脚本

选项:
  -s, --server SERVER    指定服务器地址 (默认: 10.0.0.30)
  -t, --token TOKEN      使用指定的令牌
  -g, --get-token        只获取令牌
  -c, --clean            清理令牌文件
  -h, --help             显示此帮助信息

测试流程:
  1. 获取API令牌
  2. 健康检查
  3. 状态检查
  4. 基本命令执行
  5. 用户切换测试
  6. 脚本内容执行
  7. 用户信息查询

示例:
  $0                          # 测试默认服务器
  $0 -s 10.0.0.202           # 测试指定服务器
  $0 -g                      # 只获取令牌
  $0 -c                      # 清理令牌

EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--server)
            SERVER="$2"
            URL="https://${SERVER}:8443"
            shift 2
            ;;
        -t|--token)
            TOKEN="$2"
            echo "$TOKEN" > "$TOKEN_FILE"
            shift 2
            ;;
        -g|--get-token)
            get_api_token
            exit 0
            ;;
        -c|--clean)
            rm -f "$TOKEN_FILE"
            log_success "令牌文件已清理"
            exit 0
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

# 主函数
main() {
    log_info "🚀 开始 AIOps Agent API 测试"
    log_info "目标服务器: $SERVER"
    echo

    # 检查依赖
    check_dependencies

    # 确保有令牌
    ensure_token

    # 执行测试
    test_health
    test_status
    test_basic_commands
    test_user_switch
    test_script_content
    test_user_info
    test_api_verify

    log_success "🎉 所有API测试完成！"
    log_info "令牌文件: $TOKEN_FILE"
    log_info "下次运行将自动使用现有令牌"
}

# 执行主函数
main "$@"