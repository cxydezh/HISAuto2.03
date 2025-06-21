#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试文件 - 测试home_tab_func和home_tab的集成功能
避免循环导入问题
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestHomeTabFuncIntegration(unittest.TestCase):
    """测试home_tab_func的集成功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 模拟必要的模块
        self.mock_config = Mock()
        self.mock_db_manager = Mock()
        self.mock_session = Mock()
        
    @patch('utils.home_tab_func.ConfigManager')
    @patch('utils.home_tab_func.DatabaseManager')
    def test_home_tab_func_initialization(self, mock_db_manager, mock_config):
        """测试home_tab_func类的初始化"""
        # 模拟配置
        mock_config_instance = Mock()
        mock_config_instance.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): '/path/to/db',
            ('Security', 'DBEncryptionKey'): 'encryption_key'
        }[section, key]
        mock_config.return_value = mock_config_instance
        
        # 模拟数据库管理器
        mock_db_instance = Mock()
        mock_db_instance.Session.return_value = Mock()
        mock_db_manager.return_value = mock_db_instance
        
        # 导入并测试home_tab_func
        from utils.home_tab_func import home_tab_func
        
        # 测试有效参数初始化
        valid_params = {
            'group_name': '测试行为组',
            'group_desc': '这是一个测试行为组',
            'group_user_id': 'user123',
            'group_department_id': 'dept456',
            'is_auto': False,
            'auto_time': '',
            'action_group_selected_rank': 'rank1',
            'action_tree_selected_iid': 'group_123',
            'action_group_type': 1,
            'sort_num': 1,
            'action_group_id': 123,
            'action_group_hierarchy_id': 456
        }
        
        func = home_tab_func(**valid_params)
        self.assertEqual(func.group_name, '测试行为组')
        self.assertEqual(func.group_user_id, 'user123')
        self.assertEqual(func.action_group_type, 1)
    
    def test_home_tab_func_validation(self):
        """测试home_tab_func的参数验证"""
        from utils.home_tab_func import home_tab_func
        
        # 测试缺失参数
        invalid_params = {
            'group_name': '',  # 空名称
            'group_desc': '这是一个测试行为组',
            'group_user_id': 'user123',
            'group_department_id': 'dept456',
            'is_auto': False,
            'auto_time': '',
            'action_group_selected_rank': 'rank1',
            'action_tree_selected_iid': 'group_123',
            'action_group_type': 1,
            'sort_num': 1,
            'action_group_id': 123,
            'action_group_hierarchy_id': 456
        }
        
        with self.assertRaises(ValueError):
            home_tab_func(**invalid_params)
    
    def test_action_manager_creation(self):
        """测试ActionManager的创建"""
        from utils.home_tab_func import ActionManager
        
        # 模拟home_tab
        mock_home_tab = Mock()
        mock_home_tab.current_action_group_id = None
        mock_home_tab.action_name_var = Mock()
        mock_home_tab.action_type_var = Mock()
        mock_home_tab.action_operation_type = None
        
        # 创建ActionManager实例
        action_manager = ActionManager(mock_home_tab)
        self.assertIsNotNone(action_manager)
        self.assertEqual(action_manager.home_tab, mock_home_tab)
    
    def test_action_manager_validation(self):
        """测试ActionManager的数据验证"""
        from utils.home_tab_func import ActionManager
        
        # 模拟home_tab
        mock_home_tab = Mock()
        mock_home_tab.action_name_var.get.return_value = ""
        mock_home_tab.action_type_var.get.return_value = "mouse"
        mock_home_tab.action_mouse_action_type_var.get.return_value = ""
        # 添加更多必要的属性模拟
        mock_home_tab.action_mouse_x_var.get.return_value = "0"
        mock_home_tab.action_mouse_y_var.get.return_value = "0"
        mock_home_tab.action_keyboard_type_var.get.return_value = ""
        mock_home_tab.action_keyboard_value_var.get.return_value = ""
        mock_home_tab.class_name_var.get.return_value = ""
        mock_home_tab.ai_train_group_var.get.return_value = ""
        mock_home_tab.action_print_lux_var.get.return_value = "0"
        mock_home_tab.action_print_luy_var.get.return_value = "0"
        mock_home_tab.action_print_rdx_var.get.return_value = "100"
        mock_home_tab.action_print_rdy_var.get.return_value = "100"
        mock_home_tab.function_name_var.get.return_value = ""
        
        action_manager = ActionManager(mock_home_tab)
        errors = action_manager.validate_action_data()
        
        self.assertIn("行为名称不能为空", errors)
        self.assertIn("请选择鼠标动作类型", errors)
    
    def test_text_conversion_methods(self):
        """测试文本转换方法"""
        from utils.home_tab_func import ActionManager
        
        mock_home_tab = Mock()
        action_manager = ActionManager(mock_home_tab)
        
        # 测试鼠标动作转换
        self.assertEqual(action_manager._text_to_mouse_action("左键单击"), 1)
        self.assertEqual(action_manager._text_to_mouse_action("右键单击"), 2)
        self.assertEqual(action_manager._text_to_mouse_action("未知动作"), 1)  # 默认值
        
        # 测试键盘类型转换
        self.assertEqual(action_manager._text_to_keyboard_type("按下"), 1)
        self.assertEqual(action_manager._text_to_keyboard_type("释放"), 2)
        self.assertEqual(action_manager._text_to_keyboard_type("未知类型"), 3)  # 默认值
        
        # 测试反向转换
        self.assertEqual(action_manager._mouse_action_to_text(1), "左键单击")
        self.assertEqual(action_manager._mouse_action_to_text(2), "右键单击")
        self.assertEqual(action_manager._keyboard_type_to_text(1), "按下")
        self.assertEqual(action_manager._keyboard_type_to_text(2), "释放")

class TestStandaloneFunctions(unittest.TestCase):
    """测试独立函数"""
    
    @patch('utils.home_tab_func.messagebox')
    def test_home_capture_image(self, mock_messagebox):
        """测试图像采集函数"""
        from utils.home_tab_func import _home_capture_image
        
        result = _home_capture_image(123)
        self.assertTrue(result)
        mock_messagebox.showinfo.assert_called_once()
    
    @patch('utils.home_tab_func.messagebox')
    def test_home_delete_action_group_invalid_id(self, mock_messagebox):
        """测试删除行为组函数 - 无效ID"""
        from utils.home_tab_func import _home_delete_action_group
        
        result = _home_delete_action_group(None)
        self.assertFalse(result)
        mock_messagebox.showwarning.assert_called_once()
    
    @patch('utils.home_tab_func.messagebox')
    def test_home_save_action_group(self, mock_messagebox):
        """测试保存行为组函数"""
        from utils.home_tab_func import _home_save_action_group
        
        result = _home_save_action_group(123)
        self.assertTrue(result)
        mock_messagebox.showinfo.assert_called_once()

class TestDatabaseOperations(unittest.TestCase):
    """测试数据库操作"""
    
    @patch('utils.home_tab_func.ConfigManager')
    @patch('utils.home_tab_func.DatabaseManager')
    def test_get_session_success(self, mock_db_manager, mock_config):
        """测试成功获取数据库会话"""
        from utils.home_tab_func import home_tab_func
        
        # 模拟配置
        mock_config_instance = Mock()
        mock_config_instance.get_value.side_effect = lambda section, key: {
            ('System', 'DataSource'): '/path/to/db',
            ('Security', 'DBEncryptionKey'): 'encryption_key'
        }[section, key]
        mock_config.return_value = mock_config_instance
        
        # 模拟数据库管理器
        mock_db_instance = Mock()
        mock_db_instance.Session.return_value = Mock()
        mock_db_manager.return_value = mock_db_instance
        
        # 创建实例并测试
        valid_params = {
            'group_name': '测试行为组',
            'group_desc': '这是一个测试行为组',
            'group_user_id': 'user123',
            'group_department_id': 'dept456',
            'is_auto': False,
            'auto_time': '',
            'action_group_selected_rank': 'rank1',
            'action_tree_selected_iid': 'group_123',
            'action_group_type': 1,
            'sort_num': 1,
            'action_group_id': 123,
            'action_group_hierarchy_id': 456
        }
        
        func = home_tab_func(**valid_params)
        session = func._get_session()
        
        self.assertIsNotNone(session)
        mock_db_instance.initialize.assert_called_once()
    
    @patch('utils.home_tab_func.ConfigManager')
    def test_get_session_missing_config(self, mock_config):
        """测试配置缺失时获取数据库会话"""
        from utils.home_tab_func import home_tab_func
        
        mock_config_instance = Mock()
        mock_config_instance.get_value.return_value = None
        mock_config.return_value = mock_config_instance
        
        valid_params = {
            'group_name': '测试行为组',
            'group_desc': '这是一个测试行为组',
            'group_user_id': 'user123',
            'group_department_id': 'dept456',
            'is_auto': False,
            'auto_time': '',
            'action_group_selected_rank': 'rank1',
            'action_tree_selected_iid': 'group_123',
            'action_group_type': 1,
            'sort_num': 1,
            'action_group_id': 123,
            'action_group_hierarchy_id': 456
        }
        
        func = home_tab_func(**valid_params)
        session = func._get_session()
        
        self.assertIsNone(session)

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 