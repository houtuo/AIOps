"""
用户切换模块单元测试
"""

import pytest
from unittest.mock import patch, MagicMock
from src.user_switch import UserSwitch


class TestUserSwitch:
    """用户切换测试类"""

    def setup_method(self):
        """测试方法设置"""
        self.config = {
            'user_switch': {
                'linux': {
                    'sudo_enabled': True,
                    'su_enabled': True
                },
                'windows': {
                    'runas_enabled': True
                }
            }
        }

    @patch('platform.system')
    def test_execute_as_user_linux(self, mock_system):
        """测试Linux平台用户切换执行"""
        mock_system.return_value = 'Linux'
        user_switch = UserSwitch(self.config)

        with patch('subprocess.Popen') as mock_popen:
            # 模拟成功的命令执行
            mock_process = MagicMock()
            mock_process.communicate.return_value = ('output', '')
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            with patch.object(user_switch, '_check_user_exists_linux', return_value=True):
                stdout, stderr, return_code = user_switch.execute_as_user(
                    'ls -la', 'testuser'
                )

            assert stdout == 'output'
            assert stderr == ''
            assert return_code == 0

    @patch('platform.system')
    def test_execute_as_user_windows(self, mock_system):
        """测试Windows平台用户切换执行"""
        mock_system.return_value = 'Windows'
        user_switch = UserSwitch(self.config)

        with patch('subprocess.Popen') as mock_popen:
            # 模拟成功的命令执行
            mock_process = MagicMock()
            mock_process.communicate.return_value = ('output', '')
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            with patch.object(user_switch, '_check_user_exists_windows', return_value=True):
                stdout, stderr, return_code = user_switch.execute_as_user(
                    'dir', 'testuser'
                )

            assert stdout == 'output'
            assert stderr == ''
            assert return_code == 0

    @patch('platform.system')
    def test_execute_as_user_unsupported_platform(self, mock_system):
        """测试不支持的平台"""
        mock_system.return_value = 'Darwin'  # macOS
        user_switch = UserSwitch(self.config)

        stdout, stderr, return_code = user_switch.execute_as_user(
            'ls -la', 'testuser'
        )

        assert stdout == ''
        assert '不支持的平台' in stderr
        assert return_code == -1

    @patch('platform.system')
    def test_execute_as_user_nonexistent_user(self, mock_system):
        """测试不存在的用户"""
        mock_system.return_value = 'Linux'
        user_switch = UserSwitch(self.config)

        with patch.object(user_switch, '_check_user_exists_linux', return_value=False):
            stdout, stderr, return_code = user_switch.execute_as_user(
                'ls -la', 'nonexistentuser'
            )

        assert stdout == ''
        assert '不存在' in stderr
        assert return_code == -1

    @patch('subprocess.run')
    def test_check_user_exists_linux_exists(self, mock_run):
        """测试Linux用户存在检查"""
        user_switch = UserSwitch(self.config)

        # 模拟用户存在
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        exists = user_switch._check_user_exists_linux('testuser')

        assert exists is True
        mock_run.assert_called_with(['id', 'testuser'], stdout=-1, stderr=-1, text=True)

    @patch('subprocess.run')
    def test_check_user_exists_linux_not_exists(self, mock_run):
        """测试Linux用户不存在检查"""
        user_switch = UserSwitch(self.config)

        # 模拟用户不存在
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process

        exists = user_switch._check_user_exists_linux('nonexistentuser')

        assert exists is False

    @patch('subprocess.run')
    def test_check_user_exists_windows_exists(self, mock_run):
        """测试Windows用户存在检查"""
        user_switch = UserSwitch(self.config)

        # 模拟用户存在
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        exists = user_switch._check_user_exists_windows('testuser')

        assert exists is True
        mock_run.assert_called_with(['net', 'user', 'testuser'], stdout=-1, stderr=-1, text=True)

    @patch('subprocess.run')
    def test_check_user_exists_windows_not_exists(self, mock_run):
        """测试Windows用户不存在检查"""
        user_switch = UserSwitch(self.config)

        # 模拟用户不存在
        mock_process = MagicMock()
        mock_process.returncode = 2
        mock_run.return_value = mock_process

        exists = user_switch._check_user_exists_windows('nonexistentuser')

        assert exists is False

    @patch('subprocess.run')
    def test_get_user_info_linux(self, mock_run):
        """测试获取Linux用户信息"""
        user_switch = UserSwitch(self.config)

        # 模拟getent passwd输出
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = 'testuser:x:1000:1000:Test User:/home/testuser:/bin/bash'
        mock_run.return_value = mock_process

        user_info = user_switch._get_user_info_linux('testuser')

        assert user_info is not None
        assert user_info['username'] == 'testuser'
        assert user_info['uid'] == '1000'
        assert user_info['gid'] == '1000'
        assert user_info['gecos'] == 'Test User'
        assert user_info['home'] == '/home/testuser'
        assert user_info['shell'] == '/bin/bash'

    @patch('subprocess.run')
    def test_get_user_info_linux_not_exists(self, mock_run):
        """测试获取不存在的Linux用户信息"""
        user_switch = UserSwitch(self.config)

        # 模拟用户不存在
        mock_process = MagicMock()
        mock_process.returncode = 2
        mock_run.return_value = mock_process

        user_info = user_switch._get_user_info_linux('nonexistentuser')

        assert user_info is None

    @patch('subprocess.run')
    def test_get_user_info_windows(self, mock_run):
        """测试获取Windows用户信息"""
        user_switch = UserSwitch(self.config)

        # 模拟net user输出
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '''
User name                    testuser
Full Name                    Test User
Comment                      Test account
'''
        mock_run.return_value = mock_process

        user_info = user_switch._get_user_info_windows('testuser')

        assert user_info is not None
        assert user_info['username'] == 'testuser'
        assert user_info['full_name'] == 'Test User'
        assert user_info['comment'] == 'Test account'

    @patch('platform.system')
    def test_get_available_users_linux(self, mock_system):
        """测试获取Linux可用用户列表"""
        mock_system.return_value = 'Linux'
        user_switch = UserSwitch(self.config)

        with patch('subprocess.run') as mock_run:
            # 模拟getent passwd输出
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.stdout = '''root:x:0:0:root:/root:/bin/bash
testuser:x:1000:1000:Test User:/home/testuser:/bin/bash
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
'''
            mock_run.return_value = mock_process

            users = user_switch.get_available_users()

            assert len(users) == 3
            assert 'root' in users
            assert 'testuser' in users
            assert 'nobody' in users

    @patch('platform.system')
    def test_get_available_users_windows(self, mock_system):
        """测试获取Windows可用用户列表"""
        mock_system.return_value = 'Windows'
        user_switch = UserSwitch(self.config)

        with patch('subprocess.run') as mock_run:
            # 模拟net user输出
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.stdout = '''
User accounts for \\TEST-PC
-------------------------------------------------------------------------------
Administrator            Guest                    testuser

The command completed successfully.
'''
            mock_run.return_value = mock_process

            users = user_switch.get_available_users()

            assert len(users) == 3
            assert 'Administrator' in users
            assert 'Guest' in users
            assert 'testuser' in users

    @patch('platform.system')
    def test_validate_user_permissions_linux(self, mock_system):
        """测试Linux用户权限验证"""
        mock_system.return_value = 'Linux'
        user_switch = UserSwitch(self.config)

        with patch.object(user_switch, '_check_user_exists_linux', return_value=True):
            has_permissions = user_switch.validate_user_permissions('testuser')

        assert has_permissions is True

    @patch('platform.system')
    def test_validate_user_permissions_user_not_exists(self, mock_system):
        """测试不存在的用户权限验证"""
        mock_system.return_value = 'Linux'
        user_switch = UserSwitch(self.config)

        with patch.object(user_switch, '_check_user_exists_linux', return_value=False):
            has_permissions = user_switch.validate_user_permissions('nonexistentuser')

        assert has_permissions is False