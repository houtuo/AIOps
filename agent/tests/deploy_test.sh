#!/bin/bash

# AIOps Agent 部署测试脚本
# 用于在测试环境 10.0.0.201 上进行集成测试

echo "=== AIOps Agent 部署测试 ==="

# 检查当前环境
echo "1. 检查当前环境..."
pwd
ls -la

# 生成密钥
echo "2. 生成密钥..."
python scripts/generate_keys.py

# 检查配置文件
echo "3. 检查配置文件..."
ls -la config/

# 测试模块导入
echo "4. 测试模块导入..."
python -c "
import sys
sys.path.append('.')
try:
    from src.executor import CommandExecutor
    from src.script_executor import ScriptExecutor
    from src.security import SecurityManager
    from src.user_switch import UserSwitch
    print('✓ 所有核心模块导入成功')
except Exception as e:
    print(f'✗ 模块导入失败: {e}')
"

# 运行单元测试
echo "5. 运行单元测试..."
python -m pytest tests/ -v

echo "=== 部署测试完成 ==="
echo ""
echo "下一步："
echo "1. 将项目复制到测试环境 10.0.0.201"
echo "2. 在测试环境运行此脚本"
echo "3. 启动服务器: python src/server.py"
echo "4. 运行API测试: python scripts/test_api.py"