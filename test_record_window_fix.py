#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试录制窗口修复
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
    
    def __init__(self):
        self.my_window = tk.Tk()
        self.my_window.title("测试主窗口")
        self.my_window.geometry("600x400")
        self.action_group_id = 1  # 模拟选中的行为组ID
        
        # 创建测试界面
        self._create_test_ui()
        
    def _create_test_ui(self):
        """创建测试界面"""
        # 主框架
        main_frame = ttk.Frame(self.my_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="录制窗口显示测试", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 说明
        info_label = ttk.Label(main_frame, text="点击下方按钮测试录制窗口显示", font=("Arial", 12))
        info_label.pack(pady=(0, 20))
        
        # 测试按钮
        test_button = ttk.Button(main_frame, text="测试录制窗口", command=self._test_recording_window)
        test_button.pack(pady=10)
        
        # 状态显示
        self.status_label = ttk.Label(main_frame, text="状态: 等待测试", font=("Arial", 10))
        self.status_label.pack(pady=10)
        
    def _test_recording_window(self):
        """测试录制窗口"""
        try:
            self.status_label.config(text="状态: 正在创建录制窗口...")
            self.my_window.update()
            
            # 创建录制管理器
            recorder = ActionRecorder(self)
            
            # 显示录制选项
            result = recorder.show_record_options()
            
            if result:
                self.status_label.config(text="状态: 录制窗口显示成功")
                print("录制窗口显示成功")
            else:
                self.status_label.config(text="状态: 录制窗口显示失败")
                print("录制窗口显示失败")
                
        except Exception as e:
            error_msg = f"测试录制窗口失败: {str(e)}"
            self.status_label.config(text=f"状态: {error_msg}")
            messagebox.showerror("错误", error_msg)
            print(f"错误详情: {e}")
            import traceback
            traceback.print_exc()
    
    def _refresh_action_list(self):
        """模拟刷新行为列表"""
        print("模拟刷新行为列表")
        
    def run(self):
        """运行测试"""
        print("开始测试录制窗口显示...")
        self.my_window.mainloop()

def main():
    """主函数"""
    print("开始测试录制窗口显示...")
    
    # 创建测试窗口
    home_tab = MockHomeTab()
    
    # 运行测试
    home_tab.run()

if __name__ == "__main__":
    main() 