import tkinter as tk
from tkinter import ttk
from config.config_manager import ConfigManager
from gui.tabs.Hierarchyutils import iid_to_group_rank, parse_group_rank
from models.actions import ActionsGroupHierarchy
#获取全局变量
import globalvariable
#获取数据库
from database.db_manager import DatabaseManager
#获取logger
from utils.logger import logger

#新建行为组组套
class ActionGroupHierarchy_Manager:
    """新建行为组Hierarchy"""
    def __init__(self,root,action_group_selected_rank,relate_location_selected,hierarchy_sort):
        self.action_group_selected_rank = action_group_selected_rank
        self.relate_location_selected = relate_location_selected
        self.hierarchy_sort = hierarchy_sort
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

        #根据self.action_group_selected_rank和self.relate_location_selected获取行为组Hierarchy级别
        if self.relate_location_selected == 1:
            #上方插入
            #获取group_rank_dict的第一个Value为0的key值
            first_key = ""
            for key, value in group_rank_dict.items():
                if value == 0:
                    first_key = key
                    break
            #获取group_rank_dict中first_key的ascii码
            first_key_ascii = ord(first_key)
            #将first_key_ascii减1
            first_key_ascii -= 1
            #将first_key_ascii转换为字符
            pro_first_key = chr(first_key_ascii)
            #获取group_rank_dict中pro_first_key之前的所有的key和Value组成的字符串
            group_rank_str = ""
            for key, value in group_rank_dict.items():
                if key < pro_first_key:
                    group_rank_str += key + str(value)
            #获取数据库ActionsGroupHierarchy表中group_rank包含group_rank_str的所有记录
            action_group_hierarchy_records = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_rank.contains(group_rank_str)).all()
            #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort值均加1
            max_first_key_value = 0
            for record in action_group_hierarchy_records:
                temp_group_rank_dict = parse_group_rank(record.group_rank)
                if temp_group_rank_dict[pro_first_key] > 0 and temp_group_rank_dict[first_key] == 0:    
                    #获取temp_group_rank_dict中first_key的Value
                    pro_first_key_value = temp_group_rank_dict[pro_first_key]
                    #递归获取最大的first_key_value
                    if pro_first_key_value > max_first_key_value:
                        max_first_key_value = pro_first_key_value
                    if record.sort_num >= self.hierarchy_sort:
                        record.sort_num += 1
                else: 
                    pass
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
                if value == 0:
                    first_key = key
                    break
            #获取group_rank_dict中first_key的ascii码
            first_key_ascii = ord(first_key)
            #将first_key_ascii加1
            first_key_ascii -= 1
            #将first_key_ascii转换为字符
            pro_first_key = chr(first_key_ascii)
            #获取group_rank_dict中first_key之前的所有的key和Value组成的字符串
            group_rank_str = ""
            for key, value in group_rank_dict.items():
                if key < pro_first_key:
                    group_rank_str += key + str(value)
            #获取数据库ActionsGroupHierarchy表中group_rank包含group_rank_str的所有记录
            action_group_hierarchy_records = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_rank.contains(group_rank_str)).all()
                #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort+1值均加1
            max_first_key_value = 0
            for record in action_group_hierarchy_records:
                temp_group_rank_dict = parse_group_rank(record.group_rank)
                if temp_group_rank_dict[pro_first_key] > 0 and temp_group_rank_dict[first_key] == 0 :
                    #获取temp_group_rank_dict中first_key的Value
                    pro_first_key_value = temp_group_rank_dict[pro_first_key]
                    #递归获取最大的first_key_value
                    if pro_first_key_value > max_first_key_value:
                        max_first_key_value = pro_first_key_value
                    if record.sort_num > self.hierarchy_sort:
                        record.sort_num += 1
                else: 
                    pass
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
                if value == 0:
                    first_key = key
                    break
            #获取group_rank_dict中first_key的ascii码
            first_key_ascii = ord(first_key)
            #将first_key_ascii加1
            first_key_ascii += 1
            #将first_key_ascii转换为字符
            next_first_key = chr(first_key_ascii)
            #获取group_rank_dict中next_first_key之前的所有的key和Value组成的字符串
            group_rank_str = ""
            for key, value in group_rank_dict.items():
                if key < next_first_key:
                    group_rank_str += key + str(value)
            #获取数据库ActionsGroupHierarchy表中group_rank包含group_rank_str的所有记录
            action_group_hierarchy_records = session.query(ActionsGroupHierarchy).filter(ActionsGroupHierarchy.group_rank.contains(group_rank_str)).all()
            #修改action_group_hierarchy_records的sort_num值，使sort_num值大于self.hierarchy_sort值均加1
            max_first_key_value = 0
            max_sort_num = 0
            for record in action_group_hierarchy_records:
                temp_group_rank_dict = parse_group_rank(record.group_rank)
                if temp_group_rank_dict[first_key] > 0 and temp_group_rank_dict[next_first_key] == 0:
                    #获取temp_group_rank_dict中first_key的Value
                    first_key_value = temp_group_rank_dict[first_key]
                    #递归获取最大的first_key_value
                    if first_key_value > max_first_key_value:
                        max_first_key_value = first_key_value
                    if record.sort_num > max_sort_num:
                        max_sort_num = record.sort_num
                    if record.sort_num >= self.hierarchy_sort:
                        record.sort_num += 1
                else: 
                    pass
            #创建新的group_rank
            temp_group_rank_str3 = self.action_group_selected_rank
            #获取temp_group_rank_dict
            temp_group_rank_dict3 = parse_group_rank(temp_group_rank_str3)
            #修改temp_group_rank_dict中first_key的Value
            temp_group_rank_dict3[next_first_key] = max_first_key_value + 1
            #将temp_group_rank_dict转换为group_rank_str
            temp_group_rank_str3 = ""
            for key, value in temp_group_rank_dict3.items():
                temp_group_rank_str3 += key + str(value)
            #将temp_group_rank_str3转换为group_rank
            self.group_rank = temp_group_rank_str3
            self.sort_num = max_sort_num + 1
        #创建行为组组套
        new_action_group_hierarchy = ActionsGroupHierarchy(
            group_name=self.group_name,
            group_rank=self.group_rank,
            sort_num=self.sort_num,
            doctor_id=self.doctor_id,
            department_id=self.department_id,
            group_note=self.group_note
        )
        #提交创建事务
        session.add(new_action_group_hierarchy)
        session.commit()
        #关闭session
        session.close()
        self.select_mode.destroy()