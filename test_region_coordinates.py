#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试区域坐标获取功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_region_coordinates():
    """测试区域坐标获取功能"""
    
    # 创建主窗口
    root = tk.Tk()
    root.title("区域坐标获取测试")
    root.geometry("400x300")
    
    # 创建变量
    left_top_x_var = tk.StringVar()
    left_top_y_var = tk.StringVar()
    right_bottom_x_var = tk.StringVar()
    right_bottom_y_var = tk.StringVar()
    
    # 创建界面
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(frame, text="区域坐标获取测试", font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 20))
    
    # 坐标显示区域
    coord_frame = ttk.LabelFrame(frame, text="坐标信息", padding="10")
    coord_frame.pack(fill=tk.X, pady=(0, 20))
    
    # 左上角坐标
    ttk.Label(coord_frame, text="左上角X:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(coord_frame, textvariable=left_top_x_var, state="readonly", width=10).grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(coord_frame, text="左上角Y:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(coord_frame, textvariable=left_top_y_var, state="readonly", width=10).grid(row=0, column=3, padx=5, pady=5)
    
    # 右下角坐标
    ttk.Label(coord_frame, text="右下角X:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(coord_frame, textvariable=right_bottom_x_var, state="readonly", width=10).grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(coord_frame, text="右下角Y:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(coord_frame, textvariable=right_bottom_y_var, state="readonly", width=10).grid(row=1, column=3, padx=5, pady=5)
    
    # 按钮区域
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20)
    
    def get_coordinates():
        """获取区域坐标"""
        try:
            from utils.region_coordinates import get_region_coordinates
            
            success = get_region_coordinates(
                root,
                left_top_x_var,
                left_top_y_var,
                right_bottom_x_var,
                right_bottom_y_var
            )
            
            if success:
                messagebox.showinfo("成功", "区域坐标获取成功！")
            else:
                messagebox.showwarning("警告", "区域坐标获取失败！")
                
        except Exception as e:
            messagebox.showerror("错误", f"获取区域坐标时发生异常: {str(e)}")
            print(f"异常详情: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_coordinates():
        """清空坐标"""
        left_top_x_var.set("")
        left_top_y_var.set("")
        right_bottom_x_var.set("")
        right_bottom_y_var.set("")
    
    # 获取坐标按钮
    get_btn = ttk.Button(button_frame, text="获取区域坐标", command=get_coordinates)
    get_btn.pack(side=tk.LEFT, padx=10)
    
    # 清空坐标按钮
    clear_btn = ttk.Button(button_frame, text="清空坐标", command=clear_coordinates)
    clear_btn.pack(side=tk.LEFT, padx=10)
    
    # 说明文本
    info_text = """
使用说明：
1. 点击"获取区域坐标"按钮
2. 主窗口会隐藏，显示全屏截图
3. 用鼠标拖拽选择矩形区域
4. 释放鼠标完成选择
5. 坐标会自动填充到输入框中
6. 按ESC键可以取消选择
    """
    
    info_label = ttk.Label(frame, text=info_text, justify=tk.LEFT, font=("Arial", 9))
    info_label.pack(pady=20)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    test_region_coordinates() 