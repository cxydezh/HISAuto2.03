"""
区域坐标获取功能模块
避免循环导入问题，提供独立的区域坐标获取功能
"""

import tkinter as tk
from tkinter import messagebox
import traceback
import tempfile
import shutil
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_region_coordinates(master, left_top_x_var, left_top_y_var, right_bottom_x_var, right_bottom_y_var):
    """
    获取屏幕矩形区域坐标
    
    Args:
        master: 主窗口引用
        left_top_x_var: 左上角X坐标变量
        left_top_y_var: 左上角Y坐标变量  
        right_bottom_x_var: 右下角X坐标变量
        right_bottom_y_var: 右下角Y坐标变量
        
    Returns:
        bool: 是否成功获取坐标
    """
    try:
        # 创建图像采集实例，但不保存图像，只获取坐标
        from core.pic_capture import PicCapture
        
        # 创建临时保存路径
        temp_dir = tempfile.mkdtemp()
        
        # 创建图像采集实例
        pic_capture = PicCapture(save_path=temp_dir, master=master)
        
        # 执行图像采集（用户选择区域）
        print("开始选择区域...")
        pic_capture.capture_screen()
        
        # 获取选择的坐标
        coordinates = pic_capture.get_image_coordinates()
        print(f"选择的坐标: {coordinates}")
        
        # 检查是否成功选择了区域
        if not coordinates[0] or not coordinates[1] or not coordinates[2] or not coordinates[3]:
            print("未选择有效区域")
            return False
            
        # 提取坐标值
        start_x, start_y, end_x, end_y = coordinates
        
        # 确保坐标正确（左上角到右下角）
        left_x = min(start_x, end_x)
        left_y = min(start_y, end_y)
        right_x = max(start_x, end_x)
        right_y = max(start_y, end_y)
        
        # 填充到控件变量中
        left_top_x_var.set(str(left_x))
        left_top_y_var.set(str(left_y))
        right_bottom_x_var.set(str(right_x))
        right_bottom_y_var.set(str(right_y))
        
        print(f"坐标已填充: 左上角({left_x}, {left_y}), 右下角({right_x}, {right_y})")
        
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"清理临时目录失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"获取区域坐标失败: {str(e)}")
        print(traceback.format_exc())
        messagebox.showerror("错误", f"获取区域坐标失败: {str(e)}")
        return False

def get_debug_region_coordinates(master, left_top_x_var, left_top_y_var, right_bottom_x_var, right_bottom_y_var):
    """
    获取调试面板屏幕矩形区域坐标
    
    Args:
        master: 主窗口引用
        left_top_x_var: 左上角X坐标变量
        left_top_y_var: 左上角Y坐标变量  
        right_bottom_x_var: 右下角X坐标变量
        right_bottom_y_var: 右下角Y坐标变量
        
    Returns:
        bool: 是否成功获取坐标
    """
    try:
        # 创建图像采集实例，但不保存图像，只获取坐标
        from core.pic_capture import PicCapture
        
        # 创建临时保存路径
        temp_dir = tempfile.mkdtemp()
        
        # 创建图像采集实例
        pic_capture = PicCapture(save_path=temp_dir, master=master)
        
        # 执行图像采集（用户选择区域）
        print("开始选择调试区域...")
        pic_capture.capture_screen()
        
        # 获取选择的坐标
        coordinates = pic_capture.get_image_coordinates()
        print(f"选择的调试坐标: {coordinates}")
        
        # 检查是否成功选择了区域
        if not coordinates[0] or not coordinates[1] or not coordinates[2] or not coordinates[3]:
            print("未选择有效调试区域")
            return False
            
        # 提取坐标值
        start_x, start_y, end_x, end_y = coordinates
        
        # 确保坐标正确（左上角到右下角）
        left_x = min(start_x, end_x)
        left_y = min(start_y, end_y)
        right_x = max(start_x, end_x)
        right_y = max(start_y, end_y)
        
        # 填充到控件变量中
        left_top_x_var.set(str(left_x))
        left_top_y_var.set(str(left_y))
        right_bottom_x_var.set(str(right_x))
        right_bottom_y_var.set(str(right_y))
        
        print(f"调试坐标已填充: 左上角({left_x}, {left_y}), 右下角({right_x}, {right_y})")
        
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"清理临时目录失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"获取调试区域坐标失败: {str(e)}")
        print(traceback.format_exc())
        messagebox.showerror("错误", f"获取调试区域坐标失败: {str(e)}")
        return False 