"""
安全模块

负责JWT认证和AES加密功能。
"""

import jwt
import base64
import os
import time
import logging
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecurityManager:
    """安全管理器类"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # 安全配置
        security_config = config.get('security', {})
        self.jwt_secret = security_config.get('jwt_secret', 'your-jwt-secret-here')
        self.jwt_expire_hours = security_config.get('jwt_expire_hours', 24)
        self.aes_key = security_config.get('aes_key', 'your-aes-256-key-here-32-bytes')

        # 初始化AES加密器
        self.fernet = self._init_fernet()

    def _init_fernet(self) -> Fernet:
        """初始化Fernet加密器"""
        # 确保AES密钥是32字节的
        if len(self.aes_key) != 32:
            self.logger.warning("AES密钥长度不是32字节，将进行转换")
            # 使用PBKDF2派生32字节密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'aiops_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.aes_key.encode()))
        else:
            key = base64.urlsafe_b64encode(self.aes_key.encode())

        return Fernet(key)

    def generate_jwt_token(self, payload: Dict[str, Any]) -> str:
        """
        生成JWT令牌

        Args:
            payload: 载荷数据

        Returns:
            JWT令牌字符串
        """
        try:
            # 添加过期时间
            payload['exp'] = int(time.time()) + (self.jwt_expire_hours * 3600)
            payload['iat'] = int(time.time())

            # 生成令牌
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return token

        except Exception as e:
            self.logger.error(f"生成JWT令牌失败: {e}")
            raise

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌

        Args:
            token: JWT令牌

        Returns:
            解码后的载荷数据，如果验证失败返回None
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload

        except jwt.ExpiredSignatureError:
            self.logger.warning("JWT令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"JWT令牌无效: {e}")
            return None
        except Exception as e:
            self.logger.error(f"JWT令牌验证失败: {e}")
            return None

    def encrypt_data(self, data: str) -> str:
        """
        使用AES加密数据

        Args:
            data: 要加密的数据

        Returns:
            加密后的Base64字符串
        """
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return encrypted_data.decode()

        except Exception as e:
            self.logger.error(f"数据加密失败: {e}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """
        使用AES解密数据

        Args:
            encrypted_data: 加密的数据

        Returns:
            解密后的字符串
        """
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()

        except Exception as e:
            self.logger.error(f"数据解密失败: {e}")
            raise

    def generate_api_key(self, user_id: str, permissions: list) -> Dict[str, str]:
        """
        生成API密钥

        Args:
            user_id: 用户ID
            permissions: 权限列表

        Returns:
            包含API密钥和令牌的字典
        """
        try:
            # 生成随机API密钥
            api_key = base64.urlsafe_b64encode(os.urandom(32)).decode()

            # 创建JWT载荷
            payload = {
                'user_id': user_id,
                'permissions': permissions,
                'api_key': api_key,
                'type': 'api_key'
            }

            # 生成JWT令牌
            token = self.generate_jwt_token(payload)

            return {
                'api_key': api_key,
                'token': token
            }

        except Exception as e:
            self.logger.error(f"生成API密钥失败: {e}")
            raise

    def verify_api_key(self, api_key: str, token: str) -> bool:
        """
        验证API密钥

        Args:
            api_key: API密钥
            token: JWT令牌

        Returns:
            验证是否成功
        """
        try:
            # 验证JWT令牌
            payload = self.verify_jwt_token(token)
            if not payload:
                return False

            # 检查API密钥是否匹配
            if payload.get('api_key') != api_key:
                return False

            # 检查令牌类型
            if payload.get('type') != 'api_key':
                return False

            return True

        except Exception as e:
            self.logger.error(f"API密钥验证失败: {e}")
            return False

    def hash_password(self, password: str) -> str:
        """
        哈希密码

        Args:
            password: 原始密码

        Returns:
            哈希后的密码
        """
        import hashlib
        # 使用SHA-256哈希密码
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            password: 原始密码
            hashed_password: 哈希后的密码

        Returns:
            验证是否成功
        """
        return self.hash_password(password) == hashed_password

    def generate_random_key(self, length: int = 32) -> str:
        """
        生成随机密钥

        Args:
            length: 密钥长度

        Returns:
            随机密钥字符串
        """
        return base64.urlsafe_b64encode(os.urandom(length)).decode()

    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        加密文件

        Args:
            file_path: 输入文件路径
            output_path: 输出文件路径（可选）

        Returns:
            加密后的文件路径
        """
        try:
            if not output_path:
                output_path = file_path + '.enc'

            with open(file_path, 'rb') as f:
                file_data = f.read()

            encrypted_data = self.fernet.encrypt(file_data)

            with open(output_path, 'wb') as f:
                f.write(encrypted_data)

            return output_path

        except Exception as e:
            self.logger.error(f"文件加密失败: {e}")
            raise

    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        解密文件

        Args:
            encrypted_file_path: 加密文件路径
            output_path: 输出文件路径（可选）

        Returns:
            解密后的文件路径
        """
        try:
            if not output_path:
                output_path = encrypted_file_path.replace('.enc', '')

            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)

            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            return output_path

        except Exception as e:
            self.logger.error(f"文件解密失败: {e}")
            raise

    def validate_token_permissions(self, token: str, required_permissions: list) -> bool:
        """
        验证令牌权限

        Args:
            token: JWT令牌
            required_permissions: 需要的权限列表

        Returns:
            是否具有所需权限
        """
        try:
            payload = self.verify_jwt_token(token)
            if not payload:
                return False

            user_permissions = payload.get('permissions', [])

            # 检查是否具有所有需要的权限
            for permission in required_permissions:
                if permission not in user_permissions:
                    self.logger.warning(f"缺少权限: {permission}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"权限验证失败: {e}")
            return False