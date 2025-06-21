#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主程序中的录制功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.tabs.home_tab import HomeTab
from gui.tabs.base_tab import BaseTab

def test_main_record_function():
    """测试主程序中的录制功能"""
    print("开始测试主程序录制功能...")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("主程序录制功能测试")
    root.geometry("800x600")
    
    # 创建notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 创建模拟的main_window对象
    class MockMainWindow:
        def __init__(self, window):
            self.window = window
    
    main_window = MockMainWindow(root)
    
    # 创建HomeTab
    home_tab = HomeTab(notebook, main_window)
    
    # 模拟选择行为组
    home_tab.action_group_id = 1
    
    print("主程序录制功能测试准备就绪")
    print("测试步骤：")
    print("1. 在首页标签页中点击'录制'按钮")
    print("2. 主窗口应该被隐藏，显示录制选项窗口")
    print("3. 选择录制模式并点击'确认'")
    print("4. 应该显示20x20的红色圆点图标")
    print("5. 双击图标可以恢复录制选项窗口")
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    test_main_record_function() 