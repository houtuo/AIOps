#!/usr/bin/env python3
"""
AIOps Agent 集成测试脚本

功能：
1. 环境检查
2. 模块功能测试
3. API接口测试
4. 性能测试
5. 安全测试
6. 测试报告生成

使用方法：
python test_integration.py [--server-url URL] [--auth-token TOKEN] [--output-format FORMAT]
"""

import sys
import os
import time
import json
import argparse
import subprocess
import threading
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 尝试导入所需模块
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from src.config import Config
    from src.executor import CommandExecutor
    from src.script_executor import ScriptExecutor
    from src.security import SecurityManager
    from src.user_switch import UserSwitch
    from src.server import AgentServer
    HAS_CORE_MODULES = True
except ImportError as e:
    print(f"❌ 核心模块导入失败: {e}")
    HAS_CORE_MODULES = False


class TestResult:
    """测试结果类"""

    def __init__(self, name, status, message="", duration=0, details=None):
        self.name = name
        self.status = status  # "PASS", "FAIL", "SKIP"
        self.message = message
        self.duration = duration
        self.details = details or {}

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "duration": self.duration,
            "details": self.details
        }


class IntegrationTester:
    """集成测试器"""

    def __init__(self, server_url=None, auth_token=None):
        self.server_url = server_url or "https://localhost:8443"
        self.auth_token = auth_token
        self.test_results = []
        self.config = None
        self.start_time = None

    def run_test(self, test_func, name):
        """运行单个测试"""
        start_time = time.time()

        try:
            result = test_func()
            duration = time.time() - start_time

            if result:
                self.test_results.append(TestResult(name, "PASS", "测试通过", duration))
                print(f"✅ {name} - 通过 ({duration:.2f}s)")
            else:
                self.test_results.append(TestResult(name, "FAIL", "测试失败", duration))
                print(f"❌ {name} - 失败 ({duration:.2f}s)")

        except Exception as e:
            duration = time.time() - start_time
            self.test_results.append(TestResult(name, "FAIL", str(e), duration))
            print(f"❌ {name} - 异常: {e} ({duration:.2f}s)")

    def skip_test(self, name, reason=""):
        """跳过测试"""
        self.test_results.append(TestResult(name, "SKIP", reason))
        print(f"⚠️ {name} - 跳过: {reason}")

    def run_all_tests(self):
        """运行所有测试"""
        self.start_time = time.time()

        print("🚀 开始集成测试")
        print("=" * 60)

        # 1. 环境检查
        self.run_environment_tests()

        # 2. 模块功能测试
        if HAS_CORE_MODULES:
            self.run_module_tests()
        else:
            print("⚠️ 跳过模块测试 - 核心模块导入失败")

        # 3. API接口测试
        if HAS_REQUESTS:
            self.run_api_tests()
        else:
            print("⚠️ 跳过API测试 - requests模块未安装")

        # 4. 性能测试
        self.run_performance_tests()

        # 5. 安全测试
        self.run_security_tests()

        self.generate_report()

    def run_environment_tests(self):
        """运行环境检查测试"""
        print("\n📋 环境检查测试")
        print("-" * 40)

        # Python版本检查
        def test_python_version():
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                return True
            raise Exception(f"Python版本过低: {version.major}.{version.minor}.{version.micro}")

        self.run_test(test_python_version, "Python版本检查")

        # 依赖包检查
        def test_dependencies():
            required_packages = [
                "flask", "pyjwt", "cryptography", "pyyaml", "werkzeug"
            ]

            missing = []
            for package in required_packages:
                try:
                    __import__(package.replace('-', '_'))
                except ImportError:
                    missing.append(package)

            if missing:
                raise Exception(f"缺少依赖包: {', '.join(missing)}")
            return True

        self.run_test(test_dependencies, "依赖包检查")

        # 配置文件检查
        def test_config_files():
            config_file = Path("config/default.yaml")
            if not config_file.exists():
                raise Exception("配置文件不存在: config/default.yaml")

            # 尝试加载配置
            try:
                self.config = Config.load("config/default.yaml")
                return True
            except Exception as e:
                raise Exception(f"配置文件加载失败: {e}")

        self.run_test(test_config_files, "配置文件检查")

        # SSL证书检查
        def test_ssl_certificates():
            cert_file = Path("config/server.crt")
            key_file = Path("config/server.key")

            if not cert_file.exists():
                raise Exception("SSL证书文件不存在: config/server.crt")
            if not key_file.exists():
                raise Exception("SSL私钥文件不存在: config/server.key")

            return True

        self.run_test(test_ssl_certificates, "SSL证书检查")

    def run_module_tests(self):
        """运行模块功能测试"""
        print("\n🔧 模块功能测试")
        print("-" * 40)

        # 配置模块测试
        def test_config_module():
            config = self.config

            # 检查必要配置项
            required_keys = ["server", "security", "execution"]
            for key in required_keys:
                if key not in config:
                    raise Exception(f"缺少配置项: {key}")

            # 测试配置获取
            host = Config.get("server.host")
            port = Config.get("server.port")

            if not host or not port:
                raise Exception("服务器配置获取失败")

            return True

        self.run_test(test_config_module, "配置模块测试")

        # 命令执行器测试
        def test_command_executor():
            executor = CommandExecutor(self.config)

            # 测试基本命令
            result = executor.execute("echo 'test'")
            if not result["success"]:
                raise Exception("基本命令执行失败")

            # 测试错误命令
            result = executor.execute("invalid_command_xyz")
            if result["success"]:
                raise Exception("错误命令处理异常")

            return True

        self.run_test(test_command_executor, "命令执行器测试")

        # 脚本执行器测试
        def test_script_executor():
            executor = ScriptExecutor(self.config)

            # 测试脚本执行
            result = executor.execute_script_content("echo 'script test'")
            if not result["success"]:
                raise Exception("脚本执行失败")

            # 测试脚本类型检测
            script_type = executor._detect_script_type_from_content("#!/bin/bash\necho test")
            if script_type != "shell":
                raise Exception(f"脚本类型检测失败: {script_type}")

            return True

        self.run_test(test_script_executor, "脚本执行器测试")

        # 安全模块测试
        def test_security_module():
            security = SecurityManager(self.config)

            # 测试JWT令牌
            payload = {"user_id": "test_user", "permissions": ["test"]}
            token = security.generate_jwt_token(payload)
            decoded = security.verify_jwt_token(token)

            if not decoded or decoded["user_id"] != "test_user":
                raise Exception("JWT令牌验证失败")

            # 测试API密钥
            api_key_info = security.generate_api_key("test_user", ["test"])
            is_valid = security.verify_api_key(api_key_info["api_key"], api_key_info["token"])

            if not is_valid:
                raise Exception("API密钥验证失败")

            return True

        self.run_test(test_security_module, "安全模块测试")

        # 用户切换模块测试
        def test_user_switch():
            user_switch = UserSwitch(self.config)

            # 测试平台检测
            platform = user_switch.platform
            if platform not in ["linux", "windows"]:
                raise Exception(f"平台检测失败: {platform}")

            # 测试用户存在检查
            exists = user_switch._check_user_exists_linux("root")
            if not exists:
                print("⚠️ root用户不存在检查失败，可能不是Linux系统")

            return True

        self.run_test(test_user_switch, "用户切换模块测试")

        # 服务器模块测试
        def test_server_module():
            server = AgentServer(self.config)
            app = server.create_app()

            # 检查路由
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    routes.append(f"{list(rule.methods)[0]} {rule.rule}")

            if len(routes) < 5:
                raise Exception(f"路由数量不足: {len(routes)}")

            return True

        self.run_test(test_server_module, "服务器模块测试")

    def run_api_tests(self):
        """运行API接口测试"""
        print("\n🌐 API接口测试")
        print("-" * 40)

        # 测试服务器是否运行
        def test_server_health():
            try:
                response = requests.get(f"{self.server_url}/health", verify=False, timeout=10)
                if response.status_code != 200:
                    raise Exception(f"HTTP状态码异常: {response.status_code}")

                data = response.json()
                if data.get("status") != "healthy":
                    raise Exception(f"健康状态异常: {data}")

                return True
            except requests.exceptions.RequestException as e:
                raise Exception(f"服务器连接失败: {e}")

        self.run_test(test_server_health, "服务器健康检查")

        # 测试状态接口
        def test_status_api():
            response = requests.get(f"{self.server_url}/status", verify=False, timeout=10)
            if response.status_code != 200:
                raise Exception(f"状态接口HTTP状态码异常: {response.status_code}")

            data = response.json()
            required_keys = ["hostname", "platform", "status", "version"]
            for key in required_keys:
                if key not in data:
                    raise Exception(f"状态接口缺少字段: {key}")

            return True

        self.run_test(test_status_api, "状态接口测试")

        # 如果提供了认证令牌，测试需要认证的接口
        if self.auth_token:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }

            # 测试用户列表接口
            def test_users_api():
                response = requests.get(f"{self.server_url}/users", headers=headers, verify=False, timeout=10)
                if response.status_code != 200:
                    raise Exception(f"用户列表接口HTTP状态码异常: {response.status_code}")

                data = response.json()
                if "users" not in data or not isinstance(data["users"], list):
                    raise Exception("用户列表接口返回格式异常")

                return True

            self.run_test(test_users_api, "用户列表接口测试")

            # 测试命令执行接口
            def test_command_exec_api():
                payload = {
                    "command": "whoami",
                    "user": "root"
                }

                response = requests.post(
                    f"{self.server_url}/exec/command",
                    headers=headers,
                    json=payload,
                    verify=False,
                    timeout=30
                )

                if response.status_code != 200:
                    raise Exception(f"命令执行接口HTTP状态码异常: {response.status_code}")

                data = response.json()
                if not data.get("success"):
                    raise Exception(f"命令执行失败: {data.get('error', '未知错误')}")

                return True

            self.run_test(test_command_exec_api, "命令执行接口测试")

            # 测试脚本执行接口
            def test_script_exec_api():
                payload = {
                    "script": "echo 'API script test'",
                    "user": "root"
                }

                response = requests.post(
                    f"{self.server_url}/exec/script/content",
                    headers=headers,
                    json=payload,
                    verify=False,
                    timeout=30
                )

                if response.status_code != 200:
                    raise Exception(f"脚本执行接口HTTP状态码异常: {response.status_code}")

                data = response.json()
                if not data.get("success"):
                    raise Exception(f"脚本执行失败: {data.get('error', '未知错误')}")

                return True

            self.run_test(test_script_exec_api, "脚本执行接口测试")
        else:
            self.skip_test("用户列表接口测试", "缺少认证令牌")
            self.skip_test("命令执行接口测试", "缺少认证令牌")
            self.skip_test("脚本执行接口测试", "缺少认证令牌")

    def run_performance_tests(self):
        """运行性能测试"""
        print("\n⚡ 性能测试")
        print("-" * 40)

        # 响应时间测试
        def test_response_time():
            if not HAS_REQUESTS:
                self.skip_test("响应时间测试", "requests模块未安装")
                return False

            start_time = time.time()
            try:
                response = requests.get(f"{self.server_url}/health", verify=False, timeout=10)
                response_time = time.time() - start_time

                if response_time > 2.0:
                    raise Exception(f"响应时间过长: {response_time:.2f}s")

                return True
            except Exception as e:
                raise Exception(f"响应时间测试失败: {e}")

        self.run_test(test_response_time, "响应时间测试")

        # 并发测试
        def test_concurrency():
            if not HAS_REQUESTS:
                self.skip_test("并发测试", "requests模块未安装")
                return False

            def make_request():
                try:
                    requests.get(f"{self.server_url}/health", verify=False, timeout=5)
                    return True
                except:
                    return False

            start_time = time.time()
            threads = []
            success_count = 0

            # 启动10个并发请求
            for i in range(10):
                thread = threading.Thread(target=lambda: make_request() and None)
                threads.append(thread)
                thread.start()

            # 等待所有线程完成
            for thread in threads:
                thread.join()

            total_time = time.time() - start_time

            if total_time > 10.0:
                raise Exception(f"并发处理时间过长: {total_time:.2f}s")

            return True

        self.run_test(test_concurrency, "并发测试")

    def run_security_tests(self):
        """运行安全测试"""
        print("\n🔒 安全测试")
        print("-" * 40)

        # 认证测试
        def test_authentication():
            if not HAS_REQUESTS:
                self.skip_test("认证测试", "requests模块未安装")
                return False

            # 测试未认证访问
            response = requests.get(f"{self.server_url}/users", verify=False, timeout=10)
            if response.status_code == 200:
                raise Exception("未认证访问应该被拒绝")

            return True

        self.run_test(test_authentication, "认证测试")

        # 输入验证测试
        def test_input_validation():
            if not HAS_REQUESTS or not self.auth_token:
                self.skip_test("输入验证测试", "缺少requests模块或认证令牌")
                return False

            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }

            # 测试危险命令
            dangerous_commands = [
                "rm -rf /",
                "; rm -rf /",
                "&& rm -rf /",
                "| rm -rf /"
            ]

            for cmd in dangerous_commands:
                payload = {"command": cmd, "user": "root"}
                response = requests.post(
                    f"{self.server_url}/exec/command",
                    headers=headers,
                    json=payload,
                    verify=False,
                    timeout=10
                )

                # 危险命令应该被拒绝或返回错误
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        raise Exception(f"危险命令未被阻止: {cmd}")

            return True

        self.run_test(test_input_validation, "输入验证测试")

    def generate_report(self):
        """生成测试报告"""
        total_time = time.time() - self.start_time

        # 统计结果
        passed = len([r for r in self.test_results if r.status == "PASS"])
        failed = len([r for r in self.test_results if r.status == "FAIL"])
        skipped = len([r for r in self.test_results if r.status == "SKIP"])
        total = len(self.test_results)

        # 计算通过率
        if total > 0:
            pass_rate = (passed / total) * 100
        else:
            pass_rate = 0

        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"跳过: {skipped}")
        print(f"通过率: {pass_rate:.1f}%")
        print(f"总耗时: {total_time:.2f}秒")

        # 显示失败详情
        failed_tests = [r for r in self.test_results if r.status == "FAIL"]
        if failed_tests:
            print("\n❌ 失败测试详情:")
            for result in failed_tests:
                print(f"  - {result.name}: {result.message}")

        # 生成JSON报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": pass_rate,
            "total_duration": total_time,
            "test_results": [r.to_dict() for r in self.test_results]
        }

        # 保存报告
        os.makedirs("test_reports", exist_ok=True)
        report_file = f"test_reports/integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 详细报告已保存: {report_file}")

        # 总体评估
        if failed == 0:
            print("\n🎉 所有测试通过！系统运行正常。")
        elif pass_rate >= 80:
            print("\n⚠️ 部分测试失败，但系统基本功能正常。")
        else:
            print("\n❌ 测试失败较多，需要检查系统配置和功能。")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIOps Agent 集成测试")
    parser.add_argument("--server-url", default="https://localhost:8443",
                       help="服务器URL (默认: https://localhost:8443)")
    parser.add_argument("--auth-token", help="认证令牌")
    parser.add_argument("--output-format", choices=["console", "json"], default="console",
                       help="输出格式 (默认: console)")

    args = parser.parse_args()

    # 检查requests模块
    if not HAS_REQUESTS:
        print("⚠️ requests模块未安装，部分API测试将跳过")
        print("   安装命令: pip install requests")

    # 运行测试
    tester = IntegrationTester(args.server_url, args.auth_token)
    tester.run_all_tests()


if __name__ == "__main__":
    main()