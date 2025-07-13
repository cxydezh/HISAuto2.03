from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import os
import sqlite3
from urllib.parse import quote_plus
import inspect
from models.base import Base

class DatabaseManager:
    """数据库管理类，负责处理数据库连接和会话管理,该类是单例模式,使用时需要先调用initialize方法初始化
    使用方法:
    db_manager = DatabaseManager()
    db_manager.initialize()
    db_manager.get_session()
    db_manager.create_tables()
    db_manager.drop_tables()
    db_manager.execute_query()
    """
    
    def __init__(self, db_path: str, encryption_key: str):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
            encryption_key: 数据库加密密钥
        """
        self.db_path = db_path
        self.encryption_key = encryption_key
        self.engine = None
        self.Session = None
        self.Base = Base
        
    def initialize(self) -> None:
        """初始化数据库连接"""
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 创建数据库引擎
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            connect_args={
                'check_same_thread': False
            }
        )
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
        
        # 如果是新数据库，设置加密
        if not os.path.exists(self.db_path):
            self._setup_encryption()
            
    def _setup_encryption(self) -> None:
        """设置数据库加密"""
        try:
            # 使用 sqlite3 直接连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 设置加密
            cursor.execute(f"PRAGMA key = '{self.encryption_key}'")
            cursor.execute("PRAGMA cipher = 'aes-256-cbc'")
            cursor.execute("PRAGMA kdf_iter = 64000")
            
            # 测试加密是否生效
            cursor.execute("SELECT 1")
            conn.commit()
            conn.close()
            print("数据库加密设置成功")
        except Exception as e:
            print(f"数据库加密设置失败: {str(e)}")
            raise
            
    def verify_encryption(self) -> bool:
        """
        验证数据库加密是否正确
        
        Returns:
            bool: 加密是否正确
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA key = '{self.encryption_key}'")
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            print(f"数据库加密验证失败: {str(e)}")
            return False
            
    def get_session(self) -> Session:
        """
        获取数据库会话
        
        Returns:
            Session: 数据库会话对象
        """
        if not self.Session:
            raise RuntimeError("Database not initialized")
        return self.Session()
        
    def create_tables(self) -> None:
        """创建所有数据库表"""
        if not self.engine:
            raise RuntimeError("Database not initialized")
        self.Base.metadata.create_all(self.engine)
        
    def drop_tables(self) -> None:
        """删除所有数据库表"""
        if not self.engine:
            raise RuntimeError("Database not initialized")
        self.Base.metadata.drop_all(self.engine)
        
    def execute_query(self, query: str, params: Optional[dict] = None) -> list:
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            list: 查询结果
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()
            
    def execute_update(self, query: str, params: Optional[dict] = None) -> int:
        """
        执行SQL更新操作
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 受影响的行数
        """
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            session.commit()
            return result.rowcount
            
    # 组套相关方法
    def get_all_action_suit_groups(self):
        """获取所有组套"""
        try:
            from models.action_suit import ActionsSuitGroup
            with self.get_session() as session:
                return session.query(ActionsSuitGroup).all()
        except Exception as e:
            print(f"获取组套列表失败: {e}")
            return []
            
    def create_action_suit_group(self, suit_group):
        """创建组套"""
        try:
            with self.get_session() as session:
                session.add(suit_group)
                session.commit()
                session.refresh(suit_group)
                return suit_group.id
        except Exception as e:
            print(f"创建组套失败: {e}")
            return None
            
    def update_action_suit_group(self, suit_group):
        """更新组套"""
        try:
            with self.get_session() as session:
                session.merge(suit_group)
                session.commit()
                return True
        except Exception as e:
            print(f"更新组套失败: {e}")
            return False
            
    def delete_action_suit_group(self, suit_group_id):
        """删除组套"""
        try:
            from models.action_suit import ActionsSuitGroup, ActionsSuitList
            with self.get_session() as session:
                # 先删除关联的行为列表
                session.query(ActionsSuitList).filter_by(group_id=suit_group_id).delete()
                # 再删除组套
                session.query(ActionsSuitGroup).filter_by(id=suit_group_id).delete()
                session.commit()
                return True
        except Exception as e:
            print(f"删除组套失败: {e}")
            return False
            
    def get_action_lists_by_suit_group_id(self, suit_group_id):
        """根据组套ID获取行为列表"""
        try:
            from models.action_suit import ActionsSuitList
            with self.get_session() as session:
                return session.query(ActionsSuitList).filter_by(group_id=suit_group_id).all()
        except Exception as e:
            print(f"获取行为列表失败: {e}")
            return []
            
    def get_action_list_by_id(self, action_list_id):
        """根据ID获取行为列表"""
        try:
            from models.action_suit import ActionsSuitList
            with self.get_session() as session:
                return session.query(ActionsSuitList).filter_by(id=action_list_id).first()
        except Exception as e:
            print(f"获取行为列表失败: {e}")
            return None
            
    def create_action_suit_list(self, action_list):
        """创建行为列表"""
        try:
            with self.get_session() as session:
                session.add(action_list)
                session.commit()
                session.refresh(action_list)
                return action_list.id
        except Exception as e:
            print(f"创建行为列表失败: {e}")
            return None
            
    def update_action_suit_list(self, action_list):
        """更新行为列表"""
        try:
            with self.get_session() as session:
                session.merge(action_list)
                session.commit()
                return True
        except Exception as e:
            print(f"更新行为列表失败: {e}")
            return False
            
    def delete_action_suit_list(self, action_list_id):
        """删除行为列表"""
        try:
            from models.action_suit import ActionsSuitList
            with self.get_session() as session:
                session.query(ActionsSuitList).filter_by(id=action_list_id).delete()
                session.commit()
                return True
        except Exception as e:
            print(f"删除行为列表失败: {e}")
            return False
