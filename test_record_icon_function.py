#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试录制窗口的隐藏和图标最小化功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.action_recorder_fixed import ActionRecorder

class MockHomeTab:
    """模拟HomeTab类"""
    def __init__(self, window):
        self.my_window = window
        self.action_group_id = 1  # 模拟已选择行为组

def test_record_function():
    """测试录制功能"""
    print("开始测试录制功能...")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("测试主窗口")
    root.geometry("600x400")
    
    # 创建模拟的HomeTab
    home_tab = MockHomeTab(root)
    
    # 添加一些控件到主窗口
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    title_label = ttk.Label(main_frame, text="录制功能测试", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    info_label = ttk.Label(main_frame, text="点击下面的按钮开始测试录制功能", font=("Arial", 12))
    info_label.pack(pady=10)
    
    def start_test():
        """开始测试"""
        print("开始测试录制功能...")
        recorder = ActionRecorder(home_tab)
        recorder.show_record_options()
    
    def show_main_window():
        """显示主窗口"""
        root.deiconify()
        root.lift()
        root.focus_force()
    
    # 测试按钮
    test_button = ttk.Button(main_frame, text="开始录制测试", command=start_test)
    test_button.pack(pady=20)
    
    # 恢复主窗口按钮
    restore_button = ttk.Button(main_frame, text="恢复主窗口", command=show_main_window)
    restore_button.pack(pady=10)
    
    # 退出按钮
    quit_button = ttk.Button(main_frame, text="退出测试", command=root.quit)
    quit_button.pack(pady=10)
    
    print("测试窗口已创建，请点击'开始录制测试'按钮")
    print("测试步骤：")
    print("1. 点击'开始录制测试'按钮")
    print("2. 主窗口应该被隐藏，显示录制选项窗口")
    print("3. 在录制选项窗口中选择模式并点击'确认'")
    print("4. 录制选项窗口应该关闭，显示20x20的红色圆点图标")
    print("5. 可以拖拽图标到其他位置")
    print("6. 双击图标应该恢复录制选项窗口")
    print("7. 点击'恢复主窗口'按钮可以显示主窗口")
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    test_record_function() 