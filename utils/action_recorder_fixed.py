"""
修复版行为录制功能模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import traceback
import os
import sys
import time
import threading
import keyboard
import mouse
from config.config_manager import ConfigManager
from database.db_manager import DatabaseManager
from models.actions import ActionList, ActionMouse, ActionKeyboard
import globalvariable

class ActionRecorder:
    """行为录制管理器"""
    
    def __init__(self, home_tab):
        """初始化录制管理器"""
        self.home_tab = home_tab
        self.recording = False
        self.record_window = None
        self.recorded_events = []
        self.last_event_time = None
        self.record_mode = "全部"
        self.session = None
        self.end_record_keys = None
        
        # 拖拽相关变量
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.is_minimized = False
        self.icon_window = None
        
        # 事件录制相关
        self.core_recorder = None
        self.recording_thread = None
        
    def show_record_options(self):
        """显示录制选项窗口"""
        try:
            print("开始显示录制选项窗口...")
            
            if not self.home_tab.action_group_id:
                messagebox.showwarning("警告", "请先选择行为组")
                return False
                
            print("创建录制选项窗口...")
            
            # 隐藏主窗口
            if self.home_tab and self.home_tab.my_window:
                self.home_tab.my_window.withdraw()
                print("主窗口已隐藏")
            
            # 创建录制选项窗口
            self.record_window = tk.Toplevel()
            self.record_window.title("录制选项")
            self.record_window.geometry("400x450")
            self.record_window.resizable(False, False)
            self.record_window.grab_set()
            
            # 设置窗口位置在屏幕中央
            self.record_window.update_idletasks()
            x = (self.record_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (self.record_window.winfo_screenheight() // 2) - (450 // 2)
            self.record_window.geometry(f"400x450+{x}+{y}")
            
            print("窗口创建完成，开始添加控件...")
            
            # 创建主框架
            main_frame = ttk.Frame(self.record_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = ttk.Label(main_frame, text="选择录制内容", font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # 说明文本
            info_label = ttk.Label(main_frame, text="请选择要录制的鼠标事件类型：", font=("Arial", 10))
            info_label.pack(pady=(0, 15))
            
            # 录制模式选择
            mode_var = tk.StringVar(value="全部")
            
            # 单选按钮框架
            radio_frame = ttk.Frame(main_frame)
            radio_frame.pack(pady=10)
            
            ttk.Radiobutton(radio_frame, text="单击", variable=mode_var, value="单击").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(radio_frame, text="按下弹起", variable=mode_var, value="按下弹起").pack(anchor=tk.W, pady=5)
            ttk.Radiobutton(radio_frame, text="全部", variable=mode_var, value="全部").pack(anchor=tk.W, pady=5)
            
            # 说明文本
            desc_frame = ttk.Frame(main_frame)
            desc_frame.pack(pady=20, fill=tk.X)
            
            desc_text = """
说明：
• 单击：仅录制鼠标单击事件
• 按下弹起：仅录制鼠标按下和释放事件
• 全部：录制所有鼠标事件
            """
            desc_label = ttk.Label(desc_frame, text=desc_text, font=("Arial", 9), justify=tk.LEFT)
            desc_label.pack()
            
            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=20)
            
            def start_recording():
                """开始录制"""
                print("开始录制...")
                self.record_mode = mode_var.get()
                self.record_window.quit()  # 退出事件循环
                self.record_window.destroy()
                self.record_window = None
                self.minimize_to_icon()
                
            def stop_recording():
                """停止录制"""
                self.stop_recording()
                
            # 确定按钮
            self.ok_button = ttk.Button(button_frame, text="确认", command=start_recording, state=tk.NORMAL)
            self.ok_button.pack(side=tk.LEFT, padx=10)
            
            # 终止按钮
            self.stop_button = ttk.Button(button_frame, text="终止", command=stop_recording, state=tk.DISABLED)
            self.stop_button.pack(side=tk.LEFT, padx=10)
            
            # 绑定回车键和ESC键
            self.record_window.bind('<Return>', lambda e: start_recording())
            self.record_window.bind('<Escape>', lambda e: self.cancel_recording())
            
            # 设置焦点
            self.ok_button.focus_set()
            
            print("控件添加完成，开始显示窗口...")
            
            # 强制更新窗口布局
            self.record_window.update_idletasks()
            self.record_window.update()
            
            # 确保窗口可见
            self.record_window.lift()
            self.record_window.focus_force()
            
            print("窗口准备就绪，开始事件循环...")
            
            # 使用独立的事件循环
            self.record_window.mainloop()
            
            print("事件循环结束")
            return True
            
        except Exception as e:
            print(f'显示录制选项窗口失败: {str(e)}')
            print(traceback.format_exc())
            return False
        
    def minimize_to_icon(self):
        """将窗口最小化为图标"""
        try:
            print("开始最小化到图标...")
            
            # 创建图标窗口
            self.icon_window = tk.Toplevel()
            self.icon_window.title("录制中")
            self.icon_window.geometry("20x20")
            self.icon_window.resizable(False, False)
            self.icon_window.overrideredirect(True)  # 移除标题栏
            
            # 设置窗口位置在屏幕右上角
            screen_width = self.icon_window.winfo_screenwidth()
            self.icon_window.geometry(f"20x20+{screen_width-30}+10")
            
            # 创建图标标签
            icon_label = tk.Label(self.icon_window, text="●", fg="red", bg="white", font=("Arial", 12, "bold"))
            icon_label.pack(fill=tk.BOTH, expand=True)
            
            # 绑定双击事件 - 恢复窗口
            icon_label.bind('<Double-Button-1>', self.restore_window)
            
            # 绑定拖拽事件
            icon_label.bind('<Button-1>', self.start_drag)
            icon_label.bind('<B1-Motion>', self.on_drag)
            icon_label.bind('<ButtonRelease-1>', self.stop_drag)
            
            # 忽略其他鼠标事件
            self.icon_window.bind('<Button-2>', lambda e: 'break')  # 中键
            self.icon_window.bind('<Button-3>', lambda e: 'break')  # 右键
            
            self.is_minimized = True
            print("图标窗口创建完成")
            
            # 开始录制事件
            self.start_event_recording()
            
        except Exception as e:
            print(f"最小化到图标失败: {str(e)}")
            print(traceback.format_exc())
    
    def start_drag(self, event):
        """开始拖拽"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = True
    
    def on_drag(self, event):
        """拖拽中"""
        if self.is_dragging and self.icon_window:
            x = self.icon_window.winfo_x() + (event.x - self.drag_start_x)
            y = self.icon_window.winfo_y() + (event.y - self.drag_start_y)
            self.icon_window.geometry(f"20x20+{x}+{y}")
    
    def stop_drag(self, event):
        """停止拖拽"""
        self.is_dragging = False
    
    def restore_window(self, event=None):
        """恢复录制窗口"""
        try:
            print("恢复录制窗口...")
            
            if self.icon_window:
                self.icon_window.destroy()
                self.icon_window = None
                self.is_minimized = False
            
            # 重新显示录制选项窗口，并确保按钮状态正确
            self.show_record_options_with_state()
            
        except Exception as e:
            print(f"恢复窗口失败: {str(e)}")
            print(traceback.format_exc())
    
    def show_record_options_with_state(self):
        """显示录制选项窗口（带状态）"""
        try:
            print("开始显示录制选项窗口（带状态）...")
            
            if not self.home_tab.action_group_id:
                messagebox.showwarning("警告", "请先选择行为组")
                return False
                
            print("创建录制选项窗口...")
            
            # 隐藏主窗口
            if self.home_tab and self.home_tab.my_window:
                self.home_tab.my_window.withdraw()
                print("主窗口已隐藏")
            
            # 创建录制选项窗口
            self.record_window = tk.Toplevel()
            self.record_window.title("录制选项")
            self.record_window.geometry("400x450")
            self.record_window.resizable(False, False)
            self.record_window.grab_set()
            
            # 设置窗口位置在屏幕中央
            self.record_window.update_idletasks()
            x = (self.record_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (self.record_window.winfo_screenheight() // 2) - (450 // 2)
            self.record_window.geometry(f"400x450+{x}+{y}")
            
            print("窗口创建完成，开始添加控件...")
            
            # 创建主框架
            main_frame = ttk.Frame(self.record_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = ttk.Label(main_frame, text="录制进行中", font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # 说明文本
            info_label = ttk.Label(main_frame, text="录制正在进行中，请选择操作：", font=("Arial", 10))
            info_label.pack(pady=(0, 15))
            
            # 录制状态显示
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(pady=10)
            
            status_label = ttk.Label(status_frame, text=f"已录制事件数: {len(self.recorded_events)}", font=("Arial", 10))
            status_label.pack()
            
            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=20)
            
            def continue_recording():
                """继续录制"""
                print("继续录制...")
                self.record_window.quit()  # 退出事件循环
                self.record_window.destroy()
                self.record_window = None
                self.minimize_to_icon()
                
            def stop_recording():
                """停止录制"""
                self.stop_recording()
                
            # 继续按钮
            self.ok_button = ttk.Button(button_frame, text="继续录制", command=continue_recording, state=tk.NORMAL)
            self.ok_button.pack(side=tk.LEFT, padx=10)
            
            # 终止按钮
            self.stop_button = ttk.Button(button_frame, text="终止录制", command=stop_recording, state=tk.NORMAL)
            self.stop_button.pack(side=tk.LEFT, padx=10)
            
            # 绑定回车键和ESC键
            self.record_window.bind('<Return>', lambda e: continue_recording())
            self.record_window.bind('<Escape>', lambda e: self.cancel_recording())
            
            # 设置焦点
            self.ok_button.focus_set()
            
            print("控件添加完成，开始显示窗口...")
            
            # 强制更新窗口布局
            self.record_window.update_idletasks()
            self.record_window.update()
            
            # 确保窗口可见
            self.record_window.lift()
            self.record_window.focus_force()
            
            print("窗口准备就绪，开始事件循环...")
            
            # 使用独立的事件循环
            self.record_window.mainloop()
            
            print("事件循环结束")
            return True
            
        except Exception as e:
            print(f'显示录制选项窗口失败: {str(e)}')
            print(traceback.format_exc())
            return False
    
    def cancel_recording(self):
        """取消录制"""
        if self.record_window:
            self.record_window.destroy()
            self.record_window = None
        if self.icon_window:
            self.icon_window.destroy()
            self.icon_window = None
        if self.home_tab and self.home_tab.my_window:
            self.home_tab.my_window.deiconify()
            
    def start_event_recording(self):
        """开始事件录制"""
        try:
            print("开始事件录制...")
            
            # 获取配置的结束录制快捷键
            config = ConfigManager()
            end_record_key = config.get_value('Shortcuts', 'endrecord', 'Esc')
            print(f"结束录制快捷键: {end_record_key}")
            
            # 初始化录制状态
            self.recording = True
            self.recorded_events = []
            self.last_event_time = time.time()
            
            # 获取数据库会话
            self.session = self._get_session()
            if not self.session:
                messagebox.showerror("错误", "无法获取数据库连接")
                self.cancel_recording()
                return
            
            # 启动录制线程
            self.recording_thread = threading.Thread(target=self._recording_worker, args=(end_record_key,), daemon=True)
            self.recording_thread.start()
            
            print("事件录制已启动")
            
        except Exception as e:
            print(f"启动事件录制失败: {str(e)}")
            print(traceback.format_exc())
            self.cancel_recording()
    
    def _get_session(self):
        """获取数据库会话"""
        try:
            config_manager = ConfigManager()
            db_path = config_manager.get_value('System', 'datasource')
            encryption_key = config_manager.get_value('Security', 'dbencryptionkey')
            
            if not db_path or not encryption_key:
                print("数据库配置信息不完整")
                return None
                
            db_manager = DatabaseManager(db_path, encryption_key)
            db_manager.initialize()
            return db_manager.Session()
        except Exception as e:
            print(f"获取数据库会话失败: {str(e)}")
            return None
    
    def _recording_worker(self, end_record_key):
        """录制工作线程"""
        try:
            # 设置录制选项
            press = self.record_mode in ["按下弹起", "全部"]
            release = self.record_mode in ["按下弹起", "全部"]
            click = self.record_mode in ["单击", "全部"]
            
            # 启动键盘和鼠标监听
            keyboard.on_press(self._on_key_press)
            keyboard.on_release(self._on_key_release)
            
            if click:
                mouse.on_click(self._on_mouse_click)
            if press:
                mouse.on_button(self._on_mouse_press, args=('left',))
                mouse.on_button(self._on_mouse_press, args=('right',))
                mouse.on_button(self._on_mouse_press, args=('middle',))
            if release:
                mouse.on_button(self._on_mouse_release, args=('left',))
                mouse.on_button(self._on_mouse_release, args=('right',))
                mouse.on_button(self._on_mouse_release, args=('middle',))
            
            # 监听结束录制快捷键
            self._monitor_end_key(end_record_key)
            
        except Exception as e:
            print(f"录制工作线程失败: {str(e)}")
            print(traceback.format_exc())
            self.stop_recording()
    
    def _monitor_end_key(self, end_record_key):
        """监控结束录制快捷键"""
        try:
            # 解析快捷键
            keys = self._parse_hotkey(end_record_key)
            if not keys:
                print(f"无法解析快捷键: {end_record_key}")
                return
            
            print(f"监控快捷键: {keys}")
            
            while self.recording:
                time.sleep(0.1)
                if self._check_hotkey_pressed(keys):
                    print("检测到结束录制快捷键")
                    self.stop_recording()
                    break
                    
        except Exception as e:
            print(f"监控快捷键失败: {str(e)}")
    
    def _parse_hotkey(self, hotkey_str):
        """解析快捷键字符串"""
        try:
            keys = []
            parts = hotkey_str.upper().split('+')
            
            for part in parts:
                part = part.strip()
                if part == 'ALT':
                    keys.append('alt')
                elif part == 'CTRL':
                    keys.append('ctrl')
                elif part == 'SHIFT':
                    keys.append('shift')
                elif part == 'WIN':
                    keys.append('win')
                elif part == 'ESC':
                    keys.append('esc')
                elif part == 'F12':
                    keys.append('f12')
                else:
                    if len(part) == 1:
                        keys.append(part.lower())
                    else:
                        keys.append(part.lower())
                        
            return keys
        except Exception as e:
            print(f"解析快捷键失败: {str(e)}")
            return None
    
    def _check_hotkey_pressed(self, keys):
        """检查快捷键是否被按下"""
        try:
            # 检查修饰键
            modifiers = ['alt', 'ctrl', 'shift', 'win']
            main_keys = [k for k in keys if k not in modifiers]
            mod_keys = [k for k in keys if k in modifiers]
            
            # 检查修饰键状态
            for mod in mod_keys:
                if mod == 'alt' and not keyboard.is_pressed('alt'):
                    return False
                elif mod == 'ctrl' and not keyboard.is_pressed('ctrl'):
                    return False
                elif mod == 'shift' and not keyboard.is_pressed('shift'):
                    return False
                elif mod == 'win' and not keyboard.is_pressed('win'):
                    return False
            
            # 检查主键状态
            for key in main_keys:
                if keyboard.is_pressed(key):
                    return True
            
            return False
            
        except Exception as e:
            print(f"检查快捷键失败: {str(e)}")
            return False
    
    def _on_key_press(self, event):
        """键盘按下事件处理"""
        if not self.recording:
            return
        
        current_time = time.time()
        time_diff = current_time - self.last_event_time
        
        event_data = {
            'type': 'keyboard',
            'action_code': 1,  # 按下
            'key_value': event.name,
            'time_diff': time_diff,
            'timestamp': datetime.now()
        }
        
        self.recorded_events.append(event_data)
        self.last_event_time = current_time
        print(f"记录键盘按下事件: {event.name}")
    
    def _on_key_release(self, event):
        """键盘释放事件处理"""
        if not self.recording:
            return
        
        current_time = time.time()
        time_diff = current_time - self.last_event_time
        
        event_data = {
            'type': 'keyboard',
            'action_code': 2,  # 释放
            'key_value': event.name,
            'time_diff': time_diff,
            'timestamp': datetime.now()
        }
        
        self.recorded_events.append(event_data)
        self.last_event_time = current_time
        print(f"记录键盘释放事件: {event.name}")
    
    def _on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if not self.recording:
            return
        
        # 只在按下时记录单击
        if not pressed:
            return
        
        current_time = time.time()
        time_diff = current_time - self.last_event_time
        
        # 鼠标按钮编码
        button_codes = {
            'left': 1,    # 左键单击
            'right': 2,   # 右键单击
            'middle': 3   # 中键单击
        }
        
        event_data = {
            'type': 'mouse',
            'action_code': button_codes.get(button, 1),
            'x': x,
            'y': y,
            'mouse_size': 1,
            'time_diff': time_diff,
            'timestamp': datetime.now()
        }
        
        self.recorded_events.append(event_data)
        self.last_event_time = current_time
        print(f"记录鼠标点击事件: {button} at ({x}, {y})")
    
    def _on_mouse_press(self, button):
        """鼠标按下事件处理"""
        if not self.recording:
            return
        
        current_time = time.time()
        time_diff = current_time - self.last_event_time
        x, y = mouse.get_position()
        
        # 鼠标按钮编码
        button_codes = {
            'left': 4,    # 左键按下
            'right': 6,   # 右键按下
            'middle': 8   # 中键按下
        }
        
        event_data = {
            'type': 'mouse',
            'action_code': button_codes.get(button, 4),
            'x': x,
            'y': y,
            'mouse_size': 1,
            'time_diff': time_diff,
            'timestamp': datetime.now()
        }
        
        self.recorded_events.append(event_data)
        self.last_event_time = current_time
        print(f"记录鼠标按下事件: {button} at ({x}, {y})")
    
    def _on_mouse_release(self, button):
        """鼠标释放事件处理"""
        if not self.recording:
            return
        
        current_time = time.time()
        time_diff = current_time - self.last_event_time
        x, y = mouse.get_position()
        
        # 鼠标按钮编码
        button_codes = {
            'left': 5,    # 左键释放
            'right': 7,   # 右键释放
            'middle': 9   # 中键释放
        }
        
        event_data = {
            'type': 'mouse',
            'action_code': button_codes.get(button, 5),
            'x': x,
            'y': y,
            'mouse_size': 1,
            'time_diff': time_diff,
            'timestamp': datetime.now()
        }
        
        self.recorded_events.append(event_data)
        self.last_event_time = current_time
        print(f"记录鼠标释放事件: {button} at ({x}, {y})")
    
    def stop_recording(self):
        """停止录制"""
        try:
            print("停止录制...")
            self.recording = False
            
            # 移除键盘和鼠标监听
            keyboard.unhook_all()
            mouse.unhook_all()
            
            # 保存录制的事件到数据库
            if self.recorded_events:
                self._save_recorded_events()
            
            # 关闭数据库会话
            if self.session:
                self.session.close()
                self.session = None
            
            # 关闭图标窗口
            if self.icon_window:
                self.icon_window.destroy()
                self.icon_window = None
            
            # 恢复主窗口
            if self.home_tab and self.home_tab.my_window:
                self.home_tab.my_window.deiconify()
            
            # 刷新动作列表
            if hasattr(self.home_tab, '_refresh_action_list'):
                self.home_tab._refresh_action_list()
            
            messagebox.showinfo("录制完成", f"录制已完成，共记录 {len(self.recorded_events)} 个事件")
            
        except Exception as e:
            print(f"停止录制失败: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"停止录制失败: {str(e)}")
            if self.home_tab and self.home_tab.my_window:
                self.home_tab.my_window.deiconify()
    
    def _save_recorded_events(self):
        """保存录制的事件到数据库"""
        try:
            if not self.recorded_events:
                return
            
            print(f"开始保存 {len(self.recorded_events)} 个录制事件...")
            
            for i, event in enumerate(self.recorded_events):
                # 创建动作列表记录
                action_list = ActionList(
                    group_id=self.home_tab.action_group_id,
                    action_type=event['type'],
                    action_name=f"录制事件_{i+1}",
                    next_id=None,
                    debug_group_id=None,
                    action_note=f"自动录制的{event['type']}事件",
                    user_id=globalvariable.USER_ID,
                    department_id=globalvariable.USER_DEPARTMENT_ID,
                    created_at=event['timestamp']
                )
                
                self.session.add(action_list)
                self.session.flush()  # 获取ID
                
                # 根据事件类型创建详细记录
                if event['type'] == 'mouse':
                    mouse_detail = ActionMouse(
                        mouse_action=event['action_code'],
                        x=event['x'],
                        y=event['y'],
                        mouse_size=event['mouse_size'],
                        time_diff=event['time_diff'],
                        action_list_id=action_list.id
                    )
                    self.session.add(mouse_detail)
                    
                elif event['type'] == 'keyboard':
                    keyboard_detail = ActionKeyboard(
                        keyboard_type=event['action_code'],
                        keyboard_value=event['key_value'],
                        time_diff=event['time_diff'],
                        action_list_id=action_list.id
                    )
                    self.session.add(keyboard_detail)
            
            self.session.commit()
            print(f"成功保存 {len(self.recorded_events)} 个录制事件到数据库")
            
        except Exception as e:
            self.session.rollback()
            print(f"保存录制事件失败: {str(e)}")
            print(traceback.format_exc())
            raise e

def record_action(home_tab):
    """录制行为的主函数"""
    try:
        if not home_tab.action_group_id:
            messagebox.showwarning("警告", "请先选择行为组")
            return False
            
        recorder = ActionRecorder(home_tab)
        return recorder.show_record_options()
        
    except Exception as e:
        print(f"录制行为失败: {str(e)}")
        print(traceback.format_exc())
        messagebox.showerror("错误", f"录制行为失败: {str(e)}")
        return False 