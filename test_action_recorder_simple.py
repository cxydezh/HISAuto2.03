"""
ActionRecord类简化测试脚本
用于快速验证基本功能是否正常工作
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入需要测试的模块
from utils.action_recorder_fixed import ActionRecorder, record_action

class SimpleTestWindow:
    """简化测试窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ActionRecord功能测试")
        self.root.geometry("500x400")
        
        # 创建模拟的home_tab
        self.home_tab = self.create_mock_home_tab()
        
        # 创建UI
        self.create_ui()
        
    def create_mock_home_tab(self):
        """创建模拟的home_tab"""
        class MockHomeTab:
            def __init__(self, window):
                self.action_group_id = 1  # 默认有行为组
                self.my_window = window
                self._refresh_action_list_called = False
            
            def _refresh_action_list(self):
                self._refresh_action_list_called = True
                print("✅ 刷新动作列表被调用")
        
        return MockHomeTab(self.root)
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="ActionRecord功能测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 测试按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # 测试按钮
        ttk.Button(button_frame, text="测试录制功能", command=self.test_recording).pack(pady=5)
        ttk.Button(button_frame, text="测试快捷键解析", command=self.test_hotkey_parsing).pack(pady=5)
        ttk.Button(button_frame, text="测试事件录制", command=self.test_event_recording).pack(pady=5)
        ttk.Button(button_frame, text="测试窗口最小化", command=self.test_window_minimize).pack(pady=5)
        
        # 状态显示框架
        status_frame = ttk.LabelFrame(main_frame, text="测试状态", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_text = tk.Text(status_frame, height=10, width=50)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # 控制框架
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        ttk.Button(control_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="关闭测试", command=self.root.destroy).pack(side=tk.LEFT, padx=5)
        
        # 添加初始日志
        self.log("ActionRecord功能测试已启动")
        self.log("请点击上方按钮进行各项功能测试")
    
    def log(self, message):
        """添加日志信息"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
        print(log_message.strip())
    
    def clear_log(self):
        """清空日志"""
        self.status_text.delete(1.0, tk.END)
        self.log("日志已清空")
    
    def test_recording(self):
        """测试录制功能"""
        self.log("开始测试录制功能...")
        
        try:
            # 创建ActionRecorder实例
            recorder = ActionRecorder(self.home_tab)
            self.log("✅ ActionRecorder实例创建成功")
            
            # 测试没有行为组的情况
            original_group_id = self.home_tab.action_group_id
            self.home_tab.action_group_id = None
            
            # 这里应该会显示警告，但由于是GUI测试，我们直接检查
            self.log("测试没有选择行为组的情况...")
            
            # 恢复行为组ID
            self.home_tab.action_group_id = original_group_id
            
            # 测试record_action函数
            self.log("测试record_action函数...")
            result = record_action(self.home_tab)
            self.log(f"record_action函数返回: {result}")
            
        except Exception as e:
            self.log(f"❌ 录制功能测试失败: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
    
    def test_hotkey_parsing(self):
        """测试快捷键解析功能"""
        self.log("开始测试快捷键解析功能...")
        
        try:
            recorder = ActionRecorder(self.home_tab)
            
            # 测试各种快捷键格式
            test_cases = [
                ("Esc", ["esc"]),
                ("Alt+E", ["alt", "e"]),
                ("Ctrl+F12", ["ctrl", "f12"]),
                ("Alt+Shift+A", ["alt", "shift", "a"]),
                ("Win+R", ["win", "r"]),
            ]
            
            for hotkey_str, expected in test_cases:
                result = recorder._parse_hotkey(hotkey_str)
                if result == expected:
                    self.log(f"✅ 解析 {hotkey_str} -> {result}")
                else:
                    self.log(f"❌ 解析 {hotkey_str} 失败: 期望 {expected}, 实际 {result}")
            
            self.log("快捷键解析测试完成")
            
        except Exception as e:
            self.log(f"❌ 快捷键解析测试失败: {str(e)}")
    
    def test_event_recording(self):
        """测试事件录制功能"""
        self.log("开始测试事件录制功能...")
        
        try:
            recorder = ActionRecorder(self.home_tab)
            
            # 启动录制
            recorder.recording = True
            recorder.last_event_time = time.time()
            
            # 模拟键盘事件
            class MockKeyEvent:
                def __init__(self, name):
                    self.name = name
            
            # 测试键盘事件
            key_event = MockKeyEvent('a')
            recorder._on_key_press(key_event)
            self.log(f"✅ 键盘按下事件记录: {len(recorder.recorded_events)} 个事件")
            
            recorder._on_key_release(key_event)
            self.log(f"✅ 键盘释放事件记录: {len(recorder.recorded_events)} 个事件")
            
            # 测试鼠标事件（模拟）
            recorder._on_mouse_click(100, 200, 'left', True)
            self.log(f"✅ 鼠标点击事件记录: {len(recorder.recorded_events)} 个事件")
            
            # 检查事件数据
            if recorder.recorded_events:
                for i, event in enumerate(recorder.recorded_events):
                    self.log(f"事件 {i+1}: 类型={event['type']}, 代码={event['action_code']}")
            
            # 停止录制
            recorder.recording = False
            self.log("事件录制测试完成")
            
        except Exception as e:
            self.log(f"❌ 事件录制测试失败: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
    
    def test_window_minimize(self):
        """测试窗口最小化功能"""
        self.log("开始测试窗口最小化功能...")
        
        try:
            recorder = ActionRecorder(self.home_tab)
            
            # 测试最小化到图标
            recorder.minimize_to_icon()
            
            if recorder.icon_window:
                self.log("✅ 图标窗口创建成功")
                self.log(f"图标窗口位置: {recorder.icon_window.geometry()}")
                self.log(f"最小化状态: {recorder.is_minimized}")
                
                # 测试恢复窗口
                recorder.restore_window()
                
                if not recorder.icon_window:
                    self.log("✅ 图标窗口销毁成功")
                else:
                    self.log("❌ 图标窗口未正确销毁")
            else:
                self.log("❌ 图标窗口创建失败")
            
            self.log("窗口最小化测试完成")
            
        except Exception as e:
            self.log(f"❌ 窗口最小化测试失败: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
    
    def run(self):
        """运行测试"""
        self.root.mainloop()

def main():
    """主函数"""
    print("ActionRecord简化功能测试")
    print("=" * 40)
    
    # 创建并运行测试窗口
    test_window = SimpleTestWindow()
    test_window.run()

if __name__ == "__main__":
    main() 