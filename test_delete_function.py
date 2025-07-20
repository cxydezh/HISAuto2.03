#!/usr/bin/env python3
"""
简化的删除功能测试
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟缺失的模块
sys.modules['pynput'] = Mock()
sys.modules['pynput.mouse'] = Mock()
sys.modules['pynput.keyboard'] = Mock()
sys.modules['win32gui'] = Mock()
sys.modules['win32api'] = Mock()
sys.modules['pyautogui'] = Mock()

# 直接导入模型
from models.actions import ActionGroup, ActionList, ActionsGroupHierarchy, ActionMouse, ActionKeyboard, ActionCodeTxt, ActionPrintscreen, ActionAI, ActionFunction, ActionClass
from models.action_suit import ActionsSuitGroup, ActionsSuitList, ActionsSuitGroupHierarchy, ActionSuitMouse, ActionSuitKeyboard, ActionSuitCodeTxt, ActionSuitPrintscreen, ActionSuitAI, ActionSuitFunction, ActionSuitClass
from models.debug_actions import ActionsDebugGroup, ActionDebugList, ActionsDebugGroupHierarchy, ActionDebugMouse, ActionDebugKeyboard, ActionDebugCodeTxt, ActionDebugPrintscreen, ActionDebugAI, ActionDebugFunction, ActionDebugClass
from models.base import Base


class TestDeleteFunction(unittest.TestCase):
    """测试删除功能的单元测试"""
    
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
        # 关闭数据库连接
        if hasattr(self, 'engine'):
            self.engine.dispose()
        
        # 删除临时数据库文件
        try:
            if os.path.exists(self.db_path):
                os.unlink(self.db_path)
        except PermissionError:
            # 在Windows上，有时文件可能被锁定，忽略这个错误
            pass
    
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
                action_debug_group_hierarchy_id=debug_hierarchy.id,
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
    
    def test_delete_action_group_data(self):
        """测试删除Action类型的行为组数据"""
        session = self.Session()
        
        try:
            # 验证数据存在
            group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
            self.assertIsNotNone(group)
            
            action_list = session.query(ActionList).filter_by(id=self.action_list_id).first()
            self.assertIsNotNone(action_list)
            
            mouse_action = session.query(ActionMouse).filter_by(action_list_id=self.action_list_id).first()
            self.assertIsNotNone(mouse_action)
            
            # 执行删除操作
            # 1. 删除行为详情
            session.delete(mouse_action)
            session.commit()
            
            # 2. 删除行为列表
            session.delete(action_list)
            session.commit()
            
            # 3. 删除行为组
            session.delete(group)
            session.commit()
            
            # 验证数据已被删除
            group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
            self.assertIsNone(group)
            
            action_list = session.query(ActionList).filter_by(id=self.action_list_id).first()
            self.assertIsNone(action_list)
            
            mouse_action = session.query(ActionMouse).filter_by(action_list_id=self.action_list_id).first()
            self.assertIsNone(mouse_action)
            
            print("✓ Action类型数据删除测试通过")
            
        finally:
            session.close()
    
    def test_delete_action_suit_data(self):
        """测试删除Action_suit类型的行为组数据"""
        session = self.Session()
        
        try:
            # 验证数据存在
            group = session.query(ActionsSuitGroup).filter_by(id=self.suit_group_id).first()
            self.assertIsNotNone(group)
            
            action_list = session.query(ActionsSuitList).filter_by(id=self.suit_list_id).first()
            self.assertIsNotNone(action_list)
            
            keyboard_action = session.query(ActionSuitKeyboard).filter_by(action_list_id=self.suit_list_id).first()
            self.assertIsNotNone(keyboard_action)
            
            # 执行删除操作
            # 1. 删除行为详情
            session.delete(keyboard_action)
            session.commit()
            
            # 2. 删除行为列表
            session.delete(action_list)
            session.commit()
            
            # 3. 删除行为组
            session.delete(group)
            session.commit()
            
            # 验证数据已被删除
            group = session.query(ActionsSuitGroup).filter_by(id=self.suit_group_id).first()
            self.assertIsNone(group)
            
            action_list = session.query(ActionsSuitList).filter_by(id=self.suit_list_id).first()
            self.assertIsNone(action_list)
            
            keyboard_action = session.query(ActionSuitKeyboard).filter_by(action_list_id=self.suit_list_id).first()
            self.assertIsNone(keyboard_action)
            
            print("✓ Action_suit类型数据删除测试通过")
            
        finally:
            session.close()
    
    def test_delete_debug_action_data(self):
        """测试删除debug_action类型的行为组数据"""
        session = self.Session()
        
        try:
            # 验证数据存在
            group = session.query(ActionsDebugGroup).filter_by(id=self.debug_group_id).first()
            self.assertIsNotNone(group)
            
            action_list = session.query(ActionDebugList).filter_by(id=self.debug_list_id).first()
            self.assertIsNotNone(action_list)
            
            ai_action = session.query(ActionDebugAI).filter_by(action_list_id=self.debug_list_id).first()
            self.assertIsNotNone(ai_action)
            
            # 执行删除操作
            # 1. 删除行为详情
            session.delete(ai_action)
            session.commit()
            
            # 2. 删除行为列表
            session.delete(action_list)
            session.commit()
            
            # 3. 删除行为组
            session.delete(group)
            session.commit()
            
            # 验证数据已被删除
            group = session.query(ActionsDebugGroup).filter_by(id=self.debug_group_id).first()
            self.assertIsNone(group)
            
            action_list = session.query(ActionDebugList).filter_by(id=self.debug_list_id).first()
            self.assertIsNone(action_list)
            
            ai_action = session.query(ActionDebugAI).filter_by(action_list_id=self.debug_list_id).first()
            self.assertIsNone(ai_action)
            
            print("✓ debug_action类型数据删除测试通过")
            
        finally:
            session.close()
    
    def test_delete_hierarchy_data(self):
        """测试删除层次结构数据"""
        session = self.Session()
        
        try:
            # 验证数据存在
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_hierarchy_id).first()
            self.assertIsNotNone(hierarchy)
            
            group = session.query(ActionGroup).filter_by(group_rank_id=self.action_hierarchy_id).first()
            self.assertIsNotNone(group)
            
            # 执行删除操作
            # 1. 删除行为组
            session.delete(group)
            session.commit()
            
            # 2. 删除层次结构
            session.delete(hierarchy)
            session.commit()
            
            # 验证数据已被删除
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_hierarchy_id).first()
            self.assertIsNone(hierarchy)
            
            group = session.query(ActionGroup).filter_by(group_rank_id=self.action_hierarchy_id).first()
            self.assertIsNone(group)
            
            print("✓ 层次结构数据删除测试通过")
            
        finally:
            session.close()
    
    def test_model_mapping(self):
        """测试模型映射功能"""
        # 定义模型映射字典
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
        
        # 测试Action类型的模型类获取
        self.assertEqual(MODEL_MAPPING.get("ActionList"), ActionList)
        self.assertEqual(MODEL_MAPPING.get("ActionGroup"), ActionGroup)
        self.assertEqual(MODEL_MAPPING.get("ActionsGroupHierarchy"), ActionsGroupHierarchy)
        
        # 测试Action_suit类型的模型类获取
        self.assertEqual(MODEL_MAPPING.get("ActionsSuitList"), ActionsSuitList)
        self.assertEqual(MODEL_MAPPING.get("ActionSuitGroup"), ActionsSuitGroup)
        self.assertEqual(MODEL_MAPPING.get("ActionsSuitGroupHierarchy"), ActionsSuitGroupHierarchy)
        
        # 测试debug_action类型的模型类获取
        self.assertEqual(MODEL_MAPPING.get("ActionDebugList"), ActionDebugList)
        self.assertEqual(MODEL_MAPPING.get("ActionDebugGroup"), ActionsDebugGroup)
        self.assertEqual(MODEL_MAPPING.get("ActionsDebugGroupHierarchy"), ActionsDebugGroupHierarchy)
        
        # 测试不存在的模型类
        self.assertIsNone(MODEL_MAPPING.get("InvalidModel"))
        
        print("✓ 模型映射测试通过")


if __name__ == '__main__':
    print("开始运行删除功能测试...")
    print("=" * 50)
    
    # 运行测试
    unittest.main(verbosity=2)
    
    print("=" * 50)
    print("测试完成！") 