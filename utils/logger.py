import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

from config.config_manager import ConfigManager

class Logger:
    """日志管理类，负责处理系统日志的创建和记录"""
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志文件目录
            log_level: 日志级别
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self._setup_logger()
        
    def _setup_logger(self) -> None:
        """设置日志记录器"""
        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # 创建日志文件名
        log_file = os.path.join(
            self.log_dir,
            f"hisauto_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # 创建日志记录器
        self.logger = logging.getLogger('HISAuto')
        self.logger.setLevel(self.log_level)
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message: str) -> None:
        """
        记录调试级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.debug(message)
        
    def info(self, message: str) -> None:
        """
        记录信息级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.info(message)
        
    def warning(self, message: str) -> None:
        """
        记录警告级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.warning(message)
        
    def error(self, message: str) -> None:
        """
        记录错误级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.error(message)
        
    def critical(self, message: str) -> None:
        """
        记录严重错误级别日志
        
        Args:
            message: 日志消息
        """
        self.logger.critical(message)
        
    def exception(self, message: str) -> None:
        """
        记录异常信息
        
        Args:
            message: 日志消息
        """
        self.logger.exception(message) 

# 获取配置管理器实例
config_manager = ConfigManager()
log_dir = config_manager.get_value('System', 'SysFolder', 'D:/HISAuto/') + 'logs'
logger = Logger(log_dir)
