"""
命令执行器单元测试
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.executor import CommandExecutor


class TestCommandExecutor:
    """命令执行器测试类"""

    def setup_method(self):
        """测试方法设置"""
        self.config = {
            'execution': {
                'timeout': 30,
                'max_output_size': 1024
            }
        }
        self.executor = CommandExecutor(self.config)

    def test_execute_success(self):
        """测试成功执行命令"""
        with patch('subprocess.Popen') as mock_popen:
            # 模拟成功的命令执行
            mock_process = MagicMock()
            mock_process.communicate.return_value = ('test output', '')
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = self.executor.execute('echo "test"')

            assert result['success'] is True
            assert result['output'] == 'test output'
            assert result['error'] == ''
            assert result['return_code'] == 0

    def test_execute_failure(self):
        """测试命令执行失败"""
        with patch('subprocess.Popen') as mock_popen:
            # 模拟失败的命令执行
            mock_process = MagicMock()
            mock_process.communicate.return_value = ('', 'command not found')
            mock_process.returncode = 127
            mock_popen.return_value = mock_process

            result = self.executor.execute('invalid_command')

            assert result['success'] is False
            assert result['output'] == ''
            assert result['error'] == 'command not found'
            assert result['return_code'] == 127

    def test_execute_timeout(self):
        """测试命令执行超时"""
        with patch('subprocess.Popen') as mock_popen:
            # 模拟超时
            mock_process = MagicMock()
            mock_process.communicate.side_effect = TimeoutError()
            mock_popen.return_value = mock_process

            result = self.executor.execute('sleep 10')

            assert result['success'] is False
            assert '超时' in result['error']
            assert result['return_code'] == -1

    def test_validate_command_safe(self):
        """测试安全命令验证"""
        safe_commands = [
            'ls -la',
            'echo "hello"',
            'whoami',
            'pwd'
        ]

        for cmd in safe_commands:
            assert self.executor.validate_command(cmd) is True

    def test_validate_command_empty(self):
        """测试空命令验证"""
        assert self.executor.validate_command('') is False
        assert self.executor.validate_command('   ') is False

    @patch('platform.system')
    def test_prepare_command_with_user_linux(self, mock_system):
        """测试Linux平台用户切换命令准备"""
        mock_system.return_value = 'Linux'

        command = 'ls -la'
        user = 'testuser'

        result = self.executor._prepare_command_with_user(command, user)

        assert f'su -l {user} -c' in result
        assert command in result

    @patch('platform.system')
    def test_prepare_command_with_user_windows(self, mock_system):
        """测试Windows平台用户切换命令准备"""
        mock_system.return_value = 'Windows'

        command = 'dir'
        user = 'testuser'

        result = self.executor._prepare_command_with_user(command, user)

        # Windows平台应该返回原始命令（因为runas需要密码）
        assert result == command