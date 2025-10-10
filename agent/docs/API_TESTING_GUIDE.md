# AIOps Agent API 测试指南

## 概述

本文档提供 AIOps Agent 所有API接口的详细说明和使用curl命令手动测试的方法。

## 基础信息

- **基础URL**: `https://<server_ip>:8443`
- **认证方式**: Bearer Token (JWT)
- **默认服务器**:
  - 10.0.0.30 (RedHat 8)
  - 10.0.0.202 (CentOS 7)

## 1. 认证相关API

### 1.1 生成API密钥
生成用于后续API调用的JWT令牌。

**请求**
```bash
curl -X POST https://10.0.0.30:8443/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "permissions": ["execute", "read", "write"]
  }' \
  -k
```

**响应示例**
```json
{
  "api_key": "your_api_key_here",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**保存令牌**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 1.2 验证API密钥
验证API密钥和令牌的有效性。

**请求**
```bash
curl -X POST https://10.0.0.30:8443/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key_here",
    "token": "$TOKEN"
  }' \
  -k
```

## 2. 健康检查和状态API

### 2.1 健康检查
检查服务器是否正常运行。

**请求**
```bash
curl -X GET https://10.0.0.30:8443/health \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

**响应示例**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-10T17:37:33",
  "version": "1.0.0"
}
```

### 2.2 状态检查
获取服务器详细状态信息。

**请求**
```bash
curl -X GET https://10.0.0.30:8443/status \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

**响应示例**
```json
{
  "status": "running",
  "uptime": "2 hours",
  "memory_usage": "45%",
  "cpu_usage": "12%",
  "active_connections": 3,
  "hostname": "opm-server"
}
```

## 3. 命令执行API

### 3.1 执行Shell命令
执行单个shell命令。

**请求**
```bash
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "echo \"Hello World\""
  }' \
  -k
```

**更多命令示例**

```bash
# 查看当前用户
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "whoami"}' \
  -k

# 查看工作目录
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "pwd"}' \
  -k

# 查看系统信息
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "cat /etc/redhat-release"}' \
  -k
```

### 3.2 用户切换执行命令
使用特定用户执行命令。

**请求**
```bash
# 切换到app用户执行命令
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "sudo -u app bash -c \"whoami && pwd\""
  }' \
  -k

# 在指定目录执行脚本
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "sudo -u app bash -c \"cd /home/app/script && ./test.sh\""
  }' \
  -k
```

## 4. 脚本执行API

### 4.1 执行脚本内容
直接执行提供的脚本内容。

**请求**
```bash
curl -X POST https://10.0.0.30:8443/exec/script/content \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "script": "#!/bin/bash\necho \"动态脚本测试\"\ndate\nwhoami\npwd",
    "user": "app",
    "working_dir": "/tmp"
  }' \
  -k
```

### 4.2 执行脚本文件
执行服务器上已有的脚本文件。

**请求**
```bash
curl -X POST https://10.0.0.30:8443/exec/script/file \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "script_path": "/home/app/script/test.sh",
    "user": "app",
    "working_dir": "/home/app/script"
  }' \
  -k
```

### 4.3 动态脚本执行
动态生成并执行脚本。

**请求**
```bash
curl -X POST https://10.0.0.30:8443/exec/script/dynamic \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "script": "#!/bin/bash\necho \"自定义脚本\"\nhostname\ncat /etc/hostname",
    "user": "app"
  }' \
  -k
```

## 5. 用户管理API

### 5.1 获取所有用户
获取系统用户列表。

**请求**
```bash
curl -X GET https://10.0.0.30:8443/users \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

### 5.2 获取特定用户信息
获取指定用户的详细信息。

**请求**
```bash
curl -X GET https://10.0.0.30:8443/users/app \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

## 6. 完整测试流程示例

### 6.1 自动化测试脚本
```bash
#!/bin/bash

# 设置服务器地址
SERVER="10.0.0.30"
URL="https://${SERVER}:8443"

# 生成API令牌
echo "🔑 获取API令牌..."
TOKEN_RESPONSE=$(curl -s -X POST ${URL}/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "permissions": ["execute", "read", "write"]
  }' \
  -k)

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 获取令牌失败"
  exit 1
fi

echo "✅ 令牌获取成功: ${TOKEN:0:20}..."

# 健康检查
echo "\n🏥 健康检查..."
curl -s -X GET ${URL}/health \
  -H "Authorization: Bearer $TOKEN" \
  -k | jq .

# 状态检查
echo "\n📊 状态检查..."
curl -s -X GET ${URL}/status \
  -H "Authorization: Bearer $TOKEN" \
  -k | jq .

# 执行基本命令
echo "\n💻 执行基本命令..."
curl -s -X POST ${URL}/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "echo \"Hello World\""}' \
  -k | jq .

# 用户切换测试
echo "\n👤 用户切换测试..."
curl -s -X POST ${URL}/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "sudo -u app bash -c \"whoami && pwd\""}' \
  -k | jq .

echo "\n✅ 所有测试完成"
```

### 6.2 快速测试命令
```bash
# 一键测试所有功能
./test_all_apis.sh
```

## 7. 错误处理

### 常见错误代码

| 状态码 | 说明 | 解决方法 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求体格式和参数 |
| 401 | 认证失败 | 检查Bearer令牌是否有效 |
| 404 | 接口不存在 | 检查URL路径是否正确 |
| 500 | 服务器内部错误 | 查看服务器日志 |

### 错误响应示例
```json
{
  "error": "缺少认证令牌"
}
```

## 8. 安全注意事项

1. **令牌保护**: API令牌具有执行权限，请妥善保管
2. **命令验证**: 服务器会对执行的命令进行安全检查
3. **用户权限**: 确保执行的命令在用户权限范围内
4. **日志记录**: 所有API调用都会被记录在服务器日志中

## 9. 性能建议

1. **连接复用**: 在脚本中复用HTTP连接
2. **批量操作**: 避免频繁的小命令执行
3. **超时设置**: 为长时间运行命令设置适当的超时
4. **资源监控**: 定期检查服务器资源使用情况

## 10. 故障排除

### 10.1 连接问题
```bash
# 检查服务器是否运行
curl -k https://10.0.0.30:8443/health

# 检查网络连通性
ping 10.0.0.30
```

### 10.2 认证问题
```bash
# 重新生成令牌
curl -X POST https://10.0.0.30:8443/auth/api-key ...

# 验证令牌
curl -X POST https://10.0.0.30:8443/auth/verify ...
```

### 10.3 命令执行问题
```bash
# 检查命令语法
curl -X POST ... -d '{"command": "simple_command"}'

# 查看服务器日志
ssh root@10.0.0.30 "tail -f /opt/aiops-agent/logs/server.log"
```

这个文档提供了完整的API测试指南，您可以使用这些curl命令手动测试所有功能。