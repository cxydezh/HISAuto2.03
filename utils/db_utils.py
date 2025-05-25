from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, List, Dict, Any, Union
import pandas as pd
from pathlib import Path

class DBUtils:
    """数据库操作工具类"""
    
    def __init__(self, db_url: str):
        """初始化数据库连接
        
        Args:
            db_url: 数据库连接URL
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        with self.Session() as session:
            result = session.execute(text(query), params or {})
            return [dict(row) for row in result]
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """执行SQL更新
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 影响的行数
        """
        with self.Session() as session:
            result = session.execute(text(query), params or {})
            session.commit()
            return result.rowcount
    
    def export_to_csv(self, query: str, output_path: Union[str, Path], params: Optional[Dict[str, Any]] = None) -> bool:
        """将查询结果导出为CSV文件
        
        Args:
            query: SQL查询语句
            output_path: 输出文件路径
            params: 查询参数
            
        Returns:
            bool: 是否成功
        """
        try:
            df = pd.read_sql_query(query, self.engine, params=params)
            df.to_csv(output_path, index=False)
            return True
        except Exception:
            return False
    
    def import_from_csv(self, table_name: str, csv_path: Union[str, Path]) -> bool:
        """从CSV文件导入数据
        
        Args:
            table_name: 目标表名
            csv_path: CSV文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            return True
        except Exception:
            return False
    
    def backup_database(self, backup_path: Union[str, Path]) -> bool:
        """备份数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            # 获取所有表名
            tables = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            
            # 创建备份文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                for table in tables:
                    table_name = table['name']
                    # 导出表结构
                    create_table = self.execute_query(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")[0]['sql']
                    f.write(f"{create_table};\n")
                    
                    # 导出表数据
                    data = self.execute_query(f"SELECT * FROM {table_name}")
                    for row in data:
                        columns = ', '.join(row.keys())
                        values = ', '.join([f"'{str(v)}'" for v in row.values()])
                        f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n")
            
            return True
        except Exception:
            return False
    
    def restore_database(self, backup_path: Union[str, Path]) -> bool:
        """恢复数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                sql_commands = f.read().split(';')
                
            with self.Session() as session:
                for command in sql_commands:
                    if command.strip():
                        session.execute(text(command))
                session.commit()
            
            return True
        except Exception:
            return False 