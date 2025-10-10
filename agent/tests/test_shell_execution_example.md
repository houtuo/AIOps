# test_shell_execution.py 使用示例

## 脚本概述

`test_shell_execution.py` 是一个用于测试 AIOps Agent shell 执行功能的自动化测试脚本，支持测试基本命令执行、用户切换和动态脚本执行等功能。

## 基本用法

### 1. 查看帮助信息
```bash
python3 tests/test_shell_execution.py --help
```

### 2. 测试单个服务器
```bash
# 测试 10.0.0.30
python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server 30

# 测试 10.0.0.202
python3 tests/test_shell_execution.py --url https://10.0.0.202:8443 --server 202
```

### 3. 同时测试两个服务器
```bash
python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server both
```

## 详细使用示例

### 示例 1：完整测试两个服务器
```bash
python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server both
```

**输出示例：**
```
================================================================================
测试服务器: 10.0.0.30
================================================================================
🚀 开始Shell执行测试 - 目标URL: https://10.0.0.30:8443
============================================================
🔑 获取API令牌...
✅ API令牌获取成功

=== 测试基本shell命令执行 ===
✅ 命令: echo 'Hello World'
   输出: Hello World
   退出码:
✅ 命令: whoami
   输出: root
   退出码:
...
```

### 示例 2：仅测试特定服务器
```bash
# 只测试 RedHat 8 服务器
python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server 30

# 只测试 CentOS 7 服务器
python3 tests/test_shell_execution.py --url https://10.0.0.202:8443 --server 202
```

### 示例 3：自定义URL测试
```bash
# 测试本地开发环境
python3 tests/test_shell_execution.py --url https://localhost:8443 --server 30

# 测试其他服务器
python3 tests/test_shell_execution.py --url https://192.168.1.100:8443 --server both
```

## 参数说明

| 参数 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `--url` | AIOps Agent 服务器URL | 是 | 无 |
| `--server` | 测试服务器选择 | 否 | `both` |
| `-h, --help` | 显示帮助信息 | 否 | 无 |

**server 参数选项：**
- `30`: 只测试 10.0.0.30 (RedHat 8)
- `202`: 只测试 10.0.0.202 (CentOS 7)
- `both`: 同时测试两个服务器

## 测试内容详解

### 1. 基本shell命令执行
- `echo 'Hello World'` - 验证基本输出
- `whoami` - 验证当前用户
- `pwd` - 验证工作目录
- `ls -la /home/app/` - 验证目录列表
- `cat /etc/redhat-release` - 验证系统信息

### 2. 用户切换和目录执行
- `sudo -u app bash -c 'cd /home/app/script && ./test.sh'` - 用户切换和脚本执行
- `sudo -u app bash -c 'cd /home/app/script && pwd'` - 目录切换验证
- `sudo -u app bash -c 'whoami && pwd'` - 用户和目录双重验证

### 3. 动态脚本生成和执行
- **脚本1**: 输出日期、用户、目录信息
- **脚本2**: 获取主机名信息
- **脚本3**: 目录列表和完成提示

## 输出结果说明

### 成功输出示例
```
✅ 命令: echo 'Hello World'
   输出: Hello World
   退出码:
```

### 失败输出示例
```
❌ 命令执行失败: echo 'Hello World'
   状态码: 401
   响应: {"error":"缺少认证令牌"}
```

### 测试统计
```
============================================================
📊 测试结果总结
============================================================
总测试数: 11
通过测试: 11
失败测试: 0
通过率: 100.0%

📄 测试报告已保存: shell_execution_test_report_20251010_093733.json
```

## 生成的报告文件

测试完成后会自动生成JSON格式的详细报告：

- **文件名格式**: `shell_execution_test_report_YYYYMMDD_HHMMSS.json`
- **内容**: 包含所有测试命令、输出结果、时间戳等详细信息
- **用途**: 用于后续分析和问题排查

## 常见问题排查

### 1. 认证失败
**问题**: `{"error":"缺少认证令牌"}`
**解决**: 确保服务器正常运行且API密钥生成接口可用

### 2. 连接超时
**问题**: 连接服务器超时
**解决**: 检查网络连接和服务器状态

### 3. 命令执行失败
**问题**: `{"error":"缺少命令参数"}`
**解决**: 检查服务器端命令执行接口是否正常

### 4. SSL证书警告
**问题**: `InsecureRequestWarning`
**解决**: 这是正常现象，测试脚本使用了`verify=False`忽略证书验证

## 高级用法

### 集成到自动化流程
```bash
#!/bin/bash
# 自动化测试脚本示例

# 运行测试
python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server both

# 检查退出码
if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过"
else
    echo "❌ 测试失败"
    exit 1
fi
```

### 定时测试
```bash
# 添加到crontab，每天凌晨2点运行测试
0 2 * * * cd /home/app/project/AIOps/agent && python3 tests/test_shell_execution.py --url https://10.0.0.30:8443 --server both
```

## 环境要求

- Python 3.6+
- requests 库
- PyYAML 库
- AIOps Agent 服务器运行正常

## 安装依赖

```bash
pip3 install requests PyYAML
```

这个测试脚本提供了完整的shell执行功能验证，可以确保AIOps Agent的远程命令执行功能在生产环境中稳定可靠。