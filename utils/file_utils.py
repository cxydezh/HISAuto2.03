import os
import shutil
from pathlib import Path
from typing import Optional, List, Union

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_dir(directory: Union[str, Path]) -> Path:
        """确保目录存在，如果不存在则创建
        
        Args:
            directory: 目录路径
            
        Returns:
            Path: 目录的Path对象
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """复制文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """移动文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def delete_file(file_path: Union[str, Path]) -> bool:
        """删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            Path(file_path).unlink()
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def list_files(directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            
        Returns:
            List[Path]: 文件路径列表
        """
        return list(Path(directory).glob(pattern))
    
    @staticmethod
    def read_file(file_path: Union[str, Path]) -> Optional[str]:
        """读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[str]: 文件内容，如果读取失败则返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return None
    
    @staticmethod
    def write_file(file_path: Union[str, Path], content: str) -> bool:
        """写入文件内容
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            
        Returns:
            bool: 是否成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            return False 