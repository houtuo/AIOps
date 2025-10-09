# AIOps Agent 测试目录

## 目录结构

```
tests/
├── README.md                    # 本文档
├── run_tests.sh                # 自动化测试执行脚本
├── test_basic.py               # 基础功能测试
├── test_local.py               # 本地模块测试
├── test_integration.py         # 集成测试
├── test_performance.py         # 性能测试
├── test_config.py              # 配置模块单元测试
├── test_executor.py            # 命令执行器单元测试
├── test_script_executor.py     # 脚本执行器单元测试
├── test_security.py            # 安全模块单元测试
├── test_user_switch.py         # 用户切换模块单元测试
└── test_reports/               # 测试报告目录
```

## 测试类型说明

### 🔧 单元测试
- **文件**: `test_*.py` (除集成和性能测试外)
- **目的**: 验证单个模块/函数的功能正确性
- **运行**: `pytest tests/ -v`

### 🔗 集成测试
- **文件**: `test_integration.py`
- **目的**: 验证模块间的协作和API接口
- **运行**: `python tests/test_integration.py`

### ⚡ 性能测试
- **文件**: `test_performance.py`
- **目的**: 验证系统性能和稳定性
- **运行**: `python tests/test_performance.py`

### 🧪 功能测试
- **文件**: `test_basic.py`, `test_local.py`
- **目的**: 验证系统基本功能
- **运行**: `python tests/test_basic.py`

## 快速开始

### 运行所有测试
```bash
# 使用自动化脚本（推荐）
./tests/run_tests.sh

# 或手动运行
cd tests
./run_tests.sh
```

### 运行特定测试
```bash
# 运行单元测试
pytest tests/ -v

# 运行集成测试
python tests/test_integration.py --auth-token <token>

# 运行性能测试
python tests/test_performance.py --duration 120

# 运行基础功能测试
python tests/test_basic.py

# 运行本地模块测试
python tests/test_local.py
```

## 测试报告

测试报告会自动生成在 `test_reports/` 目录中：

- **集成测试报告**: `integration_test_YYYYMMDD_HHMMSS.json`
- **性能测试报告**: `performance_test_YYYYMMDD_HHMMSS.json`
- **测试摘要**: `test_summary_YYYYMMDD_HHMMSS.txt`

## 测试配置

### 环境变量
```bash
# 设置服务器URL
export AIOPS_SERVER_URL=https://localhost:8443

# 设置认证令牌
export AIOPS_AUTH_TOKEN=your-token-here

# 设置日志级别
export AIOPS_LOG_LEVEL=DEBUG
```

### 命令行参数

#### 集成测试
```bash
python tests/test_integration.py \
  --server-url https://localhost:8443 \
  --auth-token your-token \
  --output-format console
```

#### 性能测试
```bash
python tests/test_performance.py \
  --server-url https://localhost:8443 \
  --auth-token your-token \
  --duration 60
```

## 测试依赖

确保安装以下依赖包：

```bash
pip install pytest requests psutil
```

## 故障排除

### 常见问题

1. **服务器连接失败**
   ```bash
   # 检查服务器是否运行
   curl -k https://localhost:8443/health

   # 启动服务器
   python src/server.py
   ```

2. **认证失败**
   ```bash
   # 生成API密钥
   python scripts/generate_keys.py

   # 获取认证令牌
   curl -k -X POST https://localhost:8443/auth/api-key \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_user", "permissions": ["exec:command"]}'
   ```

3. **依赖包缺失**
   ```bash
   # 安装测试依赖
   pip install -r requirements.txt
   pip install pytest requests psutil
   ```

### 调试模式

启用详细日志输出：

```bash
# 设置环境变量
export AIOPS_LOG_LEVEL=DEBUG

# 运行测试
./tests/run_tests.sh
```

## 测试覆盖率

要生成测试覆盖率报告：

```bash
# 安装覆盖率工具
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看报告
open htmlcov/index.html
```

## 持续集成

测试脚本支持在CI/CD环境中运行：

```yaml
# GitHub Actions 示例
name: AIOps Agent Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest requests psutil
      - name: Run tests
        run: ./tests/run_tests.sh
```

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-09