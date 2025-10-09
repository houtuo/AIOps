#!/usr/bin/env python3
"""
AIOps 代理程序主入口

自动化运维代理程序，支持命令执行、脚本执行、用户身份切换和加密通信。
"""

import os
import sys
import logging
import signal
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.server import AgentServer


class AIOpsAgent:
    """AIOps 代理程序主类"""

    def __init__(self):
        self.config = None
        self.server = None
        self.logger = None

    def setup_logging(self):
        """配置日志系统"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))

        # 创建日志目录
        log_file = log_config.get('file', 'logs/aiops-agent.log')
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 配置日志
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)

    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            self.logger.info(f"收到信号 {signum}，正在关闭服务...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def start(self):
        """启动代理程序"""
        try:
            # 加载配置
            self.config = Config.load()

            # 设置日志
            self.setup_logging()
            self.logger.info("AIOps 代理程序启动中...")

            # 设置信号处理器
            self.setup_signal_handlers()

            # 创建并启动服务器
            self.server = AgentServer(self.config)
            self.server.start()

        except Exception as e:
            if self.logger:
                self.logger.error(f"启动失败: {e}")
            else:
                print(f"启动失败: {e}")
            sys.exit(1)

    def stop(self):
        """停止代理程序"""
        if self.server:
            self.server.stop()
        if self.logger:
            self.logger.info("AIOps 代理程序已停止")
        sys.exit(0)


def main():
    """主函数"""
    agent = AIOpsAgent()
    agent.start()


if __name__ == "__main__":
    main()