#!/usr/bin/env python3
"""
AIOps代理程序打包配置

支持Linux RPM包和Windows EXE文件打包。
"""

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.bdist_rpm import bdist_rpm


class PostInstallCommand(install):
    """安装后处理命令"""

    def run(self):
        install.run(self)
        # 安装后创建必要的目录和文件
        self._create_directories()

    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            '/etc/aiops',
            '/var/log/aiops',
            '/var/lib/aiops',
            '/tmp/aiops'
        ]

        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"创建目录: {directory}")
            except Exception as e:
                print(f"创建目录失败 {directory}: {e}")


class CustomBdistRpm(bdist_rpm):
    """自定义RPM打包配置"""

    def initialize_options(self):
        bdist_rpm.initialize_options(self)
        # 设置RPM包信息
        self.distribution_name = 'aiops-agent'
        self.vendor = 'AIOps'
        self.packager = 'AIOps Team'
        self.group = 'Applications/System'


# 读取版本信息
def get_version():
    """获取版本号"""
    version_file = os.path.join(os.path.dirname(__file__), 'src', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('\'"')
    return '1.0.0'


# 读取依赖
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]


setup(
    name="aiops-agent",
    version=get_version(),
    description="AIOps自动化运维代理程序",
    long_description="""
AIOps自动化运维代理程序

一个跨平台的自动化运维代理程序，支持命令执行、脚本执行、用户身份切换和加密通信。

主要特性：
- 跨平台支持 (Windows/Linux)
- 命令执行和结果捕获
- 脚本执行 (Shell, PowerShell, Python)
- 用户身份切换
- TLS加密通信
- RESTful API接口
- 离线部署支持
""",
    author="AIOps Team",
    author_email="aiops@example.com",
    url="https://github.com/houtuo/AIOps",
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'aiops-agent=src.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    keywords='aiops automation agent system-administration',
    cmdclass={
        'install': PostInstallCommand,
        'bdist_rpm': CustomBdistRpm,
    },
    # RPM包特定配置
    options={
        'bdist_rpm': {
            'vendor': 'AIOps',
            'packager': 'AIOps Team',
            'group': 'Applications/System',
            'requires': 'python3 >= 3.8',
            'build_requires': 'python3-devel',
            'doc_files': ['README.md', 'docs/'],
            'changelog': 'CHANGELOG.md',
        }
    },
    # 数据文件
    data_files=[
        ('/etc/aiops', ['config/default.yaml']),
        ('/usr/lib/systemd/system', ['packaging/aiops-agent.service']),
        ('/var/log/aiops', []),
        ('/var/lib/aiops', []),
    ],
    # 脚本文件
    scripts=[
        'scripts/generate_keys.py',
        'scripts/test_api.py',
    ],
)