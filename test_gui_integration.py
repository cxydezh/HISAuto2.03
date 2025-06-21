#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI集成测试文件 - 测试home_tab的GUI功能
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestHomeTabGUIIntegration(unittest.TestCase):
    """测试HomeTab的GUI集成功能"""
    
    def test_action_manager_integration(self):
        """测试ActionManager与HomeTab的集成"""
        from utils.home_tab_func import ActionManager
        
        # 模拟home_tab
        mock_home_tab = Mock()
        mock_home_tab.current_action_group_id = 123
        mock_home_tab.action_operation_type = None
        mock_home_tab.action_name_var = Mock()
        mock_home_tab.next_action_var = Mock()
        mock_home_tab.action_type_var = Mock()
        mock_home_tab.debug_group_id = Mock()
        mock_home_tab.action_note_var = Mock()
        mock_home_tab.action_list_frame = Mock()
        mock_home_tab.action_list_frame.winfo_children.return_value = []
        mock_home_tab.btn_create_action = Mock()
        mock_home_tab.btn_modify_action = Mock()
        mock_home_tab.btn_delete_action = Mock()
        mock_home_tab.btn_save_action = Mock()
        
        # 创建ActionManager
        action_manager = ActionManager(mock_home_tab)
        
        # 测试创建行为
        result = action_manager.create_action()
        
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(mock_home_tab.action_operation_type, 1)
    
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

class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""
    
    @patch('utils.home_tab_func.messagebox')
    def test_home_tab_func_validation_error(self, mock_messagebox):
        """测试home_tab_func的验证错误处理"""
        from utils.home_tab_func import home_tab_func
        
        # 测试无效参数
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
        
        # 应该抛出ValueError
        with self.assertRaises(ValueError):
            home_tab_func(**invalid_params)

if __name__ == '__main__':
    unittest.main(verbosity=2) 