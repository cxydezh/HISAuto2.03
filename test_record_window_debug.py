#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试录制窗口显示问题
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.action_recorder_fixed import ActionRecorder

class MockHomeTab:
    """模拟HomeTab类"""
    
    def __init__(self):
        print("创建MockHomeTab...")
        self.my_window = tk.Tk()
        self.my_window.title("测试主窗口")
        self.my_window.geometry("600x400")
        self.action_group_id = 1  # 模拟选中的行为组ID
        
        # 创建测试界面
        self._create_test_ui()
        print("MockHomeTab创建完成")
        
    def _create_test_ui(self):
        """创建测试界面"""
        # 主框架
        main_frame = ttk.Frame(self.my_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="录制窗口调试测试", font=("Arial", 16, "bold"))
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
        
        # 调试信息显示
        self.debug_text = tk.Text(main_frame, height=10, width=60)
        self.debug_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
    def _log_debug(self, message):
        """记录调试信息"""
        print(message)
        self.debug_text.insert(tk.END, f"{message}\n")
        self.debug_text.see(tk.END)
        self.my_window.update()
        
    def _test_recording_window(self):
        """测试录制窗口"""
        try:
            self._log_debug("=== 开始测试录制窗口 ===")
            self.status_label.config(text="状态: 正在创建录制窗口...")
            self.my_window.update()
            
            # 检查主窗口状态
            self._log_debug(f"主窗口状态: {self.my_window.state()}")
            self._log_debug(f"主窗口几何: {self.my_window.geometry()}")
            
            # 创建录制管理器
            self._log_debug("创建ActionRecorder...")
            recorder = ActionRecorder(self)
            self._log_debug("ActionRecorder创建完成")
            
            # 显示录制选项
            self._log_debug("调用show_record_options...")
            result = recorder.show_record_options()
            self._log_debug(f"show_record_options返回: {result}")
            
            if result:
                self.status_label.config(text="状态: 录制窗口显示成功")
                self._log_debug("录制窗口显示成功")
            else:
                self.status_label.config(text="状态: 录制窗口显示失败")
                self._log_debug("录制窗口显示失败")
                
        except Exception as e:
            error_msg = f"测试录制窗口失败: {str(e)}"
            self.status_label.config(text=f"状态: {error_msg}")
            self._log_debug(f"错误详情: {e}")
            self._log_debug(f"错误堆栈: {traceback.format_exc()}")
            messagebox.showerror("错误", error_msg)
    
    def _refresh_action_list(self):
        """模拟刷新行为列表"""
        self._log_debug("模拟刷新行为列表")
        
    def run(self):
        """运行测试"""
        self._log_debug("开始测试录制窗口显示...")
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