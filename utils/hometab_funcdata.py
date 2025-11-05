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
from database.db_manager import DatabaseManager
from config.config_manager import ConfigManager
from models.actions import ActionGroup, ActionList, ActionsGroupHierarchy,ActionMouse, ActionKeyboard,ActionClass, ActionAI, ActionPrintscreen, ActionFunction,ActionCodeTxt
from models.action_suit import ActionsSuitGroup, ActionSuitList, ActionsSuitGroupHierarchy, ActionSuitMouse, ActionSuitKeyboard, ActionSuitCodeTxt, ActionSuitPrintscreen, ActionSuitAI, ActionSuitFunction, ActionSuitClass
from models.debug_actions import ActionsDebugGroup, ActionDebugList, ActionsDebugGroupHierarchy, ActionDebugMouse, ActionDebugKeyboard, ActionDebugCodeTxt, ActionDebugPrintscreen, ActionDebugAI, ActionDebugFunction, ActionDebugClass
from models.user import User
from models.department import Department
from gui.tabs.Hierarchyutils import get_parent_iid, parse_group_rank, iid_to_group_rank, parse_group_rank_to_iid, parse_list_rank_to_iid
import globalvariable
from utils.logger import Logger,logger
from utils.screenshot_tool import ScreenshotTool
from core.pic_capture import PicCapture

class hometab_funcData:
    """该类用于处理home_tab中的行为组和行为元数据，包括保存、删除、排序等操作"""
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
        "ActionSuitList": ActionSuitList,
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
    def delete_action_group(cls,sheet_type,action_tree_selected_iid,action_group_id,action_group_hierarchy_id,node_type):
        """该类函数用于根据sheet_type删除行为组,其中sheet_type:行为组表类型（如Action,Action_suit,debug_action）,action_tree_selected_iid:获取的树节点的iid,action_group_id:行为组id,action_group_hierarchy_id:行为组层次id"""
        cls.node_type = node_type
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
                cls.sheet_action_mouse = "ActionMouse"
                cls.sheet_action_keyboard = "ActionKeyboard"
                cls.sheet_action_codetxt = "ActionCodeTxt"
                cls.sheet_action_printscreen = "ActionPrintscreen"
                cls.sheet_action_ai = "ActionAI"
                cls.sheet_action_function = "ActionFunction"
                cls.sheet_action_class = "ActionClass"
            elif sheet_type == "Action_suit":
                cls.sheet_list = "ActionSuitList"
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
                cls.sheet_list = "ActionSuitList"
                cls.sheet_listgroup = "ActionSuitGroup"
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
            if cls.node_type == "group":
                # 删除action_group_hierarchy表的记录
                hierarchy = session.query(hierarchy_model).filter_by(id=action_group_hierarchy_id).first()
                if hierarchy:
                    session.delete(hierarchy)
                    session.commit()
                    logger.info(f"成功删除行为组层次: {hierarchy.group_name}")

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
            elif cls.node_type == "list":
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
            elif cls.node_type == "hierarchy_list":
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
            elif cls.node_type == "hierarchy_group":
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
    def _load_action_group_data(cls, workTreeview, treeDatatxt,action_group_id=None):
        """
        根据要求为接受的Treeview类型的参数进行树结构的数据填充
        
        Args:
            workTreeview: Treeview控件类型数据
            treeDatatxt: 用来描述用什么数据填充树形控件的数据，为text格式
                        可以是：ActionList、ActionsGroupHierarchy、ActionSuitList、ActionsSuitGroupHierarchy、ActionDebugList、ActionsDebugGroupHierarchy
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            session = cls._get_session()
            if not session:
                return False
            
            # 清空树控件
            workTreeview.delete(*workTreeview.get_children())
            
            # 根据treeDatatxt确定要使用的模型和字段
            if treeDatatxt in ["ActionList", "ActionSuitList", "ActionDebugList"]:
                # 使用list_rank字段进行分组，action_sort_num字段进行排序
                if action_group_id==None:
                    logger.error("action_group_hierarchy_id为空")
                    return False
                else:
                    #获取action_group_hierarchy_id的group_id
                    my_group_id = action_group_id
                cls._load_list_data(workTreeview, treeDatatxt, session,my_group_id)
            elif treeDatatxt in ["ActionsGroupHierarchy", "ActionsSuitGroupHierarchy", "ActionsDebugGroupHierarchy"]:
                # 使用group_rank字段进行分组，sort_num字段进行排序
                cls._load_hierarchy_data(workTreeview, treeDatatxt, session)
            else:
                logger.error(f"无效的treeDatatxt: {treeDatatxt}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"加载行为组数据失败: {str(e)}")
            print(traceback.format_exc())
            return False
        finally:
            if session:
                session.close()
    
    @classmethod
    def _load_list_data(cls, workTreeview, treeDatatxt, session, group_id=None):
        """加载ActionList、ActionSuitList、ActionDebugList类型的数据
        
        逻辑：
        1. 先填充 action_type 为 hierarchy_list 的记录（目录节点）
        2. 对于 hierarchy_list 记录：
           - A1B2C0D0E0 表示它是 A1B2 级别（C0表示C级不存在）
           - 父节点是 A1（上一级）
           - 子节点包括 A1B2C(1-∞)D0E0 格式的记录
        3. 对于非 hierarchy_list 记录：
           - 挂载到匹配的 hierarchy_list 节点下
        4. 排序规则：
           - 相同 list_rank 级别中，sort_num 为空或0或相同，按记录先后顺序排序
           - sort_num 不为0，按 sort_num 大小排序
        """
        try:
            # 根据treeDatatxt确定模型
            if treeDatatxt == "ActionList":
                model = ActionList
            elif treeDatatxt == "ActionSuitList":
                model = ActionSuitList
            elif treeDatatxt == "ActionDebugList":
                model = ActionDebugList
            else:
                return
            
            # 获取数据，如果提供了group_id则按group_id过滤
            if group_id:
                all_records = session.query(model).filter_by(group_id=group_id).all()
            else:
                all_records = session.query(model).all()
            
            # 分离 hierarchy_list 类型的记录和其他类型的记录
            hierarchy_list_records = []
            other_records = []
            
            for record in all_records:
                if not record.list_rank:
                    continue
                # 检查 action_type 字段名
                action_type = getattr(record, 'action_type', None) or getattr(record, 'list_type', None)
                if action_type == "hierarchy_list" or action_type == "list_hierarchy":
                    hierarchy_list_records.append(record)
                else:
                    other_records.append(record)
            
            # 构建 hierarchy_list 的树结构（先填充目录）
            # 按实际的 list_rank 值分组（保留0值，因为它们有含义）
            hierarchy_grouped_data = {}
            for record in hierarchy_list_records:
                if record.list_rank:
                    # 使用原始的 list_rank 作为 key，保留完整信息
                    group_key = record.list_rank
                    if group_key not in hierarchy_grouped_data:
                        hierarchy_grouped_data[group_key] = []
                    hierarchy_grouped_data[group_key].append(record)
            
            # 对每个分组的记录排序：sort_num 为空或0或相同，按记录先后顺序；sort_num 不为0，按 sort_num 排序
            for group_key in hierarchy_grouped_data:
                records = hierarchy_grouped_data[group_key]
                # 先按 sort_num 排序（sort_num 为 None 或 0 的记录会排在前面）
                records.sort(key=lambda x: (x.sort_num or 0, x.id))
                # 对于 sort_num 相同的记录，保持原有顺序（通过 id 作为第二排序键）
            
            # 构建 hierarchy_list 的树形结构（先填充目录）
            cls._build_hierarchy_list_tree(workTreeview, hierarchy_grouped_data)
            
            # 处理其他类型的记录，挂载到对应的 hierarchy_list 节点下
            # 按 list_rank 分组，然后排序
            other_grouped_data = {}
            for record in other_records:
                if record.list_rank:
                    group_key = record.list_rank
                    if group_key not in other_grouped_data:
                        other_grouped_data[group_key] = []
                    other_grouped_data[group_key].append(record)
            
            # 对每个分组的记录排序
            for group_key in other_grouped_data:
                records = other_grouped_data[group_key]
                records.sort(key=lambda x: (x.sort_num or 0, x.id))
            
            # 将其他记录挂载到对应的 hierarchy_list 节点下
            for group_key, records in other_grouped_data.items():
                # 找到这些记录应该挂载到的 hierarchy_list 节点
                parent_iid = cls._find_parent_hierarchy_list_for_other(group_key, hierarchy_grouped_data, workTreeview)
                
                for record in records:
                    record_iid = f"record_{record.id}"
                    action_type = getattr(record, 'action_type', None) or getattr(record, 'list_type', None) or ""
                    text_name = "📄"
                    values = (
                        record.action_name or "",
                        action_type,
                        record.action_note or "" if hasattr(record, 'action_note') else "",
                        record.id
                    )
                    
                    try:
                        if parent_iid and workTreeview.exists(parent_iid):
                            workTreeview.insert(parent_iid, "end", iid=record_iid, text=text_name, values=values)
                        else:
                            workTreeview.insert("", "end", iid=record_iid, text=text_name, values=values)
                    except Exception as e:
                        logger.warning(f"插入记录节点失败: {record.id}, {e}")
            
        except Exception as e:
            logger.error(f"加载列表数据失败: {str(e)}")
            print(traceback.format_exc())
    
    @classmethod
    def _get_list_rank_level(cls, list_rank):
        """获取 list_rank 的实际级别
        
        例如：A1B2C0D0E0 -> A1B2（因为C0表示C级不存在）
              A1B2C3D0E0 -> A1B2C3（因为D0表示D级不存在）
        """
        rank_dict = parse_group_rank(list_rank)
        level_parts = []
        
        # 从A到E检查，遇到0就停止
        for level in ['A', 'B', 'C', 'D', 'E']:
            if rank_dict[level] == 0:
                break
            level_parts.append(f"{level}{rank_dict[level]}")
        
        return ''.join(level_parts) if level_parts else ""
    
    @classmethod
    def _get_parent_list_rank(cls, list_rank):
        """获取 list_rank 的父级 list_rank
        
        例如：A1B2C0D0E0 -> A1B0C0D0E0（父级是A1）
              A1B2C3D0E0 -> A1B2C0D0E0（父级是A1B2）
        """
        rank_dict = parse_group_rank(list_rank)
        parent_rank_dict = rank_dict.copy()
        
        # 找到最后一个非0的级别，将其置为0
        for level in ['E', 'D', 'C', 'B']:
            if rank_dict[level] > 0:
                parent_rank_dict[level] = 0
                break
        
        # 构建父级 list_rank
        return f"A{parent_rank_dict['A']}B{parent_rank_dict['B']}C{parent_rank_dict['C']}D{parent_rank_dict['D']}E{parent_rank_dict['E']}"
    
    @classmethod
    def _build_hierarchy_list_tree(cls, workTreeview, hierarchy_grouped_data):
        """构建 hierarchy_list 的树形结构
        
        hierarchy_grouped_data 的 key 是完整的 list_rank（如 "A1B2C0D0E0"）
        """
        try:
            if not hierarchy_grouped_data:
                return
            
            # 为每个 hierarchy_list 记录计算实际级别和父级
            hierarchy_info = {}
            list_rank_to_iid = {}  # list_rank -> iid 映射，用于后续查找
            
            for list_rank, records in hierarchy_grouped_data.items():
                level = cls._get_list_rank_level(list_rank)
                parent_list_rank = cls._get_parent_list_rank(list_rank)
                parent_level = cls._get_list_rank_level(parent_list_rank)
                
                # 生成 iid：使用 parse_list_rank_to_iid 来生成 iid，确保唯一性
                # parse_list_rank_to_iid 会去掉0值部分，例如：A1B2C0D0E0 -> A1B2
                iid = parse_list_rank_to_iid(list_rank)
                if not iid:
                    # 如果 parse_list_rank_to_iid 返回 None，使用 level
                    iid = level if level else list_rank
                
                # 存储映射
                list_rank_to_iid[list_rank] = iid
                
                hierarchy_info[list_rank] = {
                    'level': level,
                    'parent_level': parent_level,
                    'parent_list_rank': parent_list_rank,
                    'iid': iid,
                    'records': records
                }
            
            # 将 list_rank_to_iid 映射存储到类变量中，供 _find_parent_hierarchy_list_for_other 使用
            cls._hierarchy_list_rank_to_iid = list_rank_to_iid
            
            # 建立父子关系：通过 parent_level 匹配查找父节点
            parent_child_map = {}  # parent_list_rank -> [child_list_ranks]
            root_nodes = []
            
            for list_rank, info in hierarchy_info.items():
                parent_level = info['parent_level']
                
                # 查找父节点（通过 parent_level 匹配）
                parent_list_rank = None
                if parent_level:  # parent_level 不为空
                    for p_list_rank, p_info in hierarchy_info.items():
                        if p_info['level'] == parent_level:
                            parent_list_rank = p_list_rank
                            break  # 找到第一个匹配的就使用
                
                if parent_list_rank and parent_list_rank in hierarchy_info:
                    # 找到父节点，避免循环依赖：检查是否会产生循环
                    if list_rank != parent_list_rank:  # 不能是自身
                        if parent_list_rank not in parent_child_map:
                            parent_child_map[parent_list_rank] = []
                        parent_child_map[parent_list_rank].append(list_rank)
                    else:
                        # 自身作为父节点，这是错误的情况，作为根节点处理
                        root_nodes.append(list_rank)
                else:
                    # 没有找到父节点，作为根节点
                    root_nodes.append(list_rank)
            
            # 递归插入节点（添加深度限制和循环检测）
            inserted_iids = set()  # 记录已插入的iid，避免重复
            inserting_stack = set()  # 记录正在插入的节点，检测循环依赖
            
            def insert_hierarchy_node(list_rank, parent_iid=None):
                # 检测循环依赖
                if list_rank in inserting_stack:
                    logger.error(f"检测到循环依赖: {list_rank}")
                    return
                
                if list_rank not in hierarchy_info:
                    return
                
                info = hierarchy_info[list_rank]
                iid = info['iid']
                records = info['records']
                
                # 检查是否已插入（避免重复）
                if iid in inserted_iids:
                    # 节点已插入，只处理子节点
                    final_iid = iid
                else:
                    inserting_stack.add(list_rank)
                    
                    # 使用第一个记录来显示（如果有多个，取第一个）
                    record = records[0]
                    
                    text_name = "📁"
                    values = (record.action_name or "", record.action_type or "", record.action_note or "" if hasattr(record, 'action_note') else "", record.id)
                    
                    try:
                        if parent_iid and workTreeview.exists(parent_iid):
                            workTreeview.insert(parent_iid, "end", iid=iid, text=text_name, values=values)
                        else:
                            workTreeview.insert("", "end", iid=iid, text=text_name, values=values)
                        final_iid = iid
                        inserted_iids.add(iid)
                    except Exception as e:
                        logger.warning(f"插入 hierarchy_list 节点失败: {list_rank}, iid: {iid}, error: {e}")
                        inserting_stack.remove(list_rank)
                        return
                    
                    inserting_stack.remove(list_rank)
                
                # 递归插入子节点
                if list_rank in parent_child_map:
                    # 对子节点排序（按 sort_num，然后按 list_rank）
                    children = sorted(parent_child_map[list_rank], 
                                    key=lambda x: (hierarchy_info[x]['records'][0].sort_num or 0, x))
                    for child_list_rank in children:
                        insert_hierarchy_node(child_list_rank, final_iid)
            
            # 从根节点开始插入
            if root_nodes:
                for root_list_rank in sorted(root_nodes, key=lambda x: (hierarchy_info[x]['records'][0].sort_num or 0, x)):
                    insert_hierarchy_node(root_list_rank)
            
            # 处理没有被插入的节点（可能是父子关系建立有问题）
            for list_rank in hierarchy_info.keys():
                iid = hierarchy_info[list_rank]['iid']
                if iid not in inserted_iids:
                    logger.warning(f"节点未被插入，尝试插入: {list_rank}, iid: {iid}")
                    insert_hierarchy_node(list_rank)
            
        except Exception as e:
            logger.error(f"构建 hierarchy_list 树结构失败: {str(e)}")
            print(traceback.format_exc())
    
    @classmethod
    def _find_parent_hierarchy_list_for_other(cls, list_rank, hierarchy_grouped_data, workTreeview):
        """为其他类型的记录找到应该挂载到的 hierarchy_list 节点的 iid
        
        规则：
        1. 如果 list_rank 完全匹配某个 hierarchy_list 的 list_rank，挂载到该节点下
        2. 如果没有完全匹配，尝试查找父级 hierarchy_list 节点
        """
        try:
            if not list_rank or not hierarchy_grouped_data:
                return None
            
            # 使用存储的映射来查找 iid
            list_rank_to_iid = getattr(cls, '_hierarchy_list_rank_to_iid', {})
            
            # 方法1：直接查找完全匹配的 hierarchy_list
            if list_rank in hierarchy_grouped_data:
                # 使用映射查找 iid
                if list_rank in list_rank_to_iid:
                    iid = list_rank_to_iid[list_rank]
                    if workTreeview.exists(iid):
                        return iid
            
            # 方法2：如果没有完全匹配，尝试查找父级 hierarchy_list 节点
            # 例如：记录的 list_rank = "A1B2C3D0E0"，查找 list_rank = "A1B2C0D0E0" 的 hierarchy_list
            record_rank_dict = parse_group_rank(list_rank)
            
            # 从最深到最浅逐级向上查找父级
            for level_char in ['E', 'D', 'C', 'B']:
                if record_rank_dict[level_char] > 0:
                    # 将当前级别置为0，查找父级
                    parent_rank_dict = record_rank_dict.copy()
                    parent_rank_dict[level_char] = 0
                    parent_list_rank = f"A{parent_rank_dict['A']}B{parent_rank_dict['B']}C{parent_rank_dict['C']}D{parent_rank_dict['D']}E{parent_rank_dict['E']}"
                    
                    # 查找该父级是否存在于 hierarchy_grouped_data 中
                    if parent_list_rank in hierarchy_grouped_data:
                        # 使用映射查找 iid
                        if parent_list_rank in list_rank_to_iid:
                            parent_iid = list_rank_to_iid[parent_list_rank]
                            if workTreeview.exists(parent_iid):
                                return parent_iid
            
            return None
            
        except Exception as e:
            logger.error(f"查找父 hierarchy_list 节点失败: {str(e)}")
            print(traceback.format_exc())
            return None
    
    @classmethod
    def _load_hierarchy_data(cls, workTreeview, treeDatatxt, session):
        """加载ActionsGroupHierarchy、ActionsSuitGroupHierarchy、ActionsDebugGroupHierarchy类型的数据"""
        try:
            # 根据treeDatatxt确定模型
            if treeDatatxt == "ActionsGroupHierarchy":
                model = ActionsGroupHierarchy
            elif treeDatatxt == "ActionsSuitGroupHierarchy":
                model = ActionsSuitGroupHierarchy
            elif treeDatatxt == "ActionsDebugGroupHierarchy":
                model = ActionsDebugGroupHierarchy
            else:
                return
            # 获取所有数据
            all_records = session.query(model).all()
            
            # 按group_rank分组，按sort_num排序
            grouped_data = {}
            for record in all_records:
                # 根据用户权限过滤数据
                if globalvariable.USER_IS_SUPER_ADMIN:
                    group_key = parse_group_rank_to_iid(record.group_rank)
                    if group_key not in grouped_data:
                            grouped_data[group_key] = []
                    grouped_data[group_key].append(record)
                else:
                    # 普通用户只能看到全局(A=2)或自己科室的层级
                    if record.group_rank.startswith("A3") or (record.user_id == globalvariable.USER_ID or globalvariable.USER_IS_SUPER_ADMIN):
                        group_key = parse_group_rank_to_iid(record.group_rank)
                        # 创建分组键
                        if group_key not in grouped_data:
                            grouped_data[group_key] = []
                        grouped_data[group_key].append(record)
            # 构建树形结构
            cls._build_tree_from_grouped_data(workTreeview, grouped_data, "group")
            
        except Exception as e:
            logger.error(f"加载层级数据失败: {str(e)}")
            print(traceback.format_exc())
    
    @classmethod
    def _build_tree_from_grouped_data(cls, workTreeview, grouped_data, data_type):
        """根据分组数据构建树形结构"""
        """嵌套字典的结构为：
        {
            "A1B1C1D1E1": {
                "obj": [obj1, obj2, ...],
                "iid": "A1B1C1D1E1",
                "children": ["A1B1C1D1E2", "A1B1C1D1E3"],
        """
        tree_dict = {}
        # 记录已插入的节点，避免重复
        inserted_nodes = set()
        # 递归插入节点到Treeview
        def insert_node(key, parent_iid = None):
            if key not in tree_dict:
                return
            # 检查数据类型
            if isinstance(tree_dict[key]['obj'], list):
                # 如果是列表，取第一个元素
                obj = tree_dict[key]['obj'][0] if tree_dict[key]['obj'] else None
                iid = tree_dict[key]['iid']
            else:
                obj = tree_dict[key]['obj']
                iid = tree_dict[key]['iid']
            if not obj:
                return
            # 确定节点的iid
    
            node = tree_dict[key]
            h = node['obj']
            if data_type == "list":
                text_name = "📁" if obj.action_type == "hierarchy_list" else "📄"
                values = (obj.action_name or "",obj.action_type, obj.action_note or "", obj.id)
            else:  # hierarchy
                text_name = "📁" if hasattr(obj, 'group_type') and obj.group_type == "hierarchy_group" else "📄"
                values = (obj.group_name or "", obj.group_type, getattr(obj, 'group_note', "") or "", obj.id)
                    
            # 插入节点
            try:
                if parent_iid and workTreeview.exists(parent_iid):
                    workTreeview.insert(parent_iid, "end", iid=iid, text=text_name, values=values)
                elif not parent_iid:
                    workTreeview.insert("", "end", iid=iid, text=text_name, values=values)
                        
                inserted_nodes.add(iid)
            except Exception as e:
                logger.warning(f"insert_node：无法插入节点 {iid}: {e}")
            # 递归插入子节点
            for child_key in sorted(node['children'], key=lambda x: tree_dict[x]['sort_num'] or 0):
                insert_node(child_key, node['iid'])
        try:
            # 先初步排序
            sorted_keys = sorted(grouped_data.keys(), key=lambda x: cls._get_sort_key(x))
            # 根据group_data数据的group_rank的值构建一个树结构的嵌套字典
            # 首先初始化嵌套字典
            for group_key in sorted_keys:
                tree_dict[group_key] = {
                        'obj': grouped_data[group_key],
                        'iid': None,
                        'children': [],
                        'parent': None,
                        'sort_num': grouped_data[group_key][0].sort_num if grouped_data[group_key][0].sort_num is not None else 0
                    }
            # 完善嵌套字典，建立父子关系
            for key, node in tree_dict.items():
                rank = parse_group_rank(key)
                    
                # 确定父节点key和当前节点iid
                if rank['E'] > 0:
                    parent_key = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                    parent_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                    node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}E{rank['E']}"
                elif rank['D'] > 0:
                    parent_key = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                    parent_iid = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                    node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}D{rank['D']}"
                elif rank['C'] > 0:
                    parent_key = f"A{rank['A']}B{rank['B']}"
                    parent_iid = f"A{rank['A']}B{rank['B']}"
                    node['iid'] = f"A{rank['A']}B{rank['B']}C{rank['C']}"
                elif rank['B'] > 0:
                    parent_key = f"A{rank['A']}"
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
            
            for tree_key,tree_item in sorted(tree_dict.items(), key=lambda x: x[1]['sort_num'] or 0):
                if tree_key:
                    if "B0" in tree_key or len(tree_key) == 2:
                        insert_node(tree_key,tree_item['parent'])
        except Exception as e:
            logger.error(f"构建树形结构失败: {str(e)}")
            print(traceback.format_exc())    
    @classmethod
    def _get_sort_key(cls, group_key):
        """获取用于排序的键值"""
        if not group_key:
            return ""
        
        rank_dict = parse_group_rank(group_key)
        
        # 创建排序键，确保层级结构正确
        # 格式：A级_B级_C级_D级_E级
        return f"{rank_dict['A']:03d}_{rank_dict['B']:03d}_{rank_dict['C']:03d}_{rank_dict['D']:03d}_{rank_dict['E']:03d}"
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