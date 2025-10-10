#!/usr/bin/env python3
"""
AIOps Agent Shell 执行测试脚本

测试功能：
1. 执行shell命令
2. 使用app用户切换到/home/app/script目录执行test.sh脚本
3. 传入shell脚本内容，随机生成脚本名称并使用app用户执行

使用方式：
python3 test_shell_execution.py --url https://localhost:8443
"""

import argparse
import requests
import json
import random
import string
import time
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.security import SecurityManager
import yaml


def generate_random_filename(prefix="test_script", extension=".sh"):
    """生成随机文件名"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{random_str}{extension}"


def get_api_token(url, security_manager):
    """获取API令牌"""
    try:
        # 生成API密钥
        payload = {
            "user_id": "test_user",
            "permissions": ["execute", "read", "write"]
        }

        response = requests.post(f"{url}/auth/api-key", json=payload, verify=False)

        if response.status_code == 200:
            api_key_info = response.json()
            return api_key_info.get("token")
        else:
            print(f"❌ 获取API令牌失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取API令牌异常: {str(e)}")
        return None


def test_basic_shell_command(url, security_manager, token):
    """测试基本shell命令执行"""
    print("\n=== 测试基本shell命令执行 ===")

    # 测试简单的shell命令
    commands = [
        {
            "command": "echo 'Hello World'"
        },
        {
            "command": "whoami"
        },
        {
            "command": "pwd"
        },
        {
            "command": "ls -la /home/app/"
        },
        {
            "command": "cat /etc/redhat-release"
        }
    ]

    results = []
    for cmd in commands:
        try:
            payload = cmd

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = requests.post(f"{url}/exec/command", json=payload, headers=headers, verify=False)

            if response.status_code == 200:
                result_data = response.json()
                result = result_data

                print(f"✅ 命令: {cmd['command']}")
                print(f"   输出: {result.get('output', '')}")
                print(f"   退出码: {result.get('return_code', '')}")

                results.append({
                    "command": cmd['command'],
                    "success": True,
                    "output": result.get('output', ''),
                    "exit_code": result.get('return_code', '')
                })
            else:
                print(f"❌ 命令执行失败: {cmd['command']}")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.text}")

                results.append({
                    "command": cmd['command'],
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })

        except Exception as e:
            print(f"❌ 命令执行异常: {cmd['command']}")
            print(f"   异常: {str(e)}")

            results.append({
                "command": cmd['command'],
                "success": False,
                "error": str(e)
            })

    return results


def test_user_switch_and_directory(url, security_manager, token):
    """测试用户切换和目录切换"""
    print("\n=== 测试用户切换和目录执行 ===")

    # 测试切换到app用户并在指定目录执行脚本
    commands = [
        {
            "command": "sudo -u app bash -c 'cd /home/app/script && ./test.sh'"
        },
        {
            "command": "sudo -u app bash -c 'cd /home/app/script && pwd'"
        },
        {
            "command": "sudo -u app bash -c 'whoami && pwd'"
        }
    ]

    results = []
    for cmd in commands:
        try:
            payload = cmd

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = requests.post(f"{url}/exec/command", json=payload, headers=headers, verify=False)

            if response.status_code == 200:
                result_data = response.json()
                result = result_data

                print(f"✅ 命令: {cmd['command']}")
                print(f"   输出: {result.get('output', '')}")
                print(f"   退出码: {result.get('return_code', '')}")

                results.append({
                    "command": cmd['command'],
                    "success": True,
                    "output": result.get('output', ''),
                    "exit_code": result.get('return_code', '')
                })
            else:
                print(f"❌ 命令执行失败: {cmd['command']}")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.text}")

                results.append({
                    "command": cmd['command'],
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })

        except Exception as e:
            print(f"❌ 命令执行异常: {cmd['command']}")
            print(f"   异常: {str(e)}")

            results.append({
                "command": cmd['command'],
                "success": False,
                "error": str(e)
            })

    return results


def test_dynamic_script_execution(url, security_manager, token):
    """测试动态脚本生成和执行"""
    print("\n=== 测试动态脚本生成和执行 ===")

    # 生成随机脚本内容
    script_contents = [
        """#!/bin/bash
echo "动态脚本测试 - 版本 1"
date
whoami
pwd
""",
        """#!/bin/bash
echo "动态脚本测试 - 版本 2"
hostname
cat /etc/hostname
""",
        """#!/bin/bash
echo "动态脚本测试 - 版本 3"
ls -la /tmp/
echo "脚本执行完成"
"""
    ]

    results = []
    for i, script_content in enumerate(script_contents):
        random_filename = generate_random_filename(f"dynamic_script_{i}")

        # 创建脚本文件并执行的命令
        command = f"""
script_content='{script_content.replace("'", "'\\''")}'
random_filename="/tmp/{random_filename}"
echo "$script_content" > "$random_filename"
chmod +x "$random_filename"
sudo -u app bash -c "$random_filename"
rm -f "$random_filename"
"""

        cmd = {
            "command": command
        }

        try:
            payload = cmd

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = requests.post(f"{url}/exec/command", json=payload, headers=headers, verify=False)

            if response.status_code == 200:
                result_data = response.json()
                result = result_data

                print(f"✅ 动态脚本: {random_filename}")
                print(f"   输出: {result.get('output', '')}")
                print(f"   退出码: {result.get('return_code', '')}")

                results.append({
                    "script_name": random_filename,
                    "success": True,
                    "output": result.get('output', ''),
                    "exit_code": result.get('return_code', '')
                })
            else:
                print(f"❌ 动态脚本执行失败: {random_filename}")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.text}")

                results.append({
                    "script_name": random_filename,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })

        except Exception as e:
            print(f"❌ 动态脚本执行异常: {random_filename}")
            print(f"   异常: {str(e)}")

            results.append({
                "script_name": random_filename,
                "success": False,
                "error": str(e)
            })

    return results


def run_comprehensive_test(url):
    """运行综合测试"""
    print(f"🚀 开始Shell执行测试 - 目标URL: {url}")
    print("=" * 60)

    # 初始化安全管理器
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'default.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    security_manager = SecurityManager(config)

    # 获取API令牌
    print("🔑 获取API令牌...")
    token = get_api_token(url, security_manager)
    if not token:
        print("❌ 无法获取API令牌，测试终止")
        return None, False
    print("✅ API令牌获取成功")

    all_results = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target_url": url,
        "basic_commands": [],
        "user_switch": [],
        "dynamic_scripts": []
    }

    # 测试1: 基本shell命令
    all_results["basic_commands"] = test_basic_shell_command(url, security_manager, token)

    # 测试2: 用户切换和目录
    all_results["user_switch"] = test_user_switch_and_directory(url, security_manager, token)

    # 测试3: 动态脚本执行
    all_results["dynamic_scripts"] = test_dynamic_script_execution(url, security_manager, token)

    # 统计结果
    total_tests = (
        len(all_results["basic_commands"]) +
        len(all_results["user_switch"]) +
        len(all_results["dynamic_scripts"])
    )

    passed_tests = sum([
        sum(1 for r in all_results["basic_commands"] if r["success"]),
        sum(1 for r in all_results["user_switch"] if r["success"]),
        sum(1 for r in all_results["dynamic_scripts"] if r["success"])
    ])

    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {(passed_tests / total_tests * 100):.1f}%")

    # 保存测试报告
    report_filename = f"shell_execution_test_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n📄 测试报告已保存: {report_filename}")

    return all_results, passed_tests == total_tests


def main():
    parser = argparse.ArgumentParser(description='AIOps Agent Shell执行测试')
    parser.add_argument('--url', required=True, help='AIOps Agent服务器URL')
    parser.add_argument('--server', choices=['30', '202', 'both'], default='both',
                       help='测试服务器: 30(10.0.0.30), 202(10.0.0.202), both(两者都测试)')

    args = parser.parse_args()

    servers = []
    if args.server == '30' or args.server == 'both':
        servers.append('10.0.0.30')
    if args.server == '202' or args.server == 'both':
        servers.append('10.0.0.202')

    if not servers:
        print("❌ 未指定要测试的服务器")
        return 1

    overall_success = True

    for server in servers:
        server_url = f"https://{server}:8443"
        print(f"\n{'='*80}")
        print(f"测试服务器: {server}")
        print(f"{'='*80}")

        try:
            results, success = run_comprehensive_test(server_url)
            if not success:
                overall_success = False
        except Exception as e:
            print(f"❌ 测试服务器 {server} 时发生异常: {str(e)}")
            overall_success = False

    print(f"\n{'='*80}")
    if overall_success:
        print("🎉 所有服务器Shell执行测试完成且全部通过！")
        return 0
    else:
        print("⚠️  Shell执行测试完成，但部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())