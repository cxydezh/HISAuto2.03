#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试录制功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.action_recorder_fixed import record_action

def test_record_function():
    """测试录制功能"""
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("录制功能测试")
        root.geometry("500x400")
        
        # 创建测试按钮
        def test_record():
            try:
                # 创建一个模拟的home_tab对象
                class MockHomeTab:
                    def __init__(self):
                        self.action_group_id = 1  # 模拟选中的行为组ID
                        self.my_window = root
                        
                mock_home_tab = MockHomeTab()
                
                # 测试录制功能
                result = record_action(mock_home_tab)
                
                if result:
                    result_label.config(text="录制功能启动成功", fg="green")
                else:
                    result_label.config(text="录制功能启动失败", fg="red")
                    
            except Exception as e:
                print(f"录制功能测试失败: {e}")
                traceback.print_exc()
                result_label.config(text=f"测试失败: {str(e)}", fg="red")
        
        # 创建说明标签
        info_label = tk.Label(root, text="录制功能测试", font=("Arial", 14, "bold"))
        info_label.pack(pady=10)
        
        instruction_label = tk.Label(root, text="点击'测试录制功能'按钮开始测试\n这将打开录制选项窗口", 
                                   font=("Arial", 10), justify=tk.LEFT)
        instruction_label.pack(pady=10)
        
        # 创建按钮
        test_btn = tk.Button(root, text="测试录制功能", command=test_record, 
                           font=("Arial", 12), bg="lightblue", padx=20, pady=10)
        test_btn.pack(pady=20)
        
        # 创建结果显示标签
        result_label = tk.Label(root, text="等待测试...", font=("Arial", 12))
        result_label.pack(pady=10)
        
        # 创建退出按钮
        exit_btn = tk.Button(root, text="退出", command=root.quit, 
                           font=("Arial", 10), bg="lightcoral", padx=15, pady=5)
        exit_btn.pack(pady=10)
        
        print("录制功能测试程序已启动")
        print("点击'测试录制功能'按钮开始测试")
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        print(f"测试程序启动失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_record_function() 