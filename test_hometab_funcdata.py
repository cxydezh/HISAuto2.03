import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟缺失的模块
sys.modules['pynput'] = Mock()
sys.modules['pynput.mouse'] = Mock()
sys.modules['pynput.keyboard'] = Mock()
sys.modules['win32gui'] = Mock()
sys.modules['win32api'] = Mock()
sys.modules['pyautogui'] = Mock()

from utils.hometab_funcdata import hometab_funcData
from models.actions import ActionGroup, ActionList, ActionsGroupHierarchy, ActionMouse, ActionKeyboard, ActionCodeTxt, ActionPrintscreen, ActionAI, ActionFunction, ActionClass
from models.action_suit import ActionsSuitGroup, ActionsSuitList, ActionsSuitGroupHierarchy, ActionSuitMouse, ActionSuitKeyboard, ActionSuitCodeTxt, ActionSuitPrintscreen, ActionSuitAI, ActionSuitFunction, ActionSuitClass
from models.debug_actions import ActionsDebugGroup, ActionDebugList, ActionsDebugGroupHierarchy, ActionDebugMouse, ActionDebugKeyboard, ActionDebugCodeTxt, ActionDebugPrintscreen, ActionDebugAI, ActionDebugFunction, ActionDebugClass
from models.base import Base


class TestHometabFuncData(unittest.TestCase):
    """测试hometab_funcData类的单元测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # 创建数据库引擎和会话
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        
        # 创建测试数据
        self.create_test_data()
        
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时数据库文件
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def create_test_data(self):
        """创建测试数据"""
        session = self.Session()
        
        try:
            # 创建Action类型的测试数据
            # 1. 创建层次结构
            action_hierarchy = ActionsGroupHierarchy(
                group_name="测试Action层次",
                group_rank="A1B1C1",
                sort_num=1,
                doctor_id=1,
                department_id=1,
                group_note="测试备注"
            )
            session.add(action_hierarchy)
            session.flush()
            
            # 2. 创建行为组
            action_group = ActionGroup(
                action_list_group_name="测试Action组",
                group_rank_id=action_hierarchy.id,
                user_id="test_user",
                department_id=1,
                sort_num=1
            )
            session.add(action_group)
            session.flush()
            
            # 3. 创建行为列表
            action_list = ActionList(
                group_id=action_group.id,
                action_type="mouse",
                action_name="测试鼠标行为",
                next_id=1
            )
            session.add(action_list)
            session.flush()
            
            # 4. 创建鼠标行为详情
            mouse_action = ActionMouse(
                mouse_action=1,
                x=100,
                y=200,
                action_list_id=action_list.id
            )
            session.add(mouse_action)
            
            # 创建Action_suit类型的测试数据
            # 1. 创建层次结构
            suit_hierarchy = ActionsSuitGroupHierarchy(
                group_name="测试Suit层次",
                group_rank="A2B2C2",
                sort_num=1,
                doctor_id=1,
                department_id=1,
                group_note="测试备注"
            )
            session.add(suit_hierarchy)
            session.flush()
            
            # 2. 创建行为组
            suit_group = ActionsSuitGroup(
                action_list_group_name="测试Suit组",
                group_rank_id=suit_hierarchy.id,
                user_id=1,
                department_id=1,
                sort_num=1
            )
            session.add(suit_group)
            session.flush()
            
            # 3. 创建行为列表
            suit_list = ActionsSuitList(
                group_id=suit_group.id,
                action_type="keyboard",
                action_name="测试键盘行为",
                next_id=1
            )
            session.add(suit_list)
            session.flush()
            
            # 4. 创建键盘行为详情
            keyboard_action = ActionSuitKeyboard(
                keyboard_type=1,
                keyboard_value="test",
                action_list_id=suit_list.id
            )
            session.add(keyboard_action)
            
            # 创建debug_action类型的测试数据
            # 1. 创建层次结构
            debug_hierarchy = ActionsDebugGroupHierarchy(
                group_name="测试Debug层次",
                group_rank="A3B3C3",
                sort_num=1,
                doctor_id=1,
                department_id=1,
                group_note="测试备注"
            )
            session.add(debug_hierarchy)
            session.flush()
            
            # 2. 创建行为组
            debug_group = ActionsDebugGroup(
                action_list_group_name="测试Debug组",
                group_rank_id=debug_hierarchy.id,
                user_id=1,
                department_id=1,
                sort_num=1
            )
            session.add(debug_group)
            session.flush()
            
            # 3. 创建行为列表
            debug_list = ActionDebugList(
                group_id=debug_group.id,
                action_type="ai",
                action_name="测试AI行为",
                next_id=1
            )
            session.add(debug_list)
            session.flush()
            
            # 4. 创建AI行为详情
            ai_action = ActionDebugAI(
                train_group_name="测试训练组",
                ai_illustration="测试AI说明",
                action_list_id=debug_list.id
            )
            session.add(ai_action)
            
            session.commit()
            
            # 保存测试数据的ID，供测试使用
            self.action_hierarchy_id = action_hierarchy.id
            self.action_group_id = action_group.id
            self.action_list_id = action_list.id
            
            self.suit_hierarchy_id = suit_hierarchy.id
            self.suit_group_id = suit_group.id
            self.suit_list_id = suit_list.id
            
            self.debug_hierarchy_id = debug_hierarchy.id
            self.debug_group_id = debug_group.id
            self.debug_list_id = debug_list.id
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @patch('utils.hometab_funcdata.ConfigManager')
    @patch('utils.hometab_funcdata.DatabaseManager')
    def test_delete_action_group_action_type(self, mock_db_manager, mock_config_manager):
        """测试删除Action类型的行为组"""
        # 模拟配置管理器
        mock_config = Mock()
        mock_config.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): self.db_path,
            ('Security', 'DBEncryptionKey'): 'test_key'
        }.get((section, key))
        mock_config_manager.return_value = mock_config
        
        # 模拟数据库管理器
        mock_db = Mock()
        mock_db.initialize.return_value = None
        mock_db.Session.return_value = self.Session
        mock_db_manager.return_value = mock_db
        
        # 执行删除操作
        result = hometab_funcData.delete_action_group(
            sheet_type="Action",
            action_tree_selected_iid="group_1",
            action_group_id=self.action_group_id,
            action_group_hierarchy_id=self.action_hierarchy_id
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据是否被删除
        session = self.Session()
        try:
            # 检查行为组是否被删除
            group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
            self.assertIsNone(group)
            
            # 检查行为列表是否被删除
            action_list = session.query(ActionList).filter_by(id=self.action_list_id).first()
            self.assertIsNone(action_list)
            
            # 检查鼠标行为详情是否被删除
            mouse_action = session.query(ActionMouse).filter_by(action_list_id=self.action_list_id).first()
            self.assertIsNone(mouse_action)
            
        finally:
            session.close()
    
    @patch('utils.hometab_funcdata.ConfigManager')
    @patch('utils.hometab_funcdata.DatabaseManager')
    def test_delete_action_group_action_suit_type(self, mock_db_manager, mock_config_manager):
        """测试删除Action_suit类型的行为组"""
        # 模拟配置管理器
        mock_config = Mock()
        mock_config.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): self.db_path,
            ('Security', 'DBEncryptionKey'): 'test_key'
        }.get((section, key))
        mock_config_manager.return_value = mock_config
        
        # 模拟数据库管理器
        mock_db = Mock()
        mock_db.initialize.return_value = None
        mock_db.Session.return_value = self.Session
        mock_db_manager.return_value = mock_db
        
        # 执行删除操作
        result = hometab_funcData.delete_action_group(
            sheet_type="Action_suit",
            action_tree_selected_iid="group_1",
            action_group_id=self.suit_group_id,
            action_group_hierarchy_id=self.suit_hierarchy_id
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据是否被删除
        session = self.Session()
        try:
            # 检查行为组是否被删除
            group = session.query(ActionsSuitGroup).filter_by(id=self.suit_group_id).first()
            self.assertIsNone(group)
            
            # 检查行为列表是否被删除
            action_list = session.query(ActionsSuitList).filter_by(id=self.suit_list_id).first()
            self.assertIsNone(action_list)
            
            # 检查键盘行为详情是否被删除
            keyboard_action = session.query(ActionSuitKeyboard).filter_by(action_list_id=self.suit_list_id).first()
            self.assertIsNone(keyboard_action)
            
        finally:
            session.close()
    
    @patch('utils.hometab_funcdata.ConfigManager')
    @patch('utils.hometab_funcdata.DatabaseManager')
    def test_delete_action_group_debug_action_type(self, mock_db_manager, mock_config_manager):
        """测试删除debug_action类型的行为组"""
        # 模拟配置管理器
        mock_config = Mock()
        mock_config.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): self.db_path,
            ('Security', 'DBEncryptionKey'): 'test_key'
        }.get((section, key))
        mock_config_manager.return_value = mock_config
        
        # 模拟数据库管理器
        mock_db = Mock()
        mock_db.initialize.return_value = None
        mock_db.Session.return_value = self.Session
        mock_db_manager.return_value = mock_db
        
        # 执行删除操作
        result = hometab_funcData.delete_action_group(
            sheet_type="debug_action",
            action_tree_selected_iid="group_1",
            action_group_id=self.debug_group_id,
            action_group_hierarchy_id=self.debug_hierarchy_id
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据是否被删除
        session = self.Session()
        try:
            # 检查行为组是否被删除
            group = session.query(ActionsDebugGroup).filter_by(id=self.debug_group_id).first()
            self.assertIsNone(group)
            
            # 检查行为列表是否被删除
            action_list = session.query(ActionDebugList).filter_by(id=self.debug_list_id).first()
            self.assertIsNone(action_list)
            
            # 检查AI行为详情是否被删除
            ai_action = session.query(ActionDebugAI).filter_by(action_list_id=self.debug_list_id).first()
            self.assertIsNone(ai_action)
            
        finally:
            session.close()
    
    @patch('utils.hometab_funcdata.ConfigManager')
    @patch('utils.hometab_funcdata.DatabaseManager')
    def test_delete_action_group_hierarchy_type(self, mock_db_manager, mock_config_manager):
        """测试删除层次结构类型的行为组"""
        # 模拟配置管理器
        mock_config = Mock()
        mock_config.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): self.db_path,
            ('Security', 'DBEncryptionKey'): 'test_key'
        }.get((section, key))
        mock_config_manager.return_value = mock_config
        
        # 模拟数据库管理器
        mock_db = Mock()
        mock_db.initialize.return_value = None
        mock_db.Session.return_value = self.Session
        mock_db_manager.return_value = mock_db
        
        # 执行删除操作
        result = hometab_funcData.delete_action_group(
            sheet_type="Action",
            action_tree_selected_iid="A1B1C1",
            action_group_id=self.action_group_id,
            action_group_hierarchy_id=self.action_hierarchy_id
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据是否被删除
        session = self.Session()
        try:
            # 检查层次结构是否被删除
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_hierarchy_id).first()
            self.assertIsNone(hierarchy)
            
            # 检查行为组是否被删除
            group = session.query(ActionGroup).filter_by(group_rank_id=self.action_hierarchy_id).first()
            self.assertIsNone(group)
            
        finally:
            session.close()
    
    @patch('utils.hometab_funcdata.ConfigManager')
    @patch('utils.hometab_funcdata.DatabaseManager')
    def test_delete_action_group_invalid_type(self, mock_db_manager, mock_config_manager):
        """测试删除无效类型的行为组"""
        # 模拟配置管理器
        mock_config = Mock()
        mock_config.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): self.db_path,
            ('Security', 'DBEncryptionKey'): 'test_key'
        }.get((section, key))
        mock_config_manager.return_value = mock_config
        
        # 模拟数据库管理器
        mock_db = Mock()
        mock_db.initialize.return_value = None
        mock_db.Session.return_value = self.Session
        mock_db_manager.return_value = mock_db
        
        # 执行删除操作
        result = hometab_funcData.delete_action_group(
            sheet_type="invalid_type",
            action_tree_selected_iid="group_1",
            action_group_id=1,
            action_group_hierarchy_id=1
        )
        
        # 验证结果
        self.assertFalse(result)
    
    @patch('utils.hometab_funcdata.ConfigManager')
    @patch('utils.hometab_funcdata.DatabaseManager')
    def test_delete_action_group_invalid_tree_iid(self, mock_db_manager, mock_config_manager):
        """测试删除无效树节点ID的行为组"""
        # 模拟配置管理器
        mock_config = Mock()
        mock_config.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): self.db_path,
            ('Security', 'DBEncryptionKey'): 'test_key'
        }.get((section, key))
        mock_config_manager.return_value = mock_config
        
        # 模拟数据库管理器
        mock_db = Mock()
        mock_db.initialize.return_value = None
        mock_db.Session.return_value = self.Session
        mock_db_manager.return_value = mock_db
        
        # 执行删除操作
        result = hometab_funcData.delete_action_group(
            sheet_type="Action",
            action_tree_selected_iid="invalid_iid",
            action_group_id=1,
            action_group_hierarchy_id=1
        )
        
        # 验证结果
        self.assertFalse(result)
    
    @patch('utils.hometab_funcdata.ConfigManager')
    @patch('utils.hometab_funcdata.DatabaseManager')
    def test_delete_action_group_nonexistent_group(self, mock_db_manager, mock_config_manager):
        """测试删除不存在的行为组"""
        # 模拟配置管理器
        mock_config = Mock()
        mock_config.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): self.db_path,
            ('Security', 'DBEncryptionKey'): 'test_key'
        }.get((section, key))
        mock_config_manager.return_value = mock_config
        
        # 模拟数据库管理器
        mock_db = Mock()
        mock_db.initialize.return_value = None
        mock_db.Session.return_value = self.Session
        mock_db_manager.return_value = mock_db
        
        # 执行删除操作
        result = hometab_funcData.delete_action_group(
            sheet_type="Action",
            action_tree_selected_iid="group_1",
            action_group_id=99999,  # 不存在的ID
            action_group_hierarchy_id=1
        )
        
        # 验证结果
        self.assertFalse(result)
    
    def test_get_model_class(self):
        """测试_get_model_class方法"""
        # 测试Action类型的模型类获取
        action_list_model = hometab_funcData._get_model_class("ActionList")
        self.assertEqual(action_list_model, ActionList)
        
        action_group_model = hometab_funcData._get_model_class("ActionGroup")
        self.assertEqual(action_group_model, ActionGroup)
        
        # 测试Action_suit类型的模型类获取
        suit_list_model = hometab_funcData._get_model_class("ActionsSuitList")
        self.assertEqual(suit_list_model, ActionsSuitList)
        
        # 测试debug_action类型的模型类获取
        debug_list_model = hometab_funcData._get_model_class("ActionDebugList")
        self.assertEqual(debug_list_model, ActionDebugList)
        
        # 测试不存在的模型类
        invalid_model = hometab_funcData._get_model_class("InvalidModel")
        self.assertIsNone(invalid_model)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 