"""
用户切换模块

负责在不同用户身份下执行命令和脚本。
"""

import os
import platform
import logging
import subprocess
from typing import Dict, Optional, Tuple


class UserSwitch:
    """用户切换类"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()

        # 用户切换配置
        user_config = config.get('user_switch', {})
        self.linux_config = user_config.get('linux', {})
        self.windows_config = user_config.get('windows', {})

    def execute_as_user(
        self,
        command: str,
        user: str,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Tuple[str, str, int]:
        """
        以指定用户身份执行命令

        Args:
            command: 要执行的命令
            user: 目标用户
            working_dir: 工作目录（可选）
            env: 环境变量（可选）

        Returns:
            (stdout, stderr, return_code)
        """
        self.logger.info(f"以用户 {user} 身份执行命令: {command}")

        if self.platform == 'linux':
            return self._execute_as_user_linux(command, user, working_dir, env)
        elif self.platform == 'windows':
            return self._execute_as_user_windows(command, user, working_dir, env)
        else:
            self.logger.error(f"不支持的平台: {self.platform}")
            return "", f"不支持的平台: {self.platform}", -1

    def _execute_as_user_linux(
        self,
        command: str,
        user: str,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Tuple[str, str, int]:
        """
        Linux平台用户切换执行

        Args:
            command: 要执行的命令
            user: 目标用户
            working_dir: 工作目录（可选）
            env: 环境变量（可选）

        Returns:
            (stdout, stderr, return_code)
        """
        try:
            # 检查用户是否存在
            if not self._check_user_exists_linux(user):
                return "", f"用户不存在: {user}", -1

            # 构建切换用户的命令
            # 使用 su -l 确保加载完整的用户环境
            if working_dir:
                # 如果指定了工作目录，先切换到该目录
                full_command = f"cd '{working_dir}' && {command}"
            else:
                full_command = command

            # 使用 su -l 命令切换用户
            # -l 选项会加载用户的完整环境（包括.bashrc等）
            su_command = f"su -l {user} -c '{full_command}'"

            # 执行命令
            process = subprocess.Popen(
                su_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()
            return_code = process.returncode

            return stdout, stderr, return_code

        except Exception as e:
            self.logger.error(f"Linux用户切换执行失败: {e}")
            return "", str(e), -1

    def _execute_as_user_windows(
        self,
        command: str,
        user: str,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Tuple[str, str, int]:
        """
        Windows平台用户切换执行

        Args:
            command: 要执行的命令
            user: 目标用户
            working_dir: 工作目录（可选）
            env: 环境变量（可选）

        Returns:
            (stdout, stderr, return_code)
        """
        try:
            # Windows平台用户切换比较复杂
            # 这里使用runas命令（需要密码）
            # 实际生产环境应该使用Windows API

            self.logger.warning("Windows平台用户切换需要密码，当前实现有限")

            # 使用runas命令
            # 注意：runas需要交互式输入密码，这里仅作为示例
            runas_command = f'runas /user:{user} "{command}"'

            process = subprocess.Popen(
                runas_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()
            return_code = process.returncode

            return stdout, stderr, return_code

        except Exception as e:
            self.logger.error(f"Windows用户切换执行失败: {e}")
            return "", str(e), -1

    def _check_user_exists_linux(self, user: str) -> bool:
        """
        检查Linux用户是否存在

        Args:
            user: 用户名

        Returns:
            用户是否存在
        """
        try:
            result = subprocess.run(
                ['id', user],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_user_exists_windows(self, user: str) -> bool:
        """
        检查Windows用户是否存在

        Args:
            user: 用户名

        Returns:
            用户是否存在
        """
        try:
            # 使用net user命令检查用户
            result = subprocess.run(
                ['net', 'user', user],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_user_info(self, user: str) -> Optional[Dict[str, any]]:
        """
        获取用户信息

        Args:
            user: 用户名

        Returns:
            用户信息字典
        """
        if self.platform == 'linux':
            return self._get_user_info_linux(user)
        elif self.platform == 'windows':
            return self._get_user_info_windows(user)
        else:
            return None

    def _get_user_info_linux(self, user: str) -> Optional[Dict[str, any]]:
        """
        获取Linux用户信息

        Args:
            user: 用户名

        Returns:
            用户信息字典
        """
        try:
            # 使用getent命令获取用户信息
            result = subprocess.run(
                ['getent', 'passwd', user],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                return None

            # 解析passwd文件格式
            # username:password:UID:GID:GECOS:home:shell
            parts = result.stdout.strip().split(':')
            if len(parts) < 7:
                return None

            return {
                'username': parts[0],
                'uid': parts[2],
                'gid': parts[3],
                'gecos': parts[4],
                'home': parts[5],
                'shell': parts[6]
            }

        except Exception as e:
            self.logger.error(f"获取Linux用户信息失败: {e}")
            return None

    def _get_user_info_windows(self, user: str) -> Optional[Dict[str, any]]:
        """
        获取Windows用户信息

        Args:
            user: 用户名

        Returns:
            用户信息字典
        """
        try:
            # 使用net user命令获取用户信息
            result = subprocess.run(
                ['net', 'user', user],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                return None

            # 解析net user输出
            info = {}
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'User name' in line:
                    info['username'] = line.split()[-1]
                elif 'Full Name' in line:
                    info['full_name'] = line.split('Full Name')[-1].strip()
                elif 'Comment' in line:
                    info['comment'] = line.split('Comment')[-1].strip()

            return info

        except Exception as e:
            self.logger.error(f"获取Windows用户信息失败: {e}")
            return None

    def validate_user_permissions(self, user: str) -> bool:
        """
        验证用户权限

        Args:
            user: 用户名

        Returns:
            是否具有足够的权限
        """
        if self.platform == 'linux':
            return self._validate_user_permissions_linux(user)
        elif self.platform == 'windows':
            return self._validate_user_permissions_windows(user)
        else:
            return False

    def _validate_user_permissions_linux(self, user: str) -> bool:
        """
        验证Linux用户权限

        Args:
            user: 用户名

        Returns:
            是否具有足够的权限
        """
        try:
            # 检查当前用户是否有权限切换到目标用户
            # 这里可以添加更复杂的权限检查逻辑

            # 简单检查：目标用户是否存在
            if not self._check_user_exists_linux(user):
                return False

            # 检查当前用户是否在sudoers中或者有su权限
            # 这里简化处理，实际应该检查/etc/sudoers和PAM配置
            return True

        except Exception as e:
            self.logger.error(f"Linux用户权限验证失败: {e}")
            return False

    def _validate_user_permissions_windows(self, user: str) -> bool:
        """
        验证Windows用户权限

        Args:
            user: 用户名

        Returns:
            是否具有足够的权限
        """
        try:
            # 检查用户是否存在
            if not self._check_user_exists_windows(user):
                return False

            # Windows权限验证比较复杂
            # 这里简化处理
            return True

        except Exception as e:
            self.logger.error(f"Windows用户权限验证失败: {e}")
            return False

    def get_available_users(self) -> list:
        """
        获取可用的用户列表

        Returns:
            用户列表
        """
        if self.platform == 'linux':
            return self._get_available_users_linux()
        elif self.platform == 'windows':
            return self._get_available_users_windows()
        else:
            return []

    def _get_available_users_linux(self) -> list:
        """
        获取Linux可用用户列表

        Returns:
            用户列表
        """
        try:
            # 获取所有用户
            result = subprocess.run(
                ['getent', 'passwd'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                return []

            users = []
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split(':')
                if len(parts) >= 1:
                    users.append(parts[0])

            return users

        except Exception as e:
            self.logger.error(f"获取Linux用户列表失败: {e}")
            return []

    def _get_available_users_windows(self) -> list:
        """
        获取Windows可用用户列表

        Returns:
            用户列表
        """
        try:
            # 获取所有用户
            result = subprocess.run(
                ['net', 'user'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                return []

            users = []
            lines = result.stdout.strip().split('\n')
            start_parsing = False

            for line in lines:
                if 'User accounts for' in line:
                    start_parsing = True
                    continue

                if start_parsing and line.strip():
                    # 跳过分隔行
                    if '---' in line:
                        continue
                    # 跳过空行
                    if not line.strip():
                        continue
                    # 跳过命令完成信息
                    if 'The command completed successfully' in line:
                        break

                    # 添加用户
                    users.extend(line.strip().split())

            return users

        except Exception as e:
            self.logger.error(f"获取Windows用户列表失败: {e}")
            return []