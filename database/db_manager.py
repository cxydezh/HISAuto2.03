from datetime import time
import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import os
import sqlite3
from urllib.parse import quote_plus
import inspect
from models.actions import ActionGroup, ActionKeyboard, ActionList, ActionMouse, ActionsGroupHierarchy,ActionCodeTxt,ActionPrintscreen,ActionAI,ActionFunction,ActionClass,ListGroupHierarchy
from models.action_suit import ActionSuitAI, ActionSuitClass, ActionSuitCodeTxt, ActionSuitFunction, ActionSuitGroup, ActionSuitKeyboard,ActionSuitMouse, ActionSuitPrintscreen, ActionsSuitGroupHierarchy,ActionsSuitList,ActionsSuitGroup,ActionsSuitMouse,ActionsSuitKeyboard,ActionsSuitCodeTxt,ActionsSuitPrintscreen,ActionsSuitAI,ActionsSuitFunction,ActionsSuitClass
from models.debug_actions import ActionDebugGroup,ActionDebugList,ActionsDebugGroup,ActionDebugMouse,ActionDebugKeyboard,ActionDebugCodeTxt,ActionDebugPrintscreen,ActionDebugAI,ActionDebugFunction,ActionDebugClass, ActionsDebugGroupHierarchy
from models.base import Base 
from models.department import Department
from models.user import User
from utils import logger

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
    MODEL_MAPPING = {
        # Action 相关模型
        "ActionList": ActionList,
        "ActionGroup": ActionGroup,
        "ActionsGroupHierarchy": ActionsGroupHierarchy,
        "ActionMouse": ActionMouse,
        "ActionKeyboard": ActionKeyboard,
        "ActionCodeTxt": ActionCodeTxt,
        "ActionPrintscreen": ActionPrintscreen,
        "ActionAI": ActionAI,
        "ActionFunction": ActionFunction,
        "ActionClass": ActionClass,
        "ListGroupHierarchy": ListGroupHierarchy,
        "ActionGroupHierarchy": ActionsGroupHierarchy,
        "ActionSuitGroupHierarchy": ActionsSuitGroupHierarchy,
        "ActionDebugGroupHierarchy": ActionsDebugGroupHierarchy,
        
        # Action_suit 相关模型
        "ActionsSuitList": ActionsSuitList,
        "ActionSuitGroup": ActionsSuitGroup,
        "ActionsSuitGroupHierarchy": ActionsSuitGroupHierarchy,
        "ActionSuitMouse": ActionSuitMouse,
        "ActionSuitKeyboard": ActionSuitKeyboard,
        "ActionSuitCodeTxt": ActionSuitCodeTxt,
        "ActionSuitPrintscreen": ActionSuitPrintscreen,
        "ActionSuitAI": ActionSuitAI,
        "ActionSuitFunction": ActionSuitFunction,
        "ActionSuitClass": ActionSuitClass,
        
        # debug_action 相关模型
        "ActionDebugList": ActionDebugList,
        "ActionDebugGroup": ActionsDebugGroup,
        "ActionsDebugGroupHierarchy": ActionsDebugGroupHierarchy,
        "ActionDebugMouse": ActionDebugMouse,
        "ActionDebugKeyboard": ActionDebugKeyboard,
        "ActionDebugCodeTxt": ActionDebugCodeTxt,
        "ActionDebugPrintscreen": ActionDebugPrintscreen,
        "ActionDebugAI": ActionDebugAI,
        "ActionDebugFunction": ActionDebugFunction,
        "ActionDebugClass": ActionDebugClass,
    }
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
        self._init_db_data()
    def _init_db_data(self):
        """初始化数据库数据"""
        if not self.engine:
            raise RuntimeError("Database not initialized")
        session = self.get_session()
        # 向department表添加一条记录，name：肾病科，code：103006，description：肾病科，updated_at：当前时间,created_at：当前时间;
        if session.query(Department).count() == 0:
            session.execute(text("INSERT INTO departments (name, code, description, updated_at, created_at) VALUES ('肾病科', '103006', '肾病科', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        # 向user表添加一条记录，user_id:1,user_name：admin，user_password：admin，department_id：103006，phone:664927,role:系统管理员，Permission：admin,updated_at：当前时间,created_at：当前时间;
        if session.query(User).count() == 0:
            session.execute(text("INSERT INTO users (user_id, username, password, department_id, phone, role, permission, updated_at, created_at) VALUES (1, 'admin', 'admin', 103006, '664927', '系统管理员', 'admin', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        # 先检测action_group_hierarchy、action_suit_group_hierarchy、action_debug_group_hierarchy表是否存在记录
        # 分别向action_group_hierarchy、action_suit_group_hierarchy、action_debug_group_hierarchy表添加3条记录。
        #第一条记录：group_name：个人，group_rank：A0B0C0D0E0，sort_num：1,updated_at：当前时间,created_at：当前时间;
        #第二条记录：group_name：科室，group_rank：A1B0C0D0E0，sort_num：2,updated_at：当前时间,created_at：当前时间;
        #第三条记录：group_name：全局，group_rank：A2B0C0D0E0，sort_num：3,updated_at：当前时间,created_at：当前时间;
        # 先检测action_group_hierarchy、action_suit_group_hierarchy、action_debug_group_hierarchy表是否存在记录
        if session.query(ActionsGroupHierarchy).count() == 0:
            # 添加3条记录
            session.execute(text("INSERT INTO actions_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('个人', 'A0B0C0D0E0', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            session.execute(text("INSERT INTO actions_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('科室', 'A1B0C0D0E0', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            session.execute(text("INSERT INTO actions_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('全局', 'A2B0C0D0E0', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        if session.query(ActionsSuitGroupHierarchy).count() == 0:
            session.execute(text("INSERT INTO actions_suit_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('个人', 'A0B0C0D0E0', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            session.execute(text("INSERT INTO actions_suit_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('科室', 'A1B0C0D0E0', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            session.execute(text("INSERT INTO actions_suit_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('全局', 'A2B0C0D0E0', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        if session.query(ActionsDebugGroupHierarchy).count() == 0:
            session.execute(text("INSERT INTO actions_debug_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('个人', 'A0B0C0D0E0', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            session.execute(text("INSERT INTO actions_debug_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('科室', 'A1B0C0D0E0', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
            session.execute(text("INSERT INTO actions_debug_group_hierarchy (group_name, group_rank, sort_num, updated_at, created_at) VALUES ('全局', 'A2B0C0D0E0', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        session.commit()
    @classmethod
    def _get_model_class(cls, sheet_name):
        """根据表名获取对应的模型类"""
        try:
            return cls.MODEL_MAPPING.get(sheet_name)
        except Exception as e:
            logger.error(f"获取模型类失败: {str(e)}")
            print(traceback.format_exc())
            return None
    @classmethod
    def add_list_record(self, list_group_name,group_id, **data):
        """
        在ActionList中添加新记录，自动维护链表
        :param list_group_name: 所属分组名称
        :param group_id: 所属分组ID
        :param data: 记录数据的字典包，字典包中包含action_type,action_name,next_id,debug_group_id,action_note,list_rank_id
        :return: 新记录的ID
        """
        with self.get_session() as session:
            try:
                # 验证分组是否存在
                if list_group_name in ["ActionList","ActionSuitList","ActionDebugList"]:
                    self.list_model = self._get_model_class(list_group_name)
                if not session.query(self.list_model).get(group_id):
                    raise ValueError(f"分组 {group_id} 不存在")
                
                # 验证data中数据的group_id是否为group_id
                for item in data:
                    if item.get('group_id') != group_id:
                        raise ValueError(f"数据中的group_id {item.get('group_id')} 不等于分组 {group_id}")
                
                # 创建新记录
                new_record = self.list_model(group_id=group_id, **data)
                session.add(new_record)
                session.flush()  # 获取新记录的ID
                
                # 查找当前分组中的最后一条记录
                last_record = session.query(self.list_model).filter(
                    self.list_model.group_id == group_id,
                    self.list_model.next_id == None,
                    self.list_model.id != new_record.id  # 排除自己
                ).first()
                
                # 如果存在最后一条记录，更新其next_id指向新记录
                if last_record:
                    last_record.next_id = new_record.id
                
                session.commit()
                logger.info(f"在分组 {group_id} 添加记录 {new_record.id}")
                return new_record.id
            except Exception as e:
                session.rollback()
                logger.error(f"添加ActionList记录失败: {e}")
                # 重试机制
                return self._retry_operation(lambda: self.add_list_record(group_id, **data), e)

    def insert_records_between(self, list_group_name,group_id, prev_id, next_id, records_data):
        """
        在两条记录之间插入一组新记录
        :param group_id: 分组ID
        :param prev_id: 前一条记录的ID
        :param next_id: 后一条记录的ID
        :param records_data: 要插入的记录数据列表
        :return: 新插入记录的ID列表
        """
        with self.get_session() as session:
            try:
                if list_group_name in ["ActionList","ActionSuitList","ActionDebugList"]:
                    self.list_model = self._get_model_class(list_group_name)
                # 验证前一条记录是否存在
                prev_record = session.query(self.list_model).get(prev_id)
                if not prev_record or prev_record.group_id != group_id:
                    raise ValueError(f"前记录 {prev_id} 无效或不属于分组 {group_id}")
                
                # 验证后一条记录是否存在
                next_record = session.query(self.list_model).get(next_id)
                if not next_record or next_record.group_id != group_id:
                    raise ValueError(f"后记录 {next_id} 无效或不属于分组 {group_id}")
                
                # 验证记录是否连续
                if prev_record.next_id != next_record.id:
                    raise ValueError(f"记录 {prev_id} 和 {next_id} 不连续")
                
                # 创建新记录
                new_records = []
                for data in records_data:
                    record = self.list_model(group_id=group_id, **data)
                    session.add(record)
                    session.flush()  # 立即获取ID
                    new_records.append(record)
                
                # 构建新记录之间的链表
                for i in range(len(new_records) - 1):
                    new_records[i].next_id = new_records[i+1].id
                
                # 将新记录链插入到原链表中
                prev_record.next_id = new_records[0].id
                new_records[-1].next_id = next_record.id
                
                session.commit()
                new_ids = [r.id for r in new_records]
                logger.info(f"在分组 {group_id} 的 {prev_id} 和 {next_id} 之间插入记录: {new_ids}")
                return new_ids
            except Exception as e:
                session.rollback()
                logger.error(f"插入记录失败: {e}")
                raise
    def insert_records_ahead(self, list_group_name,group_id, first_id, records_data):
        """
        在两条记录之间插入一组新记录
        :param group_id: 分组ID
        :param first_id: 第一条记录的ID
        :param records_data: 要插入的记录数据列表
        :return: 新插入记录的ID列表
        """
        with self.get_session() as session:
            try:
                if list_group_name in ["ActionList","ActionSuitList","ActionDebugList"]:
                    self.list_model = self._get_model_class(list_group_name)
                # 验证前一条记录是否存在
                first_record = session.query(self.list_model).get(first_id)
                if not first_record or first_record.group_id != group_id:
                    raise ValueError(f"第一条记录 {first_id} 无效或不属于分组 {group_id}")
                
                
                # 创建新记录
                new_records = []
                for data in records_data:
                    record = self.list_model(group_id=group_id, **data)
                    session.add(record)
                    session.flush()  # 立即获取ID
                    new_records.append(record)
                
                # 构建新记录之间的链表
                for i in range(len(new_records) - 1):
                    new_records[i].next_id = new_records[i+1].id
                
                # 将新记录链插入到原链表中
                new_records[-1].next_id = first_record.id
                
                session.commit()
                new_ids = [r.id for r in new_records]
                logger.info(f"在分组 {group_id} 的 {first_id} 之前插入记录: {new_ids}")
                return new_ids
            except Exception as e:
                session.rollback()
                logger.error(f"插入记录失败: {e}")
                raise
    def delete_single_record(self, list_group_name,group_id, record_id):
        """
        删除一组连续记录，自动维护链表
        :param group_id: 分组ID
        :param record_id: 要删除的记录ID
        """
        with self.get_session() as session:
            try:
                if list_group_name in ["ActionList","ActionSuitList","ActionDebugList"]:
                    self.list_model = self._get_model_class(list_group_name)
                # 验证记录
                record = session.query(self.list_model).get(record_id)
                if not record or record.group_id != group_id:
                    raise ValueError(f"记录 {record_id} 无效或不属于分组 {group_id}")
                
                # 查找前一条记录（指向起始记录的记录）
                prev_record = session.query(self.list_model).filter(
                    self.list_model.group_id == group_id,
                    self.list_model.next_id == record_id
                ).first()
                
                # 获取结束记录的下一条ID
                next_id = record.next_id
                
                # 更新前一条记录的next_id指向结束记录的下一条
                if prev_record:
                    prev_record.next_id = next_id
                # 如果没有前一条记录，说明删除的是链表头部
                # 此时不需要更新，因为头记录没有前驱
                
                # 删除范围内的所有记录
                session.query(self.list_model).filter(
                    self.list_model.group_id == group_id,
                    self.list_model.id == record_id
                ).delete(synchronize_session=False)
                
                session.commit()
                logger.info(f"在分组 {group_id} 删除记录 {record_id}")
            except Exception as e:
                session.rollback()
                logger.error(f"删除记录失败: {e}")
                # 重试机制
                return self._retry_operation(lambda: self.delete_single_record(group_id, record_id), e)
    def delete_records_range(self, list_group_name,group_id, start_id, end_id):
        """
        删除一组连续记录，自动维护链表
        :param group_id: 分组ID
        :param start_id: 要删除的起始记录ID
        :param end_id: 要删除的结束记录ID
        """
        with self.get_session() as session:
            try:
                if list_group_name in ["ActionList","ActionSuitList","ActionDebugList"]:
                    self.list_model = self._get_model_class(list_group_name)
                # 验证起始记录
                start_record = session.query(self.list_model).get(start_id)
                if not start_record or start_record.group_id != group_id:
                    raise ValueError(f"起始记录 {start_id} 无效或不属于分组 {group_id}")
                
                # 验证结束记录
                end_record = session.query(self.list_model).get(end_id)
                if not end_record or end_record.group_id != group_id:
                    raise ValueError(f"结束记录 {end_id} 无效或不属于分组 {group_id}")
                
                # 查找前一条记录（指向起始记录的记录）
                prev_record = session.query(self.list_model).filter(
                    self.list_model.group_id == group_id,
                    self.list_model.next_id == start_id
                ).first()
                
                # 获取结束记录的下一条ID
                next_id = end_record.next_id
                
                # 更新前一条记录的next_id指向结束记录的下一条
                if prev_record:
                    prev_record.next_id = next_id
                # 如果没有前一条记录，说明删除的是链表头部
                # 此时不需要更新，因为头记录没有前驱
                
                # 删除范围内的所有记录
                session.query(self.list_model).filter(
                    self.list_model.group_id == group_id,
                    self.list_model.id >= start_id,
                    self.list_model.id <= end_id
                ).delete(synchronize_session=False)
                
                session.commit()
                logger.info(f"在分组 {group_id} 删除记录 {start_id} 到 {end_id}")
            except Exception as e:
                session.rollback()
                logger.error(f"删除记录失败: {e}")
                # 重试机制
                return self._retry_operation(lambda: self.delete_records_range(group_id, start_id, end_id), e)

    def validate_group_links(self, list_group_name,group_id):
        """
        验证分组内链表完整性
        :param group_id: 分组ID
        :return: True表示链表有效
        """
        with self.get_session() as session:
            if list_group_name in ["ActionList","ActionSuitList","ActionDebugList"]:
                self.list_model = self._get_model_class(list_group_name)
            # 获取分组所有记录
            records = session.query(self.list_model).filter_by(group_id=group_id).all()
            
            # 检查next_id唯一性
            next_ids = [r.next_id for r in records if r.next_id is not None]
            if len(next_ids) != len(set(next_ids)):
                raise ValueError(f"分组 {group_id} 中存在重复的next_id")
            
            # 查找链表头（没有记录指向它）
            head = next((r for r in records if not any(
                other.next_id == r.id for other in records
            )), None)
            
            if not head:
                return True  # 空分组
                
            # 遍历链表检查环
            visited = set()
            current = head
            while current:
                if current.id in visited:
                    raise ValueError(f"分组 {group_id} 的链表中存在环")
                visited.add(current.id)
                current = next((r for r in records if r.id == current.next_id), None)
            
            # 检查所有记录是否都在链中
            if len(visited) != len(records):
                missing = set(r.id for r in records) - visited
                raise ValueError(f"分组 {group_id} 中存在孤立记录: {missing}")
            
            return True

    def _retry_operation(self, operation, max_retries=3, delay=0.5):
        """
        操作重试机制
        :param operation: 要重试的操作函数
        :param max_retries: 最大重试次数
        :param delay: 重试间隔(秒)
        """
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"操作失败，第 {attempt+1} 次重试...")
                time.sleep(delay)

    def get_group_chain(self, list_group_name,group_id):
        """
        获取分组内所有记录的链表顺序
        :param group_id: 分组ID
        :return: 记录列表，按链表顺序排列
        """
        with self.get_session() as session:
            if list_group_name in ["ActionList","ActionSuitList","ActionDebugList"]:
                self.list_model = self._get_model_class(list_group_name)
            # 获取分组所有记录
            records = session.query(self.list_model).filter_by(group_id=group_id).all()
            
            # 构建ID到记录的映射
            record_map = {r.id: r for r in records}
            
            # 查找链表头
            head = next((r for r in records if not any(
                other.next_id == r.id for other in records
            )), None)
            
            if not head:
                return []
            
            # 遍历链表
            chain = []
            current = head
            while current:
                chain.append(current)
                current = record_map.get(current.next_id) if current.next_id else None
            
            return chain