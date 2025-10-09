"""
脚本执行器单元测试
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.script_executor import ScriptExecutor


class TestScriptExecutor:
    """脚本执行器测试类"""

    def setup_method(self):
        """测试方法设置"""
        self.config = {
            'execution': {
                'timeout': 30,
                'max_output_size': 1024,
                'temp_dir': '/tmp/aiops-test'
            }
        }
        self.executor = ScriptExecutor(self.config)

    def test_detect_script_type_from_content(self):
        """测试从内容检测脚本类型"""
        # Shell脚本
        shell_script = "#!/bin/bash\necho 'hello'"
        assert self.executor._detect_script_type_from_content(shell_script) == 'shell'

        # Python脚本
        python_script = "#!/usr/bin/env python\nprint('hello')"
        assert self.executor._detect_script_type_from_content(python_script) == 'python'

        # PowerShell脚本
        powershell_script = "#!/usr/bin/env pwsh\nWrite-Host 'hello'"
        assert self.executor._detect_script_type_from_content(powershell_script) == 'powershell'

        # 无shebang的Python脚本
        python_no_shebang = "import os\nprint('hello')"
        assert self.executor._detect_script_type_from_content(python_no_shebang) == 'python'

        # 无shebang的Shell脚本
        shell_no_shebang = "echo 'hello'"
        assert self.executor._detect_script_type_from_content(shell_no_shebang) == 'shell'

    def test_create_temp_script(self):
        """测试创建临时脚本文件"""
        script_content = "echo 'test script'"
        script_type = 'shell'

        temp_path = self.executor._create_temp_script(script_content, script_type)

        # 检查文件是否存在
        assert os.path.exists(temp_path)
        # 检查文件内容
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == script_content
        # 检查文件权限
        assert os.access(temp_path, os.X_OK)

        # 清理临时文件
        self.executor._cleanup_temp_file(temp_path)

    def test_cleanup_temp_file(self):
        """测试清理临时文件"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        # 确保文件存在
        assert os.path.exists(temp_path)

        # 清理文件
        self.executor._cleanup_temp_file(temp_path)

        # 确保文件已被删除
        assert not os.path.exists(temp_path)

    @patch('src.script_executor.ScriptExecutor._execute_command')
    def test_execute_script_content(self, mock_execute):
        """测试执行脚本内容"""
        # 模拟成功的命令执行
        mock_execute.return_value = {
            'success': True,
            'output': 'test output',
            'error': '',
            'return_code': 0
        }

        script_content = "echo 'test'"
        result = self.executor.execute_script_content(script_content)

        assert result['success'] is True
        assert result['output'] == 'test output'
        mock_execute.assert_called_once()

    @patch('src.script_executor.ScriptExecutor._execute_command')
    def test_execute_dynamic_wrapper(self, mock_execute):
        """测试动态脚本封装执行"""
        # 模拟成功的命令执行
        mock_execute.return_value = {
            'success': True,
            'output': 'dynamic wrapper output',
            'error': '',
            'return_code': 0
        }

        script_content = "echo 'dynamic test'"
        result = self.executor.execute_dynamic_wrapper(script_content)

        assert result['success'] is True
        assert result['output'] == 'dynamic wrapper output'
        mock_execute.assert_called_once()

    def test_detect_script_type_by_extension(self):
        """测试通过扩展名检测脚本类型"""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'print("python")')
            python_file = f.name

        with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as f:
            f.write(b'echo "shell"')
            shell_file = f.name

        with tempfile.NamedTemporaryFile(suffix='.ps1', delete=False) as f:
            f.write(b'Write-Host "powershell"')
            powershell_file = f.name

        try:
            assert self.executor._detect_script_type(python_file) == 'python'
            assert self.executor._detect_script_type(shell_file) == 'shell'
            assert self.executor._detect_script_type(powershell_file) == 'powershell'
        finally:
            # 清理临时文件
            for file_path in [python_file, shell_file, powershell_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)

    def test_detect_script_type_by_shebang(self):
        """测试通过shebang检测脚本类型"""
        # Python shebang
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('#!/usr/bin/env python\nprint("test")')
            python_file = f.name

        # Shell shebang
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('#!/bin/bash\necho "test"')
            shell_file = f.name

        # PowerShell shebang
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('#!/usr/bin/env pwsh\nWrite-Host "test"')
            powershell_file = f.name

        try:
            assert self.executor._detect_script_type(python_file) == 'python'
            assert self.executor._detect_script_type(shell_file) == 'shell'
            assert self.executor._detect_script_type(powershell_file) == 'powershell'
        finally:
            # 清理临时文件
            for file_path in [python_file, shell_file, powershell_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)

    @patch('os.path.exists')
    def test_execute_script_file_not_exists(self, mock_exists):
        """测试执行不存在的脚本文件"""
        mock_exists.return_value = False

        result = self.executor.execute_script_file('/path/to/nonexistent/script.sh')

        assert result['success'] is False
        assert '不存在' in result['error']

    @patch('src.script_executor.ScriptExecutor._execute_command')
    def test_execute_python_script(self, mock_execute):
        """测试执行Python脚本"""
        mock_execute.return_value = {
            'success': True,
            'output': 'python output',
            'error': '',
            'return_code': 0
        }

        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            script_path = f.name

        try:
            result = self.executor._execute_python_script(script_path)
            assert result['success'] is True
            assert 'python' in mock_execute.call_args[0][0]
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    @patch('src.script_executor.ScriptExecutor._execute_command')
    def test_execute_shell_script(self, mock_execute):
        """测试执行Shell脚本"""
        mock_execute.return_value = {
            'success': True,
            'output': 'shell output',
            'error': '',
            'return_code': 0
        }

        with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as f:
            script_path = f.name

        try:
            result = self.executor._execute_shell_script(script_path)
            assert result['success'] is True
            assert 'bash' in mock_execute.call_args[0][0]
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)