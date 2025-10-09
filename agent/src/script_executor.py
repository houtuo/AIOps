"""
脚本执行器模块

负责执行各种类型的脚本，包括动态脚本转换和执行。
"""

import os
import tempfile
import subprocess
import logging
import platform
import random
import string
from typing import Dict, Optional, Tuple
from pathlib import Path


class ScriptExecutor:
    """脚本执行器类"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()

        # 执行配置
        exec_config = config.get('execution', {})
        self.timeout = exec_config.get('timeout', 300)
        self.max_output_size = exec_config.get('max_output_size', 1048576)
        self.temp_dir = exec_config.get('temp_dir', '/tmp/aiops')

        # 创建临时目录
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)

    def execute_script_file(
        self,
        script_path: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        执行本地脚本文件

        Args:
            script_path: 脚本文件路径
            user: 执行用户（可选）
            working_dir: 工作目录（可选）
            env: 环境变量（可选）

        Returns:
            执行结果
        """
        self.logger.info(f"执行脚本文件: {script_path}")

        if not os.path.exists(script_path):
            return {
                'success': False,
                'output': '',
                'error': f'脚本文件不存在: {script_path}',
                'return_code': -1
            }

        try:
            # 检测脚本类型
            script_type = self._detect_script_type(script_path)

            # 根据脚本类型执行
            if script_type == 'python':
                result = self._execute_python_script(script_path, user, working_dir, env)
            elif script_type == 'shell':
                result = self._execute_shell_script(script_path, user, working_dir, env)
            elif script_type == 'powershell':
                result = self._execute_powershell_script(script_path, user, working_dir, env)
            else:
                result = self._execute_generic_script(script_path, user, working_dir, env)

            return result

        except Exception as e:
            self.logger.error(f"脚本执行失败: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    def execute_script_content(
        self,
        script_content: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        执行脚本内容（动态转换）

        Args:
            script_content: 脚本内容
            user: 执行用户（可选）
            working_dir: 工作目录（可选）
            env: 环境变量（可选）

        Returns:
            执行结果
        """
        self.logger.info("执行动态脚本内容")

        try:
            # 检测脚本类型
            script_type = self._detect_script_type_from_content(script_content)

            # 创建临时脚本文件
            temp_script_path = self._create_temp_script(script_content, script_type)

            # 执行脚本
            if script_type == 'python':
                result = self._execute_python_script(temp_script_path, user, working_dir, env)
            elif script_type == 'shell':
                result = self._execute_shell_script(temp_script_path, user, working_dir, env)
            elif script_type == 'powershell':
                result = self._execute_powershell_script(temp_script_path, user, working_dir, env)
            else:
                result = self._execute_generic_script(temp_script_path, user, working_dir, env)

            # 清理临时文件
            self._cleanup_temp_file(temp_script_path)

            return result

        except Exception as e:
            self.logger.error(f"动态脚本执行失败: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    def _detect_script_type(self, script_path: str) -> str:
        """检测脚本文件类型"""
        # 根据扩展名和shebang检测
        ext = Path(script_path).suffix.lower()

        # 读取第一行检测shebang
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
        except:
            first_line = ""

        if first_line.startswith('#!/'):
            if 'python' in first_line:
                return 'python'
            elif 'bash' in first_line or 'sh' in first_line:
                return 'shell'
            elif 'powershell' in first_line or 'pwsh' in first_line:
                return 'powershell'

        # 根据扩展名判断
        if ext == '.py':
            return 'python'
        elif ext in ['.sh', '.bash']:
            return 'shell'
        elif ext == '.ps1':
            return 'powershell'
        else:
            # 默认作为shell脚本处理
            return 'shell'

    def _detect_script_type_from_content(self, script_content: str) -> str:
        """从脚本内容检测类型"""
        lines = script_content.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            if first_line.startswith('#!/'):
                if 'python' in first_line:
                    return 'python'
                elif 'bash' in first_line or 'sh' in first_line:
                    return 'shell'
                elif 'powershell' in first_line or 'pwsh' in first_line:
                    return 'powershell'

        # 根据内容特征判断
        if script_content.strip().startswith('import ') or 'def ' in script_content:
            return 'python'
        elif script_content.strip().startswith('#!') or 'echo' in script_content:
            return 'shell'
        elif 'Write-Host' in script_content or 'Get-' in script_content:
            return 'powershell'
        else:
            return 'shell'

    def _create_temp_script(self, script_content: str, script_type: str) -> str:
        """创建临时脚本文件"""
        # 生成随机文件名
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

        # 根据类型确定扩展名
        if script_type == 'python':
            ext = '.py'
        elif script_type == 'shell':
            ext = '.sh'
        elif script_type == 'powershell':
            ext = '.ps1'
        else:
            ext = '.sh'

        temp_path = os.path.join(self.temp_dir, f'tmp_{random_str}{ext}')

        # 写入脚本内容
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 设置执行权限
        os.chmod(temp_path, 0o755)

        return temp_path

    def _execute_python_script(
        self,
        script_path: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """执行Python脚本"""
        command = f'python "{script_path}"'
        return self._execute_command(command, user, working_dir, env)

    def _execute_shell_script(
        self,
        script_path: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """执行Shell脚本"""
        command = f'bash "{script_path}"'
        return self._execute_command(command, user, working_dir, env)

    def _execute_powershell_script(
        self,
        script_path: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """执行PowerShell脚本"""
        if self.platform == 'windows':
            command = f'powershell -File "{script_path}"'
        else:
            command = f'pwsh -File "{script_path}"'
        return self._execute_command(command, user, working_dir, env)

    def _execute_generic_script(
        self,
        script_path: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """执行通用脚本"""
        # 直接执行脚本文件
        command = f'"{script_path}"'
        return self._execute_command(command, user, working_dir, env)

    def _execute_command(
        self,
        command: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """执行命令"""
        from src.executor import CommandExecutor
        executor = CommandExecutor(self.config)
        return executor.execute(command, user, working_dir, env)

    def _cleanup_temp_file(self, file_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            self.logger.warning(f"清理临时文件失败: {e}")

    def execute_dynamic_wrapper(
        self,
        script_content: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        动态脚本封装执行（需求文档中的FR-03）

        将任意脚本内容封装为Python脚本执行
        """
        self.logger.info("执行动态脚本封装")

        try:
            # 检测原始脚本类型
            original_type = self._detect_script_type_from_content(script_content)

            # 生成随机文件名
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

            # 根据类型确定扩展名
            if original_type == 'python':
                ext = '.py'
                interpreter = 'python'
            elif original_type == 'shell':
                ext = '.sh'
                interpreter = 'bash'
            elif original_type == 'powershell':
                ext = '.ps1'
                interpreter = 'powershell' if self.platform == 'windows' else 'pwsh'
            else:
                ext = '.sh'
                interpreter = 'bash'

            temp_script_name = f'tmp_{random_str}{ext}'
            temp_script_path = os.path.join(self.temp_dir, temp_script_name)

            # 创建封装Python脚本
            wrapper_script = self._create_wrapper_script(script_content, temp_script_path, interpreter)

            # 执行封装脚本
            result = self._execute_python_script_content(wrapper_script, user, working_dir, env)

            # 清理临时文件
            self._cleanup_temp_file(temp_script_path)

            return result

        except Exception as e:
            self.logger.error(f"动态脚本封装执行失败: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    def _create_wrapper_script(self, script_content: str, temp_script_path: str, interpreter: str) -> str:
        """创建封装Python脚本"""
        wrapper_script = f'''
import subprocess
import os
import sys

script_content = """{script_content}"""

temp_script_path = "{temp_script_path}"

# 写入原始脚本内容
with open(temp_script_path, 'w', encoding='utf-8') as f:
    f.write(script_content)

# 添加执行权限
os.chmod(temp_script_path, 0o755)

# 执行脚本
result = subprocess.run(["{interpreter}", temp_script_path],
                       capture_output=True, text=True, env=os.environ)

# 输出结果
print(result.stdout)
if result.returncode != 0:
    print(result.stderr, file=sys.stderr)

# 清理临时文件
os.remove(temp_script_path)

sys.exit(result.returncode)
'''
        return wrapper_script

    def _execute_python_script_content(
        self,
        script_content: str,
        user: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """执行Python脚本内容"""
        # 创建临时Python脚本
        temp_python_script = self._create_temp_script(script_content, 'python')

        # 执行Python脚本
        result = self._execute_python_script(temp_python_script, user, working_dir, env)

        # 清理临时文件
        self._cleanup_temp_file(temp_python_script)

        return result
