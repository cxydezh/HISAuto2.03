"""
行为录制功能模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import traceback
import os
import sys
import time
import threading

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 简化导入，避免循环导入问题
try:
    from database.db_manager import DatabaseManager
    from config.config_manager import ConfigManager
    from models.actions import ActionList, ActionMouse, ActionKeyboard
    import globalvariable
    from utils.logger import Logger
except ImportError:
    class SimpleLogger:
        def __init__(self): pass
        def error(self, msg): print(f"ERROR: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
    Logger = SimpleLogger

class ActionRecorder:
    """行为录制管理器"""
    
    def __init__(self, home_tab):
        """初始化录制管理器"""
        self.home_tab = home_tab
        try:
            self.logger = Logger()
        except:
            self.logger = None
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
        
    def _log(self, level, message):
        """简化的日志记录"""
        if self.logger:
            if level == 'error':
                self.logger.error(message)
            elif level == 'info':
                self.logger.info(message)
        print(f"[{level.upper()}] {message}")
        
    def show_record_options(self):
        """显示录制选项窗口"""
        try:
            self._log('info', '开始显示录制选项窗口...')
            
            if not self.home_tab.action_group_id:
                messagebox.showwarning("警告", "请先选择行为组")
                return False
                
            self._log('info', '创建录制选项窗口...')
            
            # 创建录制选项窗口
            self.record_window = tk.Toplevel(self.home_tab.my_window)
            self.record_window.title("录制选项")
            self.record_window.geometry("400x450")
            self.record_window.resizable(False, False)
            self.record_window.transient(self.home_tab.my_window)
            self.record_window.grab_set()
            
            self._log('info', '窗口创建完成，开始添加控件...')
            
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
                self._log('info', '开始录制...')
                self.record_mode = mode_var.get()
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
            
            self._log('info', '控件添加完成，开始显示窗口...')
            
            # 强制更新窗口布局
            self.record_window.update_idletasks()
            self.record_window.update()
            
            # 确保窗口可见
            self.record_window.lift()
            self.record_window.focus_force()
            
            self._log('info', '窗口准备就绪，开始事件循环...')
            
            # 使用独立的事件循环
            self.record_window.mainloop()
            
            self._log('info', '事件循环结束')
            return True
            
        except Exception as e:
            self._log('error', f'显示录制选项窗口失败: {str(e)}')
            print(traceback.format_exc())
            return False
        
    def minimize_to_icon(self):
        """将窗口最小化为图标"""
        try:
            # 将窗口移动到右上角
            screen_width = self.record_window.winfo_screenwidth()
            icon_x = screen_width - 30
            icon_y = 50
            
            # 调整窗口大小和位置
            self.record_window.geometry(f"20x20+{icon_x}+{icon_y}")
            self.record_window.title("录制中...")
            
            # 设置窗口样式为图标
            self.record_window.overrideredirect(True)
            self.record_window.configure(bg='red')
            
            # 创建图标标签
            if hasattr(self, 'icon_label'):
                self.icon_label.destroy()
            
            self.icon_label = tk.Label(self.record_window, text="●", font=("Arial", 12), 
                                      fg="white", bg="red", cursor="hand2")
            self.icon_label.pack(expand=True, fill=tk.BOTH)
            
            # 绑定鼠标事件
            self.icon_label.bind('<Button-1>', self.restore_window)
            self.icon_label.bind('<B1-Motion>', self.on_drag)
            self.icon_label.bind('<ButtonRelease-1>', self.on_drag_release)
            
            # 绑定窗口事件
            self.record_window.bind('<Button-1>', self.on_window_click)
            self.record_window.bind('<B1-Motion>', self.on_drag)
            self.record_window.bind('<ButtonRelease-1>', self.on_drag_release)
            
            # 更新按钮状态
            self.ok_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 标记为最小化状态
            self.is_minimized = True
            
            # 开始录制
            self.start_recording_task()
            
        except Exception as e:
            self.logger.error(f"最小化窗口失败: {str(e)}")
            print(traceback.format_exc())
            
    def restore_window(self, event=None):
        """恢复窗口到原始大小"""
        try:
            # 恢复窗口样式
            self.record_window.overrideredirect(False)
            self.record_window.title("录制选项")
            self.record_window.configure(bg='SystemButtonFace')
            
            # 恢复窗口大小和位置
            self.record_window.geometry("400x450")
            
            # 居中显示
            self.record_window.update_idletasks()
            x = (self.record_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (self.record_window.winfo_screenheight() // 2) - (450 // 2)
            self.record_window.geometry(f"400x450+{x}+{y}")
            
            # 移除图标标签
            if hasattr(self, 'icon_label'):
                self.icon_label.destroy()
                delattr(self, 'icon_label')
            
            # 更新按钮状态
            self.ok_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # 标记为非最小化状态
            self.is_minimized = False
            
        except Exception as e:
            self.logger.error(f"恢复窗口失败: {str(e)}")
            print(traceback.format_exc())
            
    def on_drag(self, event):
        """处理拖拽事件"""
        if self.is_minimized:
            # 计算新位置
            new_x = self.record_window.winfo_x() + (event.x - self.drag_start_x)
            new_y = self.record_window.winfo_y() + (event.y - self.drag_start_y)
            
            # 确保不超出屏幕边界
            screen_width = self.record_window.winfo_screenwidth()
            screen_height = self.record_window.winfo_screenheight()
            
            new_x = max(0, min(new_x, screen_width - 20))
            new_y = max(0, min(new_y, screen_height - 20))
            
            # 移动窗口
            self.record_window.geometry(f"20x20+{new_x}+{new_y}")
            
    def on_drag_release(self, event):
        """处理拖拽释放事件"""
        self.is_dragging = False
        
    def on_window_click(self, event):
        """处理窗口点击事件"""
        if self.is_minimized:
            # 记录拖拽起始位置
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.is_dragging = True
            
    def cancel_recording(self):
        """取消录制"""
        if self.record_window:
            self.record_window.destroy()
            self.record_window = None
        self.home_tab.my_window.deiconify()
        
    def start_recording_task(self):
        """开始录制任务"""
        try:
            # 获取结束录制的快捷键
            config = ConfigManager()
            end_record_key = config.get_value('Shortcuts', 'endrecord')
            
            if not end_record_key:
                messagebox.showerror("错误", "未配置结束录制快捷键")
                self.home_tab.my_window.deiconify()
                return
                
            print(f"开始录制，结束快捷键: {end_record_key}")
            
            # 解析快捷键
            self.end_record_keys = self._parse_hotkey(end_record_key)
            if not self.end_record_keys:
                messagebox.showerror("错误", f"无法解析快捷键: {end_record_key}")
                self.home_tab.my_window.deiconify()
                return
            
            # 初始化录制状态
            self.recording = True
            self.recorded_events = []
            self.last_event_time = time.time()
            self.ok_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            # 获取数据库会话
            self.session = self._get_session()
            if not self.session:
                messagebox.showerror("错误", "无法获取数据库连接")
                self.home_tab.my_window.deiconify()
                return
                
            print(f"录制已开始，按 {end_record_key} 结束录制")
            
            # 启动录制逻辑
            self._start_recording()
            
        except Exception as e:
            self.logger.error(f"启动录制失败: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"启动录制失败: {str(e)}")
            self.home_tab.my_window.deiconify()
            
    def _get_session(self):
        """获取数据库会话"""
        try:
            config_manager = ConfigManager()
            db_path = config_manager.get_value('System', 'DataSource')
            encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
            
            if not db_path or not encryption_key:
                self.logger.error("数据库配置信息不完整")
                return None
                
            db_manager = DatabaseManager(db_path, encryption_key)
            db_manager.initialize()
            return db_manager.Session()
        except Exception as e:
            self.logger.error(f"获取数据库会话失败: {str(e)}")
            return None
            
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
                else:
                    if len(part) == 1:
                        keys.append(part.lower())
                    else:
                        keys.append(part.lower())
                        
            return keys
        except Exception as e:
            self.logger.error(f"解析快捷键失败: {str(e)}")
            return None
            
    def _start_recording(self):
        """启动录制"""
        try:
            self._monitor_end_key()
        except Exception as e:
            self.logger.error(f"启动录制失败: {str(e)}")
            raise e
            
    def _monitor_end_key(self):
        """监控结束录制快捷键"""
        def check_end_key():
            while self.recording:
                time.sleep(0.1)
                if self._check_hotkey_pressed():
                    self.stop_recording()
                    break
                    
        threading.Thread(target=check_end_key, daemon=True).start()
        
    def _check_hotkey_pressed(self):
        """检查快捷键是否被按下"""
        try:
            if 'alt' in self.end_record_keys and 'e' in self.end_record_keys:
                return False
            elif 'ctrl' in self.end_record_keys and 'e' in self.end_record_keys:
                return False
            elif 'f12' in self.end_record_keys:
                return False
            return False
        except Exception as e:
            self.logger.error(f"检查快捷键失败: {str(e)}")
            return False
            
    def stop_recording(self):
        """停止录制"""
        try:
            self.recording = False
            
            if self.recorded_events:
                self._save_recorded_events()
                
            if self.session:
                self.session.close()
                self.session = None
                
            if self.record_window:
                self.record_window.destroy()
                self.record_window = None
                
            self.home_tab.my_window.deiconify()
            self.home_tab._refresh_action_list()
            
            messagebox.showinfo("录制完成", f"录制已完成，共记录 {len(self.recorded_events)} 个事件")
            
        except Exception as e:
            self.logger.error(f"停止录制失败: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror("错误", f"停止录制失败: {str(e)}")
            self.home_tab.my_window.deiconify()
            
    def _save_recorded_events(self):
        """保存录制的事件到数据库"""
        try:
            if not self.recorded_events:
                return
                
            for i, event in enumerate(self.recorded_events):
                action_list = ActionList(
                    group_id=self.home_tab.action_group_id,
                    action_type=event['type'],
                    action_name=f"录制事件_{i+1}",
                    next_id=None,
                    debug_group_id=None,
                    action_note=f"自动录制的{event['type']}事件",
                    user_id=globalvariable.USER_ID,
                    department_id=globalvariable.USER_DEPARTMENT_ID,
                    created_at=datetime.now()
                )
                
                self.session.add(action_list)
                self.session.flush()
                
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
            print(f"成功保存 {len(self.recorded_events)} 个录制事件")
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"保存录制事件失败: {str(e)}")
            print(traceback.format_exc())
            raise e

def record_action(home_tab):
    """录制行为的主函数"""
    my_home_tab = home_tab
    try:
        if not my_home_tab.action_group_id:
            messagebox.showwarning("警告", "请先选择行为组")
            return False
            
        recorder = ActionRecorder(my_home_tab)
        return recorder.show_record_options()
        
    except Exception as e:
        logger = Logger()
        logger.error(f"录制行为失败: {str(e)}")
        print(traceback.format_exc())
        messagebox.showerror("错误", f"录制行为失败: {str(e)}")
        return False 