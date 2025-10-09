#!/usr/bin/env python3
"""
API测试脚本

用于测试AIOps代理程序的API接口。
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_health_check(base_url: str) -> bool:
    """测试健康检查接口"""
    print("🧪 测试健康检查接口...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 健康检查成功: {data}")
            return True
        else:
            print(f"  ✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ 健康检查异常: {e}")
        return False


def test_status(base_url: str) -> bool:
    """测试状态查询接口"""
    print("\n🧪 测试状态查询接口...")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 状态查询成功:")
            print(f"    状态: {data.get('status')}")
            print(f"    版本: {data.get('version')}")
            print(f"    平台: {data.get('platform')}")
            print(f"    主机名: {data.get('hostname')}")
            return True
        else:
            print(f"  ✗ 状态查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ 状态查询异常: {e}")
        return False


def test_command_execution(base_url: str) -> bool:
    """测试命令执行接口"""
    print("\n🧪 测试命令执行接口...")
    try:
        test_commands = [
            {"command": "echo 'Hello AIOps'", "description": "简单echo命令"},
            {"command": "ls -la /tmp", "description": "列出目录"},
            {"command": "whoami", "description": "查看当前用户"},
        ]

        success_count = 0
        for test in test_commands:
            print(f"  测试: {test['description']}")
            payload = {
                "command": test["command"]
            }

            response = requests.post(
                f"{base_url}/exec/command",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"    ✓ 执行成功 (返回码: {result.get('return_code')})")
                    success_count += 1
                else:
                    print(f"    ✗ 执行失败: {result.get('error')}")
            else:
                print(f"    ✗ 请求失败: {response.status_code}")

        print(f"  命令执行测试: {success_count}/{len(test_commands)} 成功")
        return success_count == len(test_commands)

    except Exception as e:
        print(f"  ✗ 命令执行测试异常: {e}")
        return False


def test_script_content_execution(base_url: str) -> bool:
    """测试脚本内容执行接口"""
    print("\n🧪 测试脚本内容执行接口...")
    try:
        test_scripts = [
            {
                "script": "#!/bin/bash\necho 'Shell脚本测试'\nls -la /tmp | head -5",
                "description": "Shell脚本"
            },
            {
                "script": "import os\nprint('Python脚本测试')\nprint(f'当前目录: {os.getcwd()}')\nprint(f'用户: {os.getenv(\"USER\", \"unknown\")}')",
                "description": "Python脚本"
            },
        ]

        success_count = 0
        for test in test_scripts:
            print(f"  测试: {test['description']}")
            payload = {
                "script": test["script"]
            }

            response = requests.post(
                f"{base_url}/exec/script/content",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"    ✓ 执行成功 (返回码: {result.get('return_code')})")
                    print(f"      输出: {result.get('output', '')[:100]}...")
                    success_count += 1
                else:
                    print(f"    ✗ 执行失败: {result.get('error')}")
            else:
                print(f"    ✗ 请求失败: {response.status_code}")

        print(f"  脚本内容执行测试: {success_count}/{len(test_scripts)} 成功")
        return success_count == len(test_scripts)

    except Exception as e:
        print(f"  ✗ 脚本内容执行测试异常: {e}")
        return False


def test_dynamic_script_execution(base_url: str) -> bool:
    """测试动态脚本封装执行接口"""
    print("\n🧪 测试动态脚本封装执行接口...")
    try:
        test_script = """
echo '动态脚本封装测试'
date
pwd
ls -la | head -3
"""

        payload = {
            "script": test_script
        }

        response = requests.post(
            f"{base_url}/exec/script/dynamic",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"  ✓ 动态脚本执行成功 (返回码: {result.get('return_code')})")
                print(f"    输出: {result.get('output', '')[:100]}...")
                return True
            else:
                print(f"  ✗ 动态脚本执行失败: {result.get('error')}")
                return False
        else:
            print(f"  ✗ 动态脚本请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ✗ 动态脚本执行测试异常: {e}")
        return False


def test_user_operations(base_url: str) -> bool:
    """测试用户操作接口"""
    print("\n🧪 测试用户操作接口...")
    try:
        # 测试获取用户列表
        print("  测试获取用户列表...")
        response = requests.get(f"{base_url}/users", timeout=10)

        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"    ✓ 获取用户列表成功，共 {len(users)} 个用户")
            if users:
                # 测试获取第一个用户的信息
                first_user = users[0]
                print(f"  测试获取用户信息: {first_user}")

                response = requests.get(f"{base_url}/users/{first_user}", timeout=10)
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"    ✓ 获取用户信息成功")
                    return True
                else:
                    print(f"    ✗ 获取用户信息失败: {response.status_code}")
                    return False
            else:
                print("    ⚠ 用户列表为空")
                return True
        else:
            print(f"    ✗ 获取用户列表失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ✗ 用户操作测试异常: {e}")
        return False


def test_api_key_operations(base_url: str) -> bool:
    """测试API密钥操作接口"""
    print("\n🧪 测试API密钥操作接口...")
    try:
        # 测试生成API密钥
        print("  测试生成API密钥...")
        payload = {
            "user_id": "test_user",
            "permissions": ["exec:command", "exec:script"]
        }

        response = requests.post(
            f"{base_url}/auth/api-key",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            api_key_info = response.json()
            api_key = api_key_info.get('api_key')
            token = api_key_info.get('token')

            if api_key and token:
                print(f"    ✓ 生成API密钥成功")

                # 测试验证API密钥
                print("  测试验证API密钥...")
                verify_payload = {
                    "api_key": api_key,
                    "token": token
                }

                response = requests.post(
                    f"{base_url}/auth/verify",
                    json=verify_payload,
                    timeout=10
                )

                if response.status_code == 200:
                    verify_result = response.json()
                    if verify_result.get('valid'):
                        print(f"    ✓ API密钥验证成功")
                        return True
                    else:
                        print(f"    ✗ API密钥验证失败")
                        return False
                else:
                    print(f"    ✗ API密钥验证请求失败: {response.status_code}")
                    return False
            else:
                print(f"    ✗ 生成API密钥返回数据不完整")
                return False
        else:
            print(f"    ✗ 生成API密钥失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ✗ API密钥操作测试异常: {e}")
        return False


def run_all_tests(base_url: str) -> bool:
    """运行所有测试"""
    print("🚀 开始AIOps代理程序API测试")
    print("=" * 60)

    test_functions = [
        ("健康检查", test_health_check),
        ("状态查询", test_status),
        ("命令执行", test_command_execution),
        ("脚本内容执行", test_script_content_execution),
        ("动态脚本执行", test_dynamic_script_execution),
        ("用户操作", test_user_operations),
        ("API密钥操作", test_api_key_operations),
    ]

    results = []
    for test_name, test_func in test_functions:
        start_time = time.time()
        success = test_func(base_url)
        elapsed_time = time.time() - start_time
        results.append((test_name, success, elapsed_time))

    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)

    for test_name, success, elapsed_time in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {test_name:20} {status:10} ({elapsed_time:.2f}s)")

    print(f"\n🎯 总体结果: {passed_tests}/{total_tests} 测试通过")

    if passed_tests == total_tests:
        print("✅ 所有测试通过！AIOps代理程序API功能正常。")
        return True
    else:
        print("❌ 部分测试失败，请检查代理程序配置和运行状态。")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AIOps代理程序API测试工具')
    parser.add_argument('--url', default='http://localhost:8443',
                       help='代理程序URL (默认: http://localhost:8443)')
    parser.add_argument('--test', choices=['all', 'health', 'status', 'command', 'script', 'dynamic', 'user', 'auth'],
                       default='all', help='选择要运行的测试 (默认: all)')

    args = parser.parse_args()

    base_url = args.url.rstrip('/')

    try:
        if args.test == 'all':
            success = run_all_tests(base_url)
            sys.exit(0 if success else 1)
        else:
            # 运行单个测试
            test_functions = {
                'health': test_health_check,
                'status': test_status,
                'command': test_command_execution,
                'script': test_script_content_execution,
                'dynamic': test_dynamic_script_execution,
                'user': test_user_operations,
                'auth': test_api_key_operations,
            }

            if args.test in test_functions:
                success = test_functions[args.test](base_url)
                sys.exit(0 if success else 1)
            else:
                print(f"未知的测试类型: {args.test}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()