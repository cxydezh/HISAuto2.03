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
from gui.tabs.Hierarchyutils import parse_group_rank, iid_to_group_rank
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
    @classmethod
    def _get_session(cls):
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
    def _load_group_data(cls, workTreeview, treeDatatxt):
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
                cls._load_list_data(workTreeview, treeDatatxt, session)
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
    def _load_list_data(cls, workTreeview, treeDatatxt, session):
        """加载ActionList、ActionSuitList、ActionDebugList类型的数据"""
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
            
            # 获取所有数据，按list_rank分组，按action_sort_num排序
            all_records = session.query(model).all()
            
            # 按list_rank分组
            grouped_data = {}
            for record in all_records:
                if record.list_rank:
                    rank_dict = parse_group_rank(record.list_rank)
                    # 创建分组键
                    group_key = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
                    if group_key not in grouped_data:
                        grouped_data[group_key] = []
                    grouped_data[group_key].append(record)
            
            # 对每个分组内的数据按action_sort_num排序
            for group_key in grouped_data:
                grouped_data[group_key].sort(key=lambda x: x.action_sort_num or 0)
            
            # 构建树形结构
            cls._build_tree_from_grouped_data(workTreeview, grouped_data, "list")
            
        except Exception as e:
            logger.error(f"加载列表数据失败: {str(e)}")
            print(traceback.format_exc())
    
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
                if record.group_rank:
                    rank_dict = parse_group_rank(record.group_rank)
                    # 创建分组键
                    group_key = f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
                    if group_key not in grouped_data:
                        grouped_data[group_key] = []
                    grouped_data[group_key].append(record)
            
            # 对每个分组内的数据按sort_num排序
            for group_key in grouped_data:
                grouped_data[group_key].sort(key=lambda x: x.sort_num or 0)
            
            # 构建树形结构
            cls._build_tree_from_grouped_data(workTreeview, grouped_data, "hierarchy")
            
        except Exception as e:
            logger.error(f"加载层级数据失败: {str(e)}")
            print(traceback.format_exc())
    
    @classmethod
    def _build_tree_from_grouped_data(cls, workTreeview, grouped_data, data_type):
        """根据分组数据构建树形结构"""
        try:
            # 按分组键排序，确保树的层级结构正确
            sorted_keys = sorted(grouped_data.keys(), key=lambda x: cls._get_sort_key(x))
            
            # 记录已插入的节点，避免重复
            inserted_nodes = set()
            
            for group_key in sorted_keys:
                records = grouped_data[group_key]
                
                for record in records:
                    # 确定节点的iid
                    if data_type == "list":
                        iid = cls._parse_list_rank_to_iid(record.list_rank)
                    else:  # hierarchy
                        iid = cls._parse_group_rank_to_iid(record.group_rank)
                    
                    if not iid or iid in inserted_nodes:
                        continue
                    
                    # 确定父节点iid
                    parent_iid = cls._get_parent_iid(iid)
                    
                    # 确定节点文本和图标
                    if data_type == "list":
                        text_name = "📁" if record.action_type == "group" else "📄"
                        values = (record.action_name or "", record.action_note or "", record.id)
                    else:  # hierarchy
                        text_name = "📁" if hasattr(record, 'group_type') and record.group_type == "group" else "📄"
                        values = (record.group_name or "", getattr(record, 'group_note', "") or "", record.id)
                    
                    # 插入节点
                    if parent_iid and workTreeview.exists(parent_iid):
                        workTreeview.insert(parent_iid, "end", iid=iid, text=text_name, values=values)
                    elif not parent_iid:
                        workTreeview.insert("", "end", iid=iid, text=text_name, values=values)
                    
                    inserted_nodes.add(iid)
                    
        except Exception as e:
            logger.error(f"构建树形结构失败: {str(e)}")
            print(traceback.format_exc())

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
    def _parse_list_rank_to_iid(cls, list_rank):
        """将list_rank转换为iid格式"""
        if not list_rank:
            return None
        rank_dict = parse_group_rank(list_rank)
        return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
    
    @classmethod
    def _parse_group_rank_to_iid(cls, group_rank):
        """将group_rank转换为iid格式"""
        if not group_rank:
            return None
        rank_dict = parse_group_rank(group_rank)
        return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}E{rank_dict['E']}"
    
    @classmethod
    def _get_parent_iid(cls, iid):
        """根据当前iid获取父节点iid"""
        if not iid:
            return None
        
        rank_dict = parse_group_rank(iid)
        
        # 根据层级确定父节点
        if rank_dict['E'] > 0:
            return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}D{rank_dict['D']}"
        elif rank_dict['D'] > 0:
            return f"A{rank_dict['A']}B{rank_dict['B']}C{rank_dict['C']}"
        elif rank_dict['C'] > 0:
            return f"A{rank_dict['A']}B{rank_dict['B']}"
        elif rank_dict['B'] > 0:
            return f"A{rank_dict['A']}"
        else:
            return None  # A级节点没有父节点
    
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