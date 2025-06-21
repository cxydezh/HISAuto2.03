#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试home_tab_func模块的功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.home_tab_func import home_tab_func, ActionManager, _home_capture_image, _home_delete_action_group, _home_save_action_group

class TestHomeTabFunc(unittest.TestCase):
    """测试home_tab_func类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.valid_params = {
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
    
    def test_init_with_valid_params(self):
        """测试使用有效参数初始化"""
        func = home_tab_func(**self.valid_params)
        self.assertEqual(func.group_name, '测试行为组')
        self.assertEqual(func.group_desc, '这是一个测试行为组')
        self.assertEqual(func.group_user_id, 'user123')
        self.assertEqual(func.action_group_type, 1)
    
    def test_init_with_missing_params(self):
        """测试使用缺失参数初始化"""
        invalid_params = self.valid_params.copy()
        del invalid_params['group_name']
        
        with self.assertRaises(ValueError):
            home_tab_func(**invalid_params)
    
    def test_init_with_auto_time_validation(self):
        """测试自动执行时间验证"""
        invalid_params = self.valid_params.copy()
        invalid_params['is_auto'] = True
        invalid_params['auto_time'] = ''
        
        with self.assertRaises(ValueError):
            home_tab_func(**invalid_params)
    
    @patch('utils.home_tab_func.ConfigManager')
    @patch('utils.home_tab_func.DatabaseManager')
    def test_get_session_success(self, mock_db_manager, mock_config):
        """测试成功获取数据库会话"""
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
        
        func = home_tab_func(**self.valid_params)
        session = func._get_session()
        
        self.assertIsNotNone(session)
        mock_db_instance.initialize.assert_called_once()
    
    @patch('utils.home_tab_func.ConfigManager')
    def test_get_session_missing_config(self, mock_config):
        """测试配置缺失时获取数据库会话"""
        mock_config_instance = Mock()
        mock_config_instance.get_value.return_value = None
        mock_config.return_value = mock_config_instance
        
        func = home_tab_func(**self.valid_params)
        session = func._get_session()
        
        self.assertIsNone(session)

class TestActionManager(unittest.TestCase):
    """测试ActionManager类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.mock_home_tab = Mock()
        self.action_manager = ActionManager(self.mock_home_tab)
    
    def test_create_action_no_group_selected(self):
        """测试没有选择行为组时创建行为"""
        self.mock_home_tab.current_action_group_id = None
        
        result = self.action_manager.create_action()
        
        self.assertFalse(result)
    
    def test_create_action_success(self):
        """测试成功创建行为"""
        self.mock_home_tab.current_action_group_id = 123
        self.mock_home_tab.action_name_var = Mock()
        self.mock_home_tab.next_action_var = Mock()
        self.mock_home_tab.action_type_var = Mock()
        self.mock_home_tab.debug_group_id = Mock()
        self.mock_home_tab.action_note_var = Mock()
        self.mock_home_tab.action_name_entry = Mock()
        self.mock_home_tab.next_action_entry = Mock()
        self.mock_home_tab.action_type_combo = Mock()
        self.mock_home_tab.debug_group_id_entry = Mock()
        self.mock_home_tab.action_note_entry = Mock()
        self.mock_home_tab.btn_create_action = Mock()
        self.mock_home_tab.btn_modify_action = Mock()
        self.mock_home_tab.btn_delete_action = Mock()
        self.mock_home_tab.btn_save_action = Mock()
        self.mock_home_tab.action_list_frame = Mock()
        self.mock_home_tab.action_list_frame.winfo_children.return_value = []
        
        result = self.action_manager.create_action()
        
        self.assertTrue(result)
        self.assertEqual(self.mock_home_tab.action_operation_type, 1)
    
    def test_validate_action_data_empty_name(self):
        """测试验证空行为名称"""
        self.mock_home_tab.action_name_var.get.return_value = ""
        self.mock_home_tab.action_type_var.get.return_value = "mouse"
        
        errors = self.action_manager.validate_action_data()
        
        self.assertIn("行为名称不能为空", errors)
    
    def test_validate_action_data_mouse_coordinates(self):
        """测试验证鼠标坐标"""
        self.mock_home_tab.action_name_var.get.return_value = "测试行为"
        self.mock_home_tab.action_type_var.get.return_value = "mouse"
        self.mock_home_tab.action_mouse_action_type_var.get.return_value = "左键单击"
        self.mock_home_tab.action_mouse_x_var.get.return_value = "-1"
        self.mock_home_tab.action_mouse_y_var.get.return_value = "100"
        
        errors = self.action_manager.validate_action_data()
        
        self.assertIn("鼠标坐标不能为负数", errors)
    
    def test_text_to_mouse_action(self):
        """测试鼠标动作文本转换"""
        self.assertEqual(self.action_manager._text_to_mouse_action("左键单击"), 1)
        self.assertEqual(self.action_manager._text_to_mouse_action("右键单击"), 2)
        self.assertEqual(self.action_manager._text_to_mouse_action("未知动作"), 1)
    
    def test_mouse_action_to_text(self):
        """测试鼠标动作数字转换"""
        self.assertEqual(self.action_manager._mouse_action_to_text(1), "左键单击")
        self.assertEqual(self.action_manager._mouse_action_to_text(2), "右键单击")
        self.assertEqual(self.action_manager._mouse_action_to_text(999), "左键单击")

class TestStandaloneFunctions(unittest.TestCase):
    """测试独立函数"""
    
    @patch('utils.home_tab_func.messagebox')
    def test_home_capture_image(self, mock_messagebox):
        """测试图像采集函数"""
        result = _home_capture_image(123)
        
        self.assertTrue(result)
        mock_messagebox.showinfo.assert_called_once()
    
    @patch('utils.home_tab_func.messagebox')
    def test_home_delete_action_group_invalid_id(self, mock_messagebox):
        """测试删除行为组函数 - 无效ID"""
        result = _home_delete_action_group(None)
        
        self.assertFalse(result)
        mock_messagebox.showwarning.assert_called_once()
    
    @patch('utils.home_tab_func.messagebox')
    def test_home_save_action_group(self, mock_messagebox):
        """测试保存行为组函数"""
        result = _home_save_action_group(123)
        
        self.assertTrue(result)
        mock_messagebox.showinfo.assert_called_once()

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 