#添加对home_tab.py中_save_action_group方法的支持
from datetime import datetime
from tkinter import messagebox
from gui.tabs.Hierarchyutils import iid_to_group_rank
from utils.logger import Logger,logger
from models.actions import ActionGroup, ActionsGroupHierarchy
from config.config_manager import ConfigManager
from database.db_manager import DatabaseManager

class home_tab_func:
    """用于支持home_tab.py中相关方法的实现"""
    
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
        Raises:
            ValueError: 当必要参数为空或无效时
        """
        # 验证必要参数，使用for循环验证，同时提示用户哪个参数为空
        if not all([group_name, group_user_id, group_department_id, action_group_selected_rank,action_tree_selected_iid,action_group_type,sort_num]):
            logger.error("行为组信息无效：必要参数不能为空")
            debugtxt = ""
            for param, value in [("group_name", group_name), ("group_user_id", group_user_id), ("group_department_id", group_department_id), ("action_group_selected_rank", action_group_selected_rank),("action_tree_selected_iid",action_tree_selected_iid),("action_group_type",action_group_type),("sort_num",sort_num)]:
                if not value:
                    debugtxt += f"参数{param}为空\n"
            messagebox.showinfo("提示", debugtxt)
            return False
            
        # 验证自动执行时间
        if is_auto and not auto_time:
            logger.error("行为组信息无效：auto为True时，auto_time不能为空")
            return False
            
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
        
        config_manager = ConfigManager()
        db_path = config_manager.get_value('System', 'DataSource')
        encryption_key = config_manager.get_value('Security', 'DBEncryptionKey')
        db_manager = DatabaseManager(db_path, encryption_key)
        db_manager.initialize()
        self.session = db_manager.Session()
        return self.session
    
    def _save_action_group(self)->bool:
        """保存行为组"""
        #判断行为组任务类型
        if self.action_group_type == 1:
            #新增保存
            #获取数据库会话
            session = self._get_session()
            if not session:
                return False
            #生成新增行为组记录
            new_action_group = ActionGroup(
                action_list_group_name=self.group_name,
                action_list_group_note=self.group_desc,
                is_auto=self.is_auto,
                auto_time=self.auto_time,
                user_id=self.group_user_id,
                department_id=self.group_department_id,
                setup_time=datetime.now(),
                group_rank_id=self.action_group_selected_rank,
                sort_num=self.sort_num,
            )
            session.add(new_action_group)
            session.commit()
            return True
        elif self.action_group_type == 2:
            #修改保存
            #判断self.action_tree_selected_iid是来源于Action_list_group表还是来源于ActionsGroupHierarchy表
            if self.action_tree_selected_iid.startswith("group_"):
                #来源于Action_list_group表
                group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
                if group:
                    #更新group表的记录
                    group.action_list_group_name = self.group_name
                    group.action_list_group_note = self.group_desc
                    group.is_auto = self.is_auto
                    group.auto_time = self.auto_time
                    group.update_time = datetime.now()
                    session.commit()
                    return True
                else:
                    logger.error(f"无法找到行为组记录: {self.action_tree_selected_iid}")
                    return False
            else:
                #来源于ActionsGroupHierarchy表
                hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_group_hierarchy_id).first()
                if hierarchy:
                    #更新hierarchy表的记录
                    hierarchy.group_name = self.group_name
                    hierarchy.group_note = self.group_desc
                    hierarchy.doctor_id = self.group_user_id
                    hierarchy.update_time = datetime.now()
                    session.commit()
                    return True
                else:
                    logger.error(f"无法找到行为组记录: {self.action_tree_selected_iid}")
                    return False
        else:
            logger.error(f"无效的行为组类型: {self.action_group_type}")
            return False
    def _delete_action_group(self)->bool:
        """删除行为组"""
        #获取数据库会话
        session = self._get_session()
        if not session:
            return False
        #如果选中的是来源于Action_list_group表
        if self.action_tree_selected_iid.startswith("group_"):
            #删除action_list_group表的记录
            group = session.query(ActionGroup).filter_by(id=self.action_group_id).first()
            if group:
                session.delete(group)
                session.commit()
            else:
                logger.error(f"无法找到行为组记录: {self.action_group_id}")
                return False
        elif self.action_tree_selected_iid.startswith("A"):
            #删除ActionsGroupHierarchy表的记录
            hierarchy = session.query(ActionsGroupHierarchy).filter_by(id=self.action_group_hierarchy_id).first()
            if hierarchy:
                session.delete(hierarchy)
                session.commit()
            else:
                logger.error(f"无法找到行为组记录: {self.action_group_hierarchy_id}")
                return False
        else:   
            logger.error(f"无效的行为组类型: {self.action_group_type}")
            return False
        return True

    def _session_close(self):
        """关闭数据库会话"""
        if self.session:
            self.session.close()
            self.session = None
        return True
    def _capture_image(self):
        """图像采集"""
        messagebox.showinfo("提示", "图像采集功能待实现")

def _home_capture_image(action_group_id:int):
    """图像采集"""
    #获取配置文件中的
    messagebox.showinfo("提示", "图像采集功能待实现")

def _home_delete_action_group(action_group_id:int):
    """删除行为组"""
    messagebox.showinfo("提示", "删除行为组功能待实现")

def _home_save_action_group(action_group_id:int):
    """保存行为组"""