import os
import tkinter as tk
from PIL import ImageGrab, Image
from datetime import datetime

class ScreenshotTool:
    def __init__(self):
        self.root = None
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.selection_rect = None
        self.screenshot = None
        self.save_path = None
        self.name = None
        
    def capture(self, save_path, name):
        """执行截图操作
        
        Args:
            save_path (str): 保存路径
            name (str): 图片名称
        """
        self.save_path = save_path
        self.name = name
        
        # 确保保存路径存在
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        # 创建全屏透明窗口
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True, '-alpha', 0.3)
        self.root.configure(bg='grey')
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 创建画布
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height)
        self.canvas.pack()
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_move)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.root.bind('<Escape>', self.cancel_capture)
        
        # 获取屏幕截图
        self.screenshot = ImageGrab.grab()
        
        # 显示窗口
        self.root.mainloop()
        
    def on_mouse_down(self, event):
        """鼠标按下事件处理"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 创建选择框
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
        
    def on_mouse_move(self, event):
        """鼠标移动事件处理"""
        if self.selection_rect:
            self.current_x = event.x
            self.current_y = event.y
            self.canvas.coords(
                self.selection_rect,
                self.start_x, self.start_y,
                self.current_x, self.current_y
            )
            
    def on_mouse_up(self, event):
        """鼠标释放事件处理"""
        if self.selection_rect:
            # 获取选择区域
            x1 = min(self.start_x, self.current_x)
            y1 = min(self.start_y, self.current_y)
            x2 = max(self.start_x, self.current_x)
            y2 = max(self.start_y, self.current_y)
            
            # 裁剪图片
            cropped = self.screenshot.crop((x1, y1, x2, y2))
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.name}_{timestamp}.png"
            filepath = os.path.join(self.save_path, filename)
            
            # 保存图片
            cropped.save(filepath)
            
            # 销毁窗口
            self.root.destroy()
            
    def cancel_capture(self, event):
        """取消截图"""
        self.root.destroy() 