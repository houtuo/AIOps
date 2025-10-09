#!/usr/bin/env python
"""
本地测试脚本
用于验证AIOps Agent的核心功能
"""

import sys
import os
sys.path.append('.')

def test_core_modules():
    """测试核心模块"""
    print("=== 测试核心模块 ===")

    try:
        from src.executor import CommandExecutor
        config = {'execution': {'timeout': 30, 'max_output_size': 1024}}
        executor = CommandExecutor(config)
        result = executor.execute('echo "hello world"')
        print(f"✓ 命令执行器: {result['success']}")
    except Exception as e:
        print(f"✗ 命令执行器: {e}")

    try:
        from src.script_executor import ScriptExecutor
        config = {'execution': {'timeout': 30, 'max_output_size': 1024, 'temp_dir': '/tmp'}}
        executor = ScriptExecutor(config)
        result = executor.execute_script_content('echo "script test"')
        print(f"✓ 脚本执行器: {result['success']}")
    except Exception as e:
        print(f"✗ 脚本执行器: {e}")

    try:
        from src.security import SecurityManager
        config = {'security': {'jwt_secret': 'test-secret', 'aes_key': 'test-key-32-bytes-long-key-12345'}}
        security = SecurityManager(config)
        token = security.generate_jwt_token({'user_id': 'test'})
        decoded = security.verify_jwt_token(token)
        print(f"✓ 安全模块: JWT验证成功")
    except Exception as e:
        print(f"✗ 安全模块: {e}")

    try:
        from src.user_switch import UserSwitch
        config = {'user_switch': {'linux': {'sudo_enabled': True, 'su_enabled': True}}}
        user_switch = UserSwitch(config)
        print(f"✓ 用户切换模块: 平台={user_switch.platform}")
    except Exception as e:
        print(f"✗ 用户切换模块: {e}")

def test_server():
    """测试服务器"""
    print("\n=== 测试服务器 ===")

    try:
        from src.server import AgentServer
        config = {
            'server': {'host': '127.0.0.1', 'port': 8443, 'debug': False},
            'security': {'jwt_secret': 'test-secret', 'aes_key': 'test-key-32-bytes-long-key-12345'},
            'execution': {'timeout': 30, 'max_output_size': 1024}
        }
        server = AgentServer(config)
        app = server.create_app()

        print(f"✓ 服务器创建成功: {app.name}")

        # 检查路由
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(f"{list(rule.methods)[0]} {rule.rule}")

        print(f"✓ 路由数量: {len(routes)}")
        print("主要路由:")
        for route in sorted(routes)[:10]:  # 显示前10个路由
            print(f"  {route}")

    except Exception as e:
        print(f"✗ 服务器测试失败: {e}")

def test_scripts():
    """测试脚本"""
    print("\n=== 测试脚本 ===")

    try:
        from scripts.generate_keys import generate_keys
        print("✓ 密钥生成脚本导入成功")
    except Exception as e:
        print(f"✗ 密钥生成脚本: {e}")

    try:
        from scripts.test_api import test_api
        print("✓ API测试脚本导入成功")
    except Exception as e:
        print(f"✗ API测试脚本: {e}")

if __name__ == "__main__":
    print("AIOps Agent 本地测试")
    print("=" * 50)

    test_core_modules()
    test_server()
    test_scripts()

    print("\n" + "=" * 50)
    print("本地测试完成！")
    print("\n下一步：")
    print("1. 在测试环境解决yum源问题")
    print("2. 安装Python3和相关依赖")
    print("3. 运行集成测试")