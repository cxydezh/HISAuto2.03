import hashlib
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoUtils:
    """加密解密工具类"""
    
    @staticmethod
    def generate_key(password: str, salt: bytes) -> bytes:
        """生成加密密钥
        
        Args:
            password: 密码
            salt: 盐值
            
        Returns:
            bytes: 加密密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @staticmethod
    def encrypt_data(data: str, key: bytes) -> Optional[str]:
        """加密数据
        
        Args:
            data: 要加密的数据
            key: 加密密钥
            
        Returns:
            Optional[str]: 加密后的数据，如果加密失败则返回None
        """
        try:
            f = Fernet(key)
            encrypted_data = f.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception:
            return None
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: bytes) -> Optional[str]:
        """解密数据
        
        Args:
            encrypted_data: 加密的数据
            key: 加密密钥
            
        Returns:
            Optional[str]: 解密后的数据，如果解密失败则返回None
        """
        try:
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception:
            return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希处理
        
        Args:
            password: 原始密码
            
        Returns:
            str: 哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码
        
        Args:
            password: 要验证的密码
            hashed_password: 哈希后的密码
            
        Returns:
            bool: 密码是否正确
        """
        return CryptoUtils.hash_password(password) == hashed_password 