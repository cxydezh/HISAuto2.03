"""
图像采集模块的主要实现类
"""

import os
import tkinter as tk
from tkinter import messagebox
import traceback
import pyautogui
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime
import time

class PicCapture:
    def __init__(self, save_path: str, master: tk.Tk):
        """
        初始化图像采集类
        
        Args:
            save_path (str): 图像保存的根目录路径
            master (tk.Tk): 主窗口引用
        """
        self.master = master
        self.save_path = save_path
        self.screenshot = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.photo = None
        self.window = None
        self.canvas = None
        
    def capture_screen(self):
        """
        捕获全屏截图并显示在窗口中
        """
        try:
            # 隐藏主窗口
            if self.master:
                self.master.withdraw()
                self.master.update()  # 强制更新主窗口状态以确保隐藏生效
                time.sleep(0.2)  # 短暂延迟，确保窗口完全隐藏

            # 捕获全屏
            self.screenshot = pyautogui.screenshot()
            
            # 创建全屏窗口 - 使用Toplevel而不是Tk()
            self.window = tk.Toplevel(self.master)
            self.window.attributes('-fullscreen', True)
            self.window.attributes('-topmost', True)
            self.window.overrideredirect(True)
            
            # 创建画布
            self.canvas = tk.Canvas(self.window, width=self.screenshot.width, height=self.screenshot.height)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # 显示截图 - 保持对photo的引用
            self.photo = ImageTk.PhotoImage(self.screenshot)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
            # 绑定鼠标事件
            self.canvas.bind('<Button-1>', self.on_click)
            self.canvas.bind('<B1-Motion>', self.on_drag)
            self.canvas.bind('<ButtonRelease-1>', self.on_release)
            self.canvas.bind('<Escape>', self.on_escape)  # 添加ESC键退出
            
            # 显示窗口
            self.window.deiconify()
            
            # 等待窗口关闭
            self.window.wait_window()
            
        except Exception as e:
            print(f"截图捕获失败: {e}")
            print(traceback.format_exc())
            if self.master:
                self.master.deiconify()
            raise e
        
    def on_click(self, event):
        """
        鼠标点击事件处理
        """
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        """
        鼠标拖动事件处理
        """
        if self.start_x is not None and self.start_y is not None:
            # 清除之前的矩形
            self.canvas.delete("rectangle")
            # 绘制新的矩形
            self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2, tags="rectangle"
            )
            
    def on_release(self, event):
        """
        鼠标释放事件处理
        """
        self.end_x = event.x
        self.end_y = event.y
        
        # 确保坐标正确
        if self.start_x > self.end_x:
            self.start_x, self.end_x = self.end_x, self.start_x
        if self.start_y > self.end_y:
            self.start_y, self.end_y = self.end_y, self.start_y
            
        # 验证坐标是否在图像边界内
        if self.screenshot:
            # 确保坐标不超出图像边界
            self.start_x = max(0, min(self.start_x, self.screenshot.width - 1))
            self.start_y = max(0, min(self.start_y, self.screenshot.height - 1))
            self.end_x = max(0, min(self.end_x, self.screenshot.width))
            self.end_y = max(0, min(self.end_y, self.screenshot.height))
            
            # 确保选择区域有效（至少1x1像素）
            if self.end_x <= self.start_x or self.end_y <= self.start_y:
                print("警告: 选择区域太小，重置坐标")
                self.start_x = None
                self.start_y = None
                self.end_x = None
                self.end_y = None
                self.window.destroy()
                if self.master:
                    self.master.deiconify()
                return
        
        print(f"选择的区域: ({self.start_x}, {self.start_y}) -> ({self.end_x}, {self.end_y})")
        
        # 关闭窗口并恢复主窗口
        self.window.destroy()
        if self.master:
            self.master.deiconify()
            
    def on_escape(self, event):
        """
        ESC键退出事件处理
        """
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.window.destroy()
        if self.master:
            self.master.deiconify()
        
    def get_cropped_image(self) -> Image.Image:
        """
        获取裁剪后的图像
        
        Returns:
            Image.Image: 裁剪后的图像
        """
        try:
            if not self.screenshot:
                print("错误: 没有可用的截图")
                return None
                
            if (self.start_x is None or self.start_y is None or 
                self.end_x is None or self.end_y is None):
                print("错误: 坐标未设置")
                return None
            
            # 再次验证坐标边界
            start_x = max(0, min(self.start_x, self.screenshot.width - 1))
            start_y = max(0, min(self.start_y, self.screenshot.height - 1))
            end_x = max(start_x + 1, min(self.end_x, self.screenshot.width))
            end_y = max(start_y + 1, min(self.end_y, self.screenshot.height))
            
            print(f"裁剪区域: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            print(f"图像尺寸: {self.screenshot.width} x {self.screenshot.height}")
            
            # 确保选择区域有效
            if end_x <= start_x or end_y <= start_y:
                print("错误: 无效的裁剪区域")
                return None
            
            # 执行裁剪
            cropped = self.screenshot.crop((start_x, start_y, end_x, end_y))
            print(f"裁剪成功，新图像尺寸: {cropped.width} x {cropped.height}")
            return cropped
            
        except Exception as e:
            print(f"裁剪图像时发生错误: {e}")
            print(traceback.format_exc())
            return None
        
    def save_image(self, image_name: str) -> bool:
        """
        保存图像到指定位置
        
        Args:
            image_name (str): 图像名称
            
        Returns:
            bool: 是否保存成功
        """
        try:
            if not image_name:
                print("错误: 图像名称为空")
                return False
            
            # 确保保存路径存在
            if not os.path.exists(self.save_path):
                print(f"创建保存目录: {self.save_path}")
                os.makedirs(self.save_path, exist_ok=True)
            
            # 构建完整的保存路径
            save_path = os.path.join(self.save_path, f"{image_name}.png")
            print(f"保存路径: {save_path}")
            
            # 检查文件名是否已存在
            if os.path.exists(save_path):
                print(f"警告: 文件已存在: {save_path}")
                return False
            
            # 获取裁剪后的图像
            cropped_image = self.get_cropped_image()
            if not cropped_image:
                print("错误: 无法获取裁剪后的图像")
                return False
            
            # 验证裁剪后的图像
            if cropped_image.width <= 0 or cropped_image.height <= 0:
                print("错误: 裁剪后的图像尺寸无效")
                return False
            
            print(f"准备保存图像: {cropped_image.width} x {cropped_image.height}")
            
            # 保存图像
            cropped_image.save(save_path, "PNG")
            print(f"图像保存成功: {save_path}")
            return True
            
        except Exception as e:
            print(f"保存图像时发生错误: {e}")
            print(traceback.format_exc())
            return False
        
    def get_image_coordinates(self) -> tuple:
        """
        获取图像坐标
        
        Returns:
            tuple: (start_x, start_y, end_x, end_y)
        """
        return (self.start_x, self.start_y, self.end_x, self.end_y) 