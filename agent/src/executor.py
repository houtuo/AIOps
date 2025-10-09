"""
命令执行器模块

负责执行系统命令并捕获输出。
"""

import subprocess
import logging
import platform
from typing import Dict, Optional, Tuple


class CommandExecutor:
    """命令执行器类"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()

        # 执行配置
        exec_config = config.get('execution', {})
        self.timeout = exec_config.get('timeout', 300)
        self.max_output_size = exec_config.get('max_output_size', 1048576)

    def execute(
        self,
        command: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        执行系统命令

        Args:
            command: 要执行的命令
            user: 执行命令的用户（可选）
            working_dir: 工作目录（可选）
            env: 环境变量（可选）

        Returns:
            包含执行结果的字典
        """
        self.logger.info(f"执行命令: {command}")

        try:
            # 如果指定了用户，需要切换用户执行
            if user:
                command = self._prepare_command_with_user(command, user)

            # 执行命令
            result = self._run_command(command, working_dir, env)

            return {
                'success': True,
                'output': result[0],
                'error': result[1],
                'return_code': result[2]
            }

        except subprocess.TimeoutExpired:
            self.logger.error(f"命令执行超时: {command}")
            return {
                'success': False,
                'output': '',
                'error': f'命令执行超时（超过 {self.timeout} 秒）',
                'return_code': -1
            }

        except Exception as e:
            self.logger.error(f"命令执行失败: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    def _run_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Tuple[str, str, int]:
        """
        实际执行命令

        Returns:
            (stdout, stderr, return_code)
        """
        # 根据平台选择shell
        shell = True

        # 准备环境变量
        import os
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)

        # 执行命令
        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir,
            env=cmd_env,
            text=True
        )

        # 等待命令完成
        try:
            stdout, stderr = process.communicate(timeout=self.timeout)
            return_code = process.returncode

            # 限制输出大小
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n[输出被截断...]"
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n[错误输出被截断...]"

            return stdout, stderr, return_code

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise

    def _prepare_command_with_user(self, command: str, user: str) -> str:
        """
        准备以指定用户身份执行的命令

        Args:
            command: 原始命令
            user: 目标用户

        Returns:
            修改后的命令
        """
        if self.platform == 'linux':
            # Linux平台使用su命令
            # 使用 -l 选项加载用户的完整环境
            return f"su - {user} -c '{command}'"

        elif self.platform == 'windows':
            # Windows平台使用runas命令（需要密码）
            # 注意：runas需要交互式输入密码，实际生产环境应使用Windows API
            self.logger.warning("Windows平台用户切换需要使用专门的user_switch模块")
            return command

        else:
            self.logger.warning(f"不支持的平台: {self.platform}")
            return command

    def validate_command(self, command: str) -> bool:
        """
        验证命令是否安全（基本检查）

        Args:
            command: 要验证的命令

        Returns:
            是否通过验证
        """
        # 这里可以添加命令白名单/黑名单检查
        # 或者检查危险字符

        if not command or not command.strip():
            return False

        # 可以添加更多安全检查
        # 例如：禁止某些危险命令
        dangerous_patterns = ['rm -rf /', 'mkfs', 'dd if=/dev/zero']

        for pattern in dangerous_patterns:
            if pattern in command.lower():
                self.logger.warning(f"检测到危险命令模式: {pattern}")
                # 可以选择拒绝执行或记录日志
                # 这里仅记录警告

        return True
