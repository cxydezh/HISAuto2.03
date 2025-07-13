import tkinter as tk
from tkinter import ttk, messagebox
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
import win32gui
import win32api
from database.db_manager import DatabaseManager
from config.config_manager import ConfigManager
from models.action_suit import (
    ActionsSuitGroup, ActionsSuitList, ActionsSuitGroupHierarchy,
    ActionSuitMouse, ActionSuitKeyboard, ActionSuitClass, ActionSuitAI, 
    ActionSuitPrintscreen, ActionSuitFunction, ActionSuitCodeTxt
)
from models.user import User
from models.department import Department
from gui.tabs.Hierarchyutils import parse_group_rank, iid_to_group_rank
import globalvariable
from utils.logger import Logger, logger
from utils.screenshot_tool import ScreenshotTool
from core.pic_capture import PicCapture

class SuitViewFunc:
    """用于支持suit_view.py中与组套相关的相关方法的实现"""
    
    def __init__(self, suit_view, action_group_id, current_action_id):
        """初始化组套视图功能类
        
        Args:
            suit_view: SuitView实例
            action_group_id: 行为组ID
            current_action_id: 当前行为ID
        """
        self.suit_view = suit_view
        self.action_group_id = action_group_id
        self.current_action_id = current_action_id
        self.session = None
        self.config_manager = ConfigManager()
        
    def _get_session(self):
        """获取数据库会话"""
        try:
            db_path = self.config_manager.get_value('System', 'DataSource')
            encryption_key = self.config_manager.get_value('Security', 'DBEncryptionKey')
            
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
    
    def _close_session(self):
        """关闭数据库会话"""
        if self.session:
            self.session.close()
            self.session = None
    
    def load_suit_tree(self):
        """加载组套树形数据 - 参考home_tab.py中的_refresh_action_group方法"""
        try:
            session = self._get_session()
            if not session:
                return False
            
            # 清空树
            for item in self.suit_view.suit_tree.get_children():
                self.suit_view.suit_tree.delete(item)
            
            # 获取所有组套层次数据
            hierarchies = session.query(ActionsSuitGroupHierarchy).order_by(ActionsSuitGroupHierarchy.sort_num).all()
            
            # 构建树形结构字典
            tree_dict = self._build_suit_tree_structure(hierarchies)
            
            # 递归插入节点到Treeview
            def insert_node(key, parent_iid):
                if key not in tree_dict:
                    return
                    
                node = tree_dict[key]
                h = node['obj']
                user = self._get_user_by_id(h.doctor_id)
                username = user.username if user else "未知"
                
                # 插入当前节点
                if parent_iid == "":
                    self.suit_view.suit_tree.insert("", "end", iid=node['iid'], text=h.group_name, 
                                                  values=(h.group_name, username))
                else:
                    self.suit_view.suit_tree.insert(parent_iid, "end", iid=node['iid'], text="📁", 
                                                  values=(h.group_name, username))
                
                # 递归插入子节点
                for child_key in node['children']:
                    insert_node(child_key, node['iid'])
            
            # 插入顶层节点（A级节点，B=C=D=E=0）
            inserted_nodes = set()  # 记录已插入的节点，避免重复
            
            # 首先插入A级节点（B=C=D=E=0）
            for key, node in tree_dict.items():
                rank = parse_group_rank(key)
                if (rank['B'] == 0 and rank['C'] == 0 and 
                    rank['D'] == 0 and rank['E'] == 0):
                    if key not in inserted_nodes:
                        insert_node(key, "")
                        inserted_nodes.add(key)
            
            # 查询所有组套，插入到对应层级下
            groups = session.query(ActionsSuitGroup).all()
            for group in groups:
                if not hasattr(group, 'group_rank_id') or not group.group_rank_id:
                    logger.error(f"组套 {group.action_list_group_name} 没有层次ID")
                    continue
                    
                # 获取组套对应的层级
                rank_record = session.query(ActionsSuitGroupHierarchy).filter_by(id=group.group_rank_id).first()
                if not rank_record:
                    logger.error(f"组套 {group.action_list_group_name} 没有对应的层次")
                    continue
                    
                rank_dict = parse_group_rank(rank_record.group_rank)
                
                # 确定组套应该插入到哪个层级节点下
                if rank_dict['E'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
                elif rank_dict['D'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}"
                elif rank_dict['C'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}"
                elif rank_dict['B'] > 0:
                    parent_iid = f"A{rank_dict['A']}B{rank_dict['B']}"
                else:
                    parent_iid = f"A{rank_dict['A']}"
                
                # 检查父节点是否存在
                try:
                    if self.suit_view.suit_tree.exists(parent_iid):
                        user = self._get_user_by_id(group.user_id)
                        username = user.username if user else "未知"
                        
                        # 插入组套节点
                        self.suit_view.suit_tree.insert(parent_iid, "end", text="📄", 
                                                      values=(group.action_list_group_name, username), 
                                                      iid=f"suit_{group.id}")
                    else: 
                        logger.error(f"父节点 {parent_iid} 不存在")
                except Exception as e:
                    logger.error(f"插入组套节点失败: {str(e)}")
            
            return True
        except Exception as e:
            logger.error(f"加载组套树形数据失败: {str(e)}")
            return False
        finally:
            self._close_session()
    
    def load_action_list(self, suit_id=None):
        """加载行为列表 - 参考home_tab.py中的_refresh_action_list方法"""
        try:
            session = self._get_session()
            if not session:
                return False
            
            # 清空现有数据
            for item in self.suit_view.action_list.get_children():
                self.suit_view.action_list.delete(item)
            
            if suit_id:
                # 加载指定组套下的行为列表
                actions = session.query(ActionsSuitList).filter_by(group_id=suit_id).all()
                
                for action in actions:
                    # 获取行为类型的中文描述
                    action_type_text = self._get_action_type_text(action.action_type)
                    
                    # 获取下一个行为的名称
                    next_action_name = ""
                    if action.next_id:
                        next_action = session.query(ActionsSuitList).filter_by(id=action.next_id).first()
                        if next_action:
                            next_action_name = next_action.action_name
                    
                    # 插入行为列表项
                    self.suit_view.action_list.insert("", "end", iid=str(action.id), values=(
                        action.id, 
                        action_type_text, 
                        action.action_name, 
                        next_action_name
                    ))
                
                logger.info(f"成功加载组套 {suit_id} 的行为列表，共 {len(actions)} 个行为")
            else:
                logger.info("清空行为列表")
            
            return True
        except Exception as e:
            logger.error(f"加载行为列表失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        finally:
            self._close_session()
    
    def _get_action_type_text(self, action_type):
        """获取行为类型的中文描述"""
        action_type_map = {
            "mouse": "鼠标操作",
            "keyboard": "键盘操作", 
            "class": "类操作",
            "ai": "AI操作",
            "image": "图像操作",
            "function": "函数操作",
            "code": "代码操作"
        }
        return action_type_map.get(action_type, action_type)
    
    def new_suit(self):
        """新建组套 - 参考home_tab.py中的_new_action_group方法"""
        try:
            selected = self.suit_view.suit_tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请先选择一个层次节点")
                return
            
            iid = selected[0]
            
            # 检查选中的是否是层次节点（不是组套节点）
            if iid.startswith("suit_"):
                messagebox.showwarning("提示", "请选择层次节点，而不是组套节点")
                return
            
            if iid in ("A0", "A1", "A2"):
                messagebox.showwarning("提示", "请选择具体的层次节点")
                return
            
            # 获取层次ID
            hierarchy = self._get_hierarchy_by_iid(iid)
            if not hierarchy:
                messagebox.showerror("错误", "未找到选中的层次节点")
                return
            
            # 清空表单
            self.clear_suit_form()
            
            # 设置新建模式
            self._set_suit_form_new_mode()
            
            # 保存当前层次ID
            self.current_hierarchy_id = hierarchy.id
            self.suit_group_hierarchy_rank = hierarchy.group_rank
            self.suit_group_hierarchy_id = hierarchy.id
            
            logger.info(f"开始新建组套，层次ID: {hierarchy.id}")
            messagebox.showinfo("提示", "请在表单中填写组套信息")
            
        except Exception as e:
            logger.error(f"新建组套失败: {str(e)}")
            messagebox.showerror("错误", f"新建组套失败: {str(e)}")
    
    def _set_suit_form_new_mode(self):
        """设置组套表单为新建模式"""
        try:
            # 启用表单控件
            self.suit_view.suit_name.config(state="normal")
            self.suit_view.suit_note.config(state="normal")
            
            # 设置按钮状态
            self._set_suit_buttons_new_mode()
            
        except Exception as e:
            logger.error(f"设置组套表单新建模式失败: {str(e)}")
    
    def _set_suit_buttons_new_mode(self):
        """设置组套相关按钮为新建模式"""
        try:
            # 这里可以根据实际的按钮控件名称进行调整
            if hasattr(self.suit_view, 'btn_new_suit'):
                self.suit_view.btn_new_suit.config(state='disabled')
            if hasattr(self.suit_view, 'btn_edit_suit'):
                self.suit_view.btn_edit_suit.config(state='disabled')
            if hasattr(self.suit_view, 'btn_save_suit'):
                self.suit_view.btn_save_suit.config(state='normal')
            if hasattr(self.suit_view, 'btn_delete_suit'):
                self.suit_view.btn_delete_suit.config(state='disabled')
                
        except Exception as e:
            logger.error(f"设置组套按钮新建模式失败: {str(e)}")
    
    def _get_hierarchy_by_iid(self, iid):
        """根据iid获取层次信息"""
        try:
            session = self._get_session()
            if not session:
                return None
            
            group_rank = iid_to_group_rank(iid)
            hierarchy = session.query(ActionsSuitGroupHierarchy).filter_by(group_rank=group_rank).first()
            return hierarchy
        except Exception as e:
            logger.error(f"获取层次信息失败: {str(e)}")
            return None
        finally:
            self._close_session()
    
    def edit_suit(self):
        """编辑组套 - 参考home_tab.py中的_edit_action_group方法"""
        try:
            selected = self.suit_view.suit_tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请先选择一个组套")
                return
            
            iid = selected[0]
            
            # 检查选中的是否是组套节点
            if not iid.startswith("suit_"):
                messagebox.showwarning("提示", "请选择组套节点进行编辑")
                return
            
            # 获取组套ID
            suit_id = int(iid.split("_")[1])
            
            # 加载组套数据
            if self.load_suit_data(suit_id):
                # 设置编辑模式
                self._set_suit_form_edit_mode()
                logger.info(f"开始编辑组套: {suit_id}")
            else:
                logger.error(f"加载组套数据失败: {suit_id}")
            
        except Exception as e:
            logger.error(f"编辑组套失败: {str(e)}")
            messagebox.showerror("错误", f"编辑组套失败: {str(e)}")
    
    def delete_suit(self):
        """删除组套 - 参考home_tab.py中的_delete_action_group方法"""
        try:
            selected = self.suit_view.suit_tree.selection()
            if not selected:
                messagebox.showwarning("提示", "请先选择一个组套")
                return
            
            iid = selected[0]
            
            # 检查选中的是否是组套节点
            if not iid.startswith("suit_"):
                messagebox.showwarning("提示", "请选择组套节点进行删除")
                return
            
            # 获取组套ID
            suit_id = int(iid.split("_")[1])
            
            # 获取组套信息用于确认
            session = self._get_session()
            if not session:
                return False
            
            group = session.query(ActionsSuitGroup).filter_by(id=suit_id).first()
            if not group:
                messagebox.showerror("错误", "未找到要删除的组套")
                return
            
            # 确认删除
            if not messagebox.askyesno("确认", f"确定要删除组套 '{group.action_list_group_name}' 吗？\n此操作不可恢复！"):
                return
            
            # 删除组套下的所有行为
            actions = session.query(ActionsSuitList).filter_by(group_id=suit_id).all()
            for action in actions:
                # 删除行为详细信息
                self._delete_action_detail(session, action.id, action.action_type)
                # 删除行为本身
                session.delete(action)
            
            # 删除组套
            session.delete(group)
            session.commit()
            
            messagebox.showinfo("提示", f"组套 '{group.action_list_group_name}' 删除成功")
            logger.info(f"组套删除成功: {group.action_list_group_name}")
            
            # 刷新数据
            self.refresh_data()
            self.clear_suit_form()
                
        except Exception as e:
            logger.error(f"删除组套失败: {str(e)}")
            messagebox.showerror("错误", f"删除组套失败: {str(e)}")
        finally:
            self._close_session()
    
    def _delete_action_detail(self, session, action_id, action_type):
        """删除行为详细信息"""
        try:
            if action_type == "mouse":
                detail = session.query(ActionSuitMouse).filter_by(action_list_id=action_id).first()
            elif action_type == "keyboard":
                detail = session.query(ActionSuitKeyboard).filter_by(action_list_id=action_id).first()
            elif action_type == "class":
                detail = session.query(ActionSuitClass).filter_by(action_list_id=action_id).first()
            elif action_type == "ai":
                detail = session.query(ActionSuitAI).filter_by(action_list_id=action_id).first()
            elif action_type == "image":
                detail = session.query(ActionSuitPrintscreen).filter_by(action_list_id=action_id).first()
            elif action_type == "function":
                detail = session.query(ActionSuitFunction).filter_by(action_list_id=action_id).first()
            elif action_type == "code":
                detail = session.query(ActionSuitCodeTxt).filter_by(action_list_id=action_id).first()
            else:
                return
            
            if detail:
                session.delete(detail)
                
        except Exception as e:
            logger.error(f"删除行为详细信息失败: {str(e)}")
    
    def save_suit(self):
        """保存组套 - 参考home_tab.py中的_save_action_group方法"""
        try:
            # 验证表单数据
            suit_name = self.suit_view.suit_name.get().strip()
            suit_note = self.suit_view.suit_note.get("1.0", tk.END).strip()
            
            if not suit_name:
                messagebox.showwarning("提示", "请输入组套名称")
                return
            
            session = self._get_session()
            if not session:
                return False
            
            # 检查是新建还是编辑
            if hasattr(self, 'current_suit_id') and self.current_suit_id:
                # 编辑模式
                group = session.query(ActionsSuitGroup).filter_by(id=self.current_suit_id).first()
                if group:
                    group.action_list_group_name = suit_name
                    group.action_list_group_note = suit_note
                    group.updated_at = datetime.now()
                    session.commit()
                    messagebox.showinfo("提示", "组套更新成功")
                    logger.info(f"组套更新成功: {suit_name}")
                else:
                    messagebox.showerror("错误", "未找到要更新的组套")
                    logger.error(f"未找到要更新的组套: {self.current_suit_id}")
            else:
                # 新建模式
                if not hasattr(self, 'current_hierarchy_id'):
                    messagebox.showerror("错误", "请先选择层次节点")
                    return
                
                # 获取最大排序号
                max_sort = session.query(ActionsSuitGroup).filter_by(
                    group_rank_id=self.current_hierarchy_id
                ).order_by(ActionsSuitGroup.sort_num.desc()).first()
                
                new_sort_num = (max_sort.sort_num + 1) if max_sort else 1
                
                new_group = ActionsSuitGroup(
                    action_list_group_name=suit_name,
                    action_list_group_note=suit_note,
                    group_rank_id=self.current_hierarchy_id,
                    sort_num=new_sort_num,
                    user_id=globalvariable.current_user_id,
                    department_id=globalvariable.current_department_id,
                    created_at=datetime.now()
                )
                session.add(new_group)
                session.commit()
                messagebox.showinfo("提示", "组套创建成功")
                logger.info(f"组套创建成功: {suit_name}")
            
            # 刷新数据
            self.refresh_data()
            self.clear_suit_form()
            
        except Exception as e:
            logger.error(f"保存组套失败: {str(e)}")
            messagebox.showerror("错误", f"保存组套失败: {str(e)}")
        finally:
            self._close_session()
    
    def load_suit_data(self, suit_id):
        """加载组套数据到表单:这里参考home_tab.py中的_refresh_action_group方法"""
        try:
            session = self._get_session()
            if not session:
                return False
            
            group = session.query(ActionsSuitGroup).filter_by(id=suit_id).first()
            if group:
                # 清空表单
                self.clear_suit_form()
                
                # 填充表单数据
                self.suit_view.suit_name.config(state="normal")
                self.suit_view.suit_name.delete(0, tk.END)
                self.suit_view.suit_name.insert(0, group.action_list_group_name or "")
                
                self.suit_view.suit_note.config(state="normal")
                self.suit_view.suit_note.delete("1.0", tk.END)
                self.suit_view.suit_note.insert("1.0", group.action_list_group_note or "")
                
                # 保存当前组套ID和相关信息
                self.current_suit_id = suit_id
                self.current_hierarchy_id = group.group_rank_id
                
                # 获取组套对应的层次信息
                if group.group_rank_id:
                    hierarchy = session.query(ActionsSuitGroupHierarchy).filter_by(id=group.group_rank_id).first()
                    if hierarchy:
                        self.suit_group_hierarchy_rank = hierarchy.group_rank
                        self.suit_group_hierarchy_id = hierarchy.id
                
                # 设置表单为编辑模式
                self._set_suit_form_edit_mode()
                
                # 加载该组套下的行为列表
                self.load_action_list(suit_id)
                
                # 启用相关控件
                self._set_suit_controls_state('normal')
                self._set_action_controls_state('normal')
                
                logger.info(f"成功加载组套数据: {group.action_list_group_name}")
                return True
            else:
                messagebox.showerror("错误", "未找到指定的组套")
                return False
                
        except Exception as e:
            logger.error(f"加载组套数据失败: {str(e)}")
            messagebox.showerror("错误", f"加载组套数据失败: {str(e)}")
            return False
        finally:
            self._close_session()
    
    def _set_suit_form_edit_mode(self):
        """设置组套表单为编辑模式"""
        try:
            # 启用表单控件
            self.suit_view.suit_name.config(state="normal")
            self.suit_view.suit_note.config(state="normal")
            
            # 设置按钮状态
            self._set_suit_buttons_edit_mode()
            
        except Exception as e:
            logger.error(f"设置组套表单编辑模式失败: {str(e)}")
    
    def _set_suit_buttons_edit_mode(self):
        """设置组套相关按钮为编辑模式"""
        try:
            # 这里可以根据实际的按钮控件名称进行调整
            # 示例：启用编辑相关按钮，禁用新建按钮
            if hasattr(self.suit_view, 'btn_new_suit'):
                self.suit_view.btn_new_suit.config(state='disabled')
            if hasattr(self.suit_view, 'btn_edit_suit'):
                self.suit_view.btn_edit_suit.config(state='disabled')
            if hasattr(self.suit_view, 'btn_save_suit'):
                self.suit_view.btn_save_suit.config(state='normal')
            if hasattr(self.suit_view, 'btn_delete_suit'):
                self.suit_view.btn_delete_suit.config(state='normal')
                
        except Exception as e:
            logger.error(f"设置组套按钮编辑模式失败: {str(e)}")
    
    def load_hierarchy_data(self, hierarchy_id):
        """加载层次数据到表单"""
        try:
            session = self._get_session()
            if not session:
                return False
            
            hierarchy = session.query(ActionsSuitGroupHierarchy).filter_by(id=hierarchy_id).first()
            if hierarchy:
                # 清空表单
                self.clear_suit_form()
                
                # 填充层次数据
                self.suit_view.suit_name.config(state="normal")
                self.suit_view.suit_name.delete(0, tk.END)
                self.suit_view.suit_name.insert(0, hierarchy.group_name or "")
                
                self.suit_view.suit_note.config(state="normal")
                self.suit_view.suit_note.delete("1.0", tk.END)
                self.suit_view.suit_note.insert("1.0", hierarchy.group_note or "")
                
                # 保存层次信息
                self.suit_group_hierarchy_id = hierarchy_id
                self.suit_group_hierarchy_rank = hierarchy.group_rank
                self.current_suit_id = None
                
                # 设置表单为只读模式
                self._set_suit_form_readonly_mode()
                
                # 清空行为列表
                self.load_action_list()
                
                # 禁用行为相关控件
                self._set_action_controls_state('disabled')
                
                logger.info(f"成功加载层次数据: {hierarchy.group_name}")
                return True
            else:
                messagebox.showerror("错误", "未找到指定的层次")
                return False
                
        except Exception as e:
            logger.error(f"加载层次数据失败: {str(e)}")
            messagebox.showerror("错误", f"加载层次数据失败: {str(e)}")
            return False
        finally:
            self._close_session()
    
    def _set_suit_form_readonly_mode(self):
        """设置组套表单为只读模式"""
        try:
            # 禁用表单控件
            self.suit_view.suit_name.config(state="disabled")
            self.suit_view.suit_note.config(state="disabled")
            
            # 设置按钮状态
            self._set_suit_buttons_readonly_mode()
            
        except Exception as e:
            logger.error(f"设置组套表单只读模式失败: {str(e)}")
    
    def _set_suit_buttons_readonly_mode(self):
        """设置组套相关按钮为只读模式"""
        try:
            # 这里可以根据实际的按钮控件名称进行调整
            if hasattr(self.suit_view, 'btn_new_suit'):
                self.suit_view.btn_new_suit.config(state='normal')
            if hasattr(self.suit_view, 'btn_edit_suit'):
                self.suit_view.btn_edit_suit.config(state='normal')
            if hasattr(self.suit_view, 'btn_save_suit'):
                self.suit_view.btn_save_suit.config(state='disabled')
            if hasattr(self.suit_view, 'btn_delete_suit'):
                self.suit_view.btn_delete_suit.config(state='disabled')
                
        except Exception as e:
            logger.error(f"设置组套按钮只读模式失败: {str(e)}")
    
    def clear_suit_form(self):
        """清空组套表单 - 参考home_tab.py中的_clear_action_group_info方法"""
        try:
            # 清空表单控件
            self.suit_view.suit_name.config(state="normal")
            self.suit_view.suit_name.delete(0, tk.END)
            self.suit_view.suit_name.config(state="disabled")
            
            self.suit_view.suit_note.config(state="normal")
            self.suit_view.suit_note.delete("1.0", tk.END)
            self.suit_view.suit_note.config(state="disabled")
            
            # 清空当前ID和状态
            if hasattr(self, 'current_suit_id'):
                delattr(self, 'current_suit_id')
            if hasattr(self, 'current_hierarchy_id'):
                delattr(self, 'current_hierarchy_id')
            if hasattr(self, 'suit_group_hierarchy_rank'):
                delattr(self, 'suit_group_hierarchy_rank')
            if hasattr(self, 'suit_group_hierarchy_id'):
                delattr(self, 'suit_group_hierarchy_id')
            if hasattr(self, 'suit_tree_selected_iid'):
                delattr(self, 'suit_tree_selected_iid')
            
            # 设置按钮为默认状态
            self._set_suit_buttons_default_mode()
            
            logger.info("组套表单已清空")
            
        except Exception as e:
            logger.error(f"清空组套表单失败: {str(e)}")
    
    def _set_suit_buttons_default_mode(self):
        """设置组套相关按钮为默认模式"""
        try:
            # 这里可以根据实际的按钮控件名称进行调整
            if hasattr(self.suit_view, 'btn_new_suit'):
                self.suit_view.btn_new_suit.config(state='normal')
            if hasattr(self.suit_view, 'btn_edit_suit'):
                self.suit_view.btn_edit_suit.config(state='disabled')
            if hasattr(self.suit_view, 'btn_save_suit'):
                self.suit_view.btn_save_suit.config(state='disabled')
            if hasattr(self.suit_view, 'btn_delete_suit'):
                self.suit_view.btn_delete_suit.config(state='disabled')
                
        except Exception as e:
            logger.error(f"设置组套按钮默认模式失败: {str(e)}")
    
    def refresh_data(self):
        """刷新数据 - 参考home_tab.py中的_refresh_action_group方法"""
        try:
            logger.info("开始刷新组套数据")
            
            # 刷新组套树形数据
            if self.load_suit_tree():
                logger.info("组套树形数据刷新成功")
            else:
                logger.error("组套树形数据刷新失败")
            
            # 刷新行为列表
            if hasattr(self, 'current_suit_id') and self.current_suit_id:
                if self.load_action_list(self.current_suit_id):
                    logger.info("行为列表刷新成功")
                else:
                    logger.error("行为列表刷新失败")
            else:
                # 清空行为列表
                self.load_action_list()
            
            logger.info("组套数据刷新完成")
            
        except Exception as e:
            logger.error(f"刷新数据失败: {str(e)}")
            messagebox.showerror("错误", f"刷新数据失败: {str(e)}")
    
    def on_suit_select(self, event):
        """组套选择事件处理 - 参考home_tab.py中的_on_action_tree_select方法"""
        try:
            selected = self.suit_view.suit_tree.selection()
            if not selected:
                return
            
            iid = selected[0]
            self.suit_tree_selected_iid = iid
            
            # 清空行为列表
            for item in self.suit_view.action_list.get_children():
                self.suit_view.action_list.delete(item)
            
            # 清空表单
            self.clear_suit_form()
            
            if iid in ("A0", "A1", "A2"):
                # 根节点，禁用相关控件
                self._set_suit_controls_state('disabled')
                self._set_action_controls_state('disabled')
                return
            
            try:
                if iid.startswith("suit_"):
                    # 选中的是组套（ActionsSuitGroup）
                    suit_id = int(iid.split("_")[1])
                    
                    # 使用改进的load_suit_data方法加载组套数据
                    if self.load_suit_data(suit_id):
                        logger.info(f"成功选择组套: {suit_id}")
                    else:
                        logger.error(f"加载组套数据失败: {suit_id}")
                    
                else:
                    # 选中的是组套层次（ActionsSuitGroupHierarchy）
                    selected_group_rank = iid_to_group_rank(iid)
                    self.suit_group_hierarchy_rank = selected_group_rank
                    
                    # 获取层次数据
                    session = self._get_session()
                    if not session:
                        return
                    
                    hierarchy = session.query(ActionsSuitGroupHierarchy).filter_by(group_rank=selected_group_rank).first()
                    if hierarchy:
                        # 使用改进的load_hierarchy_data方法加载层次数据
                        if self.load_hierarchy_data(hierarchy.id):
                            logger.info(f"成功选择层次: {hierarchy.group_name}")
                        else:
                            logger.error(f"加载层次数据失败: {hierarchy.id}")
                    else:
                        logger.error(f"未找到层次数据: {selected_group_rank}")
                    
                    self._close_session()
                
            except Exception as e:
                logger.error(f"处理组套选择事件失败: {str(e)}")
                messagebox.showerror("错误", f"处理组套选择事件失败: {str(e)}")
                
        except Exception as e:
            logger.error(f"组套选择事件处理失败: {str(e)}")
            messagebox.showerror("错误", f"组套选择事件处理失败: {str(e)}")
    
    def _set_suit_controls_state(self, state):
        """设置组套相关控件的状态"""
        try:
            # 设置组套表单控件的状态
            if state == 'normal':
                self.suit_view.suit_name.config(state="normal")
                self.suit_view.suit_note.config(state="normal")
            else:
                self.suit_view.suit_name.config(state="disabled")
                self.suit_view.suit_note.config(state="disabled")
        except Exception as e:
            logger.error(f"设置组套控件状态失败: {str(e)}")
    
    def _set_action_controls_state(self, state):
        """设置行为相关控件的状态"""
        try:
            # 设置行为表单控件的状态
            if state == 'normal':
                self.suit_view.action_name.config(state="normal")
                self.suit_view.next_id.config(state="normal")
                self.suit_view.debug_id.config(state="normal")
            else:
                self.suit_view.action_name.config(state="disabled")
                self.suit_view.next_id.config(state="disabled")
                self.suit_view.debug_id.config(state="disabled")
        except Exception as e:
            logger.error(f"设置行为控件状态失败: {str(e)}")
    
    def on_action_select(self, event):
        """行为选择事件处理 - 参考home_tab.py中的_on_action_list_select方法"""
        try:
            selected = self.suit_view.action_list.selection()
            if selected:
                action_item = selected[0]
                action_id = int(self.suit_view.action_list.item(action_item, "values")[0])
                
                # 使用改进的load_action_data方法加载行为数据
                if self.load_action_data(action_id):
                    logger.info(f"成功选择行为: {action_id}")
                else:
                    logger.error(f"加载行为数据失败: {action_id}")
            else:
                # 清空表单
                self.clear_action_form()
                
        except Exception as e:
            logger.error(f"行为选择事件处理失败: {str(e)}")
            messagebox.showerror("错误", f"行为选择事件处理失败: {str(e)}")
    
    def load_action_data(self, action_id):
        """加载行为数据到表单 - 参考home_tab.py中的_fill_action_data方法"""
        try:
            session = self._get_session()
            if not session:
                return False
            
            action = session.query(ActionsSuitList).filter_by(id=action_id).first()
            if action:
                # 清空表单
                self.clear_action_form()
                
                # 填充行为基本信息
                self.suit_view.action_type_var.set(action.action_type)
                self.suit_view.action_name.delete(0, tk.END)
                self.suit_view.action_name.insert(0, action.action_name or "")
                self.suit_view.next_id.delete(0, tk.END)
                self.suit_view.next_id.insert(0, str(action.next_id) if action.next_id else "")
                self.suit_view.debug_id.delete(0, tk.END)
                self.suit_view.debug_id.insert(0, str(action.debug_group_id) if action.debug_group_id else "")
                
                # 保存当前行为ID
                self.current_action_id = action_id
                
                # 根据行为类型加载详细信息
                self.load_action_detail_data(action)
                
                # 设置表单为编辑模式
                self._set_action_form_edit_mode()
                
                logger.info(f"成功加载行为数据: {action.action_name}")
                return True
            else:
                messagebox.showerror("错误", "未找到指定的行为")
                return False
                
        except Exception as e:
            logger.error(f"加载行为数据失败: {str(e)}")
            messagebox.showerror("错误", f"加载行为数据失败: {str(e)}")
            return False
        finally:
            self._close_session()
    
    def _set_action_form_edit_mode(self):
        """设置行为表单为编辑模式"""
        try:
            # 启用表单控件
            self.suit_view.action_name.config(state="normal")
            self.suit_view.next_id.config(state="normal")
            self.suit_view.debug_id.config(state="normal")
            
            # 设置按钮状态
            self._set_action_buttons_edit_mode()
            
        except Exception as e:
            logger.error(f"设置行为表单编辑模式失败: {str(e)}")
    
    def _set_action_buttons_edit_mode(self):
        """设置行为相关按钮为编辑模式"""
        try:
            # 这里可以根据实际的按钮控件名称进行调整
            if hasattr(self.suit_view, 'btn_new_action'):
                self.suit_view.btn_new_action.config(state='disabled')
            if hasattr(self.suit_view, 'btn_edit_action'):
                self.suit_view.btn_edit_action.config(state='disabled')
            if hasattr(self.suit_view, 'btn_save_action'):
                self.suit_view.btn_save_action.config(state='normal')
            if hasattr(self.suit_view, 'btn_delete_action'):
                self.suit_view.btn_delete_action.config(state='normal')
                
        except Exception as e:
            logger.error(f"设置行为按钮编辑模式失败: {str(e)}")
    
    def load_action_detail_data(self, action):
        """加载行为详细信息 - 参考home_tab.py中的_fill_action_data方法"""
        try:
            session = self._get_session()
            if not session:
                return False
            
            if action.action_type == "mouse":
                mouse_action = session.query(ActionSuitMouse).filter_by(action_list_id=action.id).first()
                if mouse_action:
                    # 填充鼠标行为数据
                    self._fill_mouse_action_data(mouse_action)
                    
            elif action.action_type == "keyboard":
                keyboard_action = session.query(ActionSuitKeyboard).filter_by(action_list_id=action.id).first()
                if keyboard_action:
                    # 填充键盘行为数据
                    self._fill_keyboard_action_data(keyboard_action)
                    
            elif action.action_type == "class":
                class_action = session.query(ActionSuitClass).filter_by(action_list_id=action.id).first()
                if class_action:
                    # 填充类行为数据
                    self._fill_class_action_data(class_action)
                    
            elif action.action_type == "ai":
                ai_action = session.query(ActionSuitAI).filter_by(action_list_id=action.id).first()
                if ai_action:
                    # 填充AI行为数据
                    self._fill_ai_action_data(ai_action)
                    
            elif action.action_type == "image":
                image_action = session.query(ActionSuitPrintscreen).filter_by(action_list_id=action.id).first()
                if image_action:
                    # 填充图像行为数据
                    self._fill_image_action_data(image_action)
                    
            elif action.action_type == "function":
                function_action = session.query(ActionSuitFunction).filter_by(action_list_id=action.id).first()
                if function_action:
                    # 填充函数行为数据
                    self._fill_function_action_data(function_action)
                    
            elif action.action_type == "code":
                code_action = session.query(ActionSuitCodeTxt).filter_by(action_list_id=action.id).first()
                if code_action:
                    # 填充代码行为数据
                    self._fill_code_action_data(code_action)
            
            logger.info(f"成功加载行为详细信息: {action.action_type}")
            
        except Exception as e:
            logger.error(f"加载行为详细信息失败: {str(e)}")
        finally:
            self._close_session()
    
    def _fill_mouse_action_data(self, mouse_action):
        """填充鼠标行为数据"""
        try:
            # 这里需要根据实际的控件名称进行调整
            if hasattr(self.suit_view, 'mouse_action_var'):
                self.suit_view.mouse_action_var.set(self._mouse_action_to_text(mouse_action.mouse_action))
            if hasattr(self.suit_view, 'mouse_x_entry'):
                self.suit_view.mouse_x_entry.delete(0, tk.END)
                self.suit_view.mouse_x_entry.insert(0, str(mouse_action.mouse_x) if mouse_action.mouse_x else "")
            if hasattr(self.suit_view, 'mouse_y_entry'):
                self.suit_view.mouse_y_entry.delete(0, tk.END)
                self.suit_view.mouse_y_entry.insert(0, str(mouse_action.mouse_y) if mouse_action.mouse_y else "")
            if hasattr(self.suit_view, 'mouse_size_entry'):
                self.suit_view.mouse_size_entry.delete(0, tk.END)
                self.suit_view.mouse_size_entry.insert(0, str(mouse_action.mouse_size) if mouse_action.mouse_size else "")
            if hasattr(self.suit_view, 'mouse_time_entry'):
                self.suit_view.mouse_time_entry.delete(0, tk.END)
                self.suit_view.mouse_time_entry.insert(0, str(mouse_action.time_diff) if mouse_action.time_diff else "")
        except Exception as e:
            logger.error(f"填充鼠标行为数据失败: {str(e)}")
    
    def _fill_keyboard_action_data(self, keyboard_action):
        """填充键盘行为数据"""
        try:
            # 这里需要根据实际的控件名称进行调整
            if hasattr(self.suit_view, 'keyboard_type_var'):
                self.suit_view.keyboard_type_var.set(self._keyboard_type_to_text(keyboard_action.keyboard_type))
            if hasattr(self.suit_view, 'keyboard_text_entry'):
                self.suit_view.keyboard_text_entry.delete(0, tk.END)
                self.suit_view.keyboard_text_entry.insert(0, keyboard_action.keyboard_text or "")
            if hasattr(self.suit_view, 'keyboard_time_entry'):
                self.suit_view.keyboard_time_entry.delete(0, tk.END)
                self.suit_view.keyboard_time_entry.insert(0, str(keyboard_action.time_diff) if keyboard_action.time_diff else "")
        except Exception as e:
            logger.error(f"填充键盘行为数据失败: {str(e)}")
    
    def _fill_class_action_data(self, class_action):
        """填充类行为数据"""
        try:
            # 这里需要根据实际的控件名称进行调整
            if hasattr(self.suit_view, 'class_name_entry'):
                self.suit_view.class_name_entry.delete(0, tk.END)
                self.suit_view.class_name_entry.insert(0, class_action.class_name or "")
            if hasattr(self.suit_view, 'class_method_entry'):
                self.suit_view.class_method_entry.delete(0, tk.END)
                self.suit_view.class_method_entry.insert(0, class_action.class_method or "")
            if hasattr(self.suit_view, 'class_time_entry'):
                self.suit_view.class_time_entry.delete(0, tk.END)
                self.suit_view.class_time_entry.insert(0, str(class_action.time_diff) if class_action.time_diff else "")
        except Exception as e:
            logger.error(f"填充类行为数据失败: {str(e)}")
    
    def _fill_ai_action_data(self, ai_action):
        """填充AI行为数据"""
        try:
            # 这里需要根据实际的控件名称进行调整
            if hasattr(self.suit_view, 'ai_prompt_entry'):
                self.suit_view.ai_prompt_entry.delete(0, tk.END)
                self.suit_view.ai_prompt_entry.insert(0, ai_action.ai_prompt or "")
            if hasattr(self.suit_view, 'ai_time_entry'):
                self.suit_view.ai_time_entry.delete(0, tk.END)
                self.suit_view.ai_time_entry.insert(0, str(ai_action.time_diff) if ai_action.time_diff else "")
        except Exception as e:
            logger.error(f"填充AI行为数据失败: {str(e)}")
    
    def _fill_image_action_data(self, image_action):
        """填充图像行为数据"""
        try:
            # 这里需要根据实际的控件名称进行调整
            if hasattr(self.suit_view, 'image_action_var'):
                self.suit_view.image_action_var.set(self._mouse_action_to_text(image_action.mouse_action))
            if hasattr(self.suit_view, 'image_path_entry'):
                self.suit_view.image_path_entry.delete(0, tk.END)
                self.suit_view.image_path_entry.insert(0, image_action.match_picture_name or "")
            if hasattr(self.suit_view, 'image_threshold_entry'):
                self.suit_view.image_threshold_entry.delete(0, tk.END)
                self.suit_view.image_threshold_entry.insert(0, str(image_action.match_threshold) if image_action.match_threshold else "")
            if hasattr(self.suit_view, 'image_text_entry'):
                self.suit_view.image_text_entry.delete(0, tk.END)
                self.suit_view.image_text_entry.insert(0, image_action.match_text or "")
            if hasattr(self.suit_view, 'image_time_entry'):
                self.suit_view.image_time_entry.delete(0, tk.END)
                self.suit_view.image_time_entry.insert(0, str(image_action.time_diff) if image_action.time_diff else "")
        except Exception as e:
            logger.error(f"填充图像行为数据失败: {str(e)}")
    
    def _fill_function_action_data(self, function_action):
        """填充函数行为数据"""
        try:
            # 这里需要根据实际的控件名称进行调整
            if hasattr(self.suit_view, 'function_name_entry'):
                self.suit_view.function_name_entry.delete(0, tk.END)
                self.suit_view.function_name_entry.insert(0, function_action.function_name or "")
            if hasattr(self.suit_view, 'function_params_entry'):
                self.suit_view.function_params_entry.delete(0, tk.END)
                self.suit_view.function_params_entry.insert(0, function_action.function_params or "")
            if hasattr(self.suit_view, 'function_time_entry'):
                self.suit_view.function_time_entry.delete(0, tk.END)
                self.suit_view.function_time_entry.insert(0, str(function_action.time_diff) if function_action.time_diff else "")
        except Exception as e:
            logger.error(f"填充函数行为数据失败: {str(e)}")
    
    def _fill_code_action_data(self, code_action):
        """填充代码行为数据"""
        try:
            # 这里需要根据实际的控件名称进行调整
            if hasattr(self.suit_view, 'code_text_entry'):
                self.suit_view.code_text_entry.delete(0, tk.END)
                self.suit_view.code_text_entry.insert(0, code_action.code_text or "")
            if hasattr(self.suit_view, 'code_time_entry'):
                self.suit_view.code_time_entry.delete(0, tk.END)
                self.suit_view.code_time_entry.insert(0, str(code_action.time_diff) if code_action.time_diff else "")
        except Exception as e:
            logger.error(f"填充代码行为数据失败: {str(e)}")
    
    def _mouse_action_to_text(self, action_code):
        """将鼠标动作代码转换为文本"""
        action_map = {
            1: "左击",
            2: "右击", 
            3: "左键按下",
            4: "右键按下",
            5: "左键释放",
            6: "右键释放",
            7: "滚轮动作"
        }
        return action_map.get(action_code, str(action_code))
    
    def _keyboard_type_to_text(self, type_code):
        """将键盘类型代码转换为文本"""
        type_map = {
            1: "输入文本",
            2: "按键",
            3: "组合键"
        }
        return type_map.get(type_code, str(type_code))
    
    def save_action(self):
        """保存行为 - 参考home_tab.py中的_save_action方法"""
        try:
            # 验证表单数据
            action_type = self.suit_view.action_type_var.get()
            action_name = self.suit_view.action_name.get().strip()
            
            if not action_type or not action_name:
                messagebox.showwarning("提示", "请填写行为类型和名称")
                return
            
            session = self._get_session()
            if not session:
                return False
            
            # 检查是新建还是编辑
            if hasattr(self, 'current_action_id') and self.current_action_id:
                # 编辑模式
                action = session.query(ActionsSuitList).filter_by(id=self.current_action_id).first()
                if action:
                    action.action_type = action_type
                    action.action_name = action_name
                    action.next_id = int(self.suit_view.next_id.get()) if self.suit_view.next_id.get() else None
                    action.debug_group_id = int(self.suit_view.debug_id.get()) if self.suit_view.debug_id.get() else None
                    action.updated_at = datetime.now()
                    
                    # 保存行为详细信息
                    self._save_action_detail(session, action.id, action_type)
                    
                    session.commit()
                    messagebox.showinfo("提示", "行为更新成功")
                    logger.info(f"行为更新成功: {action_name}")
                else:
                    messagebox.showerror("错误", "未找到要更新的行为")
                    logger.error(f"未找到要更新的行为: {self.current_action_id}")
            else:
                # 新建模式
                if not hasattr(self, 'current_suit_id') or not self.current_suit_id:
                    messagebox.showerror("错误", "请先选择组套")
                    return
                
                # 获取最大排序号
                max_sort = session.query(ActionsSuitList).filter_by(group_id=self.current_suit_id).order_by(ActionsSuitList.sort_num.desc()).first()
                new_sort_num = (max_sort.sort_num + 1) if max_sort else 1
                
                new_action = ActionsSuitList(
                    group_id=self.current_suit_id,
                    action_type=action_type,
                    action_name=action_name,
                    next_id=int(self.suit_view.next_id.get()) if self.suit_view.next_id.get() else None,
                    debug_group_id=int(self.suit_view.debug_id.get()) if self.suit_view.debug_id.get() else None,
                    sort_num=new_sort_num,
                    created_at=datetime.now()
                )
                session.add(new_action)
                session.flush()  # 获取新创建的ID
                
                # 保存行为详细信息
                self._save_action_detail(session, new_action.id, action_type)
                
                session.commit()
                messagebox.showinfo("提示", "行为创建成功")
                logger.info(f"行为创建成功: {action_name}")
            
            # 刷新数据
            self.refresh_data()
            
        except Exception as e:
            logger.error(f"保存行为失败: {str(e)}")
            messagebox.showerror("错误", f"保存行为失败: {str(e)}")
        finally:
            self._close_session()
    
    def _save_action_detail(self, session, action_id, action_type):
        """保存行为详细信息"""
        try:
            if action_type == "mouse":
                self._save_mouse_action_detail(session, action_id)
            elif action_type == "keyboard":
                self._save_keyboard_action_detail(session, action_id)
            elif action_type == "class":
                self._save_class_action_detail(session, action_id)
            elif action_type == "ai":
                self._save_ai_action_detail(session, action_id)
            elif action_type == "image":
                self._save_image_action_detail(session, action_id)
            elif action_type == "function":
                self._save_function_action_detail(session, action_id)
            elif action_type == "code":
                self._save_code_action_detail(session, action_id)
                
        except Exception as e:
            logger.error(f"保存行为详细信息失败: {str(e)}")
    
    def _save_mouse_action_detail(self, session, action_id):
        """保存鼠标行为详细信息"""
        try:
            # 检查是否已存在
            mouse_action = session.query(ActionSuitMouse).filter_by(action_list_id=action_id).first()
            
            # 获取表单数据
            mouse_x = int(self.suit_view.mouse_x_entry.get()) if hasattr(self.suit_view, 'mouse_x_entry') and self.suit_view.mouse_x_entry.get() else None
            mouse_y = int(self.suit_view.mouse_y_entry.get()) if hasattr(self.suit_view, 'mouse_y_entry') and self.suit_view.mouse_y_entry.get() else None
            mouse_size = int(self.suit_view.mouse_size_entry.get()) if hasattr(self.suit_view, 'mouse_size_entry') and self.suit_view.mouse_size_entry.get() else None
            time_diff = float(self.suit_view.mouse_time_entry.get()) if hasattr(self.suit_view, 'mouse_time_entry') and self.suit_view.mouse_time_entry.get() else None
            
            if mouse_action:
                # 更新
                mouse_action.mouse_x = mouse_x
                mouse_action.mouse_y = mouse_y
                mouse_action.mouse_size = mouse_size
                mouse_action.time_diff = time_diff
            else:
                # 新建
                mouse_action = ActionSuitMouse(
                    action_list_id=action_id,
                    mouse_x=mouse_x,
                    mouse_y=mouse_y,
                    mouse_size=mouse_size,
                    time_diff=time_diff
                )
                session.add(mouse_action)
                
        except Exception as e:
            logger.error(f"保存鼠标行为详细信息失败: {str(e)}")
    
    def _save_keyboard_action_detail(self, session, action_id):
        """保存键盘行为详细信息"""
        try:
            # 检查是否已存在
            keyboard_action = session.query(ActionSuitKeyboard).filter_by(action_list_id=action_id).first()
            
            # 获取表单数据
            keyboard_text = self.suit_view.keyboard_text_entry.get() if hasattr(self.suit_view, 'keyboard_text_entry') else ""
            time_diff = float(self.suit_view.keyboard_time_entry.get()) if hasattr(self.suit_view, 'keyboard_time_entry') and self.suit_view.keyboard_time_entry.get() else None
            
            if keyboard_action:
                # 更新
                keyboard_action.keyboard_text = keyboard_text
                keyboard_action.time_diff = time_diff
            else:
                # 新建
                keyboard_action = ActionSuitKeyboard(
                    action_list_id=action_id,
                    keyboard_text=keyboard_text,
                    time_diff=time_diff
                )
                session.add(keyboard_action)
                
        except Exception as e:
            logger.error(f"保存键盘行为详细信息失败: {str(e)}")
    
    def _save_class_action_detail(self, session, action_id):
        """保存类行为详细信息"""
        try:
            # 检查是否已存在
            class_action = session.query(ActionSuitClass).filter_by(action_list_id=action_id).first()
            
            # 获取表单数据
            class_name = self.suit_view.class_name_entry.get() if hasattr(self.suit_view, 'class_name_entry') else ""
            class_method = self.suit_view.class_method_entry.get() if hasattr(self.suit_view, 'class_method_entry') else ""
            time_diff = float(self.suit_view.class_time_entry.get()) if hasattr(self.suit_view, 'class_time_entry') and self.suit_view.class_time_entry.get() else None
            
            if class_action:
                # 更新
                class_action.class_name = class_name
                class_action.class_method = class_method
                class_action.time_diff = time_diff
            else:
                # 新建
                class_action = ActionSuitClass(
                    action_list_id=action_id,
                    class_name=class_name,
                    class_method=class_method,
                    time_diff=time_diff
                )
                session.add(class_action)
                
        except Exception as e:
            logger.error(f"保存类行为详细信息失败: {str(e)}")
    
    def _save_ai_action_detail(self, session, action_id):
        """保存AI行为详细信息"""
        try:
            # 检查是否已存在
            ai_action = session.query(ActionSuitAI).filter_by(action_list_id=action_id).first()
            
            # 获取表单数据
            ai_prompt = self.suit_view.ai_prompt_entry.get() if hasattr(self.suit_view, 'ai_prompt_entry') else ""
            time_diff = float(self.suit_view.ai_time_entry.get()) if hasattr(self.suit_view, 'ai_time_entry') and self.suit_view.ai_time_entry.get() else None
            
            if ai_action:
                # 更新
                ai_action.ai_prompt = ai_prompt
                ai_action.time_diff = time_diff
            else:
                # 新建
                ai_action = ActionSuitAI(
                    action_list_id=action_id,
                    ai_prompt=ai_prompt,
                    time_diff=time_diff
                )
                session.add(ai_action)
                
        except Exception as e:
            logger.error(f"保存AI行为详细信息失败: {str(e)}")
    
    def _save_image_action_detail(self, session, action_id):
        """保存图像行为详细信息"""
        try:
            # 检查是否已存在
            image_action = session.query(ActionSuitPrintscreen).filter_by(action_list_id=action_id).first()
            
            # 获取表单数据
            match_picture_name = self.suit_view.image_path_entry.get() if hasattr(self.suit_view, 'image_path_entry') else ""
            match_threshold = float(self.suit_view.image_threshold_entry.get()) if hasattr(self.suit_view, 'image_threshold_entry') and self.suit_view.image_threshold_entry.get() else None
            match_text = self.suit_view.image_text_entry.get() if hasattr(self.suit_view, 'image_text_entry') else ""
            time_diff = float(self.suit_view.image_time_entry.get()) if hasattr(self.suit_view, 'image_time_entry') and self.suit_view.image_time_entry.get() else None
            
            if image_action:
                # 更新
                image_action.match_picture_name = match_picture_name
                image_action.match_threshold = match_threshold
                image_action.match_text = match_text
                image_action.time_diff = time_diff
            else:
                # 新建
                image_action = ActionSuitPrintscreen(
                    action_list_id=action_id,
                    match_picture_name=match_picture_name,
                    match_threshold=match_threshold,
                    match_text=match_text,
                    time_diff=time_diff
                )
                session.add(image_action)
                
        except Exception as e:
            logger.error(f"保存图像行为详细信息失败: {str(e)}")
    
    def _save_function_action_detail(self, session, action_id):
        """保存函数行为详细信息"""
        try:
            # 检查是否已存在
            function_action = session.query(ActionSuitFunction).filter_by(action_list_id=action_id).first()
            
            # 获取表单数据
            function_name = self.suit_view.function_name_entry.get() if hasattr(self.suit_view, 'function_name_entry') else ""
            function_params = self.suit_view.function_params_entry.get() if hasattr(self.suit_view, 'function_params_entry') else ""
            time_diff = float(self.suit_view.function_time_entry.get()) if hasattr(self.suit_view, 'function_time_entry') and self.suit_view.function_time_entry.get() else None
            
            if function_action:
                # 更新
                function_action.function_name = function_name
                function_action.function_params = function_params
                function_action.time_diff = time_diff
            else:
                # 新建
                function_action = ActionSuitFunction(
                    action_list_id=action_id,
                    function_name=function_name,
                    function_params=function_params,
                    time_diff=time_diff
                )
                session.add(function_action)
                
        except Exception as e:
            logger.error(f"保存函数行为详细信息失败: {str(e)}")
    
    def _save_code_action_detail(self, session, action_id):
        """保存代码行为详细信息"""
        try:
            # 检查是否已存在
            code_action = session.query(ActionSuitCodeTxt).filter_by(action_list_id=action_id).first()
            
            # 获取表单数据
            code_text = self.suit_view.code_text_entry.get() if hasattr(self.suit_view, 'code_text_entry') else ""
            time_diff = float(self.suit_view.code_time_entry.get()) if hasattr(self.suit_view, 'code_time_entry') and self.suit_view.code_time_entry.get() else None
            
            if code_action:
                # 更新
                code_action.code_text = code_text
                code_action.time_diff = time_diff
            else:
                # 新建
                code_action = ActionSuitCodeTxt(
                    action_list_id=action_id,
                    code_text=code_text,
                    time_diff=time_diff
                )
                session.add(code_action)
                
        except Exception as e:
            logger.error(f"保存代码行为详细信息失败: {str(e)}")
    
    def delete_action(self):
        """删除行为 - 参考home_tab.py中的_delete_action方法"""
        try:
            selected = self.suit_view.action_list.selection()
            if not selected:
                messagebox.showwarning("提示", "请先选择一个行为")
                return
            
            action_item = selected[0]
            action_id = int(self.suit_view.action_list.item(action_item, "values")[0])
            
            session = self._get_session()
            if not session:
                return False
            
            # 获取行为信息用于确认
            action = session.query(ActionsSuitList).filter_by(id=action_id).first()
            if not action:
                messagebox.showerror("错误", "未找到要删除的行为")
                return
            
            # 确认删除
            if not messagebox.askyesno("确认", f"确定要删除行为 '{action.action_name}' 吗？\n此操作不可恢复！"):
                return
            
            # 删除行为详细信息
            self._delete_action_detail(session, action_id, action.action_type)
            
            # 删除行为本身
            session.delete(action)
            session.commit()
            
            messagebox.showinfo("提示", f"行为 '{action.action_name}' 删除成功")
            logger.info(f"行为删除成功: {action.action_name}")
            
            # 刷新数据
            self.refresh_data()
            self.clear_action_form()
                
        except Exception as e:
            logger.error(f"删除行为失败: {str(e)}")
            messagebox.showerror("错误", f"删除行为失败: {str(e)}")
        finally:
            self._close_session()
    
    def clear_action_form(self):
        """清空行为表单 - 参考home_tab.py中的_clear_action_form方法"""
        try:
            # 清空基本信息
            self.suit_view.action_name.delete(0, tk.END)
            self.suit_view.next_id.delete(0, tk.END)
            self.suit_view.debug_id.delete(0, tk.END)
            
            # 清空详细信息控件
            self._clear_action_detail_controls()
            
            # 清空当前行为ID
            if hasattr(self, 'current_action_id'):
                delattr(self, 'current_action_id')
            
            # 设置按钮为默认状态
            self._set_action_buttons_default_mode()
            
            logger.info("行为表单已清空")
            
        except Exception as e:
            logger.error(f"清空行为表单失败: {str(e)}")
    
    def _clear_action_detail_controls(self):
        """清空行为详细信息控件"""
        try:
            # 清空鼠标行为控件
            if hasattr(self.suit_view, 'mouse_x_entry'):
                self.suit_view.mouse_x_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'mouse_y_entry'):
                self.suit_view.mouse_y_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'mouse_size_entry'):
                self.suit_view.mouse_size_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'mouse_time_entry'):
                self.suit_view.mouse_time_entry.delete(0, tk.END)
            
            # 清空键盘行为控件
            if hasattr(self.suit_view, 'keyboard_text_entry'):
                self.suit_view.keyboard_text_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'keyboard_time_entry'):
                self.suit_view.keyboard_time_entry.delete(0, tk.END)
            
            # 清空类行为控件
            if hasattr(self.suit_view, 'class_name_entry'):
                self.suit_view.class_name_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'class_method_entry'):
                self.suit_view.class_method_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'class_time_entry'):
                self.suit_view.class_time_entry.delete(0, tk.END)
            
            # 清空AI行为控件
            if hasattr(self.suit_view, 'ai_prompt_entry'):
                self.suit_view.ai_prompt_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'ai_time_entry'):
                self.suit_view.ai_time_entry.delete(0, tk.END)
            
            # 清空图像行为控件
            if hasattr(self.suit_view, 'image_path_entry'):
                self.suit_view.image_path_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'image_threshold_entry'):
                self.suit_view.image_threshold_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'image_text_entry'):
                self.suit_view.image_text_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'image_time_entry'):
                self.suit_view.image_time_entry.delete(0, tk.END)
            
            # 清空函数行为控件
            if hasattr(self.suit_view, 'function_name_entry'):
                self.suit_view.function_name_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'function_params_entry'):
                self.suit_view.function_params_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'function_time_entry'):
                self.suit_view.function_time_entry.delete(0, tk.END)
            
            # 清空代码行为控件
            if hasattr(self.suit_view, 'code_text_entry'):
                self.suit_view.code_text_entry.delete(0, tk.END)
            if hasattr(self.suit_view, 'code_time_entry'):
                self.suit_view.code_time_entry.delete(0, tk.END)
                
        except Exception as e:
            logger.error(f"清空行为详细信息控件失败: {str(e)}")
    
    def _set_action_buttons_default_mode(self):
        """设置行为相关按钮为默认模式"""
        try:
            # 这里可以根据实际的按钮控件名称进行调整
            if hasattr(self.suit_view, 'btn_new_action'):
                self.suit_view.btn_new_action.config(state='normal')
            if hasattr(self.suit_view, 'btn_edit_action'):
                self.suit_view.btn_edit_action.config(state='disabled')
            if hasattr(self.suit_view, 'btn_save_action'):
                self.suit_view.btn_save_action.config(state='disabled')
            if hasattr(self.suit_view, 'btn_delete_action'):
                self.suit_view.btn_delete_action.config(state='disabled')
                
        except Exception as e:
            logger.error(f"设置行为按钮默认模式失败: {str(e)}")
    
    def _build_suit_tree_structure(self, hierarchies):
        """构建组套树形结构字典 - 参考home_tab.py中的build_tree_structure方法"""
        tree_dict = {}
        
        # 首先创建所有节点
        for hierarchy in hierarchies:
            rank = parse_group_rank(hierarchy.group_rank)
            key = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E{rank['E']}"
            
            # 根据用户权限过滤
            if globalvariable.USER_IS_SUPER_ADMIN:
                tree_dict[key] = {
                    'obj': hierarchy,
                    'iid': None,
                    'children': [],
                    'parent': None
                }
            else:
                # 普通用户只能看到全局(A=2)或自己科室的层级
                if rank['A'] == 2 or hierarchy.department_id == globalvariable.current_department_id:
                    tree_dict[key] = {
                        'obj': hierarchy,
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
    
    def _get_user_by_id(self, user_id):
        """根据用户ID获取用户信息 - 参考home_tab.py中的get_user_by_id方法"""
        try:
            session = self._get_session()
            if not session:
                return None
            
            user = session.query(User).filter_by(user_id=user_id).first()
            return user
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return None
        finally:
            self._close_session()
