"""
安全模块单元测试
"""

import pytest
import time
from src.security import SecurityManager


class TestSecurityManager:
    """安全管理器测试类"""

    def setup_method(self):
        """测试方法设置"""
        self.config = {
            'security': {
                'jwt_secret': 'test-jwt-secret',
                'jwt_expire_hours': 1,
                'aes_key': 'test-aes-key-32-bytes-long-key'
            }
        }
        self.security = SecurityManager(self.config)

    def test_generate_and_verify_jwt_token(self):
        """测试JWT令牌生成和验证"""
        payload = {'user_id': 'test_user', 'role': 'admin'}

        # 生成令牌
        token = self.security.generate_jwt_token(payload)
        assert token is not None

        # 验证令牌
        decoded_payload = self.security.verify_jwt_token(token)
        assert decoded_payload is not None
        assert decoded_payload['user_id'] == 'test_user'
        assert decoded_payload['role'] == 'admin'

    def test_verify_expired_token(self):
        """测试过期令牌验证"""
        # 创建一个过期的令牌
        payload = {'user_id': 'test_user', 'exp': int(time.time()) - 3600}
        token = self.security.generate_jwt_token(payload)

        # 验证应该失败
        decoded_payload = self.security.verify_jwt_token(token)
        assert decoded_payload is None

    def test_encrypt_and_decrypt_data(self):
        """测试数据加密和解密"""
        original_data = '这是要加密的敏感数据'

        # 加密数据
        encrypted_data = self.security.encrypt_data(original_data)
        assert encrypted_data is not None
        assert encrypted_data != original_data

        # 解密数据
        decrypted_data = self.security.decrypt_data(encrypted_data)
        assert decrypted_data == original_data

    def test_generate_api_key(self):
        """测试API密钥生成"""
        user_id = 'test_user'
        permissions = ['exec:command', 'exec:script']

        api_key_info = self.security.generate_api_key(user_id, permissions)

        assert 'api_key' in api_key_info
        assert 'token' in api_key_info
        assert api_key_info['api_key'] is not None
        assert api_key_info['token'] is not None

    def test_verify_api_key(self):
        """测试API密钥验证"""
        user_id = 'test_user'
        permissions = ['exec:command']

        # 生成API密钥
        api_key_info = self.security.generate_api_key(user_id, permissions)

        # 验证API密钥
        is_valid = self.security.verify_api_key(
            api_key_info['api_key'],
            api_key_info['token']
        )
        assert is_valid is True

        # 使用错误的API密钥验证
        is_valid = self.security.verify_api_key(
            'wrong-api-key',
            api_key_info['token']
        )
        assert is_valid is False

    def test_hash_password(self):
        """测试密码哈希"""
        password = 'my_secret_password'

        hashed_password = self.security.hash_password(password)

        # 哈希结果应该不同
        assert hashed_password != password
        # 哈希长度应该是64个字符（SHA-256）
        assert len(hashed_password) == 64

    def test_verify_password(self):
        """测试密码验证"""
        password = 'my_secret_password'

        hashed_password = self.security.hash_password(password)

        # 验证正确密码
        assert self.security.verify_password(password, hashed_password) is True

        # 验证错误密码
        assert self.security.verify_password('wrong_password', hashed_password) is False

    def test_generate_random_key(self):
        """测试随机密钥生成"""
        key1 = self.security.generate_random_key(32)
        key2 = self.security.generate_random_key(32)

        assert len(key1) > 0
        assert len(key2) > 0
        # 两次生成的密钥应该不同
        assert key1 != key2

    def test_validate_token_permissions(self):
        """测试令牌权限验证"""
        payload = {
            'user_id': 'test_user',
            'permissions': ['exec:command', 'exec:script', 'read:logs']
        }

        token = self.security.generate_jwt_token(payload)

        # 测试具有所需权限
        assert self.security.validate_token_permissions(
            token, ['exec:command']
        ) is True

        # 测试具有多个所需权限
        assert self.security.validate_token_permissions(
            token, ['exec:command', 'read:logs']
        ) is True

        # 测试缺少权限
        assert self.security.validate_token_permissions(
            token, ['admin:all']
        ) is False

        # 测试空权限列表
        assert self.security.validate_token_permissions(
            token, []
        ) is True