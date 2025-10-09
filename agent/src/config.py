"""
配置管理模块

负责加载和管理代理程序的配置。
"""

import os
import yaml
from pathlib import Path


class Config:
    """配置管理类"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load(cls, config_path=None):
        """加载配置"""
        if cls._config is not None:
            return cls._config

        # 确定配置文件路径
        if config_path is None:
            config_path = os.getenv('AIOPS_CONFIG', 'config/default.yaml')

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            cls._config = yaml.safe_load(f)

        # 环境变量覆盖
        cls._override_with_env()

        return cls._config

    @classmethod
    def _override_with_env(cls):
        """使用环境变量覆盖配置"""
        if not cls._config:
            return

        # 服务器配置
        if os.getenv('AIOPS_HOST'):
            cls._config['server']['host'] = os.getenv('AIOPS_HOST')
        if os.getenv('AIOPS_PORT'):
            cls._config['server']['port'] = int(os.getenv('AIOPS_PORT'))

        # 安全配置
        if os.getenv('AIOPS_JWT_SECRET'):
            cls._config['security']['jwt_secret'] = os.getenv('AIOPS_JWT_SECRET')
        if os.getenv('AIOPS_AES_KEY'):
            cls._config['security']['aes_key'] = os.getenv('AIOPS_AES_KEY')

        # 日志配置
        if os.getenv('AIOPS_LOG_LEVEL'):
            cls._config['logging']['level'] = os.getenv('AIOPS_LOG_LEVEL')

    @classmethod
    def get(cls, key, default=None):
        """获取配置值"""
        if cls._config is None:
            cls.load()

        keys = key.split('.')
        value = cls._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    @classmethod
    def reload(cls, config_path=None):
        """重新加载配置"""
        cls._config = None
        return cls.load(config_path)