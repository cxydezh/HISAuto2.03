import socket
import json
from typing import Optional, Dict, Any, Union
from pathlib import Path

class NetworkUtils:
    """网络通信工具类"""
    
    @staticmethod
    def get_local_ip() -> str:
        """获取本地IP地址
        
        Returns:
            str: 本地IP地址
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def is_port_available(port: int) -> bool:
        """检查端口是否可用
        
        Args:
            port: 端口号
            
        Returns:
            bool: 端口是否可用
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", port))
            s.close()
            return True
        except socket.error:
            return False
    
    @staticmethod
    def find_available_port(start_port: int = 8000, max_port: int = 9000) -> Optional[int]:
        """查找可用端口
        
        Args:
            start_port: 起始端口
            max_port: 最大端口
            
        Returns:
            Optional[int]: 可用端口号，如果找不到则返回None
        """
        for port in range(start_port, max_port + 1):
            if NetworkUtils.is_port_available(port):
                return port
        return None
    
    @staticmethod
    def save_network_config(config: Dict[str, Any], config_path: Union[str, Path]) -> bool:
        """保存网络配置
        
        Args:
            config: 配置字典
            config_path: 配置文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_network_config(config_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """加载网络配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 配置字典，如果加载失败则返回None
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None 