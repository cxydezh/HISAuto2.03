"""
ActionRecord类功能测试文件
测试ActionRecord类的所有功能是否正常工作
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入需要测试的模块
from utils.action_recorder_fixed import ActionRecorder, record_action
from config.config_manager import ConfigManager
from database.db_manager import DatabaseManager
from models.actions import ActionList, ActionMouse, ActionKeyboard
import globalvariable

class MockHomeTab:
    """模拟HomeTab类"""
    def __init__(self):
        self.action_group_id = 1
        self.my_window = None
        self._refresh_action_list_called = False
    
    def _refresh_action_list(self):
        """模拟刷新动作列表"""
        self._refresh_action_list_called = True

class TestActionRecorder(unittest.TestCase):
    """ActionRecord类测试用例"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建模拟的home_tab
        self.home_tab = MockHomeTab()
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        self.home_tab.my_window = self.root
        
        # 创建ActionRecorder实例
        self.recorder = ActionRecorder(self.home_tab)
        
        # 模拟全局变量
        globalvariable.USER_ID = 1
        globalvariable.USER_DEPARTMENT_ID = 1
    
    def tearDown(self):
        """测试后的清理工作"""
        # 停止录制
        if hasattr(self.recorder, 'recording') and self.recorder.recording:
            self.recorder.stop_recording()
        
        # 关闭窗口
        if hasattr(self.recorder, 'record_window') and self.recorder.record_window:
            try:
                self.recorder.record_window.destroy()
            except:
                pass
        
        if hasattr(self.recorder, 'icon_window') and self.recorder.icon_window:
            try:
                self.recorder.icon_window.destroy()
            except:
                pass
        
        # 关闭主窗口
        try:
            self.root.destroy()
        except:
            pass
    
    def test_initialization(self):
        """测试初始化"""
        print("\n=== 测试初始化 ===")
        
        # 检查基本属性
        self.assertIsNotNone(self.recorder.home_tab)
        self.assertFalse(self.recorder.recording)
        self.assertIsNone(self.recorder.record_window)
        self.assertEqual(self.recorder.recorded_events, [])
        self.assertIsNone(self.recorder.last_event_time)
        self.assertEqual(self.recorder.record_mode, "全部")
        self.assertIsNone(self.recorder.session)
        self.assertIsNone(self.recorder.end_record_keys)
        
        print("✅ 初始化测试通过")
    
    def test_show_record_options_no_action_group(self):
        """测试没有选择行为组时的情况"""
        print("\n=== 测试没有选择行为组 ===")
        
        # 临时设置action_group_id为None
        original_group_id = self.home_tab.action_group_id
        self.home_tab.action_group_id = None
        
        # 使用patch模拟messagebox.showwarning
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            result = self.recorder.show_record_options()
            
            # 检查是否显示了警告
            mock_warning.assert_called_once_with("警告", "请先选择行为组")
            self.assertFalse(result)
        
        # 恢复原始值
        self.home_tab.action_group_id = original_group_id
        print("✅ 没有选择行为组测试通过")
    
    def test_parse_hotkey(self):
        """测试快捷键解析功能"""
        print("\n=== 测试快捷键解析 ===")
        
        # 测试各种快捷键格式
        test_cases = [
            ("Esc", ["esc"]),
            ("Alt+E", ["alt", "e"]),
            ("Ctrl+F12", ["ctrl", "f12"]),
            ("Alt+Shift+A", ["alt", "shift", "a"]),
            ("Win+R", ["win", "r"]),
        ]
        
        for hotkey_str, expected in test_cases:
            result = self.recorder._parse_hotkey(hotkey_str)
            self.assertEqual(result, expected, f"解析 {hotkey_str} 失败")
            print(f"✅ 解析 {hotkey_str} -> {result}")
        
        print("✅ 快捷键解析测试通过")
    
    def test_check_hotkey_pressed(self):
        """测试快捷键检测功能"""
        print("\n=== 测试快捷键检测 ===")
        
        # 使用patch模拟keyboard.is_pressed
        with patch('keyboard.is_pressed') as mock_is_pressed:
            # 测试Alt+E组合键
            keys = ['alt', 'e']
            
            # 模拟Alt键按下，E键未按下
            mock_is_pressed.side_effect = lambda key: key == 'alt'
            result = self.recorder._check_hotkey_pressed(keys)
            self.assertFalse(result)
            
            # 模拟Alt键和E键都按下
            mock_is_pressed.side_effect = lambda key: key in ['alt', 'e']
            result = self.recorder._check_hotkey_pressed(keys)
            self.assertTrue(result)
            
            # 模拟只有E键按下，Alt键未按下
            mock_is_pressed.side_effect = lambda key: key == 'e'
            result = self.recorder._check_hotkey_pressed(keys)
            self.assertFalse(result)
        
        print("✅ 快捷键检测测试通过")
    
    def test_event_recording_simulation(self):
        """测试事件录制模拟"""
        print("\n=== 测试事件录制模拟 ===")
        
        # 启动录制
        self.recorder.recording = True
        self.recorder.last_event_time = time.time()
        
        # 模拟键盘事件
        mock_key_event = Mock()
        mock_key_event.name = 'a'
        
        # 测试键盘按下事件
        self.recorder._on_key_press(mock_key_event)
        self.assertEqual(len(self.recorder.recorded_events), 1)
        self.assertEqual(self.recorder.recorded_events[0]['type'], 'keyboard')
        self.assertEqual(self.recorder.recorded_events[0]['action_code'], 1)
        self.assertEqual(self.recorder.recorded_events[0]['key_value'], 'a')
        
        # 测试键盘释放事件
        self.recorder._on_key_release(mock_key_event)
        self.assertEqual(len(self.recorder.recorded_events), 2)
        self.assertEqual(self.recorder.recorded_events[1]['type'], 'keyboard')
        self.assertEqual(self.recorder.recorded_events[1]['action_code'], 2)
        
        # 模拟鼠标事件
        with patch('mouse.get_position', return_value=(100, 200)):
            # 测试鼠标点击事件
            self.recorder._on_mouse_click(100, 200, 'left', True)
            self.assertEqual(len(self.recorder.recorded_events), 3)
            self.assertEqual(self.recorder.recorded_events[2]['type'], 'mouse')
            self.assertEqual(self.recorder.recorded_events[2]['action_code'], 1)  # 左键单击
            self.assertEqual(self.recorder.recorded_events[2]['x'], 100)
            self.assertEqual(self.recorder.recorded_events[2]['y'], 200)
            
            # 测试鼠标按下事件
            self.recorder._on_mouse_press('left')
            self.assertEqual(len(self.recorder.recorded_events), 4)
            self.assertEqual(self.recorder.recorded_events[3]['type'], 'mouse')
            self.assertEqual(self.recorder.recorded_events[3]['action_code'], 4)  # 左键按下
            
            # 测试鼠标释放事件
            self.recorder._on_mouse_release('left')
            self.assertEqual(len(self.recorder.recorded_events), 5)
            self.assertEqual(self.recorder.recorded_events[4]['type'], 'mouse')
            self.assertEqual(self.recorder.recorded_events[4]['action_code'], 5)  # 左键释放
        
        print("✅ 事件录制模拟测试通过")
    
    def test_database_session_creation(self):
        """测试数据库会话创建"""
        print("\n=== 测试数据库会话创建 ===")
        
        # 使用patch模拟ConfigManager和DatabaseManager
        with patch('config.config_manager.ConfigManager') as mock_config_class, \
             patch('database.db_manager.DatabaseManager') as mock_db_class:
            
            # 设置模拟返回值
            mock_config = Mock()
            mock_config.get_value.side_effect = lambda section, key, default=None: {
                ('System', 'datasource'): 'test.db',
                ('Security', 'dbencryptionkey'): 'test_key'
            }.get((section, key), default)
            
            mock_config_class.return_value = mock_config
            
            mock_db_manager = Mock()
            mock_session = Mock()
            mock_db_manager.Session.return_value = mock_session
            mock_db_class.return_value = mock_db_manager
            
            # 测试获取会话
            session = self.recorder._get_session()
            self.assertIsNotNone(session)
            
            # 验证调用
            mock_config.get_value.assert_any_call('System', 'datasource')
            mock_config.get_value.assert_any_call('Security', 'dbencryptionkey')
            mock_db_manager.initialize.assert_called_once()
        
        print("✅ 数据库会话创建测试通过")
    
    def test_save_recorded_events(self):
        """测试保存录制事件到数据库"""
        print("\n=== 测试保存录制事件到数据库 ===")
        
        # 创建模拟事件数据
        self.recorder.recorded_events = [
            {
                'type': 'keyboard',
                'action_code': 1,
                'key_value': 'a',
                'time_diff': 0.1,
                'timestamp': time.time()
            },
            {
                'type': 'mouse',
                'action_code': 1,
                'x': 100,
                'y': 200,
                'mouse_size': 1,
                'time_diff': 0.2,
                'timestamp': time.time()
            }
        ]
        
        # 使用patch模拟数据库操作
        with patch('models.actions.ActionList') as mock_action_list_class, \
             patch('models.actions.ActionMouse') as mock_action_mouse_class, \
             patch('models.actions.ActionKeyboard') as mock_action_keyboard_class:
            
            # 设置模拟对象
            mock_action_list = Mock()
            mock_action_list.id = 1
            mock_action_list_class.return_value = mock_action_list
            
            mock_action_mouse = Mock()
            mock_action_mouse_class.return_value = mock_action_mouse
            
            mock_action_keyboard = Mock()
            mock_action_keyboard_class.return_value = mock_action_keyboard
            
            # 创建模拟会话
            mock_session = Mock()
            self.recorder.session = mock_session
            
            # 测试保存事件
            self.recorder._save_recorded_events()
            
            # 验证调用
            self.assertEqual(mock_session.add.call_count, 4)  # 2个ActionList + 1个ActionMouse + 1个ActionKeyboard
            mock_session.flush.assert_called()
            mock_session.commit.assert_called_once()
        
        print("✅ 保存录制事件测试通过")
    
    def test_minimize_and_restore_window(self):
        """测试窗口最小化和恢复功能"""
        print("\n=== 测试窗口最小化和恢复 ===")
        
        # 使用patch模拟show_record_options_with_state
        with patch.object(self.recorder, 'show_record_options_with_state') as mock_show_options:
            # 测试最小化到图标
            self.recorder.minimize_to_icon()
            
            # 检查图标窗口是否创建
            self.assertIsNotNone(self.recorder.icon_window)
            self.assertTrue(self.recorder.is_minimized)
            
            # 测试恢复窗口
            self.recorder.restore_window()
            
            # 检查是否调用了show_record_options_with_state
            mock_show_options.assert_called_once()
            
            # 检查图标窗口是否被销毁
            self.assertIsNone(self.recorder.icon_window)
            self.assertFalse(self.recorder.is_minimized)
        
        print("✅ 窗口最小化和恢复测试通过")
    
    def test_stop_recording(self):
        """测试停止录制功能"""
        print("\n=== 测试停止录制功能 ===")
        
        # 设置录制状态
        self.recorder.recording = True
        self.recorder.recorded_events = [{'type': 'test', 'data': 'test'}]
        
        # 使用patch模拟各种依赖
        with patch('keyboard.unhook_all') as mock_unhook_keyboard, \
             patch('mouse.unhook_all') as mock_unhook_mouse, \
             patch.object(self.recorder, '_save_recorded_events') as mock_save_events, \
             patch('tkinter.messagebox.showinfo') as mock_show_info:
            
            # 创建模拟会话
            mock_session = Mock()
            self.recorder.session = mock_session
            
            # 测试停止录制
            self.recorder.stop_recording()
            
            # 验证状态变化
            self.assertFalse(self.recorder.recording)
            self.assertIsNone(self.recorder.session)
            
            # 验证调用
            mock_unhook_keyboard.assert_called_once()
            mock_unhook_mouse.assert_called_once()
            mock_save_events.assert_called_once()
            mock_session.close.assert_called_once()
            mock_show_info.assert_called_once()
        
        print("✅ 停止录制功能测试通过")
    
    def test_record_action_function(self):
        """测试record_action函数"""
        print("\n=== 测试record_action函数 ===")
        
        # 测试没有选择行为组的情况
        original_group_id = self.home_tab.action_group_id
        self.home_tab.action_group_id = None
        
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            result = record_action(self.home_tab)
            mock_warning.assert_called_once_with("警告", "请先选择行为组")
            self.assertFalse(result)
        
        # 恢复原始值
        self.home_tab.action_group_id = original_group_id
        
        # 测试正常情况
        with patch.object(ActionRecorder, 'show_record_options', return_value=True):
            result = record_action(self.home_tab)
            self.assertTrue(result)
        
        print("✅ record_action函数测试通过")

class TestActionRecorderIntegration(unittest.TestCase):
    """ActionRecord集成测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.home_tab = MockHomeTab()
        self.root = tk.Tk()
        self.root.withdraw()
        self.home_tab.my_window = self.root
    
    def tearDown(self):
        """测试后的清理工作"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_full_recording_workflow(self):
        """测试完整的录制工作流程"""
        print("\n=== 测试完整录制工作流程 ===")
        
        recorder = ActionRecorder(self.home_tab)
        
        # 模拟配置管理器
        with patch('config.config_manager.ConfigManager') as mock_config_class:
            mock_config = Mock()
            mock_config.get_value.return_value = 'Esc'
            mock_config_class.return_value = mock_config
            
            # 模拟数据库管理器
            with patch('database.db_manager.DatabaseManager') as mock_db_class:
                mock_db_manager = Mock()
                mock_session = Mock()
                mock_db_manager.Session.return_value = mock_session
                mock_db_class.return_value = mock_db_manager
                
                # 模拟事件监听
                with patch('keyboard.on_press'), \
                     patch('keyboard.on_release'), \
                     patch('mouse.on_click'), \
                     patch('mouse.on_button'), \
                     patch('keyboard.unhook_all'), \
                     patch('mouse.unhook_all'):
                    
                    # 启动录制
                    recorder.start_event_recording()
                    
                    # 验证录制状态
                    self.assertTrue(recorder.recording)
                    self.assertIsNotNone(recorder.session)
                    
                    # 模拟一些事件
                    mock_key_event = Mock()
                    mock_key_event.name = 'a'
                    recorder._on_key_press(mock_key_event)
                    
                    # 验证事件记录
                    self.assertEqual(len(recorder.recorded_events), 1)
                    
                    # 停止录制
                    recorder.stop_recording()
                    
                    # 验证停止状态
                    self.assertFalse(recorder.recording)
                    self.assertIsNone(recorder.session)
        
        print("✅ 完整录制工作流程测试通过")

def run_gui_test():
    """运行GUI测试（可选）"""
    print("\n=== 运行GUI测试 ===")
    print("注意：GUI测试需要手动交互")
    print("1. 选择行为组")
    print("2. 点击录制按钮")
    print("3. 选择录制模式")
    print("4. 点击确认开始录制")
    print("5. 观察窗口是否最小化到右上角")
    print("6. 双击图标查看是否恢复窗口")
    print("7. 检查按钮状态是否正确")
    print("8. 按Esc键结束录制")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("ActionRecord GUI测试")
    root.geometry("400x300")
    
    # 创建模拟的home_tab
    home_tab = MockHomeTab()
    home_tab.my_window = root
    home_tab.action_group_id = 1
    
    # 创建测试按钮
    def test_record():
        recorder = ActionRecorder(home_tab)
        recorder.show_record_options()
    
    test_button = ttk.Button(root, text="测试录制功能", command=test_record)
    test_button.pack(pady=20)
    
    # 添加说明文本
    info_text = """
    GUI测试说明：
    1. 点击"测试录制功能"按钮
    2. 在弹出窗口中选择录制模式
    3. 点击"确认"开始录制
    4. 观察窗口是否最小化到右上角
    5. 双击红色圆点图标
    6. 检查恢复的窗口中按钮状态
    7. 按Esc键结束录制
    """
    
    info_label = ttk.Label(root, text=info_text, justify=tk.LEFT)
    info_label.pack(pady=20)
    
    # 关闭按钮
    close_button = ttk.Button(root, text="关闭测试", command=root.destroy)
    close_button.pack(pady=10)
    
    root.mainloop()

def main():
    """主函数"""
    print("ActionRecord类功能测试")
    print("=" * 50)
    
    # 运行单元测试
    print("\n开始运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 询问是否运行GUI测试
    print("\n" + "=" * 50)
    response = input("是否运行GUI测试？(y/n): ").lower().strip()
    if response == 'y':
        run_gui_test()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 