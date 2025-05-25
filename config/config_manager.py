import os
import configparser
from typing import Optional, Dict, Any

class ConfigManager:
    """配置管理器类，负责处理系统配置文件的读写操作"""
    
    def __init__(self, config_file: str = "HISAutoConfiguration.cfg"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
        
    def _load_config(self) -> None:
        """加载配置文件，如果文件不存在则创建默认配置"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self._create_default_config()
            
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        self.config['Server'] = {
            'RemoteServer': '\\\\172.24.20.40',
            'Port': '9222'
        }
        
        self.config['System'] = {
            'SysFolder': 'D:/HISAuto/',
            'DataSource': 'D:/HISAuto/DataSource/HISAuto.db',
            'WorkExcelFolder': 'D:/HISAuto/workFolder/',
            'WorkExcelFile': 'ExcelFile.xls',
            'SheetNum': '1',
            'Column': '1'
        }
        
        self.config['Shortcuts'] = {
            'ShortcutKey': 'Alt+J',
            'ShutDownKey': 'Alt+C'
        }
        
        self.config['AI'] = {
            'AIAddress': 'https://deepseek.zju4h.cn:4430/auth'
        }
        
        self._save_config()
        
    def _save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
            
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            section: 配置节
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
            
    def set_value(self, section: str, key: str, value: str) -> None:
        """
        设置配置值
        
        Args:
            section: 配置节
            key: 配置键
            value: 配置值
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self._save_config()
        
    def get_section(self, section: str) -> Dict[str, str]:
        """
        获取整个配置节
        
        Args:
            section: 配置节名称
            
        Returns:
            配置节的所有键值对
        """
        if self.config.has_section(section):
            return dict(self.config[section])
        return {}
        
    def update_section(self, section: str, values: Dict[str, str]) -> None:
        """
        更新整个配置节
        
        Args:
            section: 配置节名称
            values: 要更新的键值对
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        for key, value in values.items():
            self.config.set(section, key, value)
        self._save_config() 