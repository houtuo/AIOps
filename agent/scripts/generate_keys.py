#!/usr/bin/env python3
"""
密钥生成脚本

生成AES和JWT密钥，以及TLS证书。
"""

import os
import sys
import base64
import secrets
import argparse
import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.security import SecurityManager


def generate_aes_key():
    """生成AES密钥"""
    # 生成32字节的随机密钥
    key = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key).decode()


def generate_jwt_secret():
    """生成JWT密钥"""
    # 生成64字节的随机密钥
    secret = secrets.token_bytes(64)
    return base64.urlsafe_b64encode(secret).decode()


def generate_ssl_certificates(cert_dir: str):
    """
    生成自签名SSL证书

    Args:
        cert_dir: 证书保存目录
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        # 创建证书目录
        os.makedirs(cert_dir, exist_ok=True)

        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # 生成公钥
        public_key = private_key.public_key()

        # 创建证书主体
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AIOps"),
            x509.NameAttribute(NameOID.COMMON_NAME, "aiops-agent"),
        ])

        # 创建证书
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            public_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())

        # 保存私钥
        private_key_path = os.path.join(cert_dir, "server.key")
        with open(private_key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # 保存证书
        cert_path = os.path.join(cert_dir, "server.crt")
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        print(f"✓ SSL证书已生成:")
        print(f"  私钥: {private_key_path}")
        print(f"  证书: {cert_path}")

    except ImportError:
        print("⚠ 无法生成SSL证书，请安装cryptography库")
        print("  运行: pip install cryptography")


def update_config_file(config_path: str, aes_key: str, jwt_secret: str):
    """
    更新配置文件中的密钥

    Args:
        config_path: 配置文件路径
        aes_key: AES密钥
        jwt_secret: JWT密钥
    """
    try:
        import yaml

        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 更新密钥
        if 'security' not in config:
            config['security'] = {}

        config['security']['aes_key'] = aes_key
        config['security']['jwt_secret'] = jwt_secret

        # 保存配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        print(f"✓ 配置文件已更新: {config_path}")

    except Exception as e:
        print(f"✗ 更新配置文件失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成AIOps代理程序的密钥和证书')
    parser.add_argument('--config', default='config/default.yaml',
                       help='配置文件路径 (默认: config/default.yaml)')
    parser.add_argument('--cert-dir', default='config',
                       help='证书保存目录 (默认: config)')
    parser.add_argument('--no-ssl', action='store_true',
                       help='不生成SSL证书')
    parser.add_argument('--no-config-update', action='store_true',
                       help='不更新配置文件')

    args = parser.parse_args()

    print("🔐 AIOps代理程序密钥生成工具")
    print("=" * 50)

    # 生成AES密钥
    print("\n1. 生成AES加密密钥...")
    aes_key = generate_aes_key()
    print(f"   AES密钥: {aes_key}")

    # 生成JWT密钥
    print("\n2. 生成JWT签名密钥...")
    jwt_secret = generate_jwt_secret()
    print(f"   JWT密钥: {jwt_secret}")

    # 生成SSL证书
    if not args.no_ssl:
        print("\n3. 生成SSL证书...")
        generate_ssl_certificates(args.cert_dir)

    # 更新配置文件
    if not args.no_config_update:
        print("\n4. 更新配置文件...")
        config_path = Path(args.config)
        if config_path.exists():
            update_config_file(str(config_path), aes_key, jwt_secret)
        else:
            print(f"⚠ 配置文件不存在: {config_path}")

    # 输出重要信息
    print("\n" + "=" * 50)
    print("✅ 密钥生成完成！")
    print("\n重要提醒:")
    print("1. 请妥善保管生成的密钥")
    print("2. 在生产环境中请使用正式的SSL证书")
    print("3. 定期轮换密钥以增强安全性")

    # 显示生成的密钥（仅用于开发环境）
    print("\n生成的密钥:")
    print(f"AES密钥: {aes_key}")
    print(f"JWT密钥: {jwt_secret}")


if __name__ == "__main__":
    main()