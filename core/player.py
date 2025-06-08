import time
import pyautogui
import keyboard
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from models.actions import (
    ActionMouse, ActionKeyboard, ActionCodeTxt, ActionPrintscreen,
    ActionAI, ActionFunction, ActionClass, ActionList
)
from utils.logs import log_manager

class ActionPlayer:
    """行为回放器"""
    
    def __init__(self, session: Session):
        """初始化回放器
        
        Args:
            session: 数据库会话
        """
        self.session = session
        self.is_playing = False
        self.current_action_list: List[Dict[str, Any]] = []
        self.current_action_index = 0
        self.start_time = 0
        
    def load_actions(self, action_list_id: int) -> bool:
        """加载动作列表
        
        Args:
            action_list_id: 动作列表ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 获取动作列表
            action_list = self.session.query(ActionList).filter_by(id=action_list_id).first()
            if not action_list:
                return False
                
            # 获取所有动作
            actions = []
            
            # 获取鼠标动作
            mouse_actions = self.session.query(ActionMouse).filter_by(action_list_id=action_list_id).all()
            for action in mouse_actions:
                actions.append({
                    "type": "mouse",
                    "data": {
                        "mouse_action": action.mouse_action,
                        "x": action.x,
                        "y": action.y,
                        "time_diff": action.time_diff
                    }
                })
                
            # 获取键盘动作
            keyboard_actions = self.session.query(ActionKeyboard).filter_by(action_list_id=action_list_id).all()
            for action in keyboard_actions:
                actions.append({
                    "type": "keyboard",
                    "data": {
                        "keyboard_type": action.keyboard_type,
                        "keyboard_value": action.keyboard_value,
                        "time_diff": action.time_diff
                    }
                })
                
            # 获取截图动作
            printscreen_actions = self.session.query(ActionPrintscreen).filter_by(action_list_id=action_list_id).all()
            for action in printscreen_actions:
                actions.append({
                    "type": "printscreen",
                    "data": {
                        "lux": action.lux,
                        "luy": action.luy,
                        "rdx": action.rdx,
                        "rdy": action.rdy,
                        "pic_name": action.pic_name,
                        "match_picture": action.match_picture,
                        "match_text": action.match_text,
                        "time_diff": action.time_diff
                    }
                })
                
            # 获取AI动作
            ai_actions = self.session.query(ActionAI).filter_by(action_list_id=action_list_id).all()
            for action in ai_actions:
                actions.append({
                    "type": "ai",
                    "data": {
                        "train_group": action.train_group,
                        "train_name": action.train_name,
                        "long_text": action.long_text,
                        "illustration": action.illustration,
                        "time_diff": action.time_diff
                    }
                })
                
            # 按时间顺序排序
            self.current_action_list = sorted(actions, key=lambda x: x["data"]["time_diff"])
            self.current_action_index = 0
            
            log_manager.log_system("info", f"成功加载动作列表 {action_list_id}")
            return True
            
        except Exception as e:
            log_manager.log_system("error", f"加载动作列表失败: {str(e)}")
            return False
            
    def start_playing(self) -> bool:
        """开始回放
        
        Returns:
            bool: 是否成功
        """
        if self.is_playing or not self.current_action_list:
            return False
            
        self.is_playing = True
        self.current_action_index = 0
        self.start_time = time.time()
        
        log_manager.log_system("info", "开始回放行为")
        return True
        
    def stop_playing(self):
        """停止回放"""
        if not self.is_playing:
            return
            
        self.is_playing = False
        keyboard.unhook_all()
        
        log_manager.log_system("info", "停止回放行为")
        
    def play_next_action(self) -> bool:
        """执行下一个动作
        
        Returns:
            bool: 是否还有下一个动作
        """
        if not self.is_playing or self.current_action_index >= len(self.current_action_list):
            return False
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # 等待直到到达下一个动作的时间
        while self.current_action_index < len(self.current_action_list):
            action = self.current_action_list[self.current_action_index]
            if elapsed_time >= action["data"]["time_diff"]:
                self._execute_action(action)
                self.current_action_index += 1
            else:
                break
                
        return self.current_action_index < len(self.current_action_list)
        
    def _execute_action(self, action: Dict[str, Any]):
        """执行动作
        
        Args:
            action: 动作数据
        """
        action_type = action["type"]
        data = action["data"]
        
        try:
            if action_type == "mouse":
                self._execute_mouse_action(data)
            elif action_type == "keyboard":
                self._execute_keyboard_action(data)
            elif action_type == "printscreen":
                self._execute_printscreen_action(data)
            elif action_type == "ai":
                self._execute_ai_action(data)
                
        except Exception as e:
            log_manager.log_system("error", f"执行动作失败: {str(e)}")
            
    def _execute_mouse_action(self, data: Dict[str, Any]):
        """执行鼠标动作
        
        Args:
            data: 动作数据
        """
        mouse_action = data["mouse_action"]
        x = data["x"]
        y = data["y"]
        
        if mouse_action == 1:  # 左键点击
            pyautogui.click(x, y, button='left')
        elif mouse_action == 2:  # 右键点击
            pyautogui.click(x, y, button='right')
        elif mouse_action == 3:  # 中键点击
            pyautogui.click(x, y, button='middle')
        elif mouse_action == 4:  # 左键按下
            pyautogui.mouseDown(x, y, button='left')
        elif mouse_action == 5:  # 左键释放
            pyautogui.mouseUp(x, y, button='left')
        elif mouse_action == 6:  # 右键按下
            pyautogui.mouseDown(x, y, button='right')
        elif mouse_action == 7:  # 右键释放
            pyautogui.mouseUp(x, y, button='right')
        elif mouse_action == 8:  # 中键按下
            pyautogui.mouseDown(x, y, button='middle')
        elif mouse_action == 9:  # 中键释放
            pyautogui.mouseUp(x, y, button='middle')
        elif mouse_action == 0:  # 鼠标移动
            pyautogui.moveTo(x, y)
        elif mouse_action == 10:  # 鼠标滚动
            pyautogui.scroll(y, x, button='middle')
            
    def _execute_keyboard_action(self, data: Dict[str, Any]):
        """执行键盘动作
        
        Args:
            data: 动作数据
        """
        keyboard_type = data["keyboard_type"]
        keyboard_value = data["keyboard_value"]
        
        if keyboard_type == 1:  # 按下
            keyboard.press(keyboard_value)
        elif keyboard_type == 2:  # 释放
            keyboard.release(keyboard_value)
            
    def _execute_printscreen_action(self, data: Dict[str, Any]):
        """执行截图动作
        
        Args:
            data: 动作数据
        """
        lux = data["lux"]
        luy = data["luy"]
        rdx = data["rdx"]
        rdy = data["rdy"]
        pic_name = data["pic_name"]
        
        # 截图
        screenshot = pyautogui.screenshot(region=(lux, luy, rdx - lux, rdy - luy))
        screenshot.save(pic_name)
        
    def _execute_ai_action(self, data: Dict[str, Any]):
        """执行AI动作
        
        Args:
            data: 动作数据
        """
        train_group = data["train_group"]
        train_name = data["train_name"]
        long_text = data["long_text"]
        illustration = data["illustration"]
        
        # TODO: 实现AI动作的执行
        pass 