# 示例数据管理文件
from datetime import datetime, timedelta
import random
import globalvariable
from models.patient import PatientList, PatientAIResult, PatientAIResultBackup
from models.actions import ActionList, ActionGroup, ActionsGroupHierarchy, ActionMouse, ActionKeyboard, ActionCodeTxt, ActionPrintscreen, ActionAI, ActionFunction, ActionClass
from database.db_manager import DatabaseManager

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

def get_patients_by_department(department):
    """根据科室获取患者列表"""
    session = DatabaseManager.get_session()
    department_id = globalvariable.USER_DEPARTMENT_ID
    patients = session.query(PatientList).filter(PatientList.patient_department_id == department_id).all()
    session.close()
    # 将Patients转化为json
    patients_json = []
    for patient in patients:
        patient_json = {
            "id": patient.patient_id,
            "name": patient.patient_name,
            "in_hospital_time": patient.in_hospital_time,
            "age": patient.patient_age,
            "gender": patient.patient_gender,
            "department": globalvariable.USER_DEPARTMENT,
            "bed_num": patient.patient_bed_num,
            "attending_doctor_id": patient.attending_doctor_id,
            "fellow_doctor_id": patient.fellow_doctor_id,
            "resistant_doctor_id": patient.resistant_doctor_id,
            "patient_note": patient.patient_note
        }
        patients_json.append(patient_json)
    return patients_json

def get_patient_info(patient_id):
    """根据患者ID获取患者详细信息"""
    session = DatabaseManager.get_session()
    patient = session.query(PatientList).filter(PatientList.patient_id == patient_id).first()
    session.close()
    patient_json = {
        "id": patient.patient_id,
        "name": patient.patient_name,
        "in_hospital_time": patient.in_hospital_time,
        "age": patient.patient_age,
        "gender": patient.patient_gender,
        "department": globalvariable.USER_DEPARTMENT,
        "bed_num": patient.patient_bed_num,
        "attending_doctor_id": patient.attending_doctor_id,
        "fellow_doctor_id": patient.fellow_doctor_id,
        "resistant_doctor_id": patient.resistant_doctor_id,
        "patient_note": patient.patient_note
    }
    return patient_json

def get_ai_functions():
    """获取AI功能列表,也就是action_group表中的与用户相关的数据"""
    session = DatabaseManager.get_session()
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
    session = DatabaseManager.get_session()
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
    session = DatabaseManager.get_session()
    action_group = session.query(ActionGroup).filter(ActionGroup.id == function_id and ActionGroup.user_id == globalvariable.USER_ID).first()
    session.close()
    return action_group.action_list_group_note

def get_ai_func_group_func_list_name():
    """获取AI功能列表中的功能组名称组成的列表"""
    func_list_name_list = []
    session = DatabaseManager.get_session()
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
    session = DatabaseManager.get_session()
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