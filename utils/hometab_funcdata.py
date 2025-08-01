#该文件用于定义hometab_funcData类，该类用于为home_tab中的方法提供操作数据库中的数据的功能
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
import win32gui
import win32api
from database.db_manager import DatabaseManager
from config.config_manager import ConfigManager
from models.actions import ActionGroup, ActionList, ActionsGroupHierarchy,ActionMouse, ActionKeyboard,ActionClass, ActionAI, ActionPrintscreen, ActionFunction,ActionCodeTxt
from models.action_suit import ActionsSuitGroup, ActionsSuitList, ActionsSuitGroupHierarchy, ActionSuitMouse, ActionSuitKeyboard, ActionSuitCodeTxt, ActionSuitPrintscreen, ActionSuitAI, ActionSuitFunction, ActionSuitClass
from models.debug_actions import ActionsDebugGroup, ActionDebugList, ActionsDebugGroupHierarchy, ActionDebugMouse, ActionDebugKeyboard, ActionDebugCodeTxt, ActionDebugPrintscreen, ActionDebugAI, ActionDebugFunction, ActionDebugClass
from models.user import User
from models.department import Department
from gui.tabs.Hierarchyutils import parse_group_rank, iid_to_group_rank
import globalvariable
from utils.logger import Logger,logger
from utils.screenshot_tool import ScreenshotTool
from core.pic_capture import PicCapture

class hometab_funcData:

    # 模型映射字典
    MODEL_MAPPING = {
        # Action 相关模型
        "ActionList": ActionList,
        "ActionGroup": ActionGroup,
        "ActionsGroupHierarchy": ActionsGroupHierarchy,
        "ActionMouse": ActionMouse,
        "ActionKeyboard": ActionKeyboard,
        "ActionCodeTxt": ActionCodeTxt,
        "ActionPrintscreen": ActionPrintscreen,
        "ActionAI": ActionAI,
        "ActionFunction": ActionFunction,
        "ActionClass": ActionClass,
        
        # Action_suit 相关模型
        "ActionsSuitList": ActionsSuitList,
        "ActionSuitGroup": ActionsSuitGroup,
        "ActionsSuitGroupHierarchy": ActionsSuitGroupHierarchy,
        "ActionSuitMouse": ActionSuitMouse,
        "ActionSuitKeyboard": ActionSuitKeyboard,
        "ActionSuitCodeTxt": ActionSuitCodeTxt,
        "ActionSuitPrintscreen": ActionSuitPrintscreen,
        "ActionSuitAI": ActionSuitAI,
        "ActionSuitFunction": ActionSuitFunction,
        "ActionSuitClass": ActionSuitClass,
        
        # debug_action 相关模型
        "ActionDebugList": ActionDebugList,
        "ActionDebugGroup": ActionsDebugGroup,
        "ActionsDebugGroupHierarchy": ActionsDebugGroupHierarchy,
        "ActionDebugMouse": ActionDebugMouse,
        "ActionDebugKeyboard": ActionDebugKeyboard,
        "ActionDebugCodeTxt": ActionDebugCodeTxt,
        "ActionDebugPrintscreen": ActionDebugPrintscreen,
        "ActionDebugAI": ActionDebugAI,
        "ActionDebugFunction": ActionDebugFunction,
        "ActionDebugClass": ActionDebugClass,
    }

    sheet_action_mouse = ""
    sheet_action_keyboard = ""
    sheet_action_codetxt = ""
    sheet_action_printscreen = ""
    sheet_action_ai = ""
    sheet_action_function = ""
    sheet_action_class = ""
    sheet_list = ""
    sheet_listgroup = ""
    sheet_hierarchy = ""

    def __init__(self, data):
        self.data = data
    @classmethod
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
            return db_manager.Session()
        except Exception as e:
            logger.error(f"获取数据库会话失败: {str(e)}")
            return None
    @classmethod
    def _get_model_class(cls, sheet_name):
        """根据表名获取对应的模型类"""
        try:
            return cls.MODEL_MAPPING.get(sheet_name)
        except Exception as e:
            logger.error(f"获取模型类失败: {str(e)}")
            print(traceback.format_exc())
            return None
    @classmethod
    def delete_action_group(cls,sheet_type,action_tree_selected_iid,action_group_id,action_group_hierarchy_id):
        """该类函数用于根据sheet_type删除行为组,其中sheet_type:行为组表类型（如Action,Action_suit,debug_action）,action_tree_selected_iid:获取的树节点的iid,action_group_id:行为组id,action_group_hierarchy_id:行为组层次id"""
        session = None
        try:
            #获取数据库会话
            session = cls._get_session()
            if not session:
                return False
            if sheet_type == "Action":
                cls.sheet_list = "ActionList"
                cls.sheet_listgroup = "ActionGroup"
                cls.sheet_hierarchy = "ActionsGroupHierarchy"
                cls.sheet_action_mouse = "ActionMouse"
                cls.sheet_action_keyboard = "ActionKeyboard"
                cls.sheet_action_codetxt = "ActionCodeTxt"
                cls.sheet_action_printscreen = "ActionPrintscreen"
                cls.sheet_action_ai = "ActionAI"
                cls.sheet_action_function = "ActionFunction"
                cls.sheet_action_class = "ActionClass"
            elif sheet_type == "Action_list":
                cls.sheet_list = "ActionList"
                cls.sheet_listgroup = "ActionGroup"
                cls.sheet_hierarchy = "ListGroupHierarchy"
                cls.sheet_action_mouse = "ActionMouse"
                cls.sheet_action_keyboard = "ActionKeyboard"
                cls.sheet_action_codetxt = "ActionCodeTxt"
                cls.sheet_action_printscreen = "ActionPrintscreen"
                cls.sheet_action_ai = "ActionAI"
                cls.sheet_action_function = "ActionFunction"
                cls.sheet_action_class = "ActionClass"
            elif sheet_type == "Action_suit":
                cls.sheet_list = "ActionsSuitList"
                cls.sheet_listgroup = "ActionSuitGroup"
                cls.sheet_hierarchy = "ActionsSuitGroupHierarchy"
                cls.sheet_action_mouse = "ActionSuitMouse"
                cls.sheet_action_keyboard = "ActionSuitKeyboard"
                cls.sheet_action_codetxt = "ActionSuitCodeTxt"
                cls.sheet_action_printscreen = "ActionSuitPrintscreen"
                cls.sheet_action_ai = "ActionSuitAI"
                cls.sheet_action_function = "ActionSuitFunction"
                cls.sheet_action_class = "ActionSuitClass"
            elif sheet_type == "Action_suit_list":
                cls.sheet_list = "ActionsSuitList"
                cls.sheet_listgroup = "ActionSuitGroup"
                cls.sheet_hierarchy = "ListSuitHierarchy"
                cls.sheet_action_mouse = "ActionSuitMouse"
                cls.sheet_action_keyboard = "ActionSuitKeyboard"
                cls.sheet_action_codetxt = "ActionSuitCodeTxt"
                cls.sheet_action_printscreen = "ActionSuitPrintscreen"
                cls.sheet_action_ai = "ActionSuitAI"
                cls.sheet_action_function = "ActionSuitFunction"
                cls.sheet_action_class = "ActionSuitClass"
            elif sheet_type == "debug_action":
                cls.sheet_list = "ActionDebugList"
                cls.sheet_listgroup = "ActionDebugGroup"
                cls.sheet_hierarchy = "ActionsDebugGroupHierarchy"
                cls.sheet_action_mouse = "ActionDebugMouse"
                cls.sheet_action_keyboard = "ActionDebugKeyboard"
                cls.sheet_action_codetxt = "ActionDebugCodeTxt"
                cls.sheet_action_printscreen = "ActionDebugPrintscreen"
                cls.sheet_action_ai = "ActionDebugAI"
                cls.sheet_action_function = "ActionDebugFunction"
                cls.sheet_action_class = "ActionDebugClass"
            elif sheet_type == "debug_action_list":
                cls.sheet_list = "ActionDebugList"
                cls.sheet_listgroup = "ActionDebugGroup"
                cls.sheet_hierarchy = "ListDebugHierarchy"
                cls.sheet_action_mouse = "ActionDebugMouse"
                cls.sheet_action_keyboard = "ActionDebugKeyboard"
                cls.sheet_action_codetxt = "ActionDebugCodeTxt"
                cls.sheet_action_printscreen = "ActionDebugPrintscreen"
                cls.sheet_action_ai = "ActionDebugAI"
                cls.sheet_action_function = "ActionDebugFunction"
                cls.sheet_action_class = "ActionDebugClass"
            else: 
                logger.error(f"无效的行为组类型: {sheet_type}")
                return False

            # 获取对应的模型类
            list_model = cls._get_model_class(cls.sheet_list)
            listgroup_model = cls._get_model_class(cls.sheet_listgroup)
            hierarchy_model = cls._get_model_class(cls.sheet_hierarchy)
            mouse_model = cls._get_model_class(cls.sheet_action_mouse)
            keyboard_model = cls._get_model_class(cls.sheet_action_keyboard)
            codetxt_model = cls._get_model_class(cls.sheet_action_codetxt)
            printscreen_model = cls._get_model_class(cls.sheet_action_printscreen)
            ai_model = cls._get_model_class(cls.sheet_action_ai)
            function_model = cls._get_model_class(cls.sheet_action_function)
            class_model = cls._get_model_class(cls.sheet_action_class)

            if not all([list_model, listgroup_model, hierarchy_model]):
                logger.error("无法获取模型类")
                return False

            #如果选中的是来源于Action_list_group表
            if action_tree_selected_iid.startswith("group_"):
                #删除action_list_group表的记录
                group = session.query(listgroup_model).filter_by(id=action_group_id).first()
                if group:
                    group_name = group.action_list_group_name
                    #删除行为组关联的行为元
                    actions = session.query(list_model).filter_by(group_id=action_group_id).all()
                    for action in actions:
                        #删除行为元关联的子行为元
                        cls._delete_action(session, action.id, action.action_type, 
                                         mouse_model, keyboard_model, codetxt_model, 
                                         printscreen_model, ai_model, function_model, class_model)
                        session.delete(action)
                        session.commit()
                    session.delete(group)
                    session.commit()
                    logger.info(f"成功删除行为组: {group_name}")
                    return True
                else:
                    logger.error(f"无法找到行为组记录: {action_group_id}")
                    return False
            elif action_tree_selected_iid.startswith("action_"):
                #删除action_list表的记录
                action = session.query(list_model).filter_by(id=action_group_id).first()
                if action:
                    if action.action_type == "mouse":
                        action = session.query(mouse_model).filter_by(id=action_group_id).first()
                    elif action.action_type == "keyboard":
                        action = session.query(keyboard_model).filter_by(id=action_group_id).first()
                    elif action.action_type == "code_text":
                        action = session.query(codetxt_model).filter_by(id=action_group_id).first()
                    elif action.action_type == "printscreen":
                        action = session.query(printscreen_model).filter_by(id=action_group_id).first()
                    elif action.action_type == "ai":
                        action = session.query(ai_model).filter_by(id=action_group_id).first()
                    elif action.action_type == "function":
                        action = session.query(function_model).filter_by(id=action_group_id).first()
                    elif action.action_type == "class":
                        action = session.query(class_model).filter_by(id=action_group_id).first()
                    if action:
                        session.delete(action)
                        session.commit()
                        logger.info(f"成功删除行为元: {action.action_name}")
                    else:
                        logger.error(f"无法找到行为元记录: {action_group_id}")
                        return False
            elif action_tree_selected_iid.startswith("hierarchy_"):
                #删除list_group_hierarchy表的记录
                # 通过递归删除list_group_hierarchy表中相关的记录和子记录，同时删除相对应的ActionGroup表中的记录
                # 查询当前层次
                hierarchy = session.query(hierarchy_model).filter_by(id=action_group_hierarchy_id).first()
                if not hierarchy:
                    return False
                
                # 删除当前action_list_group表的记录
                groups = session.query(listgroup_model).filter_by(id=action_group_id).all()
                for group in groups:
                    group_name = group.action_list_group_name
                    actions = session.query(list_model).filter_by(group_id=group.id).all()
                    for action in actions:
                        #删除行为元关联的子行为元
                        cls._delete_action(session, action.id, action.action_type,
                                         mouse_model, keyboard_model, codetxt_model, 
                                         printscreen_model, ai_model, function_model, class_model)
                        session.delete(action)
                        session.commit()
                    session.delete(group)
                    session.commit()
                    logger.info(f"成功删除行为组: {group_name}")
                
                # 删除当前层次
                session.delete(hierarchy)
                session.commit()
                
                # 查询所有子层级记录
                hierarchy_parse_rank = parse_group_rank(hierarchy.list_rank)
                child_hierarchy_groups = session.query(hierarchy_model).filter(
                    hierarchy_model.list_rank.contains(hierarchy_parse_rank)
                ).all()
                
                for child_hierarchy_group in child_hierarchy_groups:
                    rank = parse_group_rank(child_hierarchy_group.list_rank)
                    
                    # 确定父节点key和当前节点iid
                    if rank['E'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E{rank['E']}"
                    elif rank['D'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                    elif rank['C'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                    elif rank['B'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}"
                    else:
                        continue
                    cls.delete_action_group(sheet_type, child_hierarchy_iid, child_hierarchy_group.id, child_hierarchy_group.id)
                return True
            elif action_tree_selected_iid.startswith("A"):
                # 通过递归删除ActionsGroupHierarchy表中相关的记录和子记录，同时删除相对应的ActionGroup表中的记录
                # 查询当前层次
                hierarchy = session.query(hierarchy_model).filter_by(id=action_group_hierarchy_id).first()
                if not hierarchy:
                    return False
                
                # 删除当前action_list_group表的记录
                groups = session.query(listgroup_model).filter_by(group_rank_id=action_group_hierarchy_id).all()
                for group in groups:
                    group_name = group.action_list_group_name
                    actions = session.query(list_model).filter_by(group_id=group.id).all()
                    for action in actions:
                        #删除行为元关联的子行为元
                        cls._delete_action(session, action.id, action.action_type,
                                         mouse_model, keyboard_model, codetxt_model, 
                                         printscreen_model, ai_model, function_model, class_model)
                        session.delete(action)
                        session.commit()
                    session.delete(group)
                    session.commit()
                    logger.info(f"成功删除行为组: {group_name}")
                
                # 删除当前层次
                session.delete(hierarchy)
                session.commit()
                
                # 查询所有子层级记录
                child_hierarchy_groups = session.query(hierarchy_model).filter(
                    hierarchy_model.group_rank.contains(action_tree_selected_iid)
                ).all()
                
                for child_hierarchy_group in child_hierarchy_groups:
                    child_hierarchy_group_id = child_hierarchy_group.id
                    rank = parse_group_rank(child_hierarchy_group.group_rank)
                    
                    # 确定父节点key和当前节点iid
                    if rank['E'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E{rank['E']}"
                    elif rank['D'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                    elif rank['C'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                    elif rank['B'] > 0:
                        child_hierarchy_iid = f"A{rank['A']}B{rank['B']}"
                    else:
                        continue
                    cls.delete_action_group(sheet_type, child_hierarchy_iid, child_hierarchy_group.id, child_hierarchy_group.id)
                return True
            else:   
                logger.error(f"无效的行为组类型: {action_tree_selected_iid}")
                return False
        except Exception as e:
            if session:
                session.rollback()
            print(traceback.format_exc())
            logger.error(f"删除行为组失败: {str(e)}")
            return False
        finally:
            if session:
                session.close()
    @classmethod
    def _delete_action(cls, session, action_list_id, action_type, mouse_model, keyboard_model, 
                      codetxt_model, printscreen_model, ai_model, function_model, class_model):
        """删除子行为元"""
        try:
            if not session:
                return False
        except Exception as e:
            logger.error(f"删除子行为元失败: {str(e)}")
            return False
            
        if action_type == 'mouse' and mouse_model:
            action = session.query(mouse_model).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'keyboard' and keyboard_model: 
            action = session.query(keyboard_model).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'code_text' and codetxt_model:
            action = session.query(codetxt_model).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'printscreen' and printscreen_model:
            action = session.query(printscreen_model).filter_by(id=action_list_id).first()  
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'ai' and ai_model:
            action = session.query(ai_model).filter_by(id=action_list_id).first()
            if action:      
                session.delete(action)
                session.commit()
        elif action_type == 'function' and function_model:
            action = session.query(function_model).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()
        elif action_type == 'class' and class_model:
            action = session.query(class_model).filter_by(id=action_list_id).first()
            if action:
                session.delete(action)
                session.commit()    
        return True
    @classmethod
    def _sort_action_group_up_data(cls, sheet_type,iid,hierarchy_id,group_id,sort_num):
        """将行为组向上移动,其中sheet_type:行为组表类型（如Action,Action_suit,debug_action）,iid:获取的树节点的iid,hierarchy_id:行为组层次id,group_id:行为组id"""
        try:
            if sort_num == 0:
                return False
            cls.sort_num = sort_num
            session = cls._get_session()
            if not session:
                return False
            if sheet_type == "Action":
                cls.sheet_listgroup = "ActionGroup"
                cls.sheet_hierarchy = "ActionsGroupHierarchy"
            elif sheet_type == "Action_suit":
                cls.sheet_listgroup = "ActionSuitGroup"
                cls.sheet_hierarchy = "ActionsSuitGroupHierarchy"
            elif sheet_type == "debug_action":
                cls.sheet_listgroup = "ActionDebugGroup"
                cls.sheet_hierarchy = "ActionsDebugGroupHierarchy"
            else:
                logger.error(f"无效的行为组类型: {sheet_type}")
                return False
            listgroup_model = cls._get_model_class(cls.sheet_listgroup)
            hierarchy_model = cls._get_model_class(cls.sheet_hierarchy)
            if not all([listgroup_model, hierarchy_model]):
                logger.error("无法获取模型类")
                return False
            if iid.startswith("A"):
                #获取当前层次
                hierarchy = session.query(hierarchy_model).filter_by(id=hierarchy_id).first()
                if not hierarchy:
                    return False
                # 获取当前层次的父节点
                group_rank_dict = parse_group_rank(hierarchy.group_rank)
                #获取group_rank_dict的第一个Value为0的key值
                first_key = ""
                for key, value in group_rank_dict.items():
                    if value == 0 and key != "A":
                        first_key = key
                        break
                #获取group_rank_dict中first_key的ascii码
                first_key_ascii = ord(first_key)
                #将first_key_ascii减1，但要确保不超出有效范围
                pro_first_key_ascii = first_key_ascii - 1
                #检查是否超出有效范围（A=65, B=66, C=67, D=68, E=69）
                if pro_first_key_ascii < 66:  # 如果小于'B'的ASCII码
                    pro_first_key_ascii = 66  # 设置为'B'
                #将first_key_ascii转换为字符
                pro_first_key = chr(pro_first_key_ascii)
                #获取group_rank_dict中pro_first_key之前的所有的key和Value组成的字符串
                group_rank_str = ""
                for key, value in group_rank_dict.items():
                    if key < pro_first_key:
                        group_rank_str += f"{key}{value}"
                # 获取当前组的父组的子集
                child_groups = session.query(hierarchy_model).filter(
                    hierarchy_model.group_rank.contains(group_rank_str) & 
                    (hierarchy_model.sort_num == cls.sort_num - 1)
                ).all()
                for child_group in child_groups:
                    child_group_rank_dict = parse_group_rank(child_group.group_rank)
                    if child_group_rank_dict[first_key] != 0:
                        continue
                    if child_group.sort_num == cls.sort_num-1:
                        child_group.sort_num = cls.sort_num
                # 修改当前组的排序号
                hierarchy.sort_num = cls.sort_num - 1
                session.commit()
                return True
            elif iid.startswith("group_"):
                #获取当前行为组
                group = session.query(listgroup_model).filter_by(id=group_id).first()
                if not group:
                    return False
                group_previous = session.query(listgroup_model).filter(
                    (listgroup_model.group_rank_id==hierarchy_id) & 
                    (listgroup_model.sort_num == cls.sort_num-1)).first()
                if group_previous:
                    group_previous.sort_num = cls.sort_num
                    group.sort_num = cls.sort_num - 1
                session.commit()
                return True
        except Exception as e:
            logger.error(f"将行为组向上移动失败: {str(e)}")
            print(traceback.format_exc())
            return False
    @classmethod
    def _sort_action_group_down_data(cls, sheet_type,iid,hierarchy_id,group_id,sort_num):
        """将行为组向上移动,其中sheet_type:行为组表类型（如Action,Action_suit,debug_action）,iid:获取的树节点的iid,hierarchy_id:行为组层次id,group_id:行为组id"""
        try:
            cls.sort_num = sort_num
            session = cls._get_session()
            if not session:
                return False
            if sheet_type == "Action":
                cls.sheet_listgroup = "ActionGroup"
                cls.sheet_hierarchy = "ActionsGroupHierarchy"
            elif sheet_type == "Action_suit":
                cls.sheet_listgroup = "ActionSuitGroup"
                cls.sheet_hierarchy = "ActionsSuitGroupHierarchy"
            elif sheet_type == "debug_action":
                cls.sheet_listgroup = "ActionDebugGroup"
                cls.sheet_hierarchy = "ActionsDebugGroupHierarchy"
            else:
                logger.error(f"无效的行为组类型: {sheet_type}")
                return False
            listgroup_model = cls._get_model_class(cls.sheet_listgroup)
            hierarchy_model = cls._get_model_class(cls.sheet_hierarchy)
            if not all([listgroup_model, hierarchy_model]):
                logger.error("无法获取模型类")
                return False
            if iid.startswith("A"):
                #获取当前层次
                hierarchy = session.query(hierarchy_model).filter_by(id=hierarchy_id).first()
                if not hierarchy:
                    return False
                # 获取当前层次的父节点
                group_rank_dict = parse_group_rank(hierarchy.group_rank)
                #获取group_rank_dict的第一个Value为0的key值
                first_key = ""
                for key, value in group_rank_dict.items():
                    if value == 0 and key != "A":
                        first_key = key
                        break
                #获取group_rank_dict中first_key的ascii码
                first_key_ascii = ord(first_key)
                #将first_key_ascii减1，但要确保不超出有效范围
                first_key_ascii -= 1
                #检查是否超出有效范围（A=65, B=66, C=67, D=68, E=69）
                if first_key_ascii < 66:  # 如果小于'B'的ASCII码
                    first_key_ascii = 66  # 设置为'B'
                #将first_key_ascii转换为字符
                pro_first_key = chr(first_key_ascii)
                #获取group_rank_dict中pro_first_key之前的所有的key和Value组成的字符串
                group_rank_str = ""
                for key, value in group_rank_dict.items():
                    if key < pro_first_key:
                        group_rank_str += f"{key}{value}"
                # 获取当前组的父组的子集
                child_groups = session.query(hierarchy_model).filter(
                    hierarchy_model.group_rank.contains(group_rank_str) & 
                    (hierarchy_model.sort_num == cls.sort_num + 1)
                ).all()
                for child_group in child_groups:
                    child_group_rank_dict = parse_group_rank(child_group.group_rank)
                    if child_group_rank_dict[first_key] == 0:
                        continue
                    child_group.sort_num = cls.sort_num
                # 修改当前组的排序号
                hierarchy.sort_num = sort_num + 1
                session.commit()
                return True
            elif iid.startswith("group_"):
                #获取当前行为组
                group = session.query(listgroup_model).filter_by(id=group_id).first()
                if not group:
                    return False
                group_previous = session.query(listgroup_model).filter(
                    (listgroup_model.group_rank_id==hierarchy_id) & 
                    (listgroup_model.sort_num == cls.sort_num+1)).first()
                if group_previous:
                    group_previous.sort_num = cls.sort_num
                    group.sort_num = cls.sort_num + 1
                session.commit()
                return True
        except Exception as e:
            logger.error(f"将行为组向上移动失败: {str(e)}")
            print(traceback.format_exc())
            return False
    @classmethod
    def _load_action_group_data(cls, sheet_type, action_treeview,action_list_id=None):
        """加载行为组数据,其中sheet_type:行为组表类型（如Action,Action_list,Action_suit,Action_suit_list,debug_action,debug_action_list）,action_treeview:行为组树视图"""
        try:
            session = cls._get_session()
            if not session:
                return False
            cls.action_treeview = action_treeview
            if sheet_type == "Action":
                cls.sheet_listgroup = "ActionGroup"
                cls.sheet_hierarchy = "ActionsGroupHierarchy"
            elif sheet_type == "Action_list":
                cls.sheet_listgroup = "ActionListGroup"
                cls.sheet_hierarchy = "ActionsGroupHierarchy"
            elif sheet_type == "Action_suit":
                cls.sheet_listgroup = "ActionSuitGroup"
                cls.sheet_hierarchy = "ActionsSuitGroupHierarchy"
            elif sheet_type == "Action_suit_list":
                cls.sheet_listgroup = "ActionSuitListGroup"
                cls.sheet_hierarchy = "ActionsSuitGroupHierarchy"
            elif sheet_type == "debug_action":
                cls.sheet_listgroup = "ActionDebugGroup"
                cls.sheet_hierarchy = "ActionsDebugGroupHierarchy"
            elif sheet_type == "debug_action_list":
                cls.sheet_listgroup = "ActionDebugListGroup"
                cls.sheet_hierarchy = "ActionsDebugGroupHierarchy"
            else:
                logger.error(f"无效的行为组类型: {sheet_type}")
                return False
            cls.sheet_hierarchy_model = cls._get_model_class(cls.sheet_hierarchy)
            if not cls.sheet_hierarchy_model:
                logger.error("无法获取模型类")
                return False
            cls.sheet_listgroup_model = cls._get_model_class(cls.sheet_listgroup)
            if not cls.sheet_listgroup_model:
                logger.error("无法获取模型类")
                return False
            # 清空树
            cls.action_treeview.delete(*cls.action_treeview.get_children())
            # 获取所有层级数据
            hierarchy_groups = {}
            if sheet_type == "Action_list" or sheet_type == "Action_suit_list" or sheet_type == "debug_action_list":
                hierarchies = session.query(cls.sheet_hierarchy_model).filter_by(group_id=action_list_id).all()
            else:
                hierarchies = session.query(cls.sheet_hierarchy_model).all()
            for hierarchy in hierarchies:
                rank_dict = parse_group_rank(hierarchy.group_rank)
                parent_key = cls._get_parent_key(rank_dict)
                if parent_key not in hierarchy_groups:
                    hierarchy_groups[parent_key] = []
                hierarchy_groups[parent_key].append(hierarchy)
            for parent_key in hierarchy_groups:
                hierarchy_groups[parent_key].sort(key=lambda x: x.sort_num)
            # 按照父节点key排序，然后合并所有组
            sorted_parent_keys = sorted(hierarchy_groups.keys())
            sorted_hierarchies = []
            for parent_key in sorted_parent_keys:
                sorted_hierarchies.extend(hierarchy_groups[parent_key])
            hierarchies = sorted_hierarchies
            # 使用ActionGroupManager构建树形结构
            tree_dict = cls.build_tree_structure(hierarchies)
            # 递归插入节点到Treeview
            def insert_node(key, parent_iid):
                if key not in tree_dict:
                    return
                node = tree_dict[key]
                h = node['obj']
                user = session.query(User).filter_by(id=h.doctor_id).first()
                username = user.username if user else "未知"
                # 插入当前节点
                if parent_iid == "":
                    cls.action_treeview.insert("", "end", iid=node['iid'], text=h.group_name, 
                                          values=(h.group_name, username))
                else:
                    cls.action_treeview.insert(parent_iid, "end", iid=node['iid'], text="📁", 
                                          values=(h.group_name, username))
                # 插入子节点
                for child_key in node['children']:
                    insert_node(child_key, node['iid'])
            # 插入顶层节点（A级节点，B=C=D=E=0）    
            inserted_nodes = set()  # 记录已插入的节点，避免重复
            for key, node in tree_dict.items():
                rank = parse_group_rank(key)
                if rank['B'] == 0 and rank['C'] == 0 and rank['D'] == 0 and rank['E'] == 0:
                    if key not in inserted_nodes:
                        insert_node(key, "")
                        inserted_nodes.add(key)
            # 查询所有行为组，插入到对应层级下
            groups = session.query(cls.sheet_listgroup_model).all()
            for group in groups:
                if not hasattr(group, 'group_rank_id') or not group.group_rank_id:
                    continue
                # 获取行为组对应的层级
                rank_record = session.query(cls.sheet_hierarchy_model).filter_by(id=group.group_rank_id).first()
                if not rank_record:
                    continue
                rank_dict = parse_group_rank(rank_record.group_rank)
                # 确定行为组应该插入到哪个层级节点下
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
                if cls.action_treeview.exists(parent_iid):
                    user = session.query(User).filter_by(id=group.user_id).first()
                    username = user.username if user else "未知"
                    # 插入行为组节点
                    cls.action_treeview.insert(parent_iid, "end", text="📄", 
                                              values=(group.action_list_group_name, username), 
                                              iid=f"group_{group.id}")
                else:
                    # 父节点不存在，跳过这个行为组
                    continue
            return True
        except Exception as e:
            logger.error(f"加载行为组数据失败: {str(e)}")
            print(traceback.format_exc())
        finally:
            print("加载行为组数据成功-强制关闭session")
            session.close()
    @classmethod
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
    @classmethod
    def _get_parent_key(self, rank_dict):
        """获取父节点key
        
        Args:
            rank_dict: 解析后的group_rank字典
            
        Returns:
            str: 父节点key
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
    @classmethod
    def _save_action_group_hierarchy_data(cls, sheet_type,hierarchy_id,group_name,group_note,is_auto,auto_time):
        """保存行为组层级信息,其中sheet_type:行为组表类型（如Action,Action_suit,debug_action）,iid:获取的树节点的iid,hierarchy_id:行为组层次id,group_id:行为组id"""
        try:
            session = cls._get_session()
            if not session:
                return False
            if sheet_type == "Action":
                cls.sheet_hierarchy = "ActionsGroupHierarchy"
            elif sheet_type == "Action_suit":
                cls.sheet_hierarchy = "ActionsSuitGroupHierarchy"
            elif sheet_type == "debug_action":
                cls.sheet_hierarchy = "ActionsDebugGroupHierarchy"
            else:
                logger.error(f"无效的行为组类型: {sheet_type}")
                return False
            hierarchy_model = cls._get_model_class(cls.sheet_hierarchy)
            if not hierarchy_model:
                logger.error("无法获取模型类")
                return False    
            hierarchy = session.query(hierarchy_model).filter_by(id=hierarchy_id).first()
            if not hierarchy:
                logger.error("无法获取行为组层次信息")
                return False
            hierarchy.group_name = group_name
            hierarchy.group_note = group_note
            hierarchy.is_auto = is_auto
            hierarchy.auto_time = auto_time
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"保存行为组层级信息失败: {str(e)}")
            print(traceback.format_exc())