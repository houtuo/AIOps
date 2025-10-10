# AIOps Agent 快速测试指南

## 🚀 快速开始

### 1. 使用自动化测试脚本（推荐）

```bash
# 完整测试所有API功能
./test_all_apis.sh

# 测试指定服务器
./test_all_apis.sh -s 10.0.0.202

# 只获取API令牌
./test_all_apis.sh -g

# 清理令牌文件
./test_all_apis.sh -c
```

### 2. 使用Python测试脚本

```bash
# 完整测试两个服务器
python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server both

# 测试单个服务器
python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server 30
```

## 🔑 手动测试（curl命令）

### 获取API令牌
```bash
curl -X POST https://10.0.0.30:8443/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","permissions":["execute","read","write"]}' \
  -k
```

### 保存令牌
```bash
export TOKEN="你的令牌"
```

### 基本功能测试

```bash
# 健康检查
curl -X GET https://10.0.0.30:8443/health -H "Authorization: Bearer $TOKEN" -k

# 状态检查
curl -X GET https://10.0.0.30:8443/status -H "Authorization: Bearer $TOKEN" -k

# 执行命令
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command":"echo \"Hello World\""}' \
  -k

# 用户切换
curl -X POST https://10.0.0.30:8443/exec/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command":"sudo -u app bash -c \"whoami && pwd\""}' \
  -k
```

## 📋 测试清单

### ✅ 必测功能
- [ ] 获取API令牌
- [ ] 健康检查
- [ ] 状态检查
- [ ] 基本命令执行
- [ ] 用户切换执行
- [ ] 动态脚本执行

### 🔧 可选测试
- [ ] 用户信息查询
- [ ] 脚本文件执行
- [ ] API密钥验证

## 🎯 关键验证点

1. **认证系统**: 确保Bearer令牌正常工作
2. **命令执行**: 验证shell命令可以正确执行
3. **用户权限**: 测试用户切换功能
4. **脚本执行**: 验证动态脚本生成和执行
5. **跨服务器**: 在两个服务器上测试兼容性

## ⚡ 一键测试

创建快速测试脚本 `quick_test.sh`:

```bash
#!/bin/bash
./test_all_apis.sh && python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server both
```

## 📊 预期结果

- ✅ 所有API调用返回200状态码
- ✅ 命令执行输出正确
- ✅ 用户切换功能正常
- ✅ 动态脚本可以执行
- ✅ 两个服务器表现一致

## 🔍 故障排除

### 常见问题
1. **认证失败**: 重新获取令牌
2. **连接超时**: 检查服务器状态
3. **命令失败**: 验证命令语法
4. **权限错误**: 检查用户权限

### 调试命令
```bash
# 检查服务器状态
ssh root@10.0.0.30 "systemctl status aiops-agent"

# 查看日志
ssh root@10.0.0.30 "tail -f /opt/aiops-agent/logs/server.log"

# 检查网络
ping 10.0.0.30
```

## 📞 支持信息

- **文档**: 查看 `API_TESTING_GUIDE.md` 获取详细API说明
- **脚本**: 使用提供的自动化测试脚本
- **日志**: 检查服务器日志获取详细错误信息

---

**提示**: 建议先使用自动化脚本进行完整测试，再使用curl命令进行针对性测试。