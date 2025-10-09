#!/usr/bin/env python3
"""
AIOps Agent 性能测试脚本

功能：
1. 响应时间测试
2. 并发处理测试
3. 资源使用测试
4. 负载测试

使用方法：
python test_performance.py [--server-url URL] [--auth-token TOKEN] [--duration SECONDS]
"""

import sys
import os
import time
import json
import threading
import statistics
import psutil
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class PerformanceTester:
    """性能测试器"""

    def __init__(self, server_url=None, auth_token=None):
        self.server_url = server_url or "https://localhost:8443"
        self.auth_token = auth_token
        self.results = {}
        self.metrics = {
            "response_times": [],
            "concurrent_times": [],
            "memory_usage": [],
            "cpu_usage": []
        }

    def measure_response_time(self, endpoint, method="GET", payload=None):
        """测量响应时间"""
        if not HAS_REQUESTS:
            return None

        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(f"{self.server_url}{endpoint}",
                                      headers=headers, verify=False, timeout=30)
            elif method == "POST":
                response = requests.post(f"{self.server_url}{endpoint}",
                                       headers=headers, json=payload,
                                       verify=False, timeout=30)
            else:
                return None

            response_time = time.time() - start_time

            if response.status_code == 200:
                return response_time
            else:
                return None

        except Exception:
            return None

    def test_single_request_performance(self):
        """测试单请求性能"""
        print("\n📊 单请求性能测试")
        print("-" * 40)

        endpoints = [
            ("/health", "GET", None),
            ("/status", "GET", None),
            ("/users", "GET", None)
        ]

        if self.auth_token:
            endpoints.extend([
                ("/exec/command", "POST", {"command": "echo test", "user": "root"}),
                ("/exec/script/content", "POST", {"script": "echo test", "user": "root"})
            ])

        results = {}

        for endpoint, method, payload in endpoints:
            times = []
            for i in range(10):  # 每个端点测试10次
                response_time = self.measure_response_time(endpoint, method, payload)
                if response_time is not None:
                    times.append(response_time)

            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                std_dev = statistics.stdev(times) if len(times) > 1 else 0

                results[endpoint] = {
                    "average": avg_time,
                    "min": min_time,
                    "max": max_time,
                    "std_dev": std_dev,
                    "samples": len(times)
                }

                print(f"{endpoint}:")
                print(f"  平均: {avg_time:.3f}s, 最小: {min_time:.3f}s, 最大: {max_time:.3f}s")
                print(f"  标准差: {std_dev:.3f}s, 样本数: {len(times)}")

        self.results["single_request"] = results
        return results

    def test_concurrent_performance(self, concurrent_users=10):
        """测试并发性能"""
        print(f"\n⚡ 并发性能测试 ({concurrent_users}个并发用户)")
        print("-" * 40)

        if not HAS_REQUESTS:
            print("⚠️ requests模块未安装，跳过并发测试")
            return {}

        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "start_time": time.time()
        }

        lock = threading.Lock()

        def worker(worker_id):
            """工作线程"""
            for i in range(5):  # 每个线程发送5个请求
                start_time = time.time()
                try:
                    response = requests.get(
                        f"{self.server_url}/health",
                        verify=False,
                        timeout=10
                    )
                    response_time = time.time() - start_time

                    with lock:
                        results["total_requests"] += 1
                        if response.status_code == 200:
                            results["successful_requests"] += 1
                            results["response_times"].append(response_time)
                        else:
                            results["failed_requests"] += 1

                except Exception:
                    with lock:
                        results["total_requests"] += 1
                        results["failed_requests"] += 1

        # 启动并发线程
        threads = []
        for i in range(concurrent_users):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        results["end_time"] = time.time()
        results["total_time"] = results["end_time"] - results["start_time"]

        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])
            results["requests_per_second"] = results["total_requests"] / results["total_time"]

        # 输出结果
        print(f"总请求数: {results['total_requests']}")
        print(f"成功请求: {results['successful_requests']}")
        print(f"失败请求: {results['failed_requests']}")
        print(f"成功率: {(results['successful_requests']/results['total_requests'])*100:.1f}%")
        print(f"总时间: {results['total_time']:.2f}s")

        if results["response_times"]:
            print(f"平均响应时间: {results['avg_response_time']:.3f}s")
            print(f"最小响应时间: {results['min_response_time']:.3f}s")
            print(f"最大响应时间: {results['max_response_time']:.3f}s")
            print(f"请求/秒: {results['requests_per_second']:.1f}")

        self.results["concurrent"] = results
        return results

    def monitor_resources(self, duration=30):
        """监控资源使用"""
        print(f"\n📈 资源使用监控 ({duration}秒)")
        print("-" * 40)

        # 找到服务器进程
        server_process = None
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'server.py' in ' '.join(proc.info['cmdline']):
                    server_process = psutil.Process(proc.info['pid'])
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if not server_process:
            print("⚠️ 未找到服务器进程，跳过资源监控")
            return {}

        cpu_percentages = []
        memory_usages = []
        start_time = time.time()

        print("监控中...", end="", flush=True)

        while time.time() - start_time < duration:
            try:
                cpu_percent = server_process.cpu_percent()
                memory_info = server_process.memory_info()

                cpu_percentages.append(cpu_percent)
                memory_usages.append(memory_info.rss / 1024 / 1024)  # 转换为MB

                print(".", end="", flush=True)
                time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

        print()  # 换行

        if cpu_percentages and memory_usages:
            results = {
                "cpu_avg": statistics.mean(cpu_percentages),
                "cpu_max": max(cpu_percentages),
                "memory_avg": statistics.mean(memory_usages),
                "memory_max": max(memory_usages),
                "monitor_duration": duration
            }

            print(f"CPU使用率: 平均 {results['cpu_avg']:.1f}%, 最大 {results['cpu_max']:.1f}%")
            print(f"内存使用: 平均 {results['memory_avg']:.1f}MB, 最大 {results['memory_max']:.1f}MB")

            self.results["resources"] = results
            return results

        return {}

    def test_load_performance(self, duration=60):
        """测试负载性能"""
        print(f"\n🔥 负载性能测试 ({duration}秒)")
        print("-" * 40)

        if not HAS_REQUESTS:
            print("⚠️ requests模块未安装，跳过负载测试")
            return {}

        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "start_time": time.time()
        }

        lock = threading.Lock()
        stop_event = threading.Event()

        def load_worker():
            """负载工作线程"""
            while not stop_event.is_set():
                start_time = time.time()
                try:
                    # 交替测试不同的端点
                    endpoints = ["/health", "/status"]
                    if self.auth_token:
                        endpoints.append("/users")

                    endpoint = endpoints[results["total_requests"] % len(endpoints)]

                    response = requests.get(
                        f"{self.server_url}{endpoint}",
                        verify=False,
                        timeout=10
                    )
                    response_time = time.time() - start_time

                    with lock:
                        results["total_requests"] += 1
                        if response.status_code == 200:
                            results["successful_requests"] += 1
                            results["response_times"].append(response_time)
                        else:
                            results["failed_requests"] += 1

                except Exception:
                    with lock:
                        results["total_requests"] += 1
                        results["failed_requests"] += 1

        # 启动负载线程
        threads = []
        for i in range(5):  # 5个并发线程
            thread = threading.Thread(target=load_worker)
            threads.append(thread)
            thread.start()

        # 运行指定时间
        time.sleep(duration)
        stop_event.set()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        results["end_time"] = time.time()
        results["total_time"] = results["end_time"] - results["start_time"]

        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])
            results["requests_per_second"] = results["total_requests"] / results["total_time"]

        # 输出结果
        print(f"总请求数: {results['total_requests']}")
        print(f"成功请求: {results['successful_requests']}")
        print(f"失败请求: {results['failed_requests']}")
        print(f"成功率: {(results['successful_requests']/results['total_requests'])*100:.1f}%")
        print(f"总时间: {results['total_time']:.2f}s")

        if results["response_times"]:
            print(f"平均响应时间: {results['avg_response_time']:.3f}s")
            print(f"最小响应时间: {results['min_response_time']:.3f}s")
            print(f"最大响应时间: {results['max_response_time']:.3f}s")
            print(f"请求/秒: {results['requests_per_second']:.1f}")

        self.results["load"] = results
        return results

    def run_all_tests(self, duration=60):
        """运行所有性能测试"""
        print("🚀 开始性能测试")
        print("=" * 60)

        start_time = time.time()

        # 1. 单请求性能测试
        self.test_single_request_performance()

        # 2. 并发性能测试
        self.test_concurrent_performance(concurrent_users=10)

        # 3. 资源监控
        self.monitor_resources(duration=30)

        # 4. 负载性能测试
        self.test_load_performance(duration=duration)

        total_time = time.time() - start_time

        # 生成报告
        self.generate_report(total_time)

    def generate_report(self, total_time):
        """生成性能测试报告"""
        print("\n" + "=" * 60)
        print("📊 性能测试报告")
        print("=" * 60)

        # 性能评估
        performance_issues = []
        recommendations = []

        # 检查单请求性能
        if "single_request" in self.results:
            for endpoint, metrics in self.results["single_request"].items():
                if metrics["average"] > 1.0:
                    performance_issues.append(f"{endpoint} 响应时间过长: {metrics['average']:.3f}s")

        # 检查并发性能
        if "concurrent" in self.results:
            concurrent_results = self.results["concurrent"]
            if concurrent_results.get("avg_response_time", 0) > 2.0:
                performance_issues.append(f"并发响应时间过长: {concurrent_results['avg_response_time']:.3f}s")

            if concurrent_results.get("failed_requests", 0) > 0:
                performance_issues.append(f"并发测试中有 {concurrent_results['failed_requests']} 个失败请求")

        # 检查资源使用
        if "resources" in self.results:
            resource_results = self.results["resources"]
            if resource_results["cpu_avg"] > 80:
                performance_issues.append(f"CPU使用率过高: {resource_results['cpu_avg']:.1f}%")
                recommendations.append("考虑优化代码或增加CPU资源")

            if resource_results["memory_max"] > 500:
                performance_issues.append(f"内存使用过高: {resource_results['memory_max']:.1f}MB")
                recommendations.append("检查内存泄漏或增加内存资源")

        # 检查负载性能
        if "load" in self.results:
            load_results = self.results["load"]
            if load_results.get("avg_response_time", 0) > 3.0:
                performance_issues.append(f"负载测试响应时间过长: {load_results['avg_response_time']:.3f}s")

            if load_results.get("failed_requests", 0) > 0:
                performance_issues.append(f"负载测试中有 {load_results['failed_requests']} 个失败请求")

        # 输出总结
        print(f"总测试时间: {total_time:.2f}秒")

        if performance_issues:
            print("\n❌ 性能问题:")
            for issue in performance_issues:
                print(f"  - {issue}")
        else:
            print("\n✅ 未发现明显性能问题")

        if recommendations:
            print("\n💡 优化建议:")
            for recommendation in recommendations:
                print(f"  - {recommendation}")

        # 保存详细报告
        os.makedirs("test_reports", exist_ok=True)
        report_file = f"test_reports/performance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_time,
            "results": self.results,
            "performance_issues": performance_issues,
            "recommendations": recommendations
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n📄 详细报告已保存: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIOps Agent 性能测试")
    parser.add_argument("--server-url", default="https://localhost:8443",
                       help="服务器URL (默认: https://localhost:8443)")
    parser.add_argument("--auth-token", help="认证令牌")
    parser.add_argument("--duration", type=int, default=60,
                       help="负载测试持续时间 (秒, 默认: 60)")

    args = parser.parse_args()

    # 检查requests模块
    if not HAS_REQUESTS:
        print("⚠️ requests模块未安装，部分测试将跳过")
        print("   安装命令: pip install requests")

    # 检查psutil模块
    try:
        import psutil
    except ImportError:
        print("⚠️ psutil模块未安装，资源监控将跳过")
        print("   安装命令: pip install psutil")

    # 运行测试
    tester = PerformanceTester(args.server_url, args.auth_token)
    tester.run_all_tests(duration=args.duration)


if __name__ == "__main__":
    main()