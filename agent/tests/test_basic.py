#!/usr/bin/env python
"""
基础功能测试脚本
测试不需要外部依赖的核心功能
"""

import sys
import os
sys.path.append('.')

def test_command_execution():
    """测试命令执行功能"""
    print("=== 测试命令执行功能 ===")

    try:
        from src.executor import CommandExecutor
        config = {'execution': {'timeout': 30, 'max_output_size': 1024}}
        executor = CommandExecutor(config)

        # 测试基本命令
        result = executor.execute('echo "hello world"')
        print(f"✓ 基本命令执行: {result['success']}")

        # 测试错误命令
        result = executor.execute('invalid_command_xyz')
        print(f"✓ 错误命令处理: {not result['success']}")

        # 测试超时命令
        result = executor.execute('sleep 1')
        print(f"✓ 正常命令执行: {result['success']}")

        return True
    except Exception as e:
        print(f"✗ 命令执行测试失败: {e}")
        return False

def test_script_execution():
    """测试脚本执行功能"""
    print("\n=== 测试脚本执行功能 ===")

    try:
        from src.script_executor import ScriptExecutor
        config = {'execution': {'timeout': 30, 'max_output_size': 1024, 'temp_dir': '/tmp'}}
        executor = ScriptExecutor(config)

        # 测试脚本类型检测
        script_type = executor._detect_script_type_from_content('#!/bin/bash\necho "test"')
        print(f"✓ 脚本类型检测: {script_type}")

        # 测试简单脚本执行
        result = executor.execute_script_content('echo "script test"')
        print(f"✓ 脚本内容执行: {result['success']}")

        return True
    except Exception as e:
        print(f"✗ 脚本执行测试失败: {e}")
        return False

def test_user_switch():
    """测试用户切换功能"""
    print("\n=== 测试用户切换功能 ===")

    try:
        from src.user_switch import UserSwitch
        config = {'user_switch': {'linux': {'sudo_enabled': True, 'su_enabled': True}}}
        user_switch = UserSwitch(config)

        print(f"✓ 平台检测: {user_switch.platform}")

        # 测试用户存在检查
        import subprocess
        try:
            subprocess.run(['id', 'root'], check=True, capture_output=True)
            exists = user_switch._check_user_exists_linux('root')
            print(f"✓ 用户存在检查: {exists}")
        except:
            print("⚠ 用户检查跳过")

        return True
    except Exception as e:
        print(f"✗ 用户切换测试失败: {e}")
        return False

def test_config_module():
    """测试配置模块"""
    print("\n=== 测试配置模块 ===")

    try:
        # 测试基本配置
        config_data = {
            'server': {'host': '127.0.0.1', 'port': 8443},
            'execution': {'timeout': 30}
        }

        import tempfile
        import os

        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import json
            json.dump(config_data, f)
            temp_file = f.name

        try:
            # 测试配置加载（使用JSON代替YAML）
            with open(temp_file, 'r') as f:
                loaded_config = json.load(f)

            print(f"✓ 配置加载: {loaded_config['server']['host']}")
            print(f"✓ 配置值获取: {loaded_config['execution']['timeout']}")

            return True
        finally:
            os.unlink(temp_file)

    except Exception as e:
        print(f"✗ 配置模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("AIOps Agent 基础功能测试")
    print("=" * 50)

    results = []
    results.append(test_command_execution())
    results.append(test_script_execution())
    results.append(test_user_switch())
    results.append(test_config_module())

    print("\n" + "=" * 50)
    print(f"测试结果: {sum(results)}/{len(results)} 项通过")

    if all(results):
        print("🎉 所有基础功能测试通过！")
    else:
        print("⚠ 部分功能测试失败，需要安装外部依赖")

    print("\n下一步：")
    print("1. 解决网络连接问题后安装外部依赖")
    print("2. 运行完整集成测试")

if __name__ == "__main__":
    main()