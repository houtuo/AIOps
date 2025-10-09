# AIOps Agent 测试手册

## 目录
- [测试环境要求](#测试环境要求)
- [测试类型说明](#测试类型说明)
- [单元测试](#单元测试)
- [集成测试](#集成测试)
- [功能测试](#功能测试)
- [性能测试](#性能测试)
- [安全测试](#安全测试)
- [API测试用例](#api测试用例)
- [自动化测试脚本](#自动化测试脚本)
- [测试报告](#测试报告)

---

## 测试环境要求

### 硬件环境
- **CPU**: 2核或以上
- **内存**: 2GB或以上
- **磁盘**: 1GB可用空间

### 软件环境
- **操作系统**: Linux (CentOS 7+, Ubuntu 18.04+) 或 Windows Server 2012+
- **Python**: 3.8或以上版本
- **网络**: 可访问测试服务器

### 测试工具
- **pytest**: 单元测试框架
- **curl**: API测试工具
- **requests**: Python HTTP库（可选）

---

## 测试类型说明

### 1. 单元测试
- **目的**: 验证单个模块/函数的功能正确性
- **范围**: 所有核心模块
- **工具**: pytest

### 2. 集成测试
- **目的**: 验证模块间的协作和接口
- **范围**: 模块间调用、API接口
- **工具**: pytest + 自定义测试脚本

### 3. 功能测试
- **目的**: 验证系统功能是否符合需求
- **范围**: 所有用户可见功能
- **工具**: 手动测试 + 自动化脚本

### 4. 性能测试
- **目的**: 验证系统性能和稳定性
- **范围**: 并发处理、资源使用
- **工具**: 自定义测试脚本

### 5. 安全测试
- **目的**: 验证系统安全性
- **范围**: 认证、授权、数据保护
- **工具**: 手动测试 + 安全扫描

---

## 单元测试

### 测试文件结构
```
tests/
├── test_config.py          # 配置模块测试
├── test_executor.py        # 命令执行器测试
├── test_script_executor.py # 脚本执行器测试
├── test_security.py        # 安全模块测试
└── test_user_switch.py     # 用户切换模块测试
```

### 运行单元测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_config.py -v

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 运行测试并输出详细报告
pytest tests/ -v --tb=short

# 运行失败的测试
pytest tests/ --lf
```

### 测试用例覆盖

#### 1. 配置模块测试 (test_config.py)

| 测试用例 | 描述 | 预期结果 |
|---------|------|----------|
| test_load_config_success | 成功加载配置文件 | 配置数据正确加载 |
| test_load_config_file_not_exists | 加载不存在的配置文件 | 抛出FileNotFoundError |
| test_get_config_value | 获取配置值 | 正确返回配置值 |
| test_override_with_env_variables | 环境变量覆盖配置 | 环境变量优先级更高 |
| test_singleton_pattern | 单例模式验证 | 返回相同实例 |
| test_reload_config | 重新加载配置 | 配置正确更新 |
| test_get_with_default_value | 使用默认值获取配置 | 正确返回默认值 |
| test_nested_config_get | 嵌套配置获取 | 正确返回嵌套配置 |
| test_config_with_special_characters | 特殊字符配置 | 正确处理特殊字符 |

#### 2. 命令执行器测试 (test_executor.py)

| 测试用例 | 描述 | 预期结果 |
|---------|------|----------|
| test_execute_success | 成功执行命令 | 返回成功结果 |
| test_execute_failure | 执行失败命令 | 返回失败结果 |
| test_execute_timeout | 执行超时命令 | 正确处理超时 |
| test_validate_command_safe | 验证安全命令 | 通过验证 |
| test_validate_command_empty | 验证空命令 | 拒绝空命令 |
| test_prepare_command_with_user_linux | Linux用户切换命令 | 正确格式化命令 |
| test_prepare_command_with_user_windows | Windows用户切换命令 | 正确格式化命令 |

#### 3. 脚本执行器测试 (test_script_executor.py)

| 测试用例 | 描述 | 预期结果 |
|---------|------|----------|
| test_detect_script_type_from_content | 从内容检测脚本类型 | 正确识别脚本类型 |
| test_create_temp_script | 创建临时脚本文件 | 文件正确创建 |
| test_cleanup_temp_file | 清理临时文件 | 文件正确删除 |
| test_execute_script_content | 执行脚本内容 | 脚本正确执行 |
| test_execute_dynamic_wrapper | 执行动态包装脚本 | 正确生成和执行 |
| test_detect_script_type_by_extension | 通过扩展名检测类型 | 正确识别类型 |
| test_detect_script_type_by_shebang | 通过shebang检测类型 | 正确识别类型 |
| test_execute_script_file_not_exists | 执行不存在的脚本文件 | 返回错误 |
| test_execute_python_script | 执行Python脚本 | Python脚本正确执行 |
| test_execute_shell_script | 执行Shell脚本 | Shell脚本正确执行 |

#### 4. 安全模块测试 (test_security.py)

| 测试用例 | 描述 | 预期结果 |
|---------|------|----------|
| test_generate_and_verify_jwt_token | 生成和验证JWT令牌 | 令牌正确生成和验证 |
| test_verify_expired_token | 验证过期令牌 | 过期令牌验证失败 |
| test_encrypt_and_decrypt_data | 加密和解密数据 | 数据正确加密解密 |
| test_generate_api_key | 生成API密钥 | 正确生成API密钥 |
| test_verify_api_key | 验证API密钥 | 正确验证API密钥 |
| test_hash_password | 密码哈希 | 正确生成哈希 |
| test_verify_password | 验证密码 | 正确验证密码 |
| test_generate_random_key | 生成随机密钥 | 正确生成随机密钥 |
| test_validate_token_permissions | 验证令牌权限 | 正确验证权限 |

#### 5. 用户切换模块测试 (test_user_switch.py)

| 测试用例 | 描述 | 预期结果 |
|---------|------|----------|
| test_execute_as_user_linux | Linux用户切换执行 | 正确切换用户执行 |
| test_execute_as_user_windows | Windows用户切换执行 | 正确切换用户执行 |
| test_execute_as_user_unsupported_platform | 不支持平台用户切换 | 返回错误 |
| test_execute_as_user_nonexistent_user | 不存在的用户切换 | 返回错误 |
| test_check_user_exists_linux_exists | Linux用户存在检查 | 正确检查用户存在 |
| test_check_user_exists_linux_not_exists | Linux用户不存在检查 | 正确检查用户不存在 |
| test_check_user_exists_windows_exists | Windows用户存在检查 | 正确检查用户存在 |
| test_check_user_exists_windows_not_exists | Windows用户不存在检查 | 正确检查用户不存在 |
| test_get_user_info_linux | Linux用户信息获取 | 正确获取用户信息 |
| test_get_user_info_linux_not_exists | Linux不存在的用户信息获取 | 返回错误 |
| test_get_user_info_windows | Windows用户信息获取 | 正确获取用户信息 |
| test_get_available_users_linux | Linux可用用户列表 | 正确获取用户列表 |
| test_get_available_users_windows | Windows可用用户列表 | 正确获取用户列表 |
| test_validate_user_permissions_linux | Linux用户权限验证 | 正确验证权限 |
| test_validate_user_permissions_user_not_exists | 不存在的用户权限验证 | 返回错误 |

---

## 集成测试

### 基础功能测试 (test_basic.py)

```bash
# 运行基础功能测试
python test_basic.py
```

**测试内容**:
- 命令执行功能
- 脚本执行功能
- 用户切换功能
- 配置模块功能

### 本地模块测试 (test_local.py)

```bash
# 运行本地模块测试
python test_local.py
```

**测试内容**:
- 所有核心模块导入测试
- 服务器创建测试
- 路由注册测试
- 脚本导入测试

---

## 功能测试

### 服务器功能测试

#### 1. 健康检查测试

**测试步骤**:
1. 启动服务器
2. 访问健康检查接口
3. 验证响应状态

**预期结果**:
```json
{
  "service": "aiops-agent",
  "status": "healthy"
}
```

#### 2. 状态信息测试

**测试步骤**:
1. 访问状态接口
2. 验证系统信息

**预期结果**:
```json
{
  "hostname": "wls01",
  "platform": "linux",
  "status": "running",
  "version": "1.0.0"
}
```

#### 3. 用户管理测试

**测试步骤**:
1. 获取用户列表
2. 获取特定用户信息
3. 验证用户信息完整性

**预期结果**:
- 用户列表包含系统用户
- 用户信息包含UID、GID、家目录等

---

## API测试用例

### 认证相关API

#### 1. 生成API密钥

**请求**:
```bash
curl -k -X POST https://localhost:8443/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "permissions": ["exec:command", "exec:script"]
  }'
```

**预期响应**:
```json
{
  "api_key": "UXJJiKc-DfMBJ8ZcfGceVE726k-xhOKudDYkmqTBwz4=",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**测试要点**:
- 验证API密钥格式
- 验证JWT令牌有效性
- 验证权限列表正确设置

#### 2. 验证API密钥

**请求**:
```bash
curl -k -X POST https://localhost:8443/auth/verify \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "UXJJiKc-DfMBJ8ZcfGceVE726k-xhOKudDYkmqTBwz4=",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**预期响应**:
```json
{
  "valid": true
}
```

**测试要点**:
- 验证有效令牌
- 验证过期令牌
- 验证无效令牌

### 执行相关API

#### 1. 命令执行

**请求**:
```bash
curl -k -X POST https://localhost:8443/exec/command \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "whoami",
    "user": "root"
  }'
```

**预期响应**:
```json
{
  "error": "",
  "output": "root\n",
  "return_code": 0,
  "success": true
}
```

**测试要点**:
- 基本命令执行
- 复杂命令执行
- 错误命令处理
- 超时命令处理
- 用户切换执行

#### 2. 脚本内容执行

**请求**:
```bash
curl -k -X POST https://localhost:8443/exec/script/content \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "echo Hello World",
    "user": "root"
  }'
```

**预期响应**:
```json
{
  "error": "",
  "output": "Hello World\n",
  "return_code": 0,
  "success": true
}
```

**测试要点**:
- Shell脚本执行
- Python脚本执行
- 多行脚本执行
- 带参数脚本执行

#### 3. 动态脚本执行

**请求**:
```bash
curl -k -X POST https://localhost:8443/exec/script/dynamic \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "shell",
    "code": "echo \"Dynamic script\" && date",
    "user": "root"
  }'
```

**预期响应**:
```json
{
  "error": "",
  "output": "Dynamic script\nWed Oct 9 22:45:01 UTC 2025\n",
  "return_code": 0,
  "success": true
}
```

**测试要点**:
- 动态脚本生成
- 不同语言支持
- 代码注入防护

### 用户相关API

#### 1. 获取用户列表

**请求**:
```bash
curl -k https://localhost:8443/users \
  -H "Authorization: Bearer <token>"
```

**预期响应**:
```json
{
  "users": ["root", "bin", "daemon", "adm", "lp", ...]
}
```

#### 2. 获取用户信息

**请求**:
```bash
curl -k https://localhost:8443/users/root \
  -H "Authorization: Bearer <token>"
```

**预期响应**:
```json
{
  "username": "root",
  "uid": "0",
  "gid": "0",
  "home": "/root",
  "shell": "/bin/bash",
  "gecos": "root"
}
```

---

## 性能测试

### 并发测试

**测试脚本**: `test_performance.py`

**测试场景**:
- 10个并发命令执行
- 100个并发健康检查
- 混合负载测试

**指标监控**:
- 响应时间
- 内存使用
- CPU使用率
- 错误率

### 压力测试

**测试步骤**:
1. 持续运行命令执行30分钟
2. 监控系统资源
3. 检查内存泄漏
4. 验证服务稳定性

---

## 安全测试

### 1. 认证测试

**测试用例**:
- 无效令牌访问
- 过期令牌访问
- 缺少认证头访问
- 权限不足访问

### 2. 输入验证测试

**测试用例**:
- 命令注入测试
- SQL注入测试
- 路径遍历测试
- 缓冲区溢出测试

### 3. 数据保护测试

**测试用例**:
- 敏感数据加密
- 日志中不记录敏感信息
- 传输数据加密
- 密钥安全存储

---

## 自动化测试脚本

### 完整集成测试脚本

创建 `test_integration.py` 脚本，包含：

1. **环境检查**
   - Python版本检查
   - 依赖包检查
   - 配置文件检查

2. **模块测试**
   - 所有核心模块功能测试
   - 错误处理测试
   - 边界条件测试

3. **API测试**
   - 所有API接口测试
   - 认证流程测试
   - 错误响应测试

4. **性能测试**
   - 响应时间测试
   - 并发处理测试
   - 资源使用测试

5. **安全测试**
   - 认证授权测试
   - 输入验证测试
   - 数据保护测试

### 测试报告生成

**报告内容**:
- 测试执行摘要
- 通过/失败统计
- 详细错误信息
- 性能指标
- 安全评估

**报告格式**:
- HTML报告
- JSON报告
- 控制台输出

---

## 测试执行流程

### 1. 环境准备

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成密钥
python scripts/generate_keys.py

# 3. 启动服务器
python src/server.py &

# 4. 等待服务器启动
sleep 5
```

### 2. 执行测试

```bash
# 1. 运行单元测试
pytest tests/ -v

# 2. 运行集成测试
python test_integration.py

# 3. 运行性能测试
python test_performance.py

# 4. 运行安全测试
python test_security.py
```

### 3. 生成报告

```bash
# 生成测试报告
python generate_test_report.py

# 查看报告
open test_reports/report.html
```

---

## 测试数据管理

### 测试数据

**用户数据**:
- 测试用户账号
- 权限配置
- API密钥

**命令数据**:
- 安全命令列表
- 危险命令列表
- 性能测试命令

**脚本数据**:
- 测试脚本模板
- 错误脚本示例
- 性能测试脚本

### 数据清理

**清理策略**:
- 测试前备份重要数据
- 测试后清理临时文件
- 恢复测试环境

---

## 故障排除

### 常见测试问题

#### 1. 测试环境问题

**问题**: 依赖包缺失
**解决**: `pip install -r requirements.txt`

**问题**: Python版本不兼容
**解决**: 使用Python 3.8+

#### 2. 服务器问题

**问题**: 端口被占用
**解决**: 更改端口或杀死占用进程

**问题**: SSL证书错误
**解决**: 重新生成证书

#### 3. 测试执行问题

**问题**: 测试超时
**解决**: 增加超时时间或优化测试

**问题**: 权限不足
**解决**: 以适当权限运行测试

### 调试技巧

#### 1. 日志调试

```bash
# 查看详细日志
tail -f logs/aiops-agent.log

# 启用调试模式
export AIOPS_LOG_LEVEL=DEBUG
```

#### 2. API调试

```bash
# 使用详细输出
curl -v -k https://localhost:8443/health

# 查看请求头
curl -I -k https://localhost:8443/health
```

#### 3. 性能调试

```bash
# 监控系统资源
top

# 监控网络连接
netstat -tlnp
```

---

## 测试验收标准

### 必须通过
- ✅ 所有单元测试通过
- ✅ 核心功能测试通过
- ✅ 安全测试通过
- ✅ 性能基准测试通过

### 推荐通过
- ✅ 集成测试通过率 > 90%
- ✅ API测试通过率 > 95%
- ✅ 性能测试指标达标

### 验收流程

1. **开发环境测试** - 开发者执行
2. **测试环境测试** - 测试团队执行
3. **生产环境测试** - 运维团队执行
4. **用户验收测试** - 最终用户执行

---

## 测试工具推荐

### 自动化测试工具
- **pytest**: Python测试框架
- **unittest**: Python标准测试库
- **coverage**: 代码覆盖率工具
- **tox**: 多环境测试工具

### API测试工具
- **curl**: 命令行HTTP客户端
- **Postman**: GUI API测试工具
- **requests**: Python HTTP库
- **httpie**: 用户友好的HTTP客户端

### 性能测试工具
- **locust**: Python负载测试工具
- **ab**: Apache基准测试工具
- **wrk**: 现代HTTP基准测试工具

### 安全测试工具
- **bandit**: Python安全扫描工具
- **safety**: 依赖包安全检查
- **OWASP ZAP**: Web应用安全扫描

---

## 附录

### A. 测试用例模板

```python
class TestTemplate:
    """测试用例模板"""

    def setup_method(self):
        """测试前准备"""
        pass

    def teardown_method(self):
        """测试后清理"""
        pass

    def test_example(self):
        """示例测试用例"""
        # 准备
        input_data = "test"
        expected_output = "expected"

        # 执行
        actual_output = function_under_test(input_data)

        # 验证
        assert actual_output == expected_output
```

### B. API测试模板

```python
import requests

def test_api_endpoint():
    """API端点测试模板"""

    # 准备
    url = "https://localhost:8443/health"
    headers = {
        "Authorization": "Bearer token",
        "Content-Type": "application/json"
    }

    # 执行
    response = requests.get(url, headers=headers, verify=False)

    # 验证
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### C. 性能测试模板

```python
import time
import threading

def test_performance():
    """性能测试模板"""

    def worker():
        """工作线程"""
        # 执行测试操作
        pass

    # 启动多个线程
    threads = []
    start_time = time.time()

    for i in range(10):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    end_time = time.time()

    # 计算性能指标
    total_time = end_time - start_time
    print(f"总执行时间: {total_time:.2f}秒")
```

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-09
