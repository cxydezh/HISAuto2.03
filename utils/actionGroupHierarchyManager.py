import tkinter as tk
from tkinter import ttk
import traceback
from config.config_manager import ConfigManager
from gui.tabs.Hierarchyutils import iid_to_group_rank, parse_group_rank
from models.action_suit import ActionsSuitGroupHierarchy, ListSuitHierarchy
from models.actions import ActionsGroupHierarchy, ListGroupHierarchy
from models.debug_actions import ActionsDebugGroupHierarchy, ListDebugHierarchy
#获取全局变量
import globalvariable
#获取数据库
from database.db_manager import DatabaseManager
#获取logger
from utils.logger import logger

#新建行为组组套
class ActionGroupHierarchy_Manager:
    """新建行为组Hierarchy"""
    def __init__(self,root,handle_sheet,action_group_selected_rank,relate_location_selected,hierarchy_sort=None,is_action_list=False,action_group_id=None):
        """可用于action、action_suit、action_debug。分别获取窗体参数、要操作的表格、当前行为组的group_rank、插入位置、排序号,是否是行为组列表,行为组id。"""
        self.handle_sheet = handle_sheet
        self.action_group_selected_rank = action_group_selected_rank
        self.relate_location_selected = relate_location_selected
        if hierarchy_sort == None:
            self.hierarchy_sort = 0
        else:
            self.hierarchy_sort = hierarchy_sort
        self.is_action_list = is_action_list
        self.action_group_id = action_group_id
        #根据class ActionsGroupHierarchy(BaseModel)的字段创建类的属性
        self.group_name = ""
        self.group_rank = ""
        self.sort_num = 1
        self.doctor_id = globalvariable.USER_ID
        self.department_id = globalvariable.USER_DEPARTMENT_ID
        self.group_note = ""
        self.new_group_rank_dict = {}

        #创建新建行为组组窗口并显示
        self.select_mode = tk.Toplevel(root)
        self.select_mode.title("新建行为组Hierarchy")
        self.select_mode.geometry("400x300")
        self.select_mode.resizable(False, False)
        self.select_mode.transient(root)
        self.select_mode.grab_set()
        self.select_mode.focus_set()
        
        local_mode_frame = ttk.Frame(self.select_mode)
        local_mode_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(local_mode_frame, text="行为组组名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_group_group_name_var = tk.StringVar(master=root)
        ttk.Entry(local_mode_frame, textvariable=self.action_group_group_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(local_mode_frame, text="行为组组描述:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.action_group_group_desc_var = tk.StringVar(master=root)
        ttk.Entry(local_mode_frame, textvariable=self.action_group_group_desc_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)  
        
        confirm_btn = ttk.Button(local_mode_frame, text="确定", command=self.confirm_module_suit)
        confirm_btn.grid(row=2, column=0, columnspan=2, pady=10)
        root.wait_window(self.select_mode)

    def confirm_module_suit(self):
        """新建行为组组套"""
        try:
            #获取行为组组套名称
            self.group_name = self.action_group_group_name_var.get()
            #获取行为组组套描述
            self.group_note = self.action_group_group_desc_var.get()
            #获取数据库配置
            config = ConfigManager()
            db_path = config.get_value("System", "DataSource")
            encryption_key = config.get_value("System", "EncryptionKey")
            #获取数据库
            db_manager = DatabaseManager(db_path, encryption_key)
            db_manager.initialize()
            #获取session
            session = db_manager.get_session()
            #解析self.action_group_selected_rank
            group_rank_dict = parse_group_rank(self.action_group_selected_rank)
            #新建行为组Hierarchy的group_rank的dict
            self.new_group_rank_dict = group_rank_dict.copy()
            if self.is_action_list:
                if self.relate_location_selected == 1:
                    #上方插入
                    #获取group_rank_dict的第一个Value为0的key值
                    first_key = ""
                    for key, value in group_rank_dict.items():
                        if value == 0 and key != "A":#因为A是根节点，不能插入到A上方，A0是个人行为组集合
                            first_key = key
                            break
                        if key == "E":
                            first_key = "F"
                    #获取group_rank_dict中first_key的ascii码
                    first_key_ascii = ord(first_key)
                    #将first_key_ascii减1，但要确保不超出有效范围
                    first_key_ascii -= 1
                    #检查是否超出有效范围（A=65, B=66, C=67, D=68, E=69）
                    if first_key_ascii < 65:  # 如果小于'A'的ASCII码
                        first_key_ascii = 65  # 设置为'A'
                    #将first_key_ascii转换为字符
                    pro_first_key = chr(first_key_ascii)
                    #获取group_rank_dict中pro_first_key之前的所有的key和Value组成的字符串
                    group_rank_str = ""
                    for key, value in group_rank_dict.items():
                        if key < pro_first_key:
                            group_rank_str += key + str(value)
                    #获取数据库self.handle_sheet表中group_rank包含group_rank_str的所有记录
                    if self.handle_sheet == "ListGroupHierarchy":
                        action_group_hierarchy_records = session.query(ListGroupHierarchy).filter(ListGroupHierarchy.list_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ListSuitHierarchy":
                        action_group_hierarchy_records = session.query(ListSuitHierarchy).filter(ListSuitHierarchy.list_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ListDebugHierarchy":
                        action_group_hierarchy_records = session.query(ListDebugHierarchy).filter(ListDebugHierarchy.list_rank.contains(group_rank_str)).all()
                    #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort值均加1
                    max_first_key_value = 0
                    for record in action_group_hierarchy_records:
                        temp_group_rank_dict = parse_group_rank(record.list_rank)
                        #如果temp_group_rank_dict[first_key] != 0 or temp_group_rank_dict[pro_first_key] == 0，则跳过(因为A0是个人行为组集合，不能插入到A0上方)
                        if (first_key != "F" and (temp_group_rank_dict[first_key] != 0 or temp_group_rank_dict[pro_first_key] == 0)) or (first_key == "F" and temp_group_rank_dict[pro_first_key] == 0):
                            continue
                        # 处理首部和尾部的特殊情况
                        if first_key == "F":
                            if temp_group_rank_dict[pro_first_key] == 0:
                                continue
                            else:
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num >= self.hierarchy_sort:
                                    record.sort_num += 1
                        else:
                            if (pro_first_key in temp_group_rank_dict and 
                            first_key in temp_group_rank_dict and 
                            temp_group_rank_dict[pro_first_key] > 0 and
                            temp_group_rank_dict[first_key] == 0):    
                            #获取temp_group_rank_dict中first_key的Value
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num >= self.hierarchy_sort:
                                    record.sort_num += 1

                    #提交修改事务
                    session.commit()
                    #创建新的group_rank
                    temp_group_rank_str1 = self.action_group_selected_rank
                    #获取temp_group_rank_dict
                    temp_group_rank_dict1 = parse_group_rank(temp_group_rank_str1)
                    #修改temp_group_rank_dict中first_key的Value
                    temp_group_rank_dict1[pro_first_key] = max_first_key_value + 1
                    #将temp_group_rank_dict转换为group_rank_str
                    temp_group_rank_str1 = ""
                    for key, value in temp_group_rank_dict1.items():
                        temp_group_rank_str1 += key + str(value)
                    #将temp_group_rank_str1转换为group_rank
                    self.group_rank = temp_group_rank_str1
                    self.sort_num = self.hierarchy_sort
                elif self.relate_location_selected == 2:
                    #下方插入
                    #获取group_rank_dict的第一个Value为0的key值
                    first_key = ""
                    for key, value in group_rank_dict.items():
                        if value == 0 and key != "A":
                            first_key = key
                            break
                        if key == "E":
                            first_key = "F"
                    #获取group_rank_dict中first_key的ascii码
                    first_key_ascii = ord(first_key)
                    #将first_key_ascii减1，但要确保不超出有效范围
                    first_key_ascii -= 1
                    #检查是否超出有效范围（A=65, B=66, C=67, D=68, E=69）
                    if first_key_ascii < 66:  # 如果小于'B'的ASCII码
                        first_key_ascii = 66  # 设置为'B'
                    #将first_key_ascii转换为字符
                    pro_first_key = chr(first_key_ascii)
                    #获取group_rank_dict中first_key之前的所有的key和Value组成的字符串
                    group_rank_str = ""
                    for key, value in group_rank_dict.items():
                        if key < pro_first_key:
                            group_rank_str += key + str(value)
                        else:
                            break
                    #获取数据库self.handle_sheet表中group_rank包含group_rank_str的所有记录
                    if self.handle_sheet == "ListGroupHierarchy":
                        action_group_hierarchy_records = session.query(ListGroupHierarchy).filter(ListGroupHierarchy.list_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ListSuitHierarchy":
                        action_group_hierarchy_records = session.query(ListSuitHierarchy).filter(ListSuitHierarchy.list_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ListDebugHierarchy":
                        action_group_hierarchy_records = session.query(ListDebugHierarchy).filter(ListDebugHierarchy.list_rank.contains(group_rank_str)).all()
                        #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort+1值均加1
                    max_first_key_value = 0
                    for record in action_group_hierarchy_records:
                        temp_group_rank_dict = parse_group_rank(record.list_rank)
                        if (first_key != "F" and (temp_group_rank_dict[first_key] != 0 or temp_group_rank_dict[pro_first_key] == 0)) or (first_key == "F" and temp_group_rank_dict[pro_first_key] == 0):
                            continue
                        # 处理首部和尾部的特殊情况
                        if first_key == "F":
                            if temp_group_rank_dict[pro_first_key] == 0:
                                continue
                            else:
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num > self.hierarchy_sort: 
                                    record.sort_num += 1
                        else:
                            if (pro_first_key in temp_group_rank_dict and 
                            first_key in temp_group_rank_dict and 
                            temp_group_rank_dict[pro_first_key] > 0 and
                            temp_group_rank_dict[first_key] == 0):
                            #获取temp_group_rank_dict中first_key的Value
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num > self.hierarchy_sort:
                                    record.sort_num += 1

                    #提交修改事务
                    session.commit()
                    #创建新的group_rank
                    temp_group_rank_str2 = self.action_group_selected_rank
                    #获取temp_group_rank_dict
                    temp_group_rank_dict2 = parse_group_rank(temp_group_rank_str2)
                    #修改temp_group_rank_dict中first_key的Value
                    temp_group_rank_dict2[pro_first_key] = max_first_key_value + 1
                    self.sort_num = self.hierarchy_sort+1
                    #将temp_group_rank_dict转换为group_rank_str
                    temp_group_rank_str2 = ""
                    for key, value in temp_group_rank_dict2.items():
                        temp_group_rank_str2 += key + str(value)
                    #将temp_group_rank_str2转换为group_rank
                    self.group_rank = temp_group_rank_str2
                elif self.relate_location_selected == 3:
                    #插入子项
                    #获取group_rank_dict的第一个Value为0的key值
                    first_key = ""
                    for key, value in group_rank_dict.items():
                        if value == 0 and key != "A":
                            first_key = key
                            break
                        if key == "E":
                            return False
                    #获取group_rank_dict中first_key的ascii码
                    first_key_ascii = ord(first_key)
                    #检查是否超出有效范围（A=65, B=66, C=67, D=68, E=69）
                    if first_key_ascii > 68:  # 如果大于'D'的ASCII码
                        return False
                    #将first_key_ascii转换为字符
                    next_first_key = chr(first_key_ascii + 1)
                    #获取group_rank_dict中first_key之前的所有的key和Value组成的字符串
                    group_rank_str = ""
                    for key, value in group_rank_dict.items():
                        if key < first_key:
                            group_rank_str += key + str(value)
                    #获取数据库self.handle_sheet表中group_rank包含group_rank_str的所有记录
                    if self.handle_sheet == "ListGroupHierarchy":
                        action_group_hierarchy_records = session.query(ListGroupHierarchy).filter(ListGroupHierarchy.list_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ListSuitHierarchy":
                        action_group_hierarchy_records = session.query(ListSuitHierarchy).filter(ListSuitHierarchy.list_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ListDebugHierarchy":
                        action_group_hierarchy_records = session.query(ListDebugHierarchy).filter(ListDebugHierarchy.list_rank.contains(group_rank_str)).all()
                    #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort值均加1
                    max_first_key_value = 0
                    max_sort_num = 0
                    for record in action_group_hierarchy_records:
                        temp_group_rank_dict = parse_group_rank(record.list_rank)
                        if (first_key != "E" and (temp_group_rank_dict[first_key] == 0 or temp_group_rank_dict[next_first_key] == 0)) or (first_key == "E" and temp_group_rank_dict[next_first_key] == 0):
                            continue
                        # 处理首部和尾部的特殊情况
                        if first_key == "E":
                            if temp_group_rank_dict[next_first_key] == 0:
                                continue
                            else:
                                next_first_key_value = temp_group_rank_dict[next_first_key]
                                #递归获取最大的next_first_key_value
                                if next_first_key_value > max_first_key_value:
                                    max_first_key_value = next_first_key_value
                                if record.sort_num is not None and record.sort_num > max_sort_num:
                                    max_sort_num = record.sort_num
                        else:
                            if (first_key in temp_group_rank_dict and 
                            next_first_key in temp_group_rank_dict and
                            temp_group_rank_dict[first_key] > 0 and 
                            temp_group_rank_dict[next_first_key] == 0):
                            #获取temp_group_rank_dict中first_key的Value
                                first_key_value = temp_group_rank_dict[first_key]
                                #递归获取最大的first_key_value
                                if first_key_value > max_first_key_value:
                                    max_first_key_value = first_key_value
                                if record.sort_num is not None and record.sort_num > max_sort_num:
                                    max_sort_num = record.sort_num
                    #创建新的group_rank
                    temp_group_rank_str3 = self.action_group_selected_rank
                    #获取temp_group_rank_dict
                    temp_group_rank_dict3 = parse_group_rank(temp_group_rank_str3)
                    #修改temp_group_rank_dict中first_key的Value
                    temp_group_rank_dict3[first_key] = max_first_key_value + 1
                    #将temp_group_rank_dict转换为group_rank_str
                    temp_group_rank_str3 = ""
                    for key, value in temp_group_rank_dict3.items():
                        temp_group_rank_str3 += key + str(value)
                    #将temp_group_rank_str3转换为group_rank
                    self.group_rank = temp_group_rank_str3
                    self.sort_num = max_sort_num + 1
                elif self.relate_location_selected == 4:
                    #插入项
                    #获取group_rank_dict的第一个Value为0的key值
                    self.group_rank = "A0B0C0D0E0"
                    self.sort_num = 1
            else:
                #根据self.action_group_selected_rank和self.relate_location_selected获取行为组Hierarchy级别
                if self.relate_location_selected == 1:
                    #上方插入
                    #获取group_rank_dict的第一个Value为0的key值
                    first_key = ""
                    for key, value in group_rank_dict.items():
                        if value == 0 and key != "A":#因为A是根节点，不能插入到A上方，A0是个人行为组集合
                            first_key = key
                            break
                        if key == "E":
                            first_key = "F"
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
                            group_rank_str += key + str(value)
                    #获取数据库self.handle_sheet表中group_rank包含group_rank_str的所有记录
                    if self.handle_sheet == "ActionsGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ActionsSuitGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsSuitGroupHierarchy).filter(ActionsSuitGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ActionsDebugGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsDebugGroupHierarchy).filter(ActionsDebugGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort值均加1
                    max_first_key_value = 0
                    for record in action_group_hierarchy_records:
                        temp_group_rank_dict = parse_group_rank(record.group_rank)
                        if (first_key != "F" and (temp_group_rank_dict[first_key] != 0 or temp_group_rank_dict[pro_first_key] == 0)) or (first_key == "F" and temp_group_rank_dict[pro_first_key] == 0):
                            continue
                        # 处理首部和尾部的特殊情况
                        if first_key == "F":
                            if temp_group_rank_dict[pro_first_key] == 0:
                                continue
                            else:
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num >= self.hierarchy_sort:
                                    record.sort_num += 1
                        else:
                            if (pro_first_key in temp_group_rank_dict and 
                            first_key in temp_group_rank_dict and 
                            temp_group_rank_dict[pro_first_key] > 0 and
                            temp_group_rank_dict[first_key] == 0) :    
                            #获取temp_group_rank_dict中first_key的Value
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num >= self.hierarchy_sort:
                                    record.sort_num += 1
                    #提交修改事务
                    session.commit()
                    #创建新的group_rank
                    temp_group_rank_str1 = self.action_group_selected_rank
                    #获取temp_group_rank_dict
                    temp_group_rank_dict1 = parse_group_rank(temp_group_rank_str1)
                    #修改temp_group_rank_dict中first_key的Value
                    temp_group_rank_dict1[pro_first_key] = max_first_key_value + 1
                    #将temp_group_rank_dict转换为group_rank_str
                    temp_group_rank_str1 = ""
                    for key, value in temp_group_rank_dict1.items():
                        temp_group_rank_str1 += key + str(value)
                    #将temp_group_rank_str1转换为group_rank
                    self.group_rank = temp_group_rank_str1
                    self.sort_num = self.hierarchy_sort
                elif self.relate_location_selected == 2:
                    #下方插入
                    #获取group_rank_dict的第一个Value为0的key值
                    first_key = ""
                    for key, value in group_rank_dict.items():
                        if value == 0 and key != "A":
                            first_key = key
                            break
                        if key == "E":
                            first_key = "F"
                    #获取group_rank_dict中first_key的ascii码
                    first_key_ascii = ord(first_key)
                    #将first_key_ascii减1，但要确保不超出有效范围
                    first_key_ascii -= 1
                    #检查是否超出有效范围（A=65, B=66, C=67, D=68, E=69）
                    if first_key_ascii < 66:  # 如果小于'A'的ASCII码
                        first_key_ascii = 66  # 设置为'A'
                    #将first_key_ascii转换为字符
                    pro_first_key = chr(first_key_ascii)
                    #获取group_rank_dict中first_key之前的所有的key和Value组成的字符串
                    group_rank_str = ""
                    for key, value in group_rank_dict.items():
                        if key < pro_first_key:
                            group_rank_str += key + str(value)
                    #获取数据库self.handle_sheet表中group_rank包含group_rank_str的所有记录
                    if self.handle_sheet == "ActionsGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ActionsSuitGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsSuitGroupHierarchy).filter(ActionsSuitGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ActionsDebugGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsDebugGroupHierarchy).filter(ActionsDebugGroupHierarchy.group_rank.contains(group_rank_str)).all()
                        #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort+1值均加1
                    max_first_key_value = 0
                    for record in action_group_hierarchy_records:
                        temp_group_rank_dict = parse_group_rank(record.group_rank)
                        if (first_key != "F" and (temp_group_rank_dict[first_key] != 0 or temp_group_rank_dict[pro_first_key] == 0)) or (first_key == "F" and temp_group_rank_dict[pro_first_key] == 0):
                            continue
                        # 处理首部和尾部的特殊情况
                        if first_key == "F":
                            if temp_group_rank_dict[pro_first_key] == 0:
                                continue
                            else:
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num > self.hierarchy_sort:
                                    record.sort_num += 1
                        else:
                            if (pro_first_key in temp_group_rank_dict and 
                            first_key in temp_group_rank_dict and 
                            temp_group_rank_dict[pro_first_key] > 0 and
                            temp_group_rank_dict[first_key] == 0):
                            #获取temp_group_rank_dict中first_key的Value
                                pro_first_key_value = temp_group_rank_dict[pro_first_key]
                                #递归获取最大的first_key_value
                                if pro_first_key_value > max_first_key_value:
                                    max_first_key_value = pro_first_key_value
                                if record.sort_num is not None and record.sort_num > self.hierarchy_sort:
                                    record.sort_num += 1
                    #提交修改事务
                    session.commit()
                    #创建新的group_rank
                    temp_group_rank_str2 = self.action_group_selected_rank
                    #获取temp_group_rank_dict
                    temp_group_rank_dict2 = parse_group_rank(temp_group_rank_str2)
                    #修改temp_group_rank_dict中first_key的Value
                    temp_group_rank_dict2[pro_first_key] = max_first_key_value + 1
                    self.sort_num = self.hierarchy_sort+1
                    #将temp_group_rank_dict转换为group_rank_str
                    temp_group_rank_str2 = ""
                    for key, value in temp_group_rank_dict2.items():
                        temp_group_rank_str2 += key + str(value)
                    #将temp_group_rank_str2转换为group_rank
                    self.group_rank = temp_group_rank_str2
                elif self.relate_location_selected == 3:
                    #插入子项
                    #获取group_rank_dict的第一个Value为0的key值
                    first_key = ""
                    for key, value in group_rank_dict.items():
                        if value == 0 and key != "A":
                            first_key = key
                            break
                        if key == "E":
                            return False
                    #获取group_rank_dict中first_key的ascii码
                    first_key_ascii = ord(first_key)
                    #检查是否超出有效范围（A=65, B=66, C=67, D=68, E=69）
                    if first_key_ascii > 68:  # 如果大于'D'的ASCII码
                        return False
                    #将first_key_ascii转换为字符
                    next_first_key = chr(first_key_ascii + 1)
                    #获取group_rank_dict中first_key之前的所有的key和Value组成的字符串
                    group_rank_str = ""
                    for key, value in group_rank_dict.items():
                        if key < first_key:
                            group_rank_str += key + str(value)
                    #获取数据库self.handle_sheet表中group_rank包含group_rank_str的所有记录
                    if self.handle_sheet == "ActionsGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ActionsSuitGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsSuitGroupHierarchy).filter(ActionsSuitGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    elif self.handle_sheet == "ActionsDebugGroupHierarchy":
                        action_group_hierarchy_records = session.query(ActionsDebugGroupHierarchy).filter(ActionsDebugGroupHierarchy.group_rank.contains(group_rank_str)).all()
                    #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort值均加1
                    max_first_key_value = 0
                    max_sort_num = 0
                    for record in action_group_hierarchy_records:
                        temp_group_rank_dict = parse_group_rank(record.group_rank)
                        if (first_key != "E" and (temp_group_rank_dict[first_key] == 0 or temp_group_rank_dict[next_first_key] == 0)) or (first_key == "E" and temp_group_rank_dict[first_key] == 0):
                            continue
                        # 处理首部和尾部的特殊情况
                        if first_key == "E":
                            if temp_group_rank_dict[first_key] == 0:
                                continue
                            else:
                                first_key_value = temp_group_rank_dict[first_key]
                                #递归获取最大的first_key_value
                                if first_key_value > max_first_key_value:
                                    max_first_key_value = first_key_value
                                if record.sort_num is not None and record.sort_num > max_sort_num:
                                    max_sort_num = record.sort_num
                        else:
                            if (first_key in temp_group_rank_dict and 
                            next_first_key in temp_group_rank_dict and
                            temp_group_rank_dict[first_key] > 0 and 
                            temp_group_rank_dict[next_first_key] == 0):
                            #获取temp_group_rank_dict中first_key的Value
                                first_key_value = temp_group_rank_dict[first_key]
                                #递归获取最大的first_key_value
                                if first_key_value > max_first_key_value:
                                    max_first_key_value = first_key_value
                                if record.sort_num is not None and record.sort_num > max_sort_num:  
                                    max_sort_num = record.sort_num

                    #创建新的group_rank
                    temp_group_rank_str3 = self.action_group_selected_rank
                    #获取temp_group_rank_dict
                    temp_group_rank_dict3 = parse_group_rank(temp_group_rank_str3)
                    #修改temp_group_rank_dict中first_key的Value
                    temp_group_rank_dict3[first_key] = max_first_key_value + 1
                    #将temp_group_rank_dict转换为group_rank_str
                    temp_group_rank_str3 = ""
                    for key, value in temp_group_rank_dict3.items():
                        temp_group_rank_str3 += key + str(value)
                    #将temp_group_rank_str3转换为group_rank
                    self.group_rank = temp_group_rank_str3
                    self.sort_num = max_sort_num + 1
            #创建行为组组套
            if self.handle_sheet == "ActionsGroupHierarchy":
                new_action_group_hierarchy = ActionsGroupHierarchy(
                group_name=self.group_name,
                group_rank=self.group_rank,
                sort_num=self.sort_num,
                doctor_id=self.doctor_id,
                department_id=self.department_id,
                group_note=self.group_note
                )
            elif self.handle_sheet == "ActionsSuitGroupHierarchy":
                new_action_group_hierarchy = ActionsSuitGroupHierarchy(
                    group_name=self.group_name,
                    group_rank=self.group_rank,
                    sort_num=self.sort_num,
                    doctor_id=self.doctor_id,
                    department_id=self.department_id,
                    group_note=self.group_note
                )
            elif self.handle_sheet == "ActionsDebugGroupHierarchy":
                new_action_group_hierarchy = ActionsDebugGroupHierarchy(
                    group_name=self.group_name,
                    group_rank=self.group_rank,
                    sort_num=self.sort_num,
                    doctor_id=self.doctor_id,
                    department_id=self.department_id,
                    group_note=self.group_note
                )
            elif self.handle_sheet == "ListSuitHierarchy":
                new_action_group_hierarchy = ListSuitHierarchy(
                    group_id=self.action_group_id,
                    list_name=self.group_name,
                    list_rank=self.group_rank,
                    user_id=self.doctor_id,
                    department_id=self.department_id,
                    group_note=self.group_note
                )
            elif self.handle_sheet == "ListGroupHierarchy":
                new_action_group_hierarchy = ListGroupHierarchy(
                    group_id=self.action_group_id,
                    list_name=self.group_name,
                    list_rank=self.group_rank,
                    user_id=self.doctor_id,
                    department_id=self.department_id,
                    group_note=self.group_note
                )
            elif self.handle_sheet == "ActionsDebugGroupHierarchy":
                new_action_group_hierarchy = ActionsDebugGroupHierarchy(
                    group_id=self.action_group_id,
                    list_name=self.group_name,
                    list_rank=self.group_rank,
                    user_id=self.doctor_id,
                    department_id=self.department_id,
                    group_note=self.group_note
                )
            #提交创建事务
            session.add(new_action_group_hierarchy)
            session.commit()
            self.select_mode.destroy()
            return True
        except Exception as e:
            logger.error(f"新建行为组组套失败: {str(e)}")
            print("错误", f"新建行为组组套失败: {str(e)}")
            print(traceback.format_exc())
        finally:
            if session:
                session.close()