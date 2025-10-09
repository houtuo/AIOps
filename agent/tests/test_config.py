"""
配置模块单元测试
"""

import pytest
import os
import tempfile
import yaml
from src.config import Config


class TestConfig:
    """配置管理测试类"""

    def setup_method(self):
        """测试方法设置"""
        # 重置单例实例
        Config._instance = None
        Config._config = None

    def teardown_method(self):
        """测试方法清理"""
        # 清理环境变量
        env_vars = ['AIOPS_HOST', 'AIOPS_PORT', 'AIOPS_JWT_SECRET', 'AIOPS_AES_KEY', 'AIOPS_LOG_LEVEL']
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    def create_temp_config_file(self, config_data):
        """创建临时配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            return f.name

    def test_load_config_success(self):
        """测试成功加载配置"""
        config_data = {
            'server': {
                'host': '127.0.0.1',
                'port': 8443
            },
            'security': {
                'jwt_secret': 'test-secret'
            }
        }

        config_file = self.create_temp_config_file(config_data)

        try:
            config = Config.load(config_file)

            assert config is not None
            assert config['server']['host'] == '127.0.0.1'
            assert config['server']['port'] == 8443
            assert config['security']['jwt_secret'] == 'test-secret'
        finally:
            os.unlink(config_file)

    def test_load_config_file_not_exists(self):
        """测试加载不存在的配置文件"""
        with pytest.raises(FileNotFoundError):
            Config.load('/path/to/nonexistent/config.yaml')

    def test_get_config_value(self):
        """测试获取配置值"""
        config_data = {
            'server': {
                'host': '0.0.0.0',
                'port': 8443
            },
            'logging': {
                'level': 'INFO'
            }
        }

        config_file = self.create_temp_config_file(config_data)

        try:
            Config.load(config_file)

            # 测试获取存在的配置值
            assert Config.get('server.host') == '0.0.0.0'
            assert Config.get('server.port') == 8443
            assert Config.get('logging.level') == 'INFO'

            # 测试获取不存在的配置值
            assert Config.get('nonexistent.key') is None
            assert Config.get('server.nonexistent', 'default') == 'default'
        finally:
            os.unlink(config_file)

    def test_override_with_env_variables(self):
        """测试环境变量覆盖配置"""
        config_data = {
            'server': {
                'host': '0.0.0.0',
                'port': 8443
            },
            'security': {
                'jwt_secret': 'original-secret',
                'aes_key': 'original-key'
            },
            'logging': {
                'level': 'INFO'
            }
        }

        config_file = self.create_temp_config_file(config_data)

        try:
            # 设置环境变量
            os.environ['AIOPS_HOST'] = '192.168.1.100'
            os.environ['AIOPS_PORT'] = '9000'
            os.environ['AIOPS_JWT_SECRET'] = 'env-secret'
            os.environ['AIOPS_AES_KEY'] = 'env-key'
            os.environ['AIOPS_LOG_LEVEL'] = 'DEBUG'

            config = Config.load(config_file)

            # 验证环境变量覆盖了配置文件
            assert config['server']['host'] == '192.168.1.100'
            assert config['server']['port'] == 9000
            assert config['security']['jwt_secret'] == 'env-secret'
            assert config['security']['aes_key'] == 'env-key'
            assert config['logging']['level'] == 'DEBUG'
        finally:
            os.unlink(config_file)

    def test_singleton_pattern(self):
        """测试单例模式"""
        config_data = {'test': 'value'}
        config_file = self.create_temp_config_file(config_data)

        try:
            # 第一次加载
            config1 = Config.load(config_file)
            # 第二次加载应该返回相同的实例
            config2 = Config.load(config_file)

            assert config1 is config2
            assert id(config1) == id(config2)
        finally:
            os.unlink(config_file)

    def test_reload_config(self):
        """测试重新加载配置"""
        config_data1 = {'version': '1.0'}
        config_file1 = self.create_temp_config_file(config_data1)

        config_data2 = {'version': '2.0'}
        config_file2 = self.create_temp_config_file(config_data2)

        try:
            # 第一次加载
            config1 = Config.load(config_file1)
            assert config1['version'] == '1.0'

            # 重新加载不同的配置文件
            config2 = Config.reload(config_file2)
            assert config2['version'] == '2.0'

            # 验证配置已更新
            assert Config.get('version') == '2.0'
        finally:
            os.unlink(config_file1)
            os.unlink(config_file2)

    def test_get_with_default_value(self):
        """测试使用默认值获取配置"""
        config_data = {
            'server': {
                'host': 'localhost'
            }
        }

        config_file = self.create_temp_config_file(config_data)

        try:
            Config.load(config_file)

            # 测试存在的配置值
            assert Config.get('server.host', 'default-host') == 'localhost'

            # 测试不存在的配置值使用默认值
            assert Config.get('server.port', 8080) == 8080
            assert Config.get('nonexistent.key', 'default-value') == 'default-value'
        finally:
            os.unlink(config_file)

    def test_nested_config_get(self):
        """测试嵌套配置获取"""
        config_data = {
            'database': {
                'mysql': {
                    'host': 'localhost',
                    'port': 3306
                },
                'redis': {
                    'host': '127.0.0.1',
                    'port': 6379
                }
            }
        }

        config_file = self.create_temp_config_file(config_data)

        try:
            Config.load(config_file)

            # 测试多层嵌套配置获取
            assert Config.get('database.mysql.host') == 'localhost'
            assert Config.get('database.mysql.port') == 3306
            assert Config.get('database.redis.host') == '127.0.0.1'
            assert Config.get('database.redis.port') == 6379

            # 测试不存在的嵌套配置
            assert Config.get('database.postgres.host') is None
            assert Config.get('database.mysql.password') is None
        finally:
            os.unlink(config_file)

    def test_config_with_special_characters(self):
        """测试包含特殊字符的配置"""
        config_data = {
            'security': {
                'jwt_secret': 'abc123!@#$%^&*()',
                'aes_key': 'key-with-special-chars-!@#$%'
            },
            'server': {
                'description': '测试服务器配置 - Test Server Config'
            }
        }

        config_file = self.create_temp_config_file(config_data)

        try:
            config = Config.load(config_file)

            assert config['security']['jwt_secret'] == 'abc123!@#$%^&*()'
            assert config['security']['aes_key'] == 'key-with-special-chars-!@#$%'
            assert config['server']['description'] == '测试服务器配置 - Test Server Config'
        finally:
            os.unlink(config_file)