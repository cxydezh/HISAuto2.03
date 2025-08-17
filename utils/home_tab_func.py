import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import traceback
import os
import sys
import time
import threading
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import pyautogui
from pynput import mouse, keyboard
import win32gui  # type: ignore
import win32api  # type: ignore
from database.db_manager import DatabaseManager
from config.config_manager import ConfigManager
from models.action_suit import ActionsSuitGroup, ActionsSuitGroupHierarchy
from models.actions import ActionGroup, ActionList, ActionsGroupHierarchy,ActionMouse, ActionKeyboard,ActionClass, ActionAI, ActionPrintscreen, ActionFunction,ActionCodeTxt, ListGroupHierarchy
from models.debug_actions import ActionsDebugGroup, ActionsDebugGroupHierarchy
from models.user import User
from models.department import Department
from gui.tabs.Hierarchyutils import parse_group_rank, iid_to_group_rank
import globalvariable
from utils.logger import Logger,logger
from utils.screenshot_tool import ScreenshotTool
from core.pic_capture import PicCapture
from utils.hometab_funcdata import hometab_funcData
# 移除循环导入
# from gui.tabs.Hierarchyutils import iid_to_group_rank

class home_tab_action_group_func:
    """用于支持home_tab.py中与行为组相关的相关方法的实现"""
    
    def __init__(self, group_name: str, group_desc: str, group_user_id: str,
                  group_department_id: str,is_auto: bool, auto_time: str, 
                 action_group_selected_rank: str,action_tree_selected_iid: str,
                 action_group_type:int,sort_num:int,action_group_id:int,action_group_hierarchy_id:int):
        """初始化行为组信息,用于新增保存行为组
        
        Args:
            group_name: 行为组名称
            group_desc: 行为组描述
            group_user_id: 用户ID
            group_department_id: 科室ID
            is_auto: 是否自动执行
            auto_time: 自动执行时间
            action_group_selected_rank: 行为组秩序
            action_tree_selected_iid: 行为树选中项的iid
            action_group_type: 行为组类型,1:表示新增保存；2.表示修改保存。
            sort_num: 排序号
            action_group_id: 行为组ID
            action_group_hierarchy_id: 行为组层次ID
        Raises:
            ValueError: 当必要参数为空或无效时
        """
        # 验证必要参数，使用for循环验证，同时提示用户哪个参数为空
        required_params = [
            ("group_name", group_name), 
            ("group_user_id", group_user_id), 
            ("group_department_id", group_department_id), 
            ("action_group_selected_rank", action_group_selected_rank),
            ("action_tree_selected_iid", action_tree_selected_iid),
            ("action_group_type", action_group_type),
            ("sort_num", sort_num)
        ]
       
#        missing_params = []
 #       for param, value in required_params:
 #           if not value:
 #               missing_params.append(param)
        
       
 #         if missing_params:
 #           error_msg = f"行为组信息无效：以下参数不能为空: {', '.join(missing_params)}"
 #           logger.error(error_msg)
 #           messagebox.showinfo("提示", error_msg)
 #           raise ValueError(error_msg)
            
        # 验证自动执行时间
        if is_auto and not auto_time:
            error_msg = "行为组信息无效：auto为True时，auto_time不能为空"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # 初始化属性
        self.group_name = group_name
        self.group_desc = group_desc
        self.group_user_id = group_user_id
        self.group_department_id = group_department_id
        self.is_auto = is_auto
        self.auto_time = auto_time
        self.action_group_selected_rank = action_group_selected_rank
        self.action_tree_selected_iid = action_tree_selected_iid
        self.action_group_type = action_group_type
        self.sort_num = sort_num
        self.action_group_id = action_group_id
        self.action_group_hierarchy_id = action_group_hierarchy_id
        self.session = None
        """1:表示新增保存；2.表示修改保存；"""
    def _get_session(self):
        """获取数据库会话"""
        try:
            config_manager = ConfigManager()
            db_path = config_manager.get_value('System', 'DataSource')
            encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
            
            if not db_path or not encryption_key:
                logger.error("数据库配置信息不完整")
                return None
                
            db_manager = DatabaseManager(db_path, encryption_key)
            db_manager.initialize()
            self.session = db_manager.Session()
            return self.session
        except Exception as e:
            logger.error(f"获取数据库会话失败: {str(e)}")
            return None
    
    def _save_action_group(self)->bool:
        """保存行为组"""
        session = None
        try:
            #判断行为组任务类型
            if self.action_group_type == 1:
                #新增保存
                #获取数据库会话
                session = self._get_session()
                if not session:
                    return False
                #获取最大的sort_num
                max_sort_num = 0
                groups = session.query(ActionGroup).filter_by(group_rank_id=self.action_group_hierarchy_id).all()
                if groups:
                    for group_item in groups:
                        if group_item.sort_num > max_sort_num:
                            max_sort_num = group_item.sort_num
                #生成新增行为组记录
                new_action_group = ActionGroup(
                    action_list_group_note=self.group_desc,
                    is_auto=self.is_auto,
                    auto_time=self.auto_time,
                    user_id=self.group_user_id,
                    department_id=self.group_department_id,
                    created_at=datetime.now(), 
                    group_rank_id=self.action_group_hierarchy_id,
                    sort_num=max_sort_num + 1,
                )
                session.add(new_action_group)
                session.commit()
                logger.info(f"成功创建行为组: {self.group_name}")
                return True
            elif self.action_group_type == 2:
                #修改保存
                session = self._get_session()
                if not session:
                    return False
                    
                #判断self.action_tree_selected_iid是来源于Action_list_group表还是来源于ActionsGroupHierarchy表
                if self.action_tree_selected_iid.startswith("group_"):
                    #来源于Action_list_group表
                    group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
                    if group:
                        #更新group表的记录
                        group.action_list_group_note = self.group_desc
                        group.is_auto = self.is_auto
                        group.auto_time = self.auto_time
                        group.updated_at = datetime.now()
                        session.commit()
                        logger.info(f"成功更新行为组: {self.group_name}")
                        return True
                    else:
                        logger.error(f"无法找到行为组记录: {self.action_group_id}")
                        return False
                else:
                    #来源于ActionsGroupHierarchy表
                    hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_group_hierarchy_id).first()
                    if hierarchy:
                        #更新hierarchy表的记录
                        hierarchy.group_name = self.group_name
                        hierarchy.group_note = self.group_desc
                        hierarchy.doctor_id = self.group_user_id
                        hierarchy.updated_at = datetime.now()
                        session.commit()
                        logger.info(f"成功更新行为组层次: {self.group_name}")
                        return True
                    else:
                        logger.error(f"无法找到行为组层次记录: {self.action_group_hierarchy_id}")
                        return False
            else:
                logger.error(f"无效的行为组类型: {self.action_group_type}")
                return False
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"保存行为组失败: {str(e)}")
            return False
        finally:
            if session and session != self.session:
                session.close()
    @classmethod
    def _delete_action_group(cls,action_tree_selected_iid,action_group_id,action_group_hierarchy_id)->bool:
        """删除行为组。action_tree_selected_iid为行为组列表层级iid。action_group_id为行为组id。action_group_hierarchy_id为行为组层次id。"""
        session = None
        try:
            cls.action_tree_selected_iid = action_tree_selected_iid
            cls.action_group_id = action_group_id
            cls.action_group_hierarchy_id = action_group_hierarchy_id
            hometab_funcData.delete_action_group(sheet_type="Action",action_tree_selected_iid=cls.action_tree_selected_iid,action_group_id=cls.action_group_id,action_group_hierarchy_id=cls.action_group_hierarchy_id)
            return True
        except Exception as e:
            if session:
                session.rollback()
            print(traceback.format_exc())
            logger.error(f"删除行为组失败: {str(e)}")
            return False

    def _session_close(self):
        """关闭数据库会话"""
        try:
            if self.session:
                self.session.close()
                self.session = None
                logger.info("数据库会话已关闭")
            return True
        except Exception as e:
            logger.error(f"关闭数据库会话失败: {str(e)}")
            return False
    def _capture_image(self):
        """图像采集"""
        messagebox.showinfo("提示", "图像采集功能待实现")
        
    def _delete_action(self, session, action_list_id, action_type):
        """删除子行为元"""
        try:
            if not session:
                return False
        except Exception as e:
            logger.error(f"删除子行为元失败: {str(e)}")
            return False
            
        if action_type == 'mouse':
            action = session.query(ActionMouse).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'keyboard': 
            action = session.query(ActionKeyboard).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'code_text':
            action = session.query(ActionCodeTxt).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'printscreen':
            action = session.query(ActionPrintscreen).filter_by(id=action_list_id).first()  
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'ai':
            action = session.query(ActionAI).filter_by(id=action_list_id).first()
            if action:      
                session.delete(action)
                session.commit()
        elif action_type == 'function':
            action = session.query(ActionFunction).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'class':
            action = session.query(ActionClass).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()    
        return True
def _home_capture_image(action_group_id: int, master: tk.Tk):
    """图像采集
    
    Args:
        action_group_id: 行为组ID
        master: 主窗口引用
        
    Returns:
        bool: 操作是否成功
    """
    try:
        if not action_group_id:
            messagebox.showwarning("警告", "请先选择行为组")
            return False
            
        # 获取配置信息
        from config.config_manager import ConfigManager
        config = ConfigManager()
        base_save_path = config.get_value('PicCapture', 'savepath')
        
        if not base_save_path:
            messagebox.showerror("错误", "图像保存路径未配置")
            return False
        
        # 构建完整的保存路径
        save_path = os.path.join(base_save_path, str(action_group_id), "Picture")
        print(f"图像保存路径: {save_path}")
        
        # 确保保存目录存在
        try:
            os.makedirs(save_path, exist_ok=True)
            print(f"保存目录已创建/确认: {save_path}")
        except Exception as e:
            print(f"创建保存目录失败: {e}")
            messagebox.showerror("错误", f"创建保存目录失败: {str(e)}")
            return False
        
        # 创建图像采集实例
        from core.pic_capture import PicCapture
        pic_capture = PicCapture(save_path=save_path, master=master)
        
        # 执行图像采集
        print("开始图像采集...")
        pic_capture.capture_screen()
        
        # 检查是否成功选择了区域
        coordinates = pic_capture.get_image_coordinates()
        print(f"选择的坐标: {coordinates}")
        
        if not coordinates[0] or not coordinates[1] or not coordinates[2] or not coordinates[3]:
            messagebox.showinfo("提示", "未选择图像区域，图像采集已取消")
            return False
            
        # 获取行为组名称作为图像名称
        from models.actions import ActionGroup
        from database.db_manager import DatabaseManager
        
        db_path = config.get_value('System', 'DataSource')
        encryption_key = config.get_value('Security', 'DBEncryptionKey')
        
        if not db_path or not encryption_key:
            messagebox.showerror("错误", "数据库配置信息不完整")
            return False
            
        db_manager = DatabaseManager(db_path, encryption_key)
        db_manager.initialize()
        session = db_manager.Session()
        
        try:
            group = session.query(ActionGroup).filter_by(id=action_group_id).first()
            if not group:
                messagebox.showerror("错误", "未找到指定的行为组")
                return False
                
            # 生成图像名称
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"{group.action_list_group_name}_{timestamp}"
            print(f"图像名称: {image_name}")
            
            # 保存图像
            if pic_capture.save_image(image_name):
                messagebox.showinfo("成功", f"图像采集完成，已保存为: {image_name}.png")
                return True
            else:
                messagebox.showerror("错误", "图像保存失败")
                return False
                
        except Exception as e:
            print(traceback.format_exc())
            messagebox.showerror("错误", f"获取行为组信息失败: {str(e)}")
            return False
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"图像采集失败: {str(e)}")
        print(traceback.format_exc())
        messagebox.showerror("错误", f"图像采集失败: {str(e)}")
        return False

    
class ActionManager:
    """行为元管理器，用于处理middle_panel中行为元相关的按钮功能"""
    
    def __init__(self, home_tab):
        """初始化行为元管理器
        
        Args:
            home_tab: HomeTab实例的引用，用于访问界面控件和变量
        """
        self.home_tab = home_tab
        self.logger = Logger()
    def _get_session(self):
        """获取数据库会话"""
        session = None
        #获取数据库会话
        config = ConfigManager()
        db_path = config.get_value('System', 'DataSource')
        encryption_key = config.get_value('Security', 'DBEncryptionKey')
            
        if not db_path or not encryption_key:
            messagebox.showerror("错误", "数据库配置信息不完整")
            return
                
        db_manager = DatabaseManager(db_path, encryption_key)
        db_manager.initialize()
        session = db_manager.Session()
        if not session:
            return
        self.session = session
        return session
    def create_action(self):
        """创建行为元"""
        # 检查是否有选中的行为组
        if not self.home_tab.action_group_id:
            messagebox.showinfo("提示", "请先选择行为组")
            return False
        if not self.home_tab.current_action_list_hierarchy_id:
            messagebox.showinfo("提示", "请先选择行为组列表层级或新建列表层。")
            return False
        # 设置行为元操作类型为新增
        self.home_tab.action_operation_type = 1
        
        # 启用相关控件
        self._set_action_controls_state('normal')
        
        # 清空基本信息
        self.home_tab.action_name_var.set("")
        self.home_tab.next_action_var.set("")
        self.home_tab.action_type_var.set("mouse")  # 默认选择鼠标类型
        self.home_tab.debug_group_id.set("")
        self.home_tab.action_note_var.set("")
        
        # 清空动态详情区域
        self._clear_action_detail_controls()
        
        # 修改按钮状态
        self._set_action_button_state()
        
        # 触发行为类型变更事件以显示默认控件
        self._on_action_type_changed()
        return True
    
    def modify_action(self):
        """修改行为元"""
        # 检查是否有选中的行为元
        selected = self.home_tab.action_list.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要修改的行为")
            return False
            
        # 设置行为元操作类型为修改
        self.home_tab.action_operation_type = 2
        
        # 启用相关控件
        self._set_action_controls_state('normal')
        
        # 修改按钮状态
        self._set_action_button_state()
        
        return True
    
    def delete_action(self,action_type,current_action_id,current_action_list_hierarchy_id):
        """删除行为元"""
        selected = self.home_tab.action_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的行为")
            return False
        if messagebox.askyesno("确认", "确定要删除选中的行为吗？"):
            session = None
            try:
                session = self._get_session()
                if not session:
                    return False
                if  action_type == "mouse":
                    action = session.query(ActionMouse).filter_by(id=current_action_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        messagebox.showinfo("成功", "鼠标行为删除成功")
                        return True
                elif action_type == "keyboard":
                    action = session.query(ActionKeyboard).filter_by(id=current_action_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        messagebox.showinfo("成功", "键盘行为删除成功")
                        return True
                elif action_type == "class":
                    action = session.query(ActionClass).filter_by(id=current_action_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        messagebox.showinfo("成功", "类行为删除成功")
                        return True
                elif action_type == "ai":
                    action = session.query(ActionAI).filter_by(id=current_action_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        messagebox.showinfo("成功", "AI行为删除成功")
                        return True
                elif action_type == "function":
                    action = session.query(ActionFunction).filter_by(id=current_action_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        messagebox.showinfo("成功", "函数行为删除成功")
                        return True
                elif action_type == "code_text":
                    action = session.query(ActionCodeTxt).filter_by(id=current_action_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        messagebox.showinfo("成功", "代码文本行为删除成功")
                        return True
                elif action_type == "printscreen":
                    action = session.query(ActionPrintscreen).filter_by(id=current_action_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        messagebox.showinfo("成功", "截图行为删除成功")
                        return True
                
                # 删除行为元记录
                action = session.query(ActionList).filter_by(id=current_action_id).first()
                if action:
                    action_name = action.action_name
                    session.delete(action)
                    session.commit()
                    messagebox.showinfo("成功", f"行为 '{action_name}' 删除成功")
                    # 刷新行为列表
                    self._refresh_action_list()
                    return True
                else:
                    messagebox.showerror("错误", "未找到要删除的行为")
                    return False
                
            except Exception as e:
                if session:
                    session.rollback()
                self.logger.error(f"删除行为失败: {str(e)}")
                messagebox.showerror("错误", f"删除行为失败: {str(e)}")
                return False
            finally:
                if session:
                    session.close()
        
        return False
    
    def save_action(self):
        """保存行为元"""
        session = None
        try:
            # 验证必填字段
            if not self.home_tab.action_name_var.get().strip():
                messagebox.showwarning("警告", "请输入行为名称")
                return False
                
            if not self.home_tab.action_type_var.get():
                messagebox.showwarning("警告", "请选择行为类型")
                return False
                
            # 获取数据库连接
            session = self._get_session()
            if not session:
                return False
            
            if self.home_tab.action_operation_type == 1:
                # 新增保存,不涉及保存列表层级，因为列表层级保存在ActionManager中已经被实现
                action_list = ActionList(
                    list_rank_id=self.home_tab.current_action_list_hierarchy_id,
                    group_id=self.home_tab.action_group_id,
                    action_type=self.home_tab.action_type_var.get(),
                    action_name=self.home_tab.action_name_var.get().strip(),
                    next_id=self.home_tab.next_action_var.get().strip() or None,
                    debug_group_id=self.home_tab.debug_group_id.get().strip() or None,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    action_note=self.home_tab.action_note_var.get().strip()
                )
                session.add(action_list)
                session.flush()  # 获取ID
                
                # 保存详细记录
                self._save_action_detail(session, action_list.id)
                session.commit()
                
                messagebox.showinfo("成功", "行为创建成功")
                
            elif self.home_tab.action_operation_type == 2:
                # 修改保存
                if not self.home_tab.current_action_id and self.home_tab.current_action_list_hierarchy_id:
                    # 修改列表层级
                    list_hierarchy = session.query(ListGroupHierarchy).filter_by(id=self.home_tab.current_action_list_hierarchy_id).first()
                    if list_hierarchy:
                        list_hierarchy.list_name = self.home_tab.action_name_var.get().strip()
                        list_hierarchy.group_note = self.home_tab.action_note_var.get().strip()
                        session.commit()
                        messagebox.showinfo("成功", "列表层级修改成功")
                else:
                    action_list = session.query(ActionList).filter_by(id=self.home_tab.current_action_id).first()
                    if action_list:
                        action_list.action_name = self.home_tab.action_name_var.get().strip()
                        action_list.next_id = self.home_tab.next_action_var.get().strip() or None
                        action_list.debug_group_id = self.home_tab.debug_group_id.get().strip() or None
                        action_list.updated_at = datetime.now()
                        action_list.action_note = self.home_tab.action_note_var.get().strip()
                        session.commit()
                        # 更新详细记录
                        self._update_action_detail(session, action_list.id)
                        session.commit()
                        messagebox.showinfo("成功", "行为修改成功")
                    else:
                        messagebox.showerror("错误", "未找到要修改的行为")
                        return False
            else:
                messagebox.showerror("错误", "无效的操作类型")
                return False
                
            # 重置状态
            self.home_tab.action_operation_type = None
            self.home_tab.current_action_id = None
            
            # 禁用控件
            self._set_action_controls_state('disabled')
            
            # 修改按钮状态
            self._set_action_button_state()
            
            # 刷新行为列表
            self._refresh_action_list()
            
            return True
            
        except Exception as e:
            if session:
                session.rollback()
            self.logger.error(f"保存行为失败: {str(e)}")
            messagebox.showerror("错误", f"保存行为失败: {str(e)}")
            return False
        finally:
            if session:
                session.close()
    
    def _set_action_controls_state(self, state):
        """设置行为元控件状态"""
        for ctrl in [
            self.home_tab.action_name_entry, self.home_tab.next_action_entry, 
            self.home_tab.action_type_combo, self.home_tab.debug_group_id_entry, 
            self.home_tab.action_note_entry
        ]:
            ctrl.config(state=state)
    
    def _set_action_button_state(self,state = None):
        """设置行为按钮状态"""
        if state == 'normal':  
            self.home_tab.btn_create_action_list_group.config(state='normal')
            self.home_tab.btn_create_action.config(state='normal')
            self.home_tab.btn_record_action.config(state='normal')
            self.home_tab.btn_modify_action.config(state='normal')
            self.home_tab.btn_delete_action.config(state='normal')
            self.home_tab.btn_use_suit.config(state='normal')
            self.home_tab.btn_save_action.config(state='disabled')
        else:
            self.home_tab.btn_create_action_list_group.config(state='disabled')
            self.home_tab.btn_create_action.config(state='disabled')
            self.home_tab.btn_record_action.config(state='disabled')
            self.home_tab.btn_modify_action.config(state='disabled')
            self.home_tab.btn_delete_action.config(state='disabled')
            self.home_tab.btn_use_suit.config(state='disabled')
            self.home_tab.btn_save_action.config(state='normal')
    def _clear_action_detail_controls(self):
        """清空行为详情控件"""
        # 清空动态详情区域
        for widget in self.home_tab.action_list_frame.winfo_children():
            widget.destroy()
        
        # 清空各种类型的变量
        if hasattr(self.home_tab, 'action_mouse_action_type_var'):
            self.home_tab.action_mouse_action_type_var.set("")
        if hasattr(self.home_tab, 'action_mouse_x_var'):
            self.home_tab.action_mouse_x_var.set("")
        if hasattr(self.home_tab, 'action_mouse_y_var'):
            self.home_tab.action_mouse_y_var.set("")
        if hasattr(self.home_tab, 'action_mouse_size_var'):
            self.home_tab.action_mouse_size_var.set("")
        
        if hasattr(self.home_tab, 'keyboard_type_var'):
            self.home_tab.action_keyboard_type_var.set("")
        if hasattr(self.home_tab, 'action_keyboard_value_var'):
            self.home_tab.action_keyboard_value_var.set("")
        if hasattr(self.home_tab, 'keyboard_time_diff_var'):
            self.home_tab.keyboard_time_diff_var.set("")
        
        if hasattr(self.home_tab, 'class_name_var'):
            self.home_tab.class_name_var.set("")
        if hasattr(self.home_tab, 'window_title_var'):
            self.home_tab.window_title_var.set("")
        
        if hasattr(self.home_tab, 'ai_train_group_var'):
            self.home_tab.ai_train_group_var.set("")
        if hasattr(self.home_tab, 'ai_train_long_name_var'):
            self.home_tab.ai_train_long_name_var.set("")
        if hasattr(self.home_tab, 'ai_long_txt_name_var'):
            self.home_tab.ai_long_txt_name_var.set("")
        if hasattr(self.home_tab, 'ai_illustration_var'):
            self.home_tab.ai_illustration_var.set("")
        if hasattr(self.home_tab, 'ai_note_var'):
            self.home_tab.ai_note_var.set("")
        
        if hasattr(self.home_tab, 'print_lux_var'):
            self.home_tab.print_lux_var.set("")
        if hasattr(self.home_tab, 'print_luy_var'):
            self.home_tab.print_luy_var.set("")
        if hasattr(self.home_tab, 'print_rdx_var'):
            self.home_tab.print_rdx_var.set("")
        if hasattr(self.home_tab, 'print_rdy_var'):
            self.home_tab.print_rdy_var.set("")
        if hasattr(self.home_tab, 'print_pic_name_var'):
            self.home_tab.print_pic_name_var.set("")
        if hasattr(self.home_tab, 'print_match_picture_var'):
            self.home_tab.print_match_picture_var.set("")
        if hasattr(self.home_tab, 'print_match_text_var'):
            self.home_tab.print_match_text_var.set("")
        if hasattr(self.home_tab, 'print_mouse_action_var'):
            self.home_tab.print_mouse_action_var.set("")
        
        if hasattr(self.home_tab, 'function_name_var'):
            self.home_tab.function_name_var.set("")
        if hasattr(self.home_tab, 'function_args1_var'):
            self.home_tab.function_args1_var.set("")
        if hasattr(self.home_tab, 'function_args2_var'):
            self.home_tab.function_args2_var.set("")
        if hasattr(self.home_tab, 'function_time_diff_var'):
            self.home_tab.function_time_diff_var.set("")
    
    def _on_action_type_changed(self):
        """行为类型变更事件处理"""
        # 这个方法需要调用home_tab中的_on_action_type_changed方法
        if hasattr(self.home_tab, '_on_action_type_changed'):
            self.home_tab._on_action_type_changed()
    
    def _refresh_action_list(self):
        """刷新行为列表"""
        if not self.home_tab.action_group_id:
            return
            
        try:
            # 清空行为列表
            self.home_tab.action_list.delete(*self.home_tab.action_list.get_children())
            
            # 从数据库获取行为列表
            session = self._get_session()
            if not session:
                return
                
            actions = session.query(ActionList).filter_by(group_id=self.home_tab.action_group_id).all()
            for action in actions:
                self.home_tab.action_list.insert("", "end", iid=str(action.id), values=(
                    action.id, action.action_type, action.action_name, action.next_id
                ))
                
            session.close()
        except Exception as e:
            print(traceback.format_exc())
            self.logger.error(f"刷新行为列表失败: {str(e)}")
    
    def _on_debug_action_list_select(self, event):
        """调试行为列表选择事件处理"""
        selected = self.home_tab.action_debug_list.selection()
        if not selected:
            return
        iid = selected[0]
        selected_type = self.home_tab.action_debug_list.item(iid, "values")[1]
        
        # 先全部禁用
        self._set_home_controls_state('disabled')
        
        # 只让部分控件可用
        for entry in [
            self.home_tab.action_debug_name_entry, self.home_tab.next_debug_id_entry, 
            self.home_tab.action_debug_type_combo, self.home_tab.back_id_entry, 
            self.home_tab.action_debug_note_entry
        ]:
            entry.config(state='normal')
        
        try:
            #获取数据库会话            
            session = self._get_session()
            if not session:
                return
                
            if selected_type == "group":
                # 选中的是ActionGroup
                group_id = iid
                group = session.query(ActionGroup).filter_by(id=group_id).first()
                if group:
                    # 启用按钮
                    for btn in [
                        self.home_tab.btn_create_debug_action, self.home_tab.btn_modify_debug_action, 
                        self.home_tab.btn_delete_debug_action, self.home_tab.btn_save_debug_action, 
                        self.home_tab.btn_use_debug_suit
                    ]:
                        btn.config(state='normal')

                    # 填充详情区
                    self.home_tab.action_debug_name_var.set(group.action_list_group_name or "")
                    self.home_tab.next_debug_id_var.set(group.next_id or "")
                    self.home_tab.action_debug_type_var.set(group.action_type or "")
                    self.home_tab.back_id_var.set(group.next_id or "")
                    self.home_tab.action_debug_note_var.set(group.action_list_group_note or "")
                    
                    # 填充action_debug_list
                    self.home_tab.action_debug_list.delete(*self.home_tab.action_debug_list.get_children())
                    actions = session.query(ActionList).filter_by(group_id=group_id).all()
                    for action in actions:
                        self.home_tab.action_debug_list.insert("", "end", iid=str(action.id), values=(
                            action.action_type, action.action_name, action.next_id
                        ))
            else:
                # 选中的是ActionsGroupHierarchy
                from gui.tabs.Hierarchyutils import iid_to_group_rank
                selected_group_rank = iid_to_group_rank(iid)
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(group_rank=selected_group_rank).first()
                if hierarchy:
                    self.home_tab.action_debug_name_var.set(hierarchy.group_name or "")
                    self.home_tab.next_debug_id_var.set("")
                    self.home_tab.action_debug_type_var.set("")
                    self.home_tab.back_id_var.set("")
                    self.home_tab.action_debug_note_var.set(hierarchy.group_note or "")
                
                # 启用左侧按钮
                for btn in [
                    self.home_tab.btn_create_debug_action, self.home_tab.btn_modify_debug_action, 
                    self.home_tab.btn_delete_debug_action, self.home_tab.btn_save_debug_action, 
                    self.home_tab.btn_use_debug_suit
                ]:
                    btn.config(state='normal')
                
                # 禁用中间按钮
                for btn in [
                    self.home_tab.btn_create_debug_action, self.home_tab.btn_modify_debug_action, 
                    self.home_tab.btn_delete_debug_action, self.home_tab.btn_save_debug_action, 
                    self.home_tab.btn_use_debug_suit
                ]:
                    btn.config(state='disabled')
                
                # 清空action_debug_list
                self.home_tab.action_debug_list.delete(*self.home_tab.action_debug_list.get_children())
                
            session.close()
        except Exception as e:
            self.logger.error(f"Error in _on_debug_action_list_select: {e}")
    def _get_action_list_rank(self,hierarchy_id):
        """获取行为列表的等级"""
        session = self._get_session()
        if not session:
            return
        hierarchy = session.query(ListGroupHierarchy).filter_by(id=hierarchy_id).first()
        if hierarchy:
            return hierarchy.list_rank
        else:
            return None
    
    def _fill_action_data(self, action_type, action_id,current_action_list_hierarchy_id):
        """填充行为数据到控件(因控件填充问题，action_list特有的方法)
        
        Args:
            action_type: 行为类型
            action_id: 行为ID
        """
        try:
            #获取数据库会话
            session = self._get_session()
            if not session:
                return
                
            # 根据行为类型获取对应的数据
            if action_type == "list_hierarchy":
                action_data = session.query(ListGroupHierarchy).filter_by(id =current_action_list_hierarchy_id).first()
            elif action_type == "mouse":
                action_data = session.query(ActionMouse).filter_by(action_list_id =action_id).first()
            elif action_type == "keyboard":
                action_data = session.query(ActionKeyboard).filter_by(action_list_id =action_id).first()
            elif action_type == "class":
                action_data = session.query(ActionClass).filter_by(action_list_id =action_id).first()
            elif action_type == "AI":
                action_data = session.query(ActionAI).filter_by(action_list_id =action_id).first()
            elif action_type == "image":
                action_data = session.query(ActionPrintscreen).filter_by(action_list_id =action_id).first()
            elif action_type == "function":
                action_data = session.query(ActionFunction).filter_by(action_list_id =action_id).first()
            else:
                session.close()
                return

            if not action_data:
                session.close()
                return
                
            if action_type == "list_hierarchy":
                self.home_tab.current_action_list_selected_rank = action_data.list_rank
                self.home_tab.action_list_hierarchy_name_var.set(action_data.list_name)
                self.home_tab.action_list_hierarchy_note_var.set(action_data.group_note)
            elif action_type == 'mouse':
                # 填充鼠标控件数据
                self.home_tab.action_mouse_action_type_var.set(self._mouse_action_to_text(action_data.mouse_action))
                self.home_tab.action_mouse_size_var.set(action_data.mouse_size)
                self.home_tab.action_mouse_x_var.set(action_data.x)
                self.home_tab.action_mouse_y_var.set(action_data.y)
                self.home_tab.action_mouse_time_diff_var.set(action_data.time_diff)
                
            elif action_type == 'keyboard':
                # 填充键盘控件数据
                self.home_tab.action_keyboard_type_var.set(self._keyboard_type_to_text(action_data.keyboard_type))
                self.home_tab.action_keyboard_value_var.set(action_data.keyboard_value)
                self.home_tab.action_keyboard_time_diff_var.set(action_data.time_diff)
                
            elif action_type == 'class':
                # 填充类控件数据
                self.home_tab.action_class_name_var.set(action_data.class_name)
                self.home_tab.action_window_title_var.set(action_data.windows_title)
                self.home_tab.action_class_time_diff_var.set(action_data.time_diff)
                
            elif action_type == 'AI':
                # 填充AI控件数据
                self.home_tab.action_ai_training_group_var.set(action_data.train_group_name)
                self.home_tab.action_ai_record_name_var.set(action_data.train_long_name)
                self.home_tab.action_ai_long_text_name_var.set(action_data.long_txt_name)
                self.home_tab.action_ai_illustration_var.set(action_data.ai_illustration)
                self.home_tab.action_ai_note_var.set(action_data.ai_note)
                self.home_tab.action_ai_time_diff_var.set(action_data.time_diff)
                
            elif action_type == 'image':
                # 填充图像控件数据
                self.home_tab.action_image_left_top_x_var.set(action_data.lux)
                self.home_tab.action_image_left_top_y_var.set(action_data.luy)
                self.home_tab.action_image_right_bottom_x_var.set(action_data.rdx)
                self.home_tab.action_image_right_bottom_y_var.set(action_data.rdy)
                self.home_tab.action_image_names_var.set(action_data.pic_name)
                self.home_tab.action_image_match_criteria_var.set(action_data.match_picture_name)
                self.home_tab.image_mouse_action_var.set(self._mouse_action_to_text(action_data.mouse_action))
                self.home_tab.image_time_diff_var.set(action_data.time_diff)
                
            elif action_type == 'function':
                # 填充函数控件数据
                self.home_tab.action_function_name_var.set(action_data.function_name)
                self.home_tab.action_function_parameters_var.set(action_data.args1)
                self.home_tab.action_function_arguments_var.set(action_data.args2)
                self.home_tab.function_time_diff_var.set(action_data.time_diff)
                    
            session.close()
        except Exception as e:
            print(traceback.format_exc())
            self.logger.error(f"获取行为数据失败：{str(e)}")
    
    def _set_home_controls_state(self, state):
        """设置首页控件状态"""
        for ctrl in [
            self.home_tab.group_name_entry, self.home_tab.group_last_circle_local_entry, 
            self.home_tab.group_last_circle_node_entry, self.home_tab.group_setup_time_entry, 
            self.home_tab.group_update_time_entry, self.home_tab.group_user_id_entry,
            self.home_tab.is_auto_check, self.home_tab.auto_time_entry, 
            self.home_tab.group_desc_entry
        ]:
            ctrl.config(state=state)
        self.home_tab.group_user_name_entry.config(state='disabled')
        self.home_tab.department_id_entry.config(state='disabled')
    
    def _save_action_detail(self, session, action_list_id):
        """保存行为元详细记录"""
        try:
            action_type = self.home_tab.action_type_var.get()
            
            if action_type == "mouse":
                mouse_action = self._text_to_mouse_action(self.home_tab.action_mouse_action_type_var.get())
                x_var = self.home_tab.action_mouse_x_var.get()  
                y_var = self.home_tab.action_mouse_y_var.get()
                x = int(float(x_var)) if x_var.strip() else 0
                y = int(float(y_var)) if y_var.strip() else 0
                # 处理鼠标大小字段为空的情况
                mouse_size_str = self.home_tab.action_mouse_size_var.get()
                mouse_size = int(float(mouse_size_str)) if mouse_size_str.strip() else 0
                
                action_detail = ActionMouse(
                    mouse_action=mouse_action,
                    x=x,
                    y=y,
                    mouse_size=mouse_size,
                    action_list_id=action_list_id
                )
                session.add(action_detail)
                
            elif action_type == "keyboard":
                action_detail = ActionKeyboard(
                    keyboard_type=self._text_to_keyboard_type(self.home_tab.action_keyboard_type_var.get()),
                    keyboard_value=self.home_tab.action_keyboard_value_var.get(),
                    action_list_id=action_list_id
                )
                session.add(action_detail)
                
            elif action_type == "class":
                action_detail = ActionClass(
                    class_name=self.home_tab.class_name_var.get(),
                    windows_title=self.home_tab.window_title_var.get(),
                    action_list_id=action_list_id
                )
                session.add(action_detail)
                
            elif action_type == "AI":
                action_detail = ActionAI(
                    train_group_name=self.home_tab.action_ai_training_group_var.get(),
                    train_long_name=self.home_tab.action_ai_record_name_var.get(),
                    long_txt_name=self.home_tab.action_ai_long_text_name_var.get(),
                    ai_illustration=self.home_tab.action_ai_illustration_var.get(),
                    ai_note=self.home_tab.action_ai_note_var.get(),
                    action_list_id=action_list_id
                )
                session.add(action_detail)
                
            elif action_type == "image":
                action_detail = ActionPrintscreen(
                    lux=int(self.home_tab.action_image_left_top_x_var.get() or 0),
                    luy=int(self.home_tab.action_image_left_top_y_var.get() or 0),
                    rdx=int(self.home_tab.action_image_right_bottom_x_var.get() or 0),
                    rdy=int(self.home_tab.action_image_right_bottom_y_var.get() or 0),
                    pic_name=self.home_tab.action_image_names_var.get(),
                    match_picture_name=self.home_tab.action_image_names_var.get(),
                    match_text=self.home_tab.action_image_match_criteria_var.get(),
                    mouse_action=int(self.home_tab.image_mouse_action_var.get() or 0),
                    action_list_id=action_list_id
                )
                session.add(action_detail)
                
            elif action_type == "function":
                action_detail = ActionFunction(
                    function_name=self.home_tab.function_name_var.get(),
                    args1=self.home_tab.function_args1_var.get(),
                    args2=self.home_tab.function_args2_var.get(),
                    action_list_id=action_list_id
                )
                session.add(action_detail)
            else:
                self.logger.warning(f"未知的行为类型: {action_type}")
                return False
                
            return True
        except Exception as e:
            print(traceback.format_exc())
            self.logger.error(f"保存行为详情失败: {str(e)}")
            return False
    def _update_action_detail(self, session, action_list_id):
        """更新行为元详细记录"""
        try:
            action_type = self.home_tab.action_type_var.get()
            
            # 查找并更新现有的详细记录
            if action_type == "mouse":
                action_detail = session.query(ActionMouse).filter_by(action_list_id=action_list_id).first()
                if action_detail:
                    action_detail.mouse_action = self._text_to_mouse_action(self.home_tab.action_mouse_action_type_var.get())
                    action_detail.x = int(float(self.home_tab.action_mouse_x_var.get()) or 0)
                    action_detail.y = int(float(self.home_tab.action_mouse_y_var.get()) or 0)
                    action_detail.mouse_size = int(float(self.home_tab.action_mouse_size_var.get()) or 0)
                else:
                    # 如果不存在则创建新记录
                    return self._save_action_detail(session, action_list_id)
                    
            elif action_type == "keyboard":
                action_detail = session.query(ActionKeyboard).filter_by(action_list_id=action_list_id).first()
                if action_detail:
                    action_detail.keyboard_type = self._text_to_keyboard_type(self.home_tab.action_keyboard_type_var.get())
                    action_detail.keyboard_value = self.home_tab.action_keyboard_value_var.get()
                else:
                    # 如果不存在则创建新记录
                    return self._save_action_detail(session, action_list_id)
                    
            elif action_type == "class":
                action_detail = session.query(ActionClass).filter_by(action_list_id=action_list_id).first()
                if action_detail:
                    action_detail.class_name = self.home_tab.class_name_var.get()
                    action_detail.windows_title = self.home_tab.window_title_var.get()
                else:
                    # 如果不存在则创建新记录
                    return self._save_action_detail(session, action_list_id)
                    
            elif action_type == "AI":
                action_detail = session.query(ActionAI).filter_by(action_list_id=action_list_id).first()
                if action_detail:
                    action_detail.train_group_name = self.home_tab.ai_train_group_var.get()
                    action_detail.train_long_name = self.home_tab.ai_train_long_name_var.get()
                    action_detail.long_txt_name = self.home_tab.ai_long_txt_name_var.get()
                    action_detail.ai_illustration = self.home_tab.ai_illustration_var.get()
                    action_detail.ai_note = self.home_tab.ai_note_var.get()
                else:
                    # 如果不存在则创建新记录
                    return self._save_action_detail(session, action_list_id)
                    
            elif action_type == "image":
                action_detail = session.query(ActionPrintscreen).filter_by(action_list_id=action_list_id).first()
                if action_detail:
                    action_detail.lux = int(self.home_tab.action_image_left_top_x_var.get() or 0)
                    action_detail.luy = int(self.home_tab.action_image_left_top_y_var.get() or 0)
                    action_detail.rdx = int(self.home_tab.action_image_right_bottom_x_var.get() or 0)
                    action_detail.rdy = int(self.home_tab.action_image_right_bottom_y_var.get() or 0)
                    action_detail.pic_name = self.home_tab.action_image_names_var.get()
                    action_detail.match_picture_name = self.home_tab.action_image_names_var.get()
                    action_detail.match_text = self.home_tab.action_image_match_criteria_var.get()
                    action_detail.mouse_action = int(self.home_tab.image_mouse_action_var.get() or 0)
                else:
                    # 如果不存在则创建新记录
                    return self._save_action_detail(session, action_list_id)
                    
            elif action_type == "function":
                action_detail = session.query(ActionFunction).filter_by(action_list_id=action_list_id).first()
                if action_detail:
                    action_detail.function_name = self.home_tab.function_name_var.get()
                    action_detail.args1 = self.home_tab.function_args1_var.get()
                    action_detail.args2 = self.home_tab.function_args2_var.get()
                else:
                    # 如果不存在则创建新记录
                    return self._save_action_detail(session, action_list_id)
            else:
                self.logger.warning(f"未知的行为类型: {action_type}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"更新行为详情失败: {str(e)}")
            return False
      
    def _text_to_mouse_action(self, text):
        """将鼠标动作文本转换为数字编码"""
        mouse_action_map = {
            "左键单击": 1, "右键单击": 2, "中键单击": 3,
            "左键按下": 4, "左键释放": 5, "右键按下": 6,
            "右键释放": 7, "中键按下": 8, "中键释放": 9,
            "鼠标移动": 0, "滚轮滚动": 10
        }
        return mouse_action_map.get(text, 1)
    
    def _text_to_keyboard_type(self, text):
        """将键盘类型文本转换为数字编码"""
        keyboard_type_map = {
            "按下": 1, "释放": 2, "单击": 3, "文本": 4
        }
        return keyboard_type_map.get(text, 3)
    
    def _mouse_action_to_text(self, action_code):
        """将鼠标动作数字编码转换为文本"""
        mouse_action_map = {
            1: "左键单击", 2: "右键单击", 3: "中键单击",
            4: "左键按下", 5: "左键释放", 6: "右键按下",
            7: "右键释放", 8: "中键按下", 9: "中键释放",
            0: "鼠标移动", 10: "滚轮滚动"
        }
        return mouse_action_map.get(action_code, "左键单击")
    
    def _keyboard_type_to_text(self, type_code):
        """将键盘类型数字编码转换为文本"""
        keyboard_type_map = {
            1: "按下", 2: "释放", 3: "单击", 4: "文本"
        }
        return keyboard_type_map.get(type_code, "单击")
    
    def validate_action_data(self):
        """验证行为数据"""
        errors = []
        
        # 验证基本信息
        if not self.home_tab.action_name_var.get().strip():
            errors.append("行为名称不能为空")
        
        if not self.home_tab.action_type_var.get():
            errors.append("请选择行为类型")
        
        # 根据行为类型验证特定字段
        action_type = self.home_tab.action_type_var.get()
        
        if action_type == "mouse":
            if not self.home_tab.action_mouse_action_type_var.get():
                errors.append("请选择鼠标动作类型")
            try:
                x = float(self.home_tab.action_mouse_x_var.get() or 0)
                y = float(self.home_tab.action_mouse_y_var.get() or 0)
                if x < 0 or y < 0:
                    errors.append("鼠标坐标不能为负数")
            except ValueError:
                errors.append("鼠标坐标必须是数字")
        
        elif action_type == "keyboard":
            if not self.home_tab.action_keyboard_type_var.get():
                errors.append("请选择键盘动作类型")
            if not self.home_tab.action_keyboard_value_var.get().strip():
                errors.append("键盘值不能为空")
        
        elif action_type == "class":
            if not self.home_tab.class_name_var.get().strip():
                errors.append("类名不能为空")
        
        elif action_type == "AI":
            if not self.home_tab.action_ai_training_group_var.get().strip():
                errors.append("AI训练组名不能为空")
        
        elif action_type == "image":
            try:
                lux = int(self.home_tab.action_image_left_top_x_var.get() or 0)
                luy = int(self.home_tab.action_image_left_top_y_var.get() or 0)
                rdx = int(self.home_tab.action_image_right_bottom_x_var.get() or 0)
                rdy = int(self.home_tab.action_image_right_bottom_y_var.get() or 0)
                if lux < 0 or luy < 0 or rdx < 0 or rdy < 0:
                    errors.append("图像坐标不能为负数")
                if rdx <= lux or rdy <= luy:
                    errors.append("右下角坐标必须大于左上角坐标")
            except ValueError:
                errors.append("图像坐标必须是整数")
        
        elif action_type == "function":
            if not self.home_tab.function_name_var.get().strip():
                errors.append("函数名不能为空")
        
        return errors
    
    def get_action_summary(self):
        """获取行为摘要信息"""
        action_type = self.home_tab.action_type_var.get()
        action_name = self.home_tab.action_name_var.get().strip()
        
        summary = f"行为名称: {action_name}\n行为类型: {action_type}"
        
        if action_type == "mouse":
            action_text = self.home_tab.action_mouse_action_type_var.get()
            x = self.home_tab.action_mouse_x_var.get()
            y = self.home_tab.action_mouse_y_var.get()
            summary += f"\n鼠标动作: {action_text}\n坐标: ({x}, {y})"
        
        elif action_type == "keyboard":
            action_text = self.home_tab.action_keyboard_type_var.get()
            value = self.home_tab.action_keyboard_value_var.get()
            summary += f"\n键盘动作: {action_text}\n值: {value}"
        
        elif action_type == "class":
            class_name = self.home_tab.class_name_var.get()
            summary += f"\n类名: {class_name}"
        
        elif action_type == "AI":
            train_group = self.home_tab.ai_train_group_var.get()
            summary += f"\nAI训练组: {train_group}"
        
        elif action_type == "image":
            pic_name = self.home_tab.action_image_names_var.get()
            summary += f"\n图像名称: {pic_name}"
        
        elif action_type == "function":
            func_name = self.home_tab.function_name_var.get()
            summary += f"\n函数名: {func_name}"
        
        return summary

class ActionGroupManager:
    """行为组管理器 - 处理行为组相关的数据库操作"""
    
    def __init__(self, home_tab):
        self.home_tab = home_tab
        self._session = None
    
    def _get_session(self, force_refresh=False):
        """获取数据库会话
        
        Args:
            force_refresh: 是否强制刷新session，用于数据库表结构更新后重新创建session
            
        Returns:
            session: 数据库会话对象，失败时返回None
        """
        try:
            # 如果需要强制刷新或session不存在，则创建新的session
            if force_refresh or not self._session:
                # 如果存在旧session，先关闭它
                if self._session:
                    try:
                        self._session.close()
                    except Exception as e:
                        print(f"Warning: Error closing old session: {e}")
                    self._session = None
                
                # 创建新的session
                config = ConfigManager()
                db_url = config.get_value('System', 'DataSource')
                encryption_key = config.get_value('Security', 'DBEncryptionKey')
                
                if not db_url or not encryption_key:
                    print("Error: Database configuration incomplete")
                    return None
                    
                db_manager = DatabaseManager(db_url, encryption_key)
                db_manager.initialize()
                self._session = db_manager.Session()
                
            return self._session
            
        except Exception as e:
            print(f"Error getting database session: {e}")
            # 如果创建session失败，清空缓存
            self._session = None
            return None
    
    def _close_session(self):
        """关闭数据库会话"""
        if self._session:
            try:
                self._session.close()
                self._session = None
                print("Database session closed successfully")
            except Exception as e:
                print(f"Warning: Error closing session: {e}")
                self._session = None
    
    def refresh_session(self):
        """强制刷新数据库会话，用于数据库表结构更新后调用
        
        Returns:
            bool: 刷新是否成功
        """
        try:
            session = self._get_session(force_refresh=True)
            return session is not None
        except Exception as e:
            print(f"Error refreshing session: {e}")
            return False
    
    def is_session_valid(self):
        """检查当前session是否有效
        
        Returns:
            bool: session是否有效
        """
        if not self._session:
            return False
        
        try:
            # 尝试执行一个简单的查询来验证session是否有效
            self._session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Session validation failed: {e}")
            # session无效，清空缓存
            self._session = None
            return False
    def get_current_class(self,class_action):
                    # 获取当前鼠标所在位置的应用信息
            
            # 获取当前鼠标位置
            x, y = win32api.GetCursorPos()
            
            # 获取鼠标位置下的窗口句柄
            window_handle = win32gui.WindowFromPoint((x, y))
            
            # 获取窗口类名
            current_class_name = win32gui.GetClassName(window_handle)
            
            # 获取窗口标题
            current_window_title = win32gui.GetWindowText(window_handle)
            
            logger.info(f"当前鼠标位置: ({x}, {y})")
            logger.info(f"当前窗口类名: {current_class_name}")
            logger.info(f"当前窗口标题: {current_window_title}")
            
            # 检查类名和窗口标题是否匹配
            if class_action.class_name or class_action.class_name != "":
                class_name_match = (current_class_name == class_action.class_name)
            else:
                class_name_match = True
            if class_action.windows_title or class_action.windows_title != "":
                window_title_match = (current_window_title == class_action.windows_title)
            else:
                window_title_match = True
            if class_name_match and window_title_match:
                logger.info("类名和窗口标题匹配成功")
                return True
            else:
                logger.info(f"匹配失败 - 期望类名: {class_action.class_name}, 窗口标题: {class_action.windows_title}")

    def get_action_group_data(self, sheet_name,group_id):
        """action专有的方法。获取行为组数据,sheet_name为ActionGroup或ActionsDebugGroup或ActionsSuitGroup。group_id为行为组id。"""
        # 首先检查session是否有效
        if not self.is_session_valid():
            # session无效，尝试刷新
            if not self.refresh_session():
                return None
        
        session = self._get_session(True)
        if not session:
            return None
            
        try:
            if sheet_name == "ActionGroup":
                # 获取行为组
                group = session.query(ActionGroup).filter_by(id=group_id).first()
                # 获取关联的层级信息
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=group.group_rank_id).first()
                # 获取行为列表
                actions = session.query(ActionList).filter_by(group_id=group_id).all()
            elif sheet_name == "ActionsDebugGroup":
                # 获取行为组
                group = session.query(ActionGroup).filter_by(id=group_id).first()
                # 获取关联的层级信息
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=group.group_rank_id).first()
                # 获取行为列表
                actions = session.query(ActionList).filter_by(group_id=group_id).all()
            elif sheet_name == "ActionsSuitGroup":
                # 获取行为组
                group = session.query(ActionsSuitGroup).filter_by(id=group_id).first()
                # 获取关联的层级信息
                hierarchy = session.query(ActionsSuitGroupHierarchy).filter_by(id=group.group_rank_id).first()
                # 获取行为列表
                actions = session.query(ActionList).filter_by(group_id=group_id).all()
            if not group:
                return None
            # 获取用户信息
            user = session.query(User).filter_by(user_id=group.user_id).first()
            return {
                'group': group,
                'hierarchy': hierarchy,
                'user': user,
                'actions': actions
            }
        except Exception as e:
            print(f"Error getting action group data: {e}")
            print(traceback.format_exc())
            # 如果是session相关错误，尝试刷新session
            if "session" in str(e).lower() or "connection" in str(e).lower():
                self.refresh_session()
            return None
        finally:
            if session:
                self._close_session()
    
    def get_hierarchy_data(self, hierarchy_rank):
        """获取层级数据"""
        session = self._get_session(True)
        if not session:
            return None
            
        try:
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(group_rank=hierarchy_rank).first()
            return hierarchy
        except Exception as e:
            print(f"Error getting hierarchy data: {e}")
            return None
    def get_list_hierarchy_data(self, hierarchy_rank,group_id):
        """获取层级数据"""
        session = self._get_session(True)
        if not session:
            return None
            
        try:
            hierarchy = session.query(ListGroupHierarchy).filter_by(list_rank=hierarchy_rank,group_id=group_id).first()
            return hierarchy
        except Exception as e:
            print(f"Error getting hierarchy data: {e}")
            return None
    def get_all_hierarchies(self):
        """获取所有行为组层级数据
        
        排序规则：
        1. 先按照父节点分组（相同父节点的记录归为一组）
        2. 在每个父节点组内按照sort_num排序
        
        Returns:
            list: 排序后的层级数据列表
        """
        session = self._get_session(True)
        if not session:
            return []
            
        try:
            # 获取所有层级数据
            hierarchies = session.query(ActionsGroupHierarchy).all()
            
            # 按照父节点分组，然后在每组内按sort_num排序
            sorted_hierarchies = self._sort_hierarchies_by_parent_and_sort(hierarchies)
            
            return sorted_hierarchies
        except Exception as e:
            print(f"Error getting all hierarchies: {e}")
            return []
    
    def _sort_hierarchies_by_parent_and_sort(self, hierarchies):
        """按照父节点分组，然后在每组内按sort_num排序
        
        Args:
            hierarchies: 层级数据列表
            
        Returns:
            list: 排序后的层级数据列表
        """
        try:
            # 解析每个层级的父节点
            hierarchy_groups = {}
            
            for hierarchy in hierarchies:
                rank_dict = parse_group_rank(hierarchy.group_rank)#解析group_rank字典
                parent_key = self._get_parent_key(rank_dict)
                
                if parent_key not in hierarchy_groups:
                    hierarchy_groups[parent_key] = []
                
                hierarchy_groups[parent_key].append(hierarchy)
            
            # 对每个父节点组内的记录按sort_num排序
            for parent_key in hierarchy_groups:
                hierarchy_groups[parent_key].sort(key=lambda x: x.sort_num)
            
            # 按照父节点key排序，然后合并所有组
            sorted_parent_keys = sorted(hierarchy_groups.keys())
            sorted_hierarchies = []
            
            for parent_key in sorted_parent_keys:
                sorted_hierarchies.extend(hierarchy_groups[parent_key])
            
            return sorted_hierarchies
            
        except Exception as e:
            print(f"Error sorting hierarchies: {e}")
            # 如果排序失败，返回原始列表
            return hierarchies
    
    def _get_parent_key(self, rank_dict):
        """获取父节点key
        
        Args:
            rank_dict: 解析后的group_rank字典
            
        Returns:
            str: 父节点key,也就是iid
        """
        # 根据层级确定父节点
        if rank_dict['E'] > 0:
            # E有值，父节点是D
            return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}"
        elif rank_dict['D'] > 0:
            # D有值，父节点是C
            return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}"
        elif rank_dict['C'] > 0:
            # C有值，父节点是B
            return f"A{rank_dict['A']}B{rank_dict['B']}"
        elif rank_dict['B'] > 0:
            # B有值，父节点是A
            return f"A{rank_dict['A']}"
        else:
            # A有值，这是顶级节点
            return f"A{rank_dict['A']}"
    
    def get_all_action_groups(self):
        """获取所有行为组数据"""
        session = self._get_session(True)
        if not session:
            return []
            
        try:
            groups = session.query(ActionGroup).all()
            return groups
        except Exception as e:
            print(f"Error getting all action groups: {e}")
            return []
    def run_action_group(self, group_id):
        """运行行为组"""
        self.group_id = group_id
        session = self._get_session(True)
        self.excel_value = None
        if not session:
            return False
        
        try:
            group = session.query(ActionGroup).filter_by(id=group_id).first()
            if not group:
                return False
            # 判断行为组中的excel_name、excel_sheet_num、excel_column是否为空
            if group.excel_name and group.excel_sheet_num and group.excel_column:
                # 读取excel文件
                excel_file = group.excel_name
                excel_sheet_num = group.excel_sheet_num
                excel_column = group.excel_column
                # 读取excel文件
                excel_data = pd.read_excel(excel_file, sheet_name=excel_sheet_num)
                # 获取excel文件的列
                excel_column_data = excel_data[excel_column]
                # 开始执行循环，直到excel_column_data.iloc[0]为空
                excel_loop_result = True
                while excel_column_data.iloc[0] is not None and excel_loop_result:
                    # 获取excel文件的值
                    self.excel_value = excel_column_data.iloc[0]
                    excel_loop_result = self.run_action(self.excel_value)
                    if excel_loop_result:
                        # 如果excel_loop_result为True，则在excel_column的下一列中输入"OK"
                        excel_column_data.iloc[1] = "OK"
                        continue
                    else:
                        # 如果excel_loop_result为False，则在excel_column的下一列中输入"NG"
                        excel_column_data.iloc[1] = "NG"
                        continue
            else:
                ls_result = self.run_action(self.group_id)
                if not ls_result:
                    return False
            #弹窗提示任务完成
            return True
        except Exception as e:
            self._close_session()
            print(f"Error running action group: {e}")
            print(traceback.format_exc())
            return False

    def run_action(self, excel_value):
        """执行行为列表"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取行为列表
            actions = session.query(ActionList).filter_by(group_id=self.group_id).all()  
            if not actions:
                return False
            action_loop_result = True
            #开始执行actions中的action,如果action.next_action_id为空，则下一个action按照顺序执行；如果action.next_action_id不为空，则跳转到next_action_id的action执行。
            # 创建一个索引来跟踪当前执行的action
            current_index = 0
            while current_index < len(actions):
                action = actions[current_index]
                
                # 根据action_type执行相应的操作
                if action.action_type == 'mouse':
                    action_loop_result = self.run_mouse_action(action.id)
                    logger.info(f"{action.action_name}:鼠标动作执行结果: {action_loop_result}")
                elif action.action_type == 'keyboard':
                    action_loop_result = self.run_keyboard_action(action.id)
                    logger.info(f"{action.action_name}:键盘动作执行结果: {action_loop_result}")
                elif action.action_type == 'code':
                    action_loop_result = self.run_code_action(action.id)
                    logger.info(f"{action.action_name}:代码动作执行结果: {action_loop_result}")
                elif action.action_type == 'class':
                    action_loop_result = self.run_class_action(action.id)
                    logger.info(f"{action.action_name}:类动作执行结果: {action_loop_result}")
                elif action.action_type == 'AI':
                    action_loop_result = self.run_AI_action(action.id)
                    logger.info(f"{action.action_name}:AI动作执行结果: {action_loop_result}")
                elif action.action_type == 'image':
                    action_loop_result = self.run_image_action(action.id)
                    logger.info(f"{action.action_name}:图像动作执行结果: {action_loop_result}")
                elif action.action_type == 'function':
                    action_loop_result = self.run_function_action(action.id)
                    logger.info(f"{action.action_name}:函数动作执行结果: {action_loop_result}")
                else:
                    return False
                
                # 检查执行结果
                if not action_loop_result:
                    return False
                
                # 处理下一个action
                if action.next_id and action.next_id != 'None':
                    # 如果有指定的下一个action_id，查找对应的action
                    next_action = session.query(ActionList).filter_by(id=action.next_id).first()
                    if not next_action:
                        return False
                    current_index = action.next_id
                else:
                    # 如果没有指定next_action_id，则按顺序执行下一个
                    current_index += 1
            
            return True
        except Exception as e:
            print(f"Error in run_action: {e}")
            return False

    def run_mouse_action(self, action_id):
        """执行鼠标动作"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取鼠标行为列表
            mouse_action = session.query(ActionMouse).filter_by(action_list_id=action_id).first()
            if not mouse_action:
                logger.error(f"鼠标动作列表不存在: {action_id}")
                return False
            #如果mouse_action.time_diff为空，则不等待
            if mouse_action.time_diff:
                time.sleep(mouse_action.time_diff)
            # 鼠标动作(1:左击,2:右击,3:左键按下,4:右键按下,5:左键释放,6:右键释放,7:滚轮动作)
            # 开始执行mouse_action
            if mouse_action.mouse_action == 1:
                # 开始执行click_action
                pyautogui.click(mouse_action.x,mouse_action.y)
                return True
            elif mouse_action.mouse_action == 2:
                # 开始执行右击
                pyautogui.rightClick(mouse_action.x,mouse_action.y)
                return True
            elif mouse_action.mouse_action == 3:
                # 开始执行左键按下
                pyautogui.mouseDown(mouse_action.x,mouse_action.y,button='left')
                return True
            elif mouse_action.mouse_action == 4:
                # 开始执行右键按下
                pyautogui.mouseDown(mouse_action.x,mouse_action.y,button='right')
                return True
            elif mouse_action.mouse_action == 5:
                # 开始执行左键释放
                pyautogui.mouseUp(mouse_action.x,mouse_action.y,button='left')
                return True
            elif mouse_action.mouse_action == 6:
                # 开始执行右键释放
                pyautogui.mouseUp(mouse_action.x,mouse_action.y,button='right')
                return True
            elif mouse_action.mouse_action == 7:
                # 开始执行滚轮动作
                pyautogui.scroll(mouse_action.mouse_size)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in run_mouse_action: {e}")
            print(traceback.format_exc())
            return False

    def run_keyboard_action(self, action_id):
        """执行键盘动作"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取键盘行为列表
            keyboard_action = session.query(ActionKeyboard).filter_by(action_list_id=action_id).first()
            if not keyboard_action:
                logger.error(f"键盘动作列表不存在: {action_id}")
                return False
            #如果keyboard_action.time_diff为空，则不等待
            if keyboard_action.time_diff:
                time.sleep(keyboard_action.time_diff)
            # 键盘类型(1:按下,2:释放,3:单击,4:文本)
            if keyboard_action.keyboard_type == 1:
                # 开始执行按下
                pyautogui.keyDown(keyboard_action.keyboard_value)
                return True
            elif keyboard_action.keyboard_type == 2:
                # 开始执行释放
                pyautogui.keyUp(keyboard_action.keyboard_value)
                return True
            elif keyboard_action.keyboard_type == 3:
                # 开始执行单击
                pyautogui.press(keyboard_action.keyboard_value)
                return True
            elif keyboard_action.keyboard_type == 4:
                # 开始执行文本
                pyautogui.write(keyboard_action.keyboard_value)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in run_keyboard_action: {e}")
            print(traceback.format_exc())
            return False

    def run_class_action(self, action_id):
        """执行类动作"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取类行为列表
            class_action = session.query(ActionClass).filter_by(action_list_id=action_id).first()
            if not class_action:
                logger.error(f"类动作列表不存在: {action_id}")
                return False
            #如果class_action.time_diff为空，则不等待
            if class_action.time_diff:
                time.sleep(class_action.time_diff)
            # 获取当前鼠标所在的位置所在的应用的类名，然后与class_action.class_name进行匹配
            if self.get_current_class(class_action):
                return True
            else:
                return False
        except Exception as e:
            print(f"Error in run_class_action: {e}")
            return False

    def run_AI_action(self, action_id):
        """执行AI动作"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取AI行为列表
            AI_action = session.query(ActionAI).filter_by(action_list_id=action_id).first()
            if not AI_action:
                logger.error(f"AI动作列表不存在: {action_id}")
                return False
            #如果AI_action.time_diff为空，则不等待
            if AI_action.time_diff:
                time.sleep(AI_action.time_diff)
            # 待完善
            return False
        except Exception as e:
            print(f"Error in run_AI_action: {e}")
            print(traceback.format_exc())
            return False

    def run_image_action(self, action_id):
        """执行图像动作"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取图像行为列表
            image_action = session.query(ActionPrintscreen).filter_by(action_list_id=action_id).first()
            if not image_action:
                logger.error(f"图像动作列表不存在: {action_id}")
                return False
            #如果image_action.time_diff为空，则不等待
            if image_action.time_diff:
                time.sleep(image_action.time_diff)
            # 开始执行截屏
            get_picture = pyautogui.screenshot(region=(image_action.lux,image_action.luy,image_action.rdx,image_action.rdy))
            # 如果image_action.match_picture_name不为空，则开始执行匹配图片
            if image_action.match_picture_name:
                # 先获取本地图片路径，本地图片路径为系统配置文件中sysfolder的值+Action_group+{user_id}+picture
                config = ConfigManager()
                local_picture_path = os.path.join(config.get_value('System', 'SysFolder'), r'\Action_group\{}\picture\{}'.format(globalvariable.USER_ID, image_action.match_picture_name))
                # 开始执行截图与本地图片匹配，如果匹配到，则开始执行鼠标动作
                try:
                    # 检查本地图片是否存在
                    if not os.path.exists(local_picture_path):
                        logger.error(f"本地匹配图片不存在: {local_picture_path}")
                        return False
                    
                    # 保存当前截图到临时文件用于匹配
                    temp_screenshot_path = os.path.join(os.path.dirname(local_picture_path), f"temp_screenshot_{int(time.time())}.png")
                    get_picture.save(temp_screenshot_path)
                    
                    logger.info(f"开始匹配图片: {image_action.match_picture_name}")
                    # 设置匹配置信度阈值
                    confidence = 0.8  # 可以根据需要调整匹配精度
                    
                    # 使用OpenCV进行更精确的图像匹配
                    import cv2
                    import numpy as np
                    
                    # 读取图像
                    template = cv2.imread(local_picture_path)
                    screenshot = cv2.imread(temp_screenshot_path)
                    
                    # 清理临时文件
                    try:
                        os.remove(temp_screenshot_path)
                    except:
                        pass
                    
                    if template is None or screenshot is None:
                        logger.error("无法读取图像文件")
                        return False
                    
                    # 执行模板匹配
                    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    # 设置匹配阈值
                    if max_val >= confidence:
                        logger.info(f"图片匹配成功，相似度: {max_val:.2f}")
                        # 根据鼠标动作类型执行相应操作
                        if image_action.mouse_action == 0:
                            # 无动作
                            return True
                        elif image_action.mouse_action == 1:
                            # 左击
                            pyautogui.click(pyautogui.locateCenterOnScreen(local_picture_path))
                            return True
                        elif image_action.mouse_action == 2:
                            # 右击
                            pyautogui.rightClick(pyautogui.locateCenterOnScreen(local_picture_path))
                            return True
                        elif image_action.mouse_action == 3:
                            # 左键按下
                            pyautogui.mouseDown(pyautogui.locateCenterOnScreen(local_picture_path),button='left')
                            return True
                        elif image_action.mouse_action == 4:
                            # 右键按下
                            pyautogui.mouseDown(pyautogui.locateCenterOnScreen(local_picture_path),button='right')
                            return True
                        elif image_action.mouse_action == 5:
                            # 左键释放
                            pyautogui.mouseUp(pyautogui.locateCenterOnScreen(local_picture_path),button='left')
                            return True
                        elif image_action.mouse_action == 6:
                            # 右键释放
                            pyautogui.mouseUp(pyautogui.locateCenterOnScreen(local_picture_path),button='right')
                            return True
                        elif image_action.mouse_action == 7:
                            # 滚轮动作
                            pyautogui.scroll(image_action.mouse_size)
                            return True
                        else:
                            return True
                    else:
                        logger.warning(f"图片匹配失败，相似度: {max_val:.2f}")
                        return False
                        
                except Exception as e:
                    logger.error(f"图像匹配失败: {e}")
                    return False
            # 如果image_action.match_text不为空，则开始执行匹配文本
            if image_action.match_text:
                # 先获取本地图片路径，本地图片路径为系统配置文件中sysfolder的值+Action_group+{user_id}+picture
                config = ConfigManager()
                local_picture_path = os.path.join(config.get_value('System', 'SysFolder'), r'\Action_group\{}\picture\{}'.format(globalvariable.USER_ID, image_action.match_picture_name))
                # 开始执行匹配文本
                try:
                    import easyocr
                    reader = easyocr.Reader(['chinese_simp', 'english'])
                    result = reader.readtext(get_picture)
                    
                    if result:
                        for item in result:
                            if item[1] == image_action.match_text:
                                # 计算文本区域坐标
                                bbox = item[0]
                                x_min = min(point[0] for point in bbox)
                                y_min = min(point[1] for point in bbox)
                                x_max = max(point[0] for point in bbox)
                                y_max = max(point[1] for point in bbox)
                                return (x_min, y_min, x_max, y_max)
                    return False
                except Exception as e:
                    logger.error(f"文本识别失败: {e}")
                    return False
            return True
        except Exception as e:
            print(f"Error in run_image_action: {e}")
            print(traceback.format_exc())
            return False

    def run_code_action(self, action_id):
        """执行代码动作"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取代码行为列表
            code_action = session.query(ActionCodeTxt).filter_by(action_list_id=action_id).first()
            if not code_action:
                logger.error(f"代码动作列表不存在: {action_id}")
                return False
            #如果code_action.time_diff为空，则不等待
            if code_action.time_diff:
                time.sleep(code_action.time_diff)
            # 执行代码文本
            # 这里可以添加代码执行逻辑
            return True
        except Exception as e:
            print(f"Error in run_code_action: {e}")
            print(traceback.format_exc())
            return False

    def run_function_action(self, action_id):
        """执行函数动作"""
        session = self._get_session(True)
        if not session:
            return False
            
        try:
            # 获取函数行为列表
            function_action = session.query(ActionFunction).filter_by(action_list_id=action_id).first()
            if not function_action:
                logger.error(f"函数动作列表不存在: {action_id}")
                return False
            #如果function_action.time_diff为空，则不等待
            if function_action.time_diff:
                time.sleep(function_action.time_diff)
            # 执行函数
            # 这里可以添加函数执行逻辑
            return True
        except Exception as e:
            print(f"Error in run_function_action: {e}")
            print(traceback.format_exc())
            return False

    def build_tree_structure(self, hierarchies):
        """构建树形结构数据"""
        tree_dict = {}
        
        for h in hierarchies:
            rank_dict = parse_group_rank(h.group_rank)
            key = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
            
            # 根据用户权限过滤
            if globalvariable.USER_IS_SUPER_ADMIN:
                tree_dict[key] = {
                    'obj': h,
                    'iid': None,
                    'children': [],
                    'parent': None
                }
            else:
                # 普通用户只能看到全局(A=2)或自己科室的层级
                if rank_dict['A'] == 2 or h.department_id == globalvariable.USER_DEPARTMENT_ID:
                    tree_dict[key] = {
                        'obj': h,
                        'iid': None,
                        'children': [],
                        'parent': None
                    }
        
        # 建立父子关系
        for key, node in tree_dict.items():
            rank = parse_group_rank(key)
            
            # 确定父节点key和当前节点iid
            if rank['E'] > 0:
                parent_key = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E0"
                parent_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E{rank['E']}"
            elif rank['D'] > 0:
                parent_key = f"A{rank['A']}B{rank['B']}C{rank['C']}D0E0"
                parent_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
            elif rank['C'] > 0:
                parent_key = f"A{rank['A']}B{rank['B']}C0D0E0"
                parent_iid = f"A{rank['A']}B{rank['B']}"
                node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}"
            elif rank['B'] > 0:
                parent_key = f"A{rank['A']}B0C0D0E0"
                parent_iid = f"A{rank['A']}"
                node['iid'] = f"A{rank['A']}B{rank['B']}"
            else:
                parent_key = None
                parent_iid = None
                node['iid'] = f"A{rank['A']}"
            
            # 设置父子关系
            if parent_key and parent_key in tree_dict:
                node['parent'] = parent_iid
                tree_dict[parent_key]['children'].append(key)
            else:
                node['parent'] = None
        
        return tree_dict
    
    def get_user_by_id(self, user_id):
        """根据用户ID获取用户信息"""
        session = self._get_session(True)
        if not session:
            return None
            
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            return user
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None
    
    def get_hierarchy_by_id(self, hierarchy_id):
        """根据层级ID获取层级信息"""
        # 首先检查session是否有效
        if not self.is_session_valid():
            # session无效，尝试刷新
            if not self.refresh_session():
                return None
        
        session = self._get_session(True)
        if not session:
            return None
            
        try:
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=hierarchy_id).first()
            return hierarchy
        except Exception as e:
            print(f"Error getting hierarchy by id: {e}")
            # 如果是session相关错误，尝试刷新session
            if "session" in str(e).lower() or "connection" in str(e).lower():
                self.refresh_session()
            return None
    
    def handle_database_schema_update(self):
        """处理数据库表结构更新后的操作
        
        当数据库表结构发生变化时，调用此方法可以：
        1. 强制刷新session以获取最新的表结构
        2. 清理可能存在的缓存数据
        3. 重新初始化相关组件
        
        Returns:
            bool: 操作是否成功
        """
        try:
            print("Handling database schema update...")
            
            # 强制刷新session
            if not self.refresh_session():
                print("Failed to refresh session after schema update")
                return False
            
            # 验证新session是否有效
            if not self.is_session_valid():
                print("New session is not valid after schema update")
                return False
            
            print("Database schema update handled successfully")
            return True
            
        except Exception as e:
            print(f"Error handling database schema update: {e}")
            return False