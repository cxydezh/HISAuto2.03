#!/usr/bin/env python3
"""
测试图像采集功能
"""

import tkinter as tk
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_image_capture():
    """测试图像采集功能"""
    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("图像采集测试")
        root.geometry("400x300")
        
        # 创建测试按钮
        def test_capture():
            try:
                from core.pic_capture import PicCapture
                from config.config_manager import ConfigManager
                
                config = ConfigManager()
                save_path = config.get_value('System', 'PatientsSource')
                
                if not save_path:
                    print("错误: 图像保存路径未配置")
                    return
                
                print(f"保存路径: {save_path}")
                
                # 创建图像采集实例
                pic_capture = PicCapture(save_path=save_path, master=root)
                
                # 执行图像采集
                print("开始图像采集...")
                pic_capture.capture_screen()
                
                # 检查是否成功选择了区域
                coordinates = pic_capture.get_image_coordinates()
                print(f"选择的坐标: {coordinates}")
                
                if coordinates[0] is not None and coordinates[1] is not None:
                    # 保存测试图像
                    if pic_capture.save_image("test_capture"):
                        print("图像采集测试成功!")
                    else:
                        print("图像保存失败")
                else:
                    print("未选择图像区域")
                    
            except Exception as e:
                print(f"图像采集测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 创建按钮
        test_btn = tk.Button(root, text="测试图像采集", command=test_capture)
        test_btn.pack(pady=20)
        
        # 创建退出按钮
        exit_btn = tk.Button(root, text="退出", command=root.quit)
        exit_btn.pack(pady=10)
        
        print("图像采集测试程序已启动")
        print("点击'测试图像采集'按钮开始测试")
        print("在截图界面中，点击并拖动鼠标选择区域，然后释放鼠标完成采集")
        print("按ESC键可以取消采集")
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        print(f"测试程序启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_capture() 