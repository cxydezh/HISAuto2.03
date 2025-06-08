import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

class LogManager:
    """日志管理器，用于管理系统的所有日志"""
    
    def __init__(self, log_dir: str = "logs"):
        """初始化日志管理器
        
        Args:
            log_dir: 日志文件存储目录
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建不同的日志记录器
        self.system_logger = self._setup_logger("system", "system.log")
        self.user_logger = self._setup_logger("user", "user.log")
        self.task_logger = self._setup_logger("task", "task.log")
        
    def _setup_logger(self, name: str, filename: str) -> logging.Logger:
        """设置日志记录器
        
        Args:
            name: 日志记录器名称
            filename: 日志文件名
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            self.log_dir / filename,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_system(self, level: str, message: str):
        """记录系统日志
        
        Args:
            level: 日志级别 (debug, info, warning, error, critical)
            message: 日志消息
        """
        log_func = getattr(self.system_logger, level.lower())
        log_func(message)
        
    def log_user_action(self, user_id: int, action: str, status: str = "success"):
        """记录用户操作日志
        
        Args:
            user_id: 用户ID
            action: 操作描述
            status: 操作状态
        """
        self.user_logger.info(f"User {user_id} - {action} - {status}")
        
    def log_task(self, task_id: int, action: str, status: str, details: str = ""):
        """记录任务执行日志
        
        Args:
            task_id: 任务ID
            action: 任务动作
            status: 任务状态
            details: 详细信息
        """
        self.task_logger.info(f"Task {task_id} - {action} - {status} - {details}")

# 创建全局日志管理器实例
log_manager = LogManager() 