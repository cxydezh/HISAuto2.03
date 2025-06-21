#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQLAlchemy 2.0兼容性修复
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.tabs.home_tab import HomeTab

def test_sqlalchemy_fix():
    """测试SQLAlchemy修复"""
    print("开始测试SQLAlchemy 2.0兼容性修复...")
    
    # 创建主窗口
    root = tk.Tk()
    root.title("SQLAlchemy修复测试")
    root.geometry("800x600")
    
    # 创建notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 创建模拟的main_window对象
    class MockMainWindow:
        def __init__(self, window):
            self.window = window
    
    main_window = MockMainWindow(root)
    
    try:
        # 创建HomeTab
        home_tab = HomeTab(notebook, main_window)
        print("✅ HomeTab创建成功")
        
        # 测试ActionManager
        action_manager = home_tab.action_manager
        print("✅ ActionManager创建成功")
        
        # 测试ActionGroupManager
        action_group_manager = home_tab.action_group_manager
        print("✅ ActionGroupManager创建成功")
        
        print("✅ SQLAlchemy 2.0兼容性修复验证成功")
        print("所有模块都可以正常导入和初始化")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 添加测试说明
    info_frame = ttk.Frame(root)
    info_frame.pack(fill=tk.X, padx=10, pady=10)
    
    info_label = ttk.Label(info_frame, text="SQLAlchemy 2.0兼容性修复测试完成", font=("Arial", 12, "bold"))
    info_label.pack()
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    test_sqlalchemy_fix() 