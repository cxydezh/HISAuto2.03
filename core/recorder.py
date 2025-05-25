import time
import pyautogui
import keyboard
import mouse
from typing import Optional, Dict, Any, List, Set, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from models.actions import (
    ActionMouse, ActionKeyboard, ActionCodeTxt, ActionPrintscreen,
    ActionAI, ActionFunction, ActionClass, ActionList
)
from utils.logs import log_manager

class ActionRecorder:
    """行为录制器"""
    
    # 鼠标事件编码
    MOUSE_LEFT_CLICK = 1      # 左键单击
    MOUSE_RIGHT_CLICK = 2     # 右键单击
    MOUSE_MIDDLE_CLICK = 3    # 中键单击
    MOUSE_LEFT_PRESS = 4      # 左键按下
    MOUSE_LEFT_RELEASE = 5    # 左键释放
    MOUSE_RIGHT_PRESS = 6     # 右键按下
    MOUSE_RIGHT_RELEASE = 7   # 右键释放
    MOUSE_MIDDLE_PRESS = 8    # 中键按下
    MOUSE_MIDDLE_RELEASE = 9  # 中键释放
    MOUSE_MOVE = 0           # 鼠标移动
    MOUSE_SCROLL = 10        # 鼠标滚动
    
    def __init__(self, session: Session):
        """初始化录制器
        
        Args:
            session: 数据库会话
        """
        self.session = session
        self.is_recording = False
        self.last_action_time = 0
        self.current_action_list: List[Dict[str, Any]] = []
        self.current_action_type: Optional[str] = None
        self.current_action_data: Dict[str, Any] = {}
        
        # 录制行为选择
        self.record_mouse_press = True  # 是否录制鼠标按下
        self.record_mouse_release = True  # 是否录制鼠标释放
        self.record_mouse_click = True  # 是否录制鼠标点击
        self.record_mouse_move = False  # 是否录制鼠标移动
        
        # 移动事件采样参数
        self.move_sample_interval = 0.1  # 移动事件采样间隔(秒)
        self.last_move_time = 0  # 上次移动事件时间
        
        # 鼠标事件监听器
        self.mouse_listeners = {
            'press': None,
            'release': None,
            'click': None,
            'move': None,
            'scroll': None
        }
        
    def set_recording_options(self, press: bool = True, release: bool = True,
                            click: bool = True, move: bool = False,
                            move_sample_interval: float = 0.1):
        """设置录制选项
        
        Args:
            press: 是否录制鼠标按下
            release: 是否录制鼠标释放
            click: 是否录制鼠标点击
            move: 是否录制鼠标移动
            move_sample_interval: 移动事件采样间隔(秒)
        """
        self.record_mouse_press = press
        self.record_mouse_release = release
        self.record_mouse_click = click
        self.record_mouse_move = move
        self.move_sample_interval = move_sample_interval
        
    def start_recording(self) -> bool:
        """开始录制
        
        Returns:
            bool: 是否成功
        """
        if self.is_recording:
            return False
            
        self.is_recording = True
        self.last_action_time = time.time()
        self.last_move_time = time.time()
        self.current_action_list = []
        self.current_action_type = None
        self.current_action_data = {}
        
        # 设置键盘监听
        keyboard.on_press(self._on_key_press)
        keyboard.on_release(self._on_key_release)
        
        # 设置鼠标监听
        if self.record_mouse_press:
            self.mouse_listeners['press'] = mouse.on_button(self._on_mouse_press, args=('left',))
            self.mouse_listeners['press'] = mouse.on_button(self._on_mouse_press, args=('right',))
            self.mouse_listeners['press'] = mouse.on_button(self._on_mouse_press, args=('middle',))
        if self.record_mouse_release:
            self.mouse_listeners['release'] = mouse.on_button(self._on_mouse_release, args=('left',))
            self.mouse_listeners['release'] = mouse.on_button(self._on_mouse_release, args=('right',))
            self.mouse_listeners['release'] = mouse.on_button(self._on_mouse_release, args=('middle',))
        if self.record_mouse_click:
            self.mouse_listeners['click'] = mouse.on_click(self._on_mouse_click)
        if self.record_mouse_move:
            self.mouse_listeners['move'] = mouse.on_move(self._on_mouse_move)
            
        # 设置鼠标滚轮监听
        self.mouse_listeners['scroll'] = mouse.on_scroll(self._on_mouse_scroll)
        
        log_manager.log_system("info", "开始录制行为")
        return True
        
    def stop_recording(self) -> List[Dict[str, Any]]:
        """停止录制
        
        Returns:
            List[Dict[str, Any]]: 录制的行为列表
        """
        if not self.is_recording:
            return []
            
        self.is_recording = False
        
        # 移除键盘监听
        keyboard.unhook_all()
        
        # 移除鼠标监听
        for listener in self.mouse_listeners.values():
            if listener:
                mouse.unhook(listener)
        
        # 保存最后一个动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        log_manager.log_system("info", "停止录制行为")
        return self.current_action_list
        
    def _on_key_press(self, event):
        """键盘按下事件处理
        
        Args:
            event: 键盘事件
        """
        if not self.is_recording:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_action_time
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的键盘动作
        self.current_action_type = "keyboard"
        self.current_action_data = {
            "keyboard_type": 1,  # 按下
            "keyboard_value": event.name,
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        
    def _on_key_release(self, event):
        """键盘释放事件处理
        
        Args:
            event: 键盘事件
        """
        if not self.is_recording:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_action_time
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的键盘动作
        self.current_action_type = "keyboard"
        self.current_action_data = {
            "keyboard_type": 2,  # 释放
            "keyboard_value": event.name,
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        
    def _on_mouse_press(self, button: str):
        """鼠标按下事件处理
        
        Args:
            button: 鼠标按钮
        """
        if not self.is_recording or not self.record_mouse_press:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_action_time
        x, y = self._get_mouse_position()
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的鼠标动作
        self.current_action_type = "mouse"
        self.current_action_data = {
            "mouse_action": {
                "left": 4,    # 左键按下
                "right": 6,   # 右键按下
                "middle": 8   # 中键按下
            }.get(button, 4),
            "x": x,
            "y": y,
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        
    def _on_mouse_release(self, button: str):
        """鼠标释放事件处理
        
        Args:
            button: 鼠标按钮
        """
        if not self.is_recording or not self.record_mouse_release:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_action_time
        x, y = self._get_mouse_position()
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的鼠标动作
        self.current_action_type = "mouse"
        self.current_action_data = {
            "mouse_action": {
                "left": 5,    # 左键释放
                "right": 7,   # 右键释放
                "middle": 9   # 中键释放
            }.get(button, 5),
            "x": x,
            "y": y,
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        
    def _on_mouse_click(self, x: int, y: int, button: str, pressed: bool):
        """鼠标点击事件处理
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            button: 鼠标按钮
            pressed: 是否按下
        """
        if not self.is_recording or not self.record_mouse_click:
            return
        # 只在按下时记录一次单击
        if not pressed:
            return
        # 如果同时录制press/release，则跳过click事件以避免重复记录
        if self.record_mouse_press and self.record_mouse_release:
            return

        current_time = time.time()
        time_diff = current_time - self.last_action_time

        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()

        # 记录单击事件
        self.current_action_type = "mouse"
        self.current_action_data = {
            "mouse_action": {
                "left": 1,    # 单击
                "right": 2,   # 右击
                "middle": 3   # 中击
            }.get(button, 1),
            "x": x,
            "y": y,
            "time_diff": time_diff
        }

        self.last_action_time = current_time
        
    def _on_mouse_move(self, x: int, y: int):
        """鼠标移动事件处理
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
        """
        if not self.is_recording or not self.record_mouse_move:
            return
            
        current_time = time.time()
        
        # 移动事件采样
        if current_time - self.last_move_time < self.move_sample_interval:
            return
            
        time_diff = current_time - self.last_action_time
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的鼠标动作
        self.current_action_type = "mouse"
        self.current_action_data = {
            "mouse_action": self.MOUSE_MOVE,
            "x": x,
            "y": y,
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        self.last_move_time = current_time
        
    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int):
        """鼠标滚轮事件处理
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            dx: 水平滚动量
            dy: 垂直滚动量
        """
        if not self.is_recording:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_action_time
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的鼠标动作
        self.current_action_type = "mouse"
        self.current_action_data = {
            "mouse_action": self.MOUSE_SCROLL,
            "x": dx,  # 使用dx作为x参数
            "y": dy,  # 使用dy作为y参数
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        
    def _get_mouse_position(self) -> Tuple[int, int]:
        """获取鼠标位置
        
        Returns:
            Tuple[int, int]: 鼠标坐标(x, y)
        """
        return mouse.get_position()
        
    def record_screenshot(self, x1: int, y1: int, x2: int, y2: int,
                         pic_name: str, match_picture: Optional[str] = None,
                         match_text: Optional[str] = None):
        """记录屏幕截图
        
        Args:
            x1: 左上角X坐标
            y1: 左上角Y坐标
            x2: 右下角X坐标
            y2: 右下角Y坐标
            pic_name: 图片名称
            match_picture: 匹配的图片文件名
            match_text: 匹配的文本
        """
        if not self.is_recording:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_action_time
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的截图动作
        self.current_action_type = "printscreen"
        self.current_action_data = {
            "lux": x1,
            "luy": y1,
            "rdx": x2,
            "rdy": y2,
            "pic_name": pic_name,
            "match_picture": match_picture,
            "match_text": match_text,
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        
    def record_ai_action(self, train_group: str, train_name: str,
                        long_text: str, illustration: str):
        """记录AI动作
        
        Args:
            train_group: 训练组名称
            train_name: 训练名称
            long_text: 长文本
            illustration: 说明
        """
        if not self.is_recording:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_action_time
        
        # 保存当前动作
        if self.current_action_type and self.current_action_data:
            self._save_current_action()
            
        # 记录新的AI动作
        self.current_action_type = "ai"
        self.current_action_data = {
            "train_group": train_group,
            "train_name": train_name,
            "long_text": long_text,
            "illustration": illustration,
            "time_diff": time_diff
        }
        
        self.last_action_time = current_time
        
    def _save_current_action(self):
        """保存当前动作"""
        if not self.current_action_type or not self.current_action_data:
            return
            
        action_data = {
            "type": self.current_action_type,
            "data": self.current_action_data,
            "timestamp": datetime.now()
        }
        
        self.current_action_list.append(action_data)
        self.current_action_type = None
        self.current_action_data = {}
        
    def save_to_database(self, action_list_id: int) -> bool:
        """将录制的动作保存到数据库
        
        Args:
            action_list_id: 动作列表ID
            
        Returns:
            bool: 是否成功
        """
        try:
            for action in self.current_action_list:
                action_type = action["type"]
                data = action["data"]
                
                if action_type == "mouse":
                    action_mouse = ActionMouse(
                        mouse_action=data["mouse_action"],
                        x=data["x"],
                        y=data["y"],
                        time_diff=data["time_diff"],
                        action_list_id=action_list_id
                    )
                    self.session.add(action_mouse)
                    
                elif action_type == "keyboard":
                    action_keyboard = ActionKeyboard(
                        keyboard_type=data["keyboard_type"],
                        keyboard_value=data["keyboard_value"],
                        time_diff=data["time_diff"],
                        action_list_id=action_list_id
                    )
                    self.session.add(action_keyboard)
                    
                elif action_type == "printscreen":
                    action_printscreen = ActionPrintscreen(
                        lux=data["lux"],
                        luy=data["luy"],
                        rdx=data["rdx"],
                        rdy=data["rdy"],
                        pic_name=data["pic_name"],
                        match_picture=data["match_picture"],
                        match_text=data["match_text"],
                        time_diff=data["time_diff"],
                        action_list_id=action_list_id
                    )
                    self.session.add(action_printscreen)
                    
                elif action_type == "ai":
                    action_ai = ActionAI(
                        train_group=data["train_group"],
                        train_name=data["train_name"],
                        long_text=data["long_text"],
                        illustration=data["illustration"],
                        time_diff=data["time_diff"],
                        action_list_id=action_list_id
                    )
                    self.session.add(action_ai)
                    
            self.session.commit()
            log_manager.log_system("info", f"成功保存动作列表 {action_list_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            log_manager.log_system("error", f"保存动作列表失败: {str(e)}")
            return False 