import random
import string
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Department, User, PatientList
from models import ActionsSuitGroup, ActionsSuitList, ActionSuitMouse, ActionSuitKeyboard
from models import ActionsDebugGroup, ActionDebugList, ActionDebugMouse, ActionDebugKeyboard
from models import TaskList, TaskListFinished, AutoTask

from database.db_manager import DatabaseManager
from config.config_manager import ConfigManager

def generate_test_data():
    """生成测试数据"""
    # 创建部门列表（确保唯一性）
    departments = []
    dept_codes = ['MED', 'SUR', 'ER', 'RAD', 'LAB']
    for i, code in enumerate(dept_codes):
        dept = Department(
            name=f"科室{i+1}",
            code=f"{code}_{i}_{datetime.now().timestamp()}",  # 确保唯一性
            description=f"测试科室{i+1}"
        )
        departments.append(dept)
    
    # 创建用户列表
    users = []
    for i in range(10):
        department = random.choice(departments)
        user = User(
            user_id=f"U{i:03d}_{i}_{datetime.now().timestamp()}",  # 确保唯一性
            username=f"user{i}",
            department_id=department.code,
            password=f"pass{i}",
            role=random.choice(['doctor', 'department_admin', 'system_admin'])
        )
        users.append(user)
    
    # 创建患者列表
    patients = []
    for i in range(15):
        patient = PatientList(
            patient_bed_num=f"B{i+1}",
            patient_name=f"患者{i+1}",
            patient_id=f"PID{i:04d}",
            patient_age=random.randint(18, 80),
            patient_ward=f"病区{i+1}",
            attending_doctor_id=random.choice(users).id,
            fellow_doctor_id=random.choice(users).id,
            resistant_doctor_id=random.choice(users).id,
            patient_diagnosis="常见疾病诊断",
            patient_care_rank=random.choice(["一级", "二级", "三级"]),
            patient_fee=f"{random.randint(1000, 10000)}元",
            in_hospital_time=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        patients.append(patient)
    
    # 创建ActionSuitGroup
    action_suit_groups = []
    for i in range(10):
        # 确保使用已存在的用户和部门
        user = random.choice(users) if users else None
        department = random.choice(departments) if departments else None
        
        if not user or not department:
            print(f"跳过创建ActionSuitGroup：用户={not user}, 部门={not department}")
            continue
        
        action_suit_group = ActionsSuitGroup(
            action_list_group_name=f"行为组_{i}",
            sort_num=i,
            group_rank_id=None,  # 暂时不设置外键
            department_id=department.code,
            user_id=user.id
        )
        action_suit_groups.append(action_suit_group)
    
    # 创建ActionsSuitList
    action_suit_lists = []
    for i in range(15):
        action_suit_list = ActionsSuitList(
            action_type=f"type_{i%5}",
            action_name=f"动作_{i}",
            group_id=random.choice(action_suit_groups).id,
            next_id=None if i == 9 else i+1,
            setup_time=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        action_suit_lists.append(action_suit_list)
    
    # 创建ActionSuitMouse
    action_suit_mouses = []
    for i in range(20):
        action_suit_mouse = ActionSuitMouse(
            mouse_action=(i % 7) + 1,
            mouse_size=round(random.uniform(1.0, 10.0), 2),
            action_list_id=random.choice(action_suit_lists).id
        )
        action_suit_mouses.append(action_suit_mouse)
    
    # 创建ActionSuitKeyboard
    action_suit_keyboards = []
    for i in range(20):
        action_suit_keyboard = ActionSuitKeyboard(
            keyboard_type=(i % 4) + 1,
            keyboard_value=f"key_value_{i}",
            action_list_id=random.choice(action_suit_lists).id
        )
        action_suit_keyboards.append(action_suit_keyboard)
    
    # 创建ActionsDebugGroup
    actions_debug_groups = []
    for i in range(10):
        actions_debug_group = ActionsDebugGroup(
            action_list_group_name=f"调试组_{i}",
            sort_num=i,
            group_rank=f"rank_{i%3}",
            department_id=random.choice(departments).code,
            user_id=random.choice(users).id
        )
        actions_debug_groups.append(actions_debug_group)
    
    # 创建ActionDebugList
    action_debug_lists = []
    for i in range(15):
        action_debug_list = ActionDebugList(
            action_type=f"type_{i%5}",
            action_name=f"调试动作_{i}",
            group_id=random.choice(actions_debug_groups).id,
            next_id=None if i == 9 else i+1,
            setup_time=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        action_debug_lists.append(action_debug_list)
    
    # 创建ActionDebugMouse
    action_debug_mouses = []
    for i in range(20):
        action_debug_mouse = ActionDebugMouse(
            mouse_action=(i % 7) + 1,
            mouse_size=round(random.uniform(1.0, 10.0), 2),
            action_list_id=random.choice(action_debug_lists).id
        )
        action_debug_mouses.append(action_debug_mouse)
    
    # 创建ActionDebugKeyboard
    action_debug_keyboards = []
    for i in range(20):
        action_debug_keyboard = ActionDebugKeyboard(
            keyboard_type=(i % 4) + 1,
            keyboard_value=f"key_value_{i}",
            action_list_id=random.choice(action_debug_lists).id
        )
        action_debug_keyboards.append(action_debug_keyboard)
    
    # 创建任务列表
    tasks = []
    for i in range(15):
        user = random.choice(users)
        action_suit_group = random.choice(action_suit_groups)
        task = TaskList(
            task_start_time=datetime.now() - timedelta(days=random.randint(1, 30)),
            task_priority=random.randint(1, 5),
            task_user_id=user.id,
            task_user_name=user.username,
            task_ip=f"192.168.1.{i%255 + 1}",
            task_is_auto=bool(i % 2),
            actions_group_id=action_suit_group.id
        )
        tasks.append(task)
    
    # 创建已完成任务列表
    finished_tasks = []
    for i in range(10):
        user = random.choice(users)
        action_suit_group = random.choice(action_suit_groups)
        finished_task = TaskListFinished(
            task_start_time=datetime.now() - timedelta(days=random.randint(1, 30)),
            task_priority=random.randint(1, 5),
            task_user_id=user.id,
            task_user_name=user.username,
            task_ip=f"192.168.1.{i%255 + 1}",
            task_is_auto=bool(i % 2),
            actions_group_id=action_suit_group.id,
            finished_time=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        finished_tasks.append(finished_task)
    
    # 创建自动任务
    auto_tasks = []
    for i in range(10):
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            # 确保随机选择不为空
            user = random.choice(users) if users else None
            action_suit_group = random.choice(action_suit_groups) if action_suit_groups else None
            
            if user and action_suit_group:
                break
            retry_count += 1
            print(f"第{i}个自动任务尝试第{retry_count}次寻找有效用户和行为组")
        
        if retry_count >= max_retries:
            print(f"第{i}个自动任务达到最大重试次数，跳过创建")
            continue
        
        auto_task = AutoTask(
            task_start_time=datetime.now() - timedelta(days=random.randint(1, 30)),
            task_priority=random.randint(1, 5),
            task_user_id=user.id,
            task_user_name=user.username,
            task_ip=f"192.168.1.{i%255 + 1}",
            actions_group_id=action_suit_group.id,
            auto_time=f"{random.randint(0, 23)}:{random.randint(0, 59):02d}"
        )
        auto_tasks.append(auto_task)
    
    return {
        'departments': departments,
        'users': users,
        'patients': patients,
        'action_suit_groups': action_suit_groups,
        'action_suit_lists': action_suit_lists,
        'action_suit_mouses': action_suit_mouses,
        'action_suit_keyboards': action_suit_keyboards,
        'actions_debug_groups': actions_debug_groups,
        'action_debug_lists': action_debug_lists,
        'action_debug_mouses': action_debug_mouses,
        'action_debug_keyboards': action_debug_keyboards,
        'tasks': tasks,
        'finished_tasks': finished_tasks,
        'auto_tasks': auto_tasks
    }

if __name__ == '__main__':
    # 获取配置
    config_manager = ConfigManager()
    db_path = config_manager.get_value('System', 'DataSource')
    encryption_key = config_manager.get_value('System', 'encryption_key', 'default_key_123456')
    
    # 初始化数据库管理器
    db_manager = DatabaseManager(db_path=db_path, encryption_key=encryption_key)
    db_manager.initialize()  # 初始化数据库连接
    session = db_manager.get_session()  # 获取会话
    try:
        # 生成测试数据
        test_data = generate_test_data()
        
        # 插入部门数据
        for dept in test_data['departments']:
            session.add(dept)
        
        # 插入用户数据
        for user in test_data['users']:
            session.add(user)
        
        # 插入患者数据
        for patient in test_data['patients']:
            session.add(patient)
        
        # 插入ActionSuitGroup数据
        valid_action_suit_groups = []
        for group in test_data['action_suit_groups']:
            if group.user and group.department:  # 确保关联对象存在
                session.add(group)
                valid_action_suit_groups.append(group)
            else:
                print(f"跳过无效的ActionSuitGroup：用户={not group.user}, 部门={not group.department}")
        
        # 更新有效的ActionSuitGroup列表
        test_data['action_suit_groups'] = valid_action_suit_groups
        
        # 插入ActionsSuitList数据
        for list_item in test_data['action_suit_lists']:
            session.add(list_item)
        
        # 插入ActionSuitMouse数据
        for mouse in test_data['action_suit_mouses']:
            session.add(mouse)
        
        # 插入ActionSuitKeyboard数据
        for keyboard in test_data['action_suit_keyboards']:
            session.add(keyboard)
        
        # 插入ActionsDebugGroup数据
        for group in test_data['actions_debug_groups']:
            session.add(group)
        
        # 插入ActionDebugList数据
        for list_item in test_data['action_debug_lists']:
            session.add(list_item)
        
        # 插入ActionDebugMouse数据
        for mouse in test_data['action_debug_mouses']:
            session.add(mouse)
        
        # 插入ActionDebugKeyboard数据
        for keyboard in test_data['action_debug_keyboards']:
            session.add(keyboard)
        
        # 插入任务数据
        for task in test_data['tasks']:
            session.add(task)
        
        # 插入已完成任务数据
        for finished_task in test_data['finished_tasks']:
            session.add(finished_task)
        
        # 插入自动任务数据
        for auto_task in test_data['auto_tasks']:
            session.add(auto_task)
        
        # 提交事务
        session.commit()
        print("测试数据插入成功！")
    except Exception as e:
        session.rollback()
        print(f"数据插入失败: {str(e)}")
    finally:
        session.close()