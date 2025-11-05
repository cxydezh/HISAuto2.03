# 示例数据管理文件
from datetime import datetime, timedelta
import random
import globalvariable
from models.patient import PatientList, PatientAIResult, PatientAIResultBackup
from models.actions import ActionList, ActionGroup, ActionsGroupHierarchy, ActionMouse, ActionKeyboard, ActionCodeTxt, ActionPrintscreen, ActionAI, ActionFunction, ActionClass
from database.db_manager import DatabaseManager
from config.config_manager import ConfigManager

# 全局数据库管理器实例（延迟初始化）
_config_manager = None
_db_path = None
_encryption_key = None
_db_manager = None

def _get_db_manager():
    """延迟初始化数据库管理器（懒加载模式）"""
    global _config_manager, _db_path, _encryption_key, _db_manager
    
    if _db_manager is not None:
        return _db_manager
    
    # 只在第一次需要时才初始化
    if _config_manager is None:
        _config_manager = ConfigManager()
        _db_path = _config_manager.get_value('System', 'DataSource')
        _encryption_key = _config_manager.get_value('Security', 'DBEncryptionKey')
    
    if not _db_path or not _encryption_key:
        raise RuntimeError("数据库配置信息不完整，无法初始化DatabaseManager")
    
    _db_manager = DatabaseManager(_db_path, _encryption_key)
    _db_manager.initialize()
    return _db_manager

# 科室数据
DEPARTMENTS = [
    {"id": "personal", "name": "个人"},
    {"id": "department", "name": "科室"},
    {"id": "hospital", "name": "全院"}
]

# 套餐类型数据
suit_type = ("个人", "科室", "全局")
def get_departments():
    """获取科室列表"""
    return DEPARTMENTS

# 患者数据现在由前端通过Excel文件导入，不再需要后端加载
# get_patients_by_department() 已删除
# get_patient_info() 已删除

def get_ai_functions():
    """获取AI功能列表,也就是action_group表中的与用户相关的数据"""
    db_manager = _get_db_manager()
    session = db_manager.get_session()
    action_group = session.query(ActionGroup).filter(ActionGroup.user_id == globalvariable.USER_ID).all()
    session.close()
    action_group_json = []
    for action_group in action_group:
        action_group_item = {
            "id": action_group.id,
            "action_group_name": action_group.action_list_group_name,
            "action_group_note": action_group.action_list_group_note,
        }
        action_group_json.append(action_group_item)
    return action_group_json

def get_ai_workflow1(action_group_id):
    """获取指定AI功能的工作流程，也就是获取与action_list表中id对应的list_group_hierarchy表中相关的数据"""
    db_manager = _get_db_manager()
    session = db_manager.get_session()
    list_group_hierarchy = session.query(ActionList).filter(ActionList.group_id == action_group_id and ActionList.list_rank.contains("B0")).all()
    session.close()
    list_group_hierarchy_json = []
    for list_group_hierarchy in list_group_hierarchy:
        list_group_hierarchy_item = {
            "id": list_group_hierarchy.id,
            "hierarchy_name": list_group_hierarchy.list_name,
            "hierarchy_note": list_group_hierarchy.group_note,
        }
        list_group_hierarchy_json.append(list_group_hierarchy_item)
    return list_group_hierarchy_json

def get_ai_function_description(function_id):
    """获取AI功能描述"""
    db_manager = _get_db_manager()
    session = db_manager.get_session()
    action_group = session.query(ActionGroup).filter(ActionGroup.id == function_id and ActionGroup.user_id == globalvariable.USER_ID).first()
    session.close()
    return action_group.action_list_group_note

def get_ai_func_group_func_list_name():
    """获取AI功能列表中的功能组名称组成的列表"""
    func_list_name_list = []
    db_manager = _get_db_manager()
    session = db_manager.get_session()
    action_group = session.query(ActionGroup).filter(ActionGroup.user_id == globalvariable.USER_ID).all()
    session.close()
    for action_group in action_group:
        func_dict = {}
        func_dict["func_list_name"] = action_group.action_list_group_name
        func_dict["func_list_id"] = action_group.id
        func_list_name_list.append(func_dict)
    return func_list_name_list

def get_ai_suit_list():
    """获取AI功能列表中的功能组类型组成的列表"""
    return suit_type
def get_ai_workflow(suit_name):
    """获取指定AI套餐的AI功能列表"""
    db_manager = _get_db_manager()
    session = db_manager.get_session()
    if suit_name == "个人":
        action_group = session.query(ActionGroup).filter(ActionGroup.user_id == globalvariable.USER_ID).all()
    elif suit_name == "科室":
        action_group_pro = session.query(ActionGroup).filter(ActionGroup.department_id == globalvariable.USER_DEPARTMENT_ID).all()
        for action_group_item in action_group_pro:
            action_group_rank = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_id == action_group_item.id).first()
            if action_group_rank.hierarchy_rank.contains("A1"):
                action_group.append(action_group_item)
    elif suit_name == "全局":
        action_group_pro = session.query(ActionGroup).all()
        for action_group_item in action_group_pro:
            action_group_rank = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_id == action_group_item.id).first()
            if action_group_rank.hierarchy_rank.contains("A2"):
                action_group.append(action_group_item)
    session.close()
    func_list = []
    for action_group_item in action_group:
        
        func_list_item = {
            "func_list_name": action_group_item.action_list_group_name,
            "func_list_id": action_group_item.id,
            "func_list_note": action_group_item.action_list_group_note,
        }
        func_list.append(func_list_item)
    for func_group_item in func_group:
        if suit_name in func_group_item["func_list_type"]:
            func_list.append(func_group_item)
    return func_list

def get_ai_workflow_by_func_list_id(func_list_id):
    """获取指定AI功能列表的AI功能列表"""
    for func_group_item in func_group:
        if func_list_id in func_group_item["func_list_id"]:
            return func_group_item["func_list"]
    return None
def get_patient_ai_result(patient_id,func_list_id):
    """获取指定患者和AI功能的AI结果"""
    for patient_ai_result_item in patient_AI_result:
        if patient_ai_result_item["Patient_id"] == patient_id and patient_ai_result_item["func_list_id"] == func_list_id:
            return patient_ai_result_item["func_list_result"]
    return None

def get_ai_hierarchy_list(suit_type):
    """获取AI功能列表（从actions_group_hierarchy表）
    
    Args:
        suit_type: 'personal'（个人）、'department'（科室）、'global'（全局）
    
    Returns:
        list: 包含 id、group_name、group_note 的字典列表
    """
    db_manager = _get_db_manager()
    session = db_manager.get_session()
    try:
        query = session.query(ActionsGroupHierarchy)
        
        # 过滤条件：group_type != 'hierarchy_group'
        query = query.filter(ActionsGroupHierarchy.group_type != 'hierarchy_group')
        
        if suit_type == 'personal':
            # 个人：group_rank 以 "A1B" 开头，doctor_id == 当前用户ID
            query = query.filter(
                ActionsGroupHierarchy.group_rank.like('A1B%'),
                ActionsGroupHierarchy.doctor_id == globalvariable.USER_ID
            )
        elif suit_type == 'department':
            # 科室：group_rank 以 "A2B" 开头，department_id == 当前用户科室ID
            query = query.filter(
                ActionsGroupHierarchy.group_rank.like('A2B%'),
                ActionsGroupHierarchy.department_id == globalvariable.USER_DEPARTMENT_ID
            )
        elif suit_type == 'global':
            # 全局：group_rank 以 "A3B" 开头
            query = query.filter(
                ActionsGroupHierarchy.group_rank.like('A3B%')
            )
        else:
            return []
        
        # 执行查询
        results = query.all()
        
        # 转换为字典列表
        result_list = []
        for item in results:
            result_list.append({
                'id': item.id,
                'group_name': item.group_name or '',
                'group_note': item.group_note or ''
            })
        
        return result_list
    except Exception as e:
        print(f"获取AI功能列表时出错: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        session.close()

def get_ai_actions_by_group_id(group_id):
    """获取指定行为组下所有 action_type 为 'AI' 的记录
    
    Args:
        group_id: 行为组ID (ActionGroup.id 或 ActionsGroupHierarchy.id)
    
    Returns:
        list: 包含 action_name 和 ai_illustration 的字典列表
    """
    db_manager = _get_db_manager()
    session = db_manager.get_session()
    try:
        # 首先判断 group_id 是 ActionGroup.id 还是 ActionsGroupHierarchy.id
        # 查询 ActionGroup 以确认
        action_group = session.query(ActionGroup).filter_by(id=group_id).first()
        actual_group_id = group_id
        
        if not action_group:
            # 如果不是 ActionGroup.id，尝试查询 ActionsGroupHierarchy
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=group_id).first()
            if hierarchy:
                # 从 ActionsGroupHierarchy 获取关联的 ActionGroup
                # ActionGroup 通过 group_rank_id 外键关联到 ActionsGroupHierarchy.id
                action_group_by_hierarchy = session.query(ActionGroup).filter_by(
                    group_rank_id=group_id
                ).first()
                if action_group_by_hierarchy:
                    actual_group_id = action_group_by_hierarchy.id
                else:
                    # 如果通过外键找不到，尝试通过 relationship 查找
                    if hierarchy.action_groups:
                        # 如果有关联的 ActionGroup，使用第一个
                        actual_group_id = hierarchy.action_groups[0].id if hierarchy.action_groups else None
                    else:
                        return []
            else:
                return []
        
        if not actual_group_id:
            return []
        
        # 查询该行为组下所有 action_type 为 'AI' 的 ActionList 记录
        ai_action_lists = session.query(ActionList).filter(
            ActionList.group_id == actual_group_id,
            ActionList.action_type == 'AI'
        ).all()
        
        # 获取每个 ActionList 对应的 ActionAI 详细信息
        result_list = []
        for action_list in ai_action_lists:
            # 获取对应的 ActionAI 记录
            action_ai = session.query(ActionAI).filter_by(action_list_id=action_list.id).first()
            
            if action_ai:
                result_list.append({
                    'action_name': action_list.action_name or action_ai.train_long_name or '未命名',
                    'ai_illustration': action_ai.ai_illustration or '',
                    'train_group_name': action_ai.train_group_name or '',
                    'train_long_name': action_ai.train_long_name or '',
                    'long_txt_name': action_ai.long_txt_name or '',
                    'ai_note': action_ai.ai_note or ''
                })
            else:
                # 如果没有 ActionAI 记录，仍然返回 ActionList 的信息
                result_list.append({
                    'action_name': action_list.action_name or '未命名',
                    'ai_illustration': '',
                    'train_group_name': '',
                    'train_long_name': '',
                    'long_txt_name': '',
                    'ai_note': action_list.action_note or ''
                })
        
        return result_list
    except Exception as e:
        print(f"获取AI动作列表时出错: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        session.close()